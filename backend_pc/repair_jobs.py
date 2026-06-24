"""
repair_jobs.py — Répare les jobs_planning marqués ASSIGNE à tort
GE Healthcare Buc | Ligne Pristina | RFID

Contexte :
  L'ancien bug d'assignation faisait passer TOUTES les opérations d'un OF
  en ASSIGNE (au lieu de la seule opération choisie). Le sync Oracle
  préserve le statut ASSIGNE → ces lignes restent bloquées pour toujours.

Ce script :
  1. Trouve les jobs_planning ASSIGNE qui n'ont AUCUNE entrée réelle
     dans cart_mission_jobs (= cassés par l'ancien bug)
  2. Les remet en RELEASED
  3. Affiche un avant / après

Lancer sur le Pi :
  python3 /home/ge/backend/repair_jobs.py
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "rfid_app"),
        password=os.getenv("MYSQL_PASSWORD", "rfid_pass"),
        database=os.getenv("MYSQL_DB", "rfid_buc"),
        charset="utf8mb4"
    )


# Jobs ASSIGNE sans entrée correspondante dans cart_mission_jobs = cassés
SQL_SELECT = """
    SELECT jp.of_number, jp.operation_code
    FROM jobs_planning jp
    LEFT JOIN cart_mission_jobs cmj
           ON cmj.of_number = jp.of_number
          AND cmj.operation_code = jp.operation_code
    WHERE jp.statut = 'ASSIGNE' AND cmj.id IS NULL
    ORDER BY jp.of_number, jp.operation_code
"""

SQL_UPDATE = """
    UPDATE jobs_planning jp
    LEFT JOIN cart_mission_jobs cmj
           ON cmj.of_number = jp.of_number
          AND cmj.operation_code = jp.operation_code
    SET jp.statut = 'RELEASED'
    WHERE jp.statut = 'ASSIGNE' AND cmj.id IS NULL
"""


def afficher_comptes(cur, titre):
    cur.execute("SELECT statut, COUNT(*) AS n FROM jobs_planning GROUP BY statut")
    comptes = cur.fetchall()
    print(f"\n  {titre}")
    for statut, n in comptes:
        print(f"    {statut:<12} : {n}")


def main():
    print("=" * 55)
    print("  RÉPARATION jobs_planning — ASSIGNE cassés → RELEASED")
    print("=" * 55)

    db = get_db()
    cur = db.cursor()

    afficher_comptes(cur, "AVANT :")

    # 1. Aperçu de ce qui va être réparé
    cur.execute(SQL_SELECT)
    casses = cur.fetchall()
    print(f"\n  → {len(casses)} ligne(s) ASSIGNE sans mission réelle (à réparer) :")
    for of_number, op in casses[:50]:
        print(f"      {of_number:<20} {op}")
    if len(casses) > 50:
        print(f"      ... et {len(casses) - 50} de plus")

    if not casses:
        print("\n  ✅ Rien à réparer — aucune ligne cassée.")
        cur.close(); db.close()
        return

    # 2. Réparation
    cur.execute(SQL_UPDATE)
    db.commit()
    print(f"\n  ✅ {cur.rowcount} ligne(s) remise(s) en RELEASED.")

    afficher_comptes(cur, "APRÈS :")

    cur.close()
    db.close()
    print("\n[OK] Réparation terminée.\n")


if __name__ == "__main__":
    main()
