"""
Test connexion Oracle GLTEST — OFs Released BUC
"""

import oracledb
import getpass
import os
import platform
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ── Connexion ────────────────────────────────────────────────
HOST    = "qahceaexa-scan.ge-healthcare.net"
PORT    = 1521
SERVICE = "ebs_gltest"
print("=" * 60)
print("Connexion Oracle GLTEST — GE Healthcare")
print("=" * 60)
USER     = os.getenv("ORACLE_USER", "SSO250028087")
PASSWORD = os.getenv("ORACLE_PASSWORD") or getpass.getpass(f"Password SSO ({USER}) : ")

try:
    # Mode thick — Oracle Instant Client (Windows ou Linux ARM64)
    if platform.system() == "Windows":
        try:
            oracledb.init_oracle_client(
                lib_dir=r"C:\Users\250028087\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_0"
            )
        except Exception:
            pass   # Deja initialise
    elif platform.system() == "Linux":
        try:
            oracledb.init_oracle_client(
                lib_dir="/home/ge/instantclient_23_26"
            )
            print("[OK] Oracle Instant Client ARM64 charge")
        except Exception as e:
            print(f"[WARN] init_oracle_client : {e}")

    dsn = f"{HOST}:{PORT}/{SERVICE}"
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=dsn)
    print(f"[OK] Connecte a Oracle GLTEST ({SERVICE})")

    cursor = conn.cursor()

    # ── Requete OFs Released BUC (org 1731) ─────────────────
    sql = """
        SELECT
            wen.WIP_ENTITY_NAME                              AS num_job,
            ite.SEGMENT1                                     AS item_code,
            ite.DESCRIPTION                                  AS description,
            'OP' || LPAD(wop.OPERATION_SEQ_NUM, 2, '0')     AS operation_code,
            wop.OPERATION_SEQ_NUM                            AS op_seq,
            NVL(wop.QUANTITY_COMPLETED, 0)                   AS qty_faite,
            wdj.START_QUANTITY                               AS qty_totale,
            wdj.SCHEDULED_COMPLETION_DATE                    AS date_besoin,
            wdj.CREATION_DATE                                AS date_creation
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
    """

    cursor.execute(sql)
    rows = cursor.fetchall()

    print(f"\n[OFs Released BUC (org 1731) — {len(rows)} lignes]\n")
    print(f"{'NUM JOB':<20} {'ITEM CODE':<15} {'OP':>5} {'QTY_F':>6} {'QTY_T':>6}  DESCRIPTION")
    print("-" * 90)

    for row in rows:
        num_job, item_code, description, op_code, op_seq, qty_faite, qty_totale, date_besoin, date_creation = row
        print(f"{str(num_job):<20} {str(item_code):<15} {str(op_code):>5} {str(int(qty_faite)):>6} {str(int(qty_totale)):>6}  {str(description)[:30]}")

    cursor.close()
    conn.close()

except oracledb.Error as e:
    print(f"[ERR Oracle] {e}")
except Exception as e:
    print(f"[ERR] {e}")
