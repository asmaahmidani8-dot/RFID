"""
TEST 2 — Mesure de la distance de lecture
Teste la fiabilite a differentes distances
"""

import serial
import serial.tools.list_ports
import time
import json

PORT = None
BAUD = 115200


def trouver_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if any(x in p.description for x in ["CP210", "CH340", "USB Serial"]):
            return p.device
    return ports[0].device if ports else None


def lire_uid(ser, timeout=3):
    """Attend un UID pendant X secondes. Retourne None si rien."""
    ser.timeout = timeout
    line = ser.readline().decode("utf-8", errors="ignore").strip()
    if not line:
        return None
    try:
        data = json.loads(line)
        return data.get("uid")
    except:
        if len(line) >= 8:
            return line
        return None


def main():
    global PORT

    print("=" * 50)
    print("  TEST DISTANCE — Pepper C1")
    print("=" * 50)

    if PORT is None:
        PORT = trouver_port()

    if PORT is None:
        print("ERREUR : Aucun lecteur detecte")
        return

    ser = serial.Serial(PORT, BAUD, timeout=3)
    distances = [1, 2, 3, 4, 5, 6, 7, 8, 10]
    resultats = {}

    print("\nTest de fiabilite par distance.")
    print("Pour chaque distance : 10 tentatives de lecture.\n")

    for d in distances:
        input(f"Place le badge a {d} cm du lecteur puis appuie sur ENTREE...")
        ok = 0
        print(f"  Test en cours (10 tentatives)...", end="", flush=True)

        for i in range(10):
            uid = lire_uid(ser, timeout=1)
            if uid:
                ok += 1
                print(".", end="", flush=True)
            else:
                print("x", end="", flush=True)
            time.sleep(0.2)

        resultats[d] = ok
        print(f"  {ok}/10")

    ser.close()

    print("\n" + "=" * 50)
    print("  RESULTATS")
    print("=" * 50)
    for d, ok in resultats.items():
        barre = "#" * ok + "-" * (10 - ok)
        statut = "OK" if ok >= 8 else ("LIMITE" if ok >= 5 else "ECHEC")
        print(f"  {d:2d} cm : [{barre}] {ok}/10  {statut}")

    print("\nDistance recommandee pour installation :")
    fiables = [d for d, ok in resultats.items() if ok >= 8]
    if fiables:
        print(f"  Jusqu'a {max(fiables)} cm (lecture fiable a 80%+)")
    else:
        print("  Aucune distance fiable — verifier le badge et le lecteur")


if __name__ == "__main__":
    main()
