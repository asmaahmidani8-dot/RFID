"""
TEST 1 — Lecture directe Pepper C1 via port COM
Lancer ce script pour voir les UIDs bruts
"""

import serial
import serial.tools.list_ports
import time
import json

# ─── CONFIG ───────────────────────────────────────
PORT = None   # laisser None pour détection automatique
BAUD = 115200
# ──────────────────────────────────────────────────


def trouver_port_auto():
    """Cherche automatiquement le port du Pepper C1."""
    ports = serial.tools.list_ports.comports()
    print("Ports COM détectés :")
    for p in ports:
        print(f"  {p.device} — {p.description}")

    # Chercher CP210x ou CH340 (drivers Pepper C1)
    for p in ports:
        if any(x in p.description for x in ["CP210", "CH340", "USB Serial", "UART"]):
            print(f"\nPepper C1 trouvé sur : {p.device}")
            return p.device

    if ports:
        print(f"\nPremier port disponible : {ports[0].device}")
        return ports[0].device

    return None


def main():
    global PORT

    print("=" * 50)
    print("  TEST PEPPER C1 — Lecture UID via USB")
    print("=" * 50)

    # Détection automatique
    if PORT is None:
        PORT = trouver_port_auto()

    if PORT is None:
        print("\nERREUR : Aucun port COM détecté")
        print("Vérifier que le Pepper C1 est branché en USB")
        input("Appuyer sur ENTREE pour quitter...")
        return

    print(f"\nConnexion sur {PORT} ({BAUD} baud)...")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=2)
        print("Connecte !")
    except Exception as e:
        print(f"ERREUR connexion : {e}")
        input("Appuyer sur ENTREE pour quitter...")
        return

    print("\nPose un badge sur le lecteur...\n")
    print("-" * 50)

    nb_scans = 0

    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            print(f"Brut recu : {line}")

            # Essayer de parser JSON
            try:
                data = json.loads(line)
                if "uid" in data:
                    nb_scans += 1
                    uid = data["uid"]
                    print(f"\n  Badge #{nb_scans} detecte !")
                    print(f"  UID  : {uid}")
                    print(f"  Type : {data.get('type', 'inconnu')}")
                    print(f"  TS   : {data.get('ts', 'inconnu')}")
                    print("-" * 50)

            except json.JSONDecodeError:
                # Pas du JSON — afficher quand meme
                if line.startswith("UID") or len(line) in [8, 14]:
                    nb_scans += 1
                    print(f"\n  Badge #{nb_scans} detecte !")
                    print(f"  UID brut : {line}")
                    print("-" * 50)

        except KeyboardInterrupt:
            print("\n\nArret manuel.")
            break
        except Exception as e:
            print(f"Erreur lecture : {e}")
            time.sleep(1)

    ser.close()
    print(f"\nTotal badges lus : {nb_scans}")


if __name__ == "__main__":
    main()
