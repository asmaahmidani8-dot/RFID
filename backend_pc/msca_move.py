"""
msca_move.py — Move Transaction MSCA via telnet (STANDALONE / TEST)
GE Healthcare Buc | Ligne Pristina | RFID

But : valider la navigation MSCA en isolé AVANT de l'intégrer à l'app.
   Tu donnes  Job + To Seq + Qty  → le script écrit le move dans MSCA
   et lit l'écran jusqu'à voir "Txn Success".

Lancer (sur le Pi, réseau usine) :
   cd ~/backend_test
   python3 msca_move.py

Navigation validée (capturée écran par écran le 2026-06-17) :
   Device List → 1 (Default)
   Login : user 250028087 + mdp + Database GLTEST (déjà pré-rempli → Entrée)
   Responsibilities → 1 (GEMSEU_INV_MSCA_FR_GEMS Mobile User)
   Menu → 3 (Manufacturing) → 1 (Assy & Material Txn) → 1 (Move Assy)
   Org Code → BXD
   Job → [Assembly/From Seq/From Step auto] → To Seq → To Step "To move"
   → Entrée jusqu'à <Save> → "Txn Success"
"""

import os
import re
import socket
import time
import getpass
from datetime import datetime, time as dtime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
MWA_HOST = os.getenv("MSCA_HOST", "ebsgltest.ge-healthcare.net")  # GLTEST (validé)
MWA_PORT = int(os.getenv("MSCA_PORT", "10200"))

MSCA_USER = os.getenv("MSCA_USER", "250028087")       # SANS préfixe SSO
MSCA_PASS = os.getenv("MSCA_PASSWORD", "")
MSCA_ORG  = os.getenv("MSCA_ORG", "BXD")

# Codes de navigation (menus) — faciles à ajuster si la config MSCA change
NAV_DEVICE   = "1"        # Device List → 1 (Default)
NAV_RESP     = "1"        # Responsibilities → 1 (Mobile User)
NAV_MFG      = "3"        # Menu → 3 (Manufacturing)
NAV_ASSY_MAT = "1"        # → 1 (Assy & Material Txn)
NAV_MOVE     = "1"        # → 1 (Move Assy)
TO_STEP      = "To move"  # champ To Step (toujours "To move")

# Marqueurs d'écran
OK_MARKER  = "txn success"
ERR_MARKER = ["error", "invalid", "no result", "required field",
              "cannot", "already logged", "authentication failed"]

# Maintenance MSCA (bloquer 10h58 → 11h06, comme HINO)
MAINT_START = dtime(10, 58)
MAINT_END   = dtime(11, 6)

TIMEOUT_CONNECT = 10
TIMEOUT_READ    = 1.0   # ← détection "fin d'écran" : 1s au lieu de 5s = ~4x plus rapide
READ_SIZE       = 4096


# ══════════════════════════════════════════════════════════════
# Session telnet MSCA
# ══════════════════════════════════════════════════════════════
class MscaTelnet:
    def __init__(self, host=MWA_HOST, port=MWA_PORT, verbose=True):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.sock = None
        self.screens = []

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=TIMEOUT_CONNECT)
        self.sock.settimeout(TIMEOUT_READ)
        self._log(f"[CONNECT] {self.host}:{self.port}")
        time.sleep(0.5)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None
                self._log("[DISCONNECT]")

    def read_screen(self, wait=0.4):
        """Lit l'écran MSCA (tout ce que le serveur envoie).
        wait = petite pause pour laisser l'écran arriver ; la boucle recv lit
        ensuite tout ce qui vient jusqu'au TIMEOUT_READ."""
        time.sleep(wait)
        data = b""
        try:
            while True:
                chunk = self.sock.recv(READ_SIZE)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        screen = data.decode("utf-8", errors="replace")
        self.screens.append(screen)
        if self.verbose:
            print("┌─ ÉCRAN " + "─" * 50)
            print(screen)
            print("└" + "─" * 58)
        return screen

    def send(self, text="", label=""):
        """Envoie une valeur + Entrée (comme taper au clavier)."""
        self.sock.sendall((text + "\r\n").encode("utf-8"))
        self._log(f"[SEND]{' '+label if label else ''} → {text!r}")
        time.sleep(0.15)

    def send_ctrl_n(self):
        """Ctrl+N = nouveau move sans logout (pour enchaîner — usage futur)."""
        self.sock.sendall(b"\x0e")  # Ctrl+N
        self._log("[SEND] Ctrl+N")
        time.sleep(0.3)

    def _log(self, msg):
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")


# ══════════════════════════════════════════════════════════════
# Vérifs
# ══════════════════════════════════════════════════════════════
def is_maintenance():
    now = datetime.now().time()
    return MAINT_START <= now <= MAINT_END


def _has(screen, markers):
    s = (screen or "").lower()
    if isinstance(markers, str):
        markers = [markers]
    return any(m in s for m in markers)


def _menu_number(screen, keyword):
    """Lit un MENU MSCA et retourne le NUMÉRO de la ligne qui contient `keyword`.
    Ex : ligne '3. Manufacturing' + keyword='manufacturing' → '3'.
    Marche quel que soit l'ordre des options (pilotage par LECTURE, pas par position).
    None si l'option n'est pas trouvée à l'écran."""
    kw = keyword.lower()
    for line in (screen or "").splitlines():
        m = re.match(r"\s*(\d+)\s*[\.\)\-]?\s+(.*)", line)
        if m and kw in m.group(2).lower():
            return m.group(1)
    return None


def _choose(session, screen, keyword, confirm, fallback=None, max_reads=5):
    """Choisit dans un menu l'option qui contient `keyword` (numéro lu à l'écran),
    l'envoie, puis ATTEND l'écran suivant (`confirm`). Retourne (ok, écran, erreur).
    Si le keyword est introuvable et qu'un `fallback` (numéro fixe) est donné, on l'essaie."""
    num = _menu_number(screen, keyword)
    if not num and fallback:
        num = fallback
    if not num:
        return False, screen, f"Option '{keyword}' introuvable dans le menu"
    session.send(num, f"→{keyword} (n°{num})")
    found, scr = _wait(session, confirm, max_reads=max_reads)
    if not found:
        return False, scr, f"Écran attendu après '{keyword}' non atteint (n°{num} inattendu ?)"
    return True, scr, None


# ══════════════════════════════════════════════════════════════
# LE MOVE — navigation SYNCHRONISÉE (anti-désync)
# On ATTEND le bon écran (par son texte) AVANT chaque saisie.
# ══════════════════════════════════════════════════════════════
def _wait(session, markers, max_reads=8, wait=0.4):
    """Lit l'écran JUSQU'À voir un des marqueurs. Retourne (trouvé, dernier_écran)."""
    acc = ""
    scr = ""
    for _ in range(max_reads):
        scr = session.read_screen(wait=wait)
        acc += "\n" + scr
        if _has(acc, markers):
            return True, scr
    return False, scr


def do_move(session, user, password, org, job, to_seq, qty=1, sn=None, database="GLTEST"):
    """
    Effectue UNE Move Transaction WIP via MSCA.
    ANTI-DÉSYNC : avant chaque saisie, on attend le bon écran (marqueur texte).
    Si l'op est SÉRIALISÉE (écran Components / Parent SN apparaît), il faut
    fournir `sn` (un n° de série dispo du composant) : Parent SN négligé (Entrée)
    puis saisie du SN du composant.
    Retourne : { "success": bool, "message": str }
    """
    print(f"\n{'='*60}")
    print(f"  MOVE  |  Job {job}  →  To Seq {to_seq}  |  Qty {qty}  |  Org {org}")
    print(f"{'='*60}\n")

    session.connect()
    try:
        # 1) Device List → Default
        _wait(session, ["device list", "symbol device"], max_reads=4)
        session.send(NAV_DEVICE, "Device→Default")

        # 2) Login (écran User Name / Password / Database GLTEST)
        _wait(session, ["user name", "applications"], max_reads=5)
        session.send(user, "Username")
        time.sleep(0.4)
        session.send(password, "Password")
        # Database GLTEST pré-rempli : le login se valide soit directement,
        # soit après une Entrée. On s'ADAPTE (au lieu d'envoyer une Entrée en trop).
        # APRÈS login on peut tomber sur : la LISTE des responsabilités,
        # OU directement le MENU Mobile User (compte mono-responsabilité → pas de liste).
        MENU_MARKERS = ["pick/ship", "put away"]   # = on est dans le menu Mobile User
        found, scr = _wait(session, ["responsib", "invalid password"] + MENU_MARKERS, max_reads=3)
        if _has(scr, "invalid password"):
            return {"success": False, "message": "Login refusé (user/mdp)"}
        if not found:
            session.send("", "Database (Entrée)")
            found, scr = _wait(session, ["responsib"] + MENU_MARKERS, max_reads=4)

        # 3) Responsibilité — INTELLIGENT (lecture de l'écran) :
        #    - si on est DÉJÀ dans le menu (mono-responsabilité) → on ne touche à RIEN
        #    - sinon on est sur la LISTE → on choisit "Mobile User" (numéro LU à l'écran)
        if not _has(scr, MENU_MARKERS):
            num = _menu_number(scr, "mobile user") or NAV_RESP
            session.send(num, f"Resp→Mobile User (n°{num})")
            found, scr = _wait(session, MENU_MARKERS, max_reads=5)
            if not found:
                return {"success": False,
                        "message": "Menu Mobile User non atteint après choix responsabilité"}

        # 4) Manufacturing — numéro LU à l'écran (pas une position fixe)
        ok, scr, err = _choose(session, scr, "manufacturing",
                               ["assy & material", "work order-less", "resource txn"],
                               fallback=NAV_MFG)
        if not ok:
            return {"success": False, "message": err}

        # 5) Assy & Material Txn
        ok, scr, err = _choose(session, scr, "assy & material",
                               ["complete assy", "scrap assy", "reject assy", "move assy"],
                               fallback=NAV_ASSY_MAT)
        if not ok:
            return {"success": False, "message": err}

        # 6) Move Assy → on arrive au formulaire (org ou directement From/To Seq)
        ok, scr, err = _choose(session, scr, "move assy",
                               ["from seq", "to seq", "organization", "org code", "job"],
                               fallback=NAV_MOVE)
        if not ok:
            return {"success": False, "message": err}

        # 7) Organisation : si l'écran demande encore l'org → BXD (sinon on est déjà au form)
        if not _has(scr, ["from seq", "to seq"]):
            session.send(org, "Org Code")
            _wait(session, ["from seq", "to seq", "job"], max_reads=5)

        # 8) Job → To Seq → To Step
        session.send(job, "Job")           # auto-remplit Assembly/From Seq/From Step
        found, scr = _wait(session, ["to seq", "from step", "assembly", "no result", "invalid"], max_reads=5)
        if _has(scr, ["no result", "invalid"]):
            return {"success": False, "message": f"Job introuvable : {job}"}
        session.send(str(to_seq), "To Seq")
        _wait(session, ["to step", "overcompl", "uom"], max_reads=4)
        session.send(TO_STEP, "To Step = 'To move'")

        # 9) Finalisation : on avance vers <Save>, en gérant l'écran SÉRIE
        #    (Parent SN / SN) DÈS qu'il apparaît — robuste au timing.
        sn_done = False
        scr = session.read_screen(wait=1.8)
        for i in range(14):
            if _has(scr, OK_MARKER) or _has(scr, ERR_MARKER):
                break
            # Écran SÉRIE détecté → Parent SN négligé + saisie du SN (une seule fois)
            if _has(scr, "parent sn") and not sn_done:
                if not sn:
                    return {"success": False,
                            "message": f"Op {to_seq} sérialisée : un n° de série (SN) requis mais non fourni"}
                print(f"\n🔢 Écran SÉRIE détecté → Parent SN (négligé) + SN : {sn}")
                session.send("", "Parent SN (négligé → Entrée)")
                session.read_screen(wait=1.0)
                session.send(str(sn), f"SN composant = {sn}")
                sn_done = True
                scr = session.read_screen(wait=1.5)
                continue
            # Sinon : Entrée pour avancer vers <Save>
            session.send("", f"Entrée vers <Save> #{i+1}")
            scr = session.read_screen(wait=1.5)

        # 10) Verdict
        if _has(scr, OK_MARKER):
            print("\n✅ [OK] 'Txn Success' détecté")
            return {"success": True, "message": "Txn Success"}
        if _has(scr, ERR_MARKER):
            msg = " ".join(scr.split())[:200]
            print(f"\n❌ [ERR] {msg}")
            return {"success": False, "message": msg}
        print("\n⚠️ [WARN] Ni succès ni erreur connue (voir écrans ci-dessus)")
        return {"success": False, "message": "Réponse inattendue"}

    except Exception as e:
        print(f"\n❌ [EXCEPTION] {e}")
        return {"success": False, "message": f"Exception : {e}"}
    finally:
        session.disconnect()


# ══════════════════════════════════════════════════════════════
# MAIN — test interactif
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  TEST MOVE MSCA (standalone)  —  GE Healthcare Buc RFID")
    print(f"  MWA : {MWA_HOST}:{MWA_PORT}")
    print("=" * 60)

    if is_maintenance():
        print("\n[STOP] Fenêtre maintenance MSCA (10h58–11h06) — réessaie après 11h06.")
        raise SystemExit

    user = input(f"\nUsername MSCA [{MSCA_USER}] : ").strip() or MSCA_USER
    pwd  = MSCA_PASS or getpass.getpass("Password MSCA : ")
    org  = input(f"Org Code [{MSCA_ORG}] : ").strip() or MSCA_ORG
    job  = input("Job / OF (ex: FL666PTN_Iter8.4) : ").strip()
    tseq = input("To Seq (l'op du chariot, ex: 20) : ").strip()
    qty  = input("Qty [1] : ").strip() or "1"
    sn   = input("N° de série SN (si op SÉRIALISÉE comme 110, ex PXB0201_08 ; sinon Entrée) : ").strip() or None

    if not job or not tseq:
        print("[ERR] Job et To Seq obligatoires.")
        raise SystemExit

    session = MscaTelnet(verbose=True)
    res = do_move(session, user, pwd, org, job, tseq, qty, sn)

    print("\n" + "=" * 60)
    print(f"  RÉSULTAT : {'✅ SUCCÈS' if res['success'] else '❌ ÉCHEC'}  —  {res['message']}")
    print("=" * 60 + "\n")
