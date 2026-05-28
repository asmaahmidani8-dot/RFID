"""
test_oracle.py — Test connexion Oracle GLTEST + OFs Released
GE Healthcare Buc | Projet RFID
"""

import os
import sys
import platform
from dotenv import load_dotenv

# ── Charger .env ──────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

HOST    = os.getenv("ORACLE_HOST",    "qahceaexa-scan.ge-healthcare.net")
PORT    = int(os.getenv("ORACLE_PORT", "1521"))
SERVICE = os.getenv("ORACLE_SERVICE", "ebs_gltest")
USER    = os.getenv("ORACLE_USER",    "SSO250028087")
PASS    = os.getenv("ORACLE_PASSWORD", "")

# ── Import oracledb ───────────────────────────────────────────
try:
    import oracledb
except ImportError:
    print("[ERR] oracledb non installe  →  pip install oracledb")
    sys.exit(1)

print("=" * 60)
print("  TEST ORACLE GLTEST — GE Healthcare Buc")
print("=" * 60)
print(f"  OS      : {platform.system()} {platform.machine()}")
print(f"  Host    : {HOST}:{PORT}/{SERVICE}")
print(f"  User    : {USER}")
print("=" * 60)

# ── Oracle Instant Client (thick mode — obligatoire GE) ───────
IC_PATHS = {
    "Windows": r"C:\Users\250028087\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_0",
    "Linux":   "/home/ge/instantclient_23_26",
}

ic_path = IC_PATHS.get(platform.system(), "")
if ic_path and os.path.isdir(ic_path):
    try:
        oracledb.init_oracle_client(lib_dir=ic_path)
        print(f"[OK] Instant Client  : {ic_path}")
    except Exception as e:
        print(f"[WARN] init_oracle_client : {e}")
else:
    print(f"[WARN] Instant Client introuvable : {ic_path}")
    print("       Mode thin — peut echouer avec Oracle GE (verifier 10g)")

# ── Mot de passe ──────────────────────────────────────────────
if not PASS:
    import getpass
    PASS = getpass.getpass(f"\nPassword Oracle ({USER}) : ")

# ── Connexion + requete ───────────────────────────────────────
print(f"\n[..] Connexion Oracle...")

try:
    dsn  = f"{HOST}:{PORT}/{SERVICE}"
    conn = oracledb.connect(user=USER, password=PASS, dsn=dsn)
    print(f"[OK] Connecte a Oracle {SERVICE} !\n")

    cur = conn.cursor()
    print("[..] Requete OFs Released BUC (org 1731, 90 jours)...")

    sql = """
        SELECT
            wen.WIP_ENTITY_NAME                              AS num_job,
            ite.SEGMENT1                                     AS item_code,
            ite.DESCRIPTION                                  AS description,
            'OP' || LPAD(wop.OPERATION_SEQ_NUM, 2, '0')     AS operation_code,
            NVL(wop.QUANTITY_COMPLETED, 0)                   AS qty_faite,
            wdj.START_QUANTITY                               AS qty_totale,
            wdj.SCHEDULED_COMPLETION_DATE                    AS date_besoin
        FROM
            apps.WIP_DISCRETE_JOBS   wdj,
            apps.WIP_ENTITIES        wen,
            apps.MTL_SYSTEM_ITEMS_B  ite,
            apps.WIP_OPERATIONS      wop
        WHERE
            wdj.WIP_ENTITY_ID    = wen.WIP_ENTITY_ID
            AND wdj.PRIMARY_ITEM_ID  = ite.INVENTORY_ITEM_ID
            AND wdj.ORGANIZATION_ID  = ite.ORGANIZATION_ID
            AND wdj.WIP_ENTITY_ID    = wop.WIP_ENTITY_ID
            AND wdj.STATUS_TYPE      = 3
            AND wdj.ORGANIZATION_ID  = '1731'
            AND wdj.CREATION_DATE    > SYSDATE - 90
            AND NVL(wop.QUANTITY_COMPLETED, 0) < wdj.START_QUANTITY
        ORDER BY
            wdj.SCHEDULED_COMPLETION_DATE ASC,
            wen.WIP_ENTITY_NAME ASC,
            wop.OPERATION_SEQ_NUM ASC
        FETCH FIRST 30 ROWS ONLY
    """

    cur.execute(sql)
    rows = cur.fetchall()

    print(f"[OK] {len(rows)} ligne(s) retournee(s)\n")
    print(f"{'NUM JOB':<22} {'ITEM':<16} {'OP':>5}  {'QF':>5} {'QT':>5}  DATE BESOIN")
    print("-" * 75)

    for row in rows:
        num_job, item_code, desc, op_code, qty_f, qty_t, date_b = row
        db_str = date_b.strftime("%Y-%m-%d") if date_b else "—"
        print(f"{str(num_job):<22} {str(item_code):<16} {str(op_code):>5}  "
              f"{int(qty_f):>5} {int(qty_t):>5}  {db_str}")

    cur.close()
    conn.close()
    print("\n[OK] Test Oracle termine avec succes")

except oracledb.Error as e:
    print(f"\n[ERR Oracle] {e}")
    print("\nCauses possibles :")
    print("  ORA-01017 → mot de passe incorrect dans .env")
    print("  ORA-12541 → port 1521 bloque (verifier : nc -zv host 1521)")
    print("  DPY-3015  → Oracle Instant Client manquant ou mauvais chemin")

except Exception as e:
    print(f"\n[ERR] {e}")
