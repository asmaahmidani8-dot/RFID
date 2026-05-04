"""
TEST 3 — Simuler un scan sans badge physique
Envoie de faux UIDs au serveur Flask pour tester le dashboard
"""

import requests
import time
import random

URL_FLASK = "http://localhost:5000/api/scan"

# Faux badges enregistres
FAUX_BADGES = [
    {"uid": "A3F2C1D4", "chariot": "CHR-F1-OP20-1"},
    {"uid": "B7E4A2F1", "chariot": "CHR-F1-OP20-2"},
    {"uid": "C1D9B3E8", "chariot": "CHR-F2-OP10-1"},
    {"uid": "D4A1C7B2", "chariot": "CHR-P1-OP70-1"},
    {"uid": "E8F3B2A9", "chariot": "CHR-F3-1"},
]

def simuler_scan(badge, scanner_id="SCAN_SUPERMARCHE"):
    """Envoie un scan simule au serveur Flask."""
    payload = {
        "uid"       : badge["uid"],
        "scanner_id": scanner_id,
        "type"      : "MIFARE_CLASSIC_1K",
    }
    try:
        r = requests.post(URL_FLASK, json=payload, timeout=3)
        data = r.json()
        print(f"  Envoye : {badge['uid']} ({badge['chariot']}) → {data['status']}")
        return data
    except requests.ConnectionError:
        print("  ERREUR : Serveur Flask non joignable")
        print("  Lancer d'abord : python backend/app.py")
        return None
    except Exception as e:
        print(f"  ERREUR : {e}")
        return None


def menu():
    print("\n" + "=" * 45)
    print("  SIMULATEUR DE SCANS RFID")
    print("=" * 45)
    print("  1. Simuler 1 scan (badge aleatoire)")
    print("  2. Simuler sequence complete (5 scans)")
    print("  3. Simuler boucle automatique")
    print("  4. Choisir un badge specifique")
    print("  0. Quitter")
    print("=" * 45)
    return input("  Choix : ").strip()


def main():
    print("\nTest de connexion au serveur Flask...")
    try:
        r = requests.get("http://localhost:5000/api/test", timeout=2)
        print(f"  Flask OK — {r.json()['message']}")
    except:
        print("  ATTENTION : Flask ne repond pas")
        print("  Lance d'abord : python backend/app.py")
        print("  On continue quand meme pour les tests...\n")

    while True:
        choix = menu()

        if choix == "0":
            print("Au revoir.")
            break

        elif choix == "1":
            badge = random.choice(FAUX_BADGES)
            print(f"\nSimulation scan — {badge['chariot']}")
            simuler_scan(badge)

        elif choix == "2":
            print("\nSequence complete — 5 scans differents :")
            scanners = [
                "SCAN_SUPERMARCHE",
                "SCAN_ZONE_OP20",
                "SCAN_ZONE_OP70",
                "SCAN_ZONE_OP90",
                "SCAN_SUPERMARCHE",
            ]
            for i, (badge, scanner) in enumerate(zip(FAUX_BADGES, scanners)):
                print(f"\n  Scan {i+1}/5 — Scanner : {scanner}")
                simuler_scan(badge, scanner)
                time.sleep(1)
            print("\nSequence terminee — ouvrir http://localhost:5000")

        elif choix == "3":
            print("\nBoucle automatique — CTRL+C pour arreter")
            try:
                i = 0
                while True:
                    badge = FAUX_BADGES[i % len(FAUX_BADGES)]
                    simuler_scan(badge)
                    i += 1
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\nBoucle arretee.")

        elif choix == "4":
            print("\nBadges disponibles :")
            for i, b in enumerate(FAUX_BADGES):
                print(f"  {i+1}. {b['uid']} — {b['chariot']}")
            choix_badge = input("Numero du badge : ").strip()
            try:
                idx = int(choix_badge) - 1
                badge = FAUX_BADGES[idx]
                simuler_scan(badge)
            except:
                print("Choix invalide.")


if __name__ == "__main__":
    main()
