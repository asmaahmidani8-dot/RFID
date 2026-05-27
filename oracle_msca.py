"""
oracle_msca.py — Move Transaction automatique via MWA MSCA
GE Healthcare Buc | Ligne Pristina

Connexion directe au MWA (port 10400) — remplace Velocity + Keyence
"""

import socket
import time
import getpass
from datetime import datetime, time as dtime

# ── CONFIG MWA ────────────────────────────────────────────────
# GLTEST  (remplace par l'adresse donnée par Keyence)
MWA_HOST_TEST = "ebsmwaexpgltest.ge-healthcare.net"   # ← à confirmer
MWA_HOST_PROD = "ebsmwaexpglprod.ge-healthcare.net"
MWA_PORT      = 10400

# Mode actif
MWA_HOST = MWA_HOST_TEST   # changer en PROD pour la production

# ── MAINTENANCE MSCA (bloquer 10h58 → 11h06) ─────────────────
MAINT_START = dtime(10, 58)
MAINT_END   = dtime(11, 6)

# ── TIMEOUTS ─────────────────────────────────────────────────
TIMEOUT_CONNECT = 10    # secondes
TIMEOUT_READ    = 5     # secondes entre les écrans
READ_SIZE       = 4096  # octets par lecture


# ══════════════════════════════════════════════════════════════
# Classe principale
# ══════════════════════════════════════════════════════════════
class MscaSession:
    """
    Connexion socket au MWA Oracle MSCA.
    Simule la navigation clavier d'un opérateur dans MSCA.
    """

    def __init__(self, host=MWA_HOST, port=MWA_PORT):
        self.host    = host
        self.port    = port
        self.sock    = None
        self.log     = []

    # ── Connexion ─────────────────────────────────────────────
    def connect(self):
        self.sock = socket.create_connection(
            (self.host, self.port),
            timeout=TIMEOUT_CONNECT
        )
        self.sock.settimeout(TIMEOUT_READ)
        self._log(f"[CONNECT] {self.host}:{self.port}")
        time.sleep(0.5)

    def disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            self._log("[DISCONNECT]")

    # ── Lire l'écran MSCA ─────────────────────────────────────
    def read_screen(self, wait=1.0):
        time.sleep(wait)
        data = b""
        try:
            while True:
                chunk = self.sock.recv(READ_SIZE)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass   # fin de la réponse
        screen = data.decode("utf-8", errors="replace")
        self._log(f"[SCREEN]\n{screen}")
        return screen

    # ── Envoyer une valeur + Entrée ───────────────────────────
    def send(self, text=""):
        msg = (text + "\r\n").encode("utf-8")
        self.sock.sendall(msg)
        self._log(f"[SEND] {repr(text)}")
        time.sleep(0.3)

    # ── Envoyer touche fonction (F1-F12) ──────────────────────
    # Les codes varient selon config MWA — adapter si besoin
    FKEYS = {
        "F1":  "\x1bOP",
        "F2":  "\x1bOQ",
        "F3":  "\x1bOR",
        "F4":  "\x1bOS",
        "F5":  "\x1b[15~",
        "F6":  "\x1b[17~",
        "F7":  "\x1b[18~",
        "F8":  "\x1b[19~",
        "F9":  "\x1b[20~",
        "F10": "\x1b[21~",
        "F11": "\x1b[23~",
        "F12": "\x1b[24~",
    }

    def send_fkey(self, key):
        code = self.FKEYS.get(key.upper(), "")
        if code:
            self.sock.sendall(code.encode("utf-8"))
            self._log(f"[FKEY] {key}")
            time.sleep(0.3)
        else:
            self._log(f"[WARN] Touche inconnue : {key}")

    # ── Log interne ───────────────────────────────────────────
    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.log.append(line)
        print(line)


# ══════════════════════════════════════════════════════════════
# Vérifications avant exécution
# ══════════════════════════════════════════════════════════════
def is_maintenance_window():
    """Retourne True si on est dans la fenêtre maintenance MSCA."""
    now = datetime.now().time()
    if MAINT_START <= now <= MAINT_END:
        print(f"[WAIT] Maintenance MSCA {MAINT_START}→{MAINT_END} — pause")
        return True
    return False


# ══════════════════════════════════════════════════════════════
# Move Transaction MSCA — Navigation écran par écran
# ══════════════════════════════════════════════════════════════
def do_move_transaction(session, user, password, org,
                         of_number, from_op, to_op, qty):
    """
    Navigue dans MSCA pour effectuer une Move Transaction.

    Paramètres :
        user       : compte Oracle MSCA (ex: SSO250028087)
        password   : mot de passe Oracle MSCA
        org        : organisation (ex: BUC ou 1731)
        of_number  : numéro OF (ex: WO-12345)
        from_op    : opération source (ex: 10)
        to_op      : opération destination (ex: 20)
        qty        : quantité à mouvementer (ex: 1)
    """

    print(f"\n{'='*55}")
    print(f"  MOVE TRANSACTION")
    print(f"  OF: {of_number}  OP: {from_op}→{to_op}  QTY: {qty}")
    print(f"{'='*55}\n")

    session.connect()

    try:
        # ── Écran 1 : Connexion MWA ───────────────────────────
        screen = session.read_screen(wait=1.5)

        # Envoi username
        session.send(user)
        screen = session.read_screen()

        # Envoi password
        session.send(password)
        screen = session.read_screen()

        # Organisation
        session.send(org)
        screen = session.read_screen()

        # ── Écran 2 : Menu principal ──────────────────────────
        # Naviguer vers Move Transactions WIP
        # (le numéro de menu dépend de ta config MSCA — à adapter)
        session.send("")          # Entrée pour valider l'org
        screen = session.read_screen()

        # ── Écran 3 : Saisie Move Transaction ─────────────────
        # Numéro de job
        session.send(of_number)
        screen = session.read_screen()

        # Opération source
        session.send(str(from_op))
        screen = session.read_screen()

        # Opération destination
        session.send(str(to_op))
        screen = session.read_screen()

        # Quantité
        session.send(str(qty))
        screen = session.read_screen()

        # ── Confirmation ──────────────────────────────────────
        session.send("")   # Entrée = confirmer
        screen = session.read_screen(wait=2.0)

        # Vérifier le succès dans la réponse écran
        if "success" in screen.lower() or "complete" in screen.lower():
            print("[OK] Move Transaction effectuée avec succès")
            return True
        else:
            print("[WARN] Réponse inattendue — vérifier manuellement")
            print(screen[:300])
            return False

    except Exception as e:
        print(f"[ERR] {e}")
        return False

    finally:
        session.disconnect()


# ══════════════════════════════════════════════════════════════
# TEST — Connexion simple (sans Move Transaction)
# Pour voir les écrans MSCA et adapter la navigation
# ══════════════════════════════════════════════════════════════
def test_connexion():
    """
    Test de connexion pure — affiche ce que renvoie MSCA écran par écran.
    Permet de cartographier les menus MSCA avant de coder la navigation.
    """
    print("=" * 55)
    print("  TEST CONNEXION MWA MSCA GLTEST")
    print("=" * 55)

    USER     = input("Username MSCA : ") or "SSO250028087"
    PASSWORD = getpass.getpass("Password MSCA : ")
    ORG      = input("Organisation [BUC] : ") or "BUC"

    session = MscaSession()
    session.connect()

    print("\n[>>] Écran initial MWA :")
    screen = session.read_screen(wait=2.0)

    print("\n[>>] Envoi username...")
    session.send(USER)
    screen = session.read_screen()

    print("\n[>>] Envoi password...")
    session.send(PASSWORD)
    screen = session.read_screen()

    print("\n[>>] Envoi organisation...")
    session.send(ORG)
    screen = session.read_screen(wait=2.0)

    print("\n[>>] Appui Entrée...")
    session.send("")
    screen = session.read_screen(wait=2.0)

    print("\n[>>] Navigation interactive (tape les valeurs, vide = F3, 'exit' = quitter) :")
    while True:
        val = input("  > ")
        if val.lower() == "exit":
            break
        elif val == "":
            session.send_fkey("F3")
        else:
            session.send(val)
        session.read_screen()

    session.disconnect()
    print("\n[FIN] Test terminé")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  oracle_msca.py — GE Healthcare Buc RFID")
    print("  MWA :", MWA_HOST, "Port :", MWA_PORT)
    print("=" * 55)
    print("\n  1. Test connexion (voir les écrans MSCA)")
    print("  2. Test Move Transaction complet")
    choix = input("\nChoix [1/2] : ").strip()

    if choix == "1":
        test_connexion()

    elif choix == "2":
        if is_maintenance_window():
            print("[STOP] Fenêtre maintenance — réessayer après 11h06")
        else:
            USER     = input("Username MSCA : ") or "SSO250028087"
            PASSWORD = getpass.getpass("Password MSCA : ")
            ORG      = input("Organisation [BUC] : ") or "BUC"
            OF       = input("Numéro OF : ")
            FROM_OP  = input("Opération source (ex: 10) : ")
            TO_OP    = input("Opération destination (ex: 20) : ")
            QTY      = input("Quantité [1] : ") or "1"

            session = MscaSession()
            do_move_transaction(
                session, USER, PASSWORD, ORG,
                OF, FROM_OP, TO_OP, QTY
            )
