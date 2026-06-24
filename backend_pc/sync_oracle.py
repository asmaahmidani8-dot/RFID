"""
sync_oracle.py — Synchronisation Oracle GLTEST → MySQL rfid_buc
GE Healthcare Buc | Ligne Pristina

Ce script :
  1. Se connecte à Oracle GLTEST
  2. Récupère tous les OFs Released (STATUS_TYPE=3) de l'org BUC (1731)
  3. Les insère / met à jour dans MySQL jobs_planning sur le Raspberry Pi
"""

import sys
import os
import getpass
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Dépendances ───────────────────────────────────────────────
try:
    import oracledb
    import platform
    # Mode thick — nécessaire pour Oracle GE Healthcare (verifier 10g)
    if platform.system() == "Windows":
        try:
            oracledb.init_oracle_client(
                lib_dir=r"C:\Users\250028087\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_0"
            )
        except Exception:
            pass   # Déjà initialisé
    elif platform.system() == "Linux":
        try:
            oracledb.init_oracle_client(
                lib_dir="/home/ge/instantclient_23_26"
            )
            print("[OK] Oracle Instant Client ARM64 chargé")
        except Exception as e:
            print(f"[WARN] init_oracle_client : {e}")
except ImportError:
    print("[ERR] oracledb non installé → pip install oracledb")
    sys.exit(1)

try:
    import mysql.connector
except ImportError:
    print("[ERR] mysql-connector non installé → pip install mysql-connector-python")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# CONFIG ORACLE (GLTEST)
# ══════════════════════════════════════════════════════════════
ORACLE_HOST    = os.getenv("ORACLE_HOST",    "qahceaexa-scan.ge-healthcare.net")
ORACLE_PORT    = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "ebs_gltest")
ORACLE_USER    = os.getenv("ORACLE_USER",    "SSO250028087")
ORACLE_PASS    = os.getenv("ORACLE_PASSWORD", "")   # via .env ou saisie

ORACLE_ORG     = "1731"   # BUC Pristina
ORACLE_JOURS   = 90       # OFs créés dans les 90 derniers jours


# ══════════════════════════════════════════════════════════════
# CONFIG MYSQL (Raspberry Pi)
# ══════════════════════════════════════════════════════════════
MYSQL_HOST   = os.getenv("MYSQL_HOST",   "raspberrypi.local")
MYSQL_PORT   = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER   = os.getenv("MYSQL_USER",   "rfid_app")
MYSQL_PASS   = os.getenv("MYSQL_PASSWORD", "rfid_pass")
MYSQL_DB     = os.getenv("MYSQL_DB",     "rfid_buc")


# ══════════════════════════════════════════════════════════════
# REQUÊTE ORACLE — OFs Released + opérations ouvertes
# ══════════════════════════════════════════════════════════════
SQL_ORACLE = f"""
    SELECT
        wen.WIP_ENTITY_NAME                              AS of_number,
        ite.SEGMENT1                                     AS item_code,
        SUBSTR(ite.DESCRIPTION, 1, 150)                  AS item_desc,
        'OP' || LPAD(wop.OPERATION_SEQ_NUM, 2, '0')      AS operation_code,
        NVL(wop.QUANTITY_COMPLETED, 0)                   AS qty_faite,
        wdj.START_QUANTITY                               AS qty_totale,
        CAST(wdj.SCHEDULED_COMPLETION_DATE AS DATE)      AS date_besoin
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
        AND wdj.ORGANIZATION_ID  = '{ORACLE_ORG}'
        AND wdj.CREATION_DATE    > SYSDATE - {ORACLE_JOURS}
        AND NVL(wop.QUANTITY_COMPLETED, 0) < wdj.START_QUANTITY
    ORDER BY
        wdj.SCHEDULED_COMPLETION_DATE ASC,
        wen.WIP_ENTITY_NAME ASC,
        wop.OPERATION_SEQ_NUM ASC
"""


# ══════════════════════════════════════════════════════════════
# CONNEXIONS
# ══════════════════════════════════════════════════════════════
def connecter_oracle(password):
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    print(f"[..] Oracle  → {ORACLE_HOST}/{ORACLE_SERVICE}")
    conn = oracledb.connect(
        user=ORACLE_USER,
        password=password,
        dsn=dsn
    )
    print(f"[OK] Oracle connecté")
    return conn


def connecter_mysql():
    print(f"[..] MySQL   → {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset="utf8mb4"
    )
    print(f"[OK] MySQL connecté")
    return conn


# ══════════════════════════════════════════════════════════════
# SYNC PRINCIPALE
# ══════════════════════════════════════════════════════════════
def synchroniser(conn_oracle, conn_mysql):
    now = datetime.now()
    print(f"\n{'='*55}")
    print(f"  SYNC Oracle → MySQL  —  {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}")

    # ── 1. Récupérer depuis Oracle ────────────────────────────
    print(f"\n[..] Requête Oracle (org {ORACLE_ORG}, {ORACLE_JOURS} jours)...")
    cur_oracle = conn_oracle.cursor()
    cur_oracle.execute(SQL_ORACLE)
    rows = cur_oracle.fetchall()
    cur_oracle.close()
    print(f"[OK] {len(rows)} ligne(s) Oracle (OF × opération)")

    if not rows:
        print("[INFO] Aucun OF Released trouvé — rien à synchroniser")
        return

    # ── 2. Insérer / mettre à jour dans MySQL ────────────────
    cur_mysql = conn_mysql.cursor()
    nb_new = nb_upd = nb_skip = nb_err = 0

    # SQL INSERT avec ON DUPLICATE KEY UPDATE
    # La clé unique est (of_number, operation_code)
    sql_upsert = """
        INSERT INTO jobs_planning
            (organisation, of_number, operation_code,
             item_code, item_desc, statut,
             qty_totale, qty_faite, date_besoin, synced_le)
        VALUES
            (%s, %s, %s, %s, %s, 'RELEASED', %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            item_code   = VALUES(item_code),
            item_desc   = VALUES(item_desc),
            qty_totale  = VALUES(qty_totale),
            qty_faite   = VALUES(qty_faite),
            date_besoin = VALUES(date_besoin),
            synced_le   = VALUES(synced_le)
    """
    # Note : ON DUPLICATE KEY ne change pas le statut si déjà ASSIGNE/TERMINE
    # → mais met à jour les quantités et dates

    for row in rows:
        of_number, item_code, item_desc, operation_code, qty_faite, qty_totale, date_besoin = row
        try:
            cur_mysql.execute(sql_upsert, (
                "BXD",
                str(of_number),
                str(operation_code),
                str(item_code) if item_code else None,
                str(item_desc)[:150] if item_desc else None,
                float(qty_totale) if qty_totale else 0,
                float(qty_faite)  if qty_faite  else 0,
                date_besoin if date_besoin else None,
                now
            ))

            if cur_mysql.rowcount == 1:
                nb_new += 1
                print(f"  + {of_number:<20} {operation_code}  [{item_code}]")
            elif cur_mysql.rowcount == 2:
                nb_upd += 1
            else:
                nb_skip += 1

        except Exception as e:
            nb_err += 1
            print(f"  [ERR] {of_number}/{operation_code} : {e}")

    conn_mysql.commit()

    # ── 3. Fermer les jobs RELEASED dans MySQL mais absents d'Oracle ──
    # Construire la liste des clés Oracle (of_number, operation_code)
    cles_oracle = set()
    for row in rows:
        of_number_r, _, _, operation_code_r, _, _, _ = row
        cles_oracle.add((str(of_number_r), str(operation_code_r)))

    # Récupérer tous les jobs RELEASED dans MySQL
    cur_mysql.execute("""
        SELECT of_number, operation_code FROM jobs_planning
        WHERE statut = 'RELEASED'
    """)
    jobs_mysql = cur_mysql.fetchall()

    nb_closed = 0
    for (of_m, op_m) in jobs_mysql:
        if (str(of_m), str(op_m)) not in cles_oracle:
            cur_mysql.execute("""
                UPDATE jobs_planning SET statut = 'CLOSED'
                WHERE of_number = %s AND operation_code = %s AND statut = 'RELEASED'
            """, (of_m, op_m))
            nb_closed += 1

    conn_mysql.commit()
    cur_mysql.close()

    # ── 4. Résumé ─────────────────────────────────────────────
    print(f"\n{'─'*45}")
    print(f"  Nouveaux insérés  : {nb_new}")
    print(f"  Mis à jour        : {nb_upd}")
    print(f"  Inchangés         : {nb_skip}")
    print(f"  Fermés (CLOSED)   : {nb_closed}")
    print(f"  Erreurs           : {nb_err}")
    print(f"  Total Oracle      : {len(rows)}")
    print(f"{'─'*45}")


# ══════════════════════════════════════════════════════════════
# ROUTING D'OFs PRÉCIS — appelé à l'ASSIGNATION (par app.py)
# ══════════════════════════════════════════════════════════════
def fetch_routing_for_of(of_numbers, password=None):
    """Au moment où le WS assigne un job à un chariot : récupère le routing
    complet (séquence des ops) de ce/ces OF et le stocke dans job_routing.
    Sert à connaître l'ORDRE des moves. Retourne le nb de lignes écrites."""
    if not of_numbers:
        return 0
    pwd = password or ORACLE_PASS
    if not pwd:
        print("[WARN] fetch_routing_for_of : pas de mot de passe Oracle (.env)")
        return 0

    of_list = [str(o) for o in of_numbers]
    conn_o = connecter_oracle(pwd)
    conn_m = connecter_mysql()
    try:
        in_clause = ",".join(f":{i+1}" for i in range(len(of_list)))
        sql = f"""
            SELECT wen.WIP_ENTITY_NAME    AS of_number,
                   wop.OPERATION_SEQ_NUM  AS seq,
                   wop.COUNT_POINT_TYPE   AS count_point,
                   wop.BACKFLUSH_FLAG     AS backflush
            FROM apps.WIP_OPERATIONS wop, apps.WIP_ENTITIES wen
            WHERE wop.WIP_ENTITY_ID = wen.WIP_ENTITY_ID
              AND wen.WIP_ENTITY_NAME IN ({in_clause})
            ORDER BY wen.WIP_ENTITY_NAME, wop.OPERATION_SEQ_NUM
        """
        cur_o = conn_o.cursor()
        cur_o.execute(sql, of_list)
        rows = cur_o.fetchall()
        cur_o.close()

        cur_m = conn_m.cursor()
        sql_upsert = """
            INSERT INTO job_routing (of_number, operation_seq_num, count_point, backflush)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                count_point = VALUES(count_point),
                backflush   = VALUES(backflush)
        """
        n = 0
        for of_number, seq, count_point, backflush in rows:
            cur_m.execute(sql_upsert, (
                str(of_number), int(seq),
                int(count_point) if count_point is not None else None,
                int(backflush)   if backflush   is not None else None,
            ))
            n += 1
        conn_m.commit()
        cur_m.close()
        print(f"[OK] Routing assignation : {n} op(s) pour {len(of_list)} OF")
        return n
    finally:
        conn_o.close()
        conn_m.close()


# ══════════════════════════════════════════════════════════════
# SN AUTO pour une op SÉRIALISÉE (appelé par le bouton Move)
# ══════════════════════════════════════════════════════════════
def get_sn_for_op(of_number, to_seq, password=None):
    """Pour une op potentiellement sérialisée : trouve le composant série requis
    + son locator d'appro, et retourne 1 n° de série dispo (str), ou None
    (si pas de composant série à cet op, ou aucun SN dispo au bon locator)."""
    pwd = password or ORACLE_PASS
    if not pwd:
        return None
    conn = connecter_oracle(pwd)
    try:
        cur = conn.cursor()
        # 1) Composant SÉRIALISÉ requis à cet op + son locator d'appro
        cur.execute("""
            SELECT msi.segment1, wro.supply_locator_id
            FROM   apps.wip_requirement_operations wro
            JOIN   apps.wip_entities we
                   ON we.wip_entity_id = wro.wip_entity_id
            JOIN   apps.mtl_system_items_b msi
                   ON msi.inventory_item_id = wro.inventory_item_id
                  AND msi.organization_id   = wro.organization_id
            WHERE  we.wip_entity_name = :1
              AND  wro.operation_seq_num = :2
              AND  msi.serial_number_control_code > 1
            ORDER BY wro.inventory_item_id
        """, [str(of_number), int(to_seq)])
        comp_row = cur.fetchone()
        if not comp_row:
            return None   # pas de composant série à cet op → move normal
        composant, loc_id = comp_row

        # 2) 1 SN dispo de ce composant, au locator d'appro
        cur.execute("""
            SELECT msn.serial_number
            FROM   apps.mtl_serial_numbers msn
            JOIN   apps.mtl_system_items_b msi
                   ON msi.inventory_item_id = msn.inventory_item_id
                  AND msi.organization_id   = msn.current_organization_id
            WHERE  msi.segment1 = :1
              AND  msn.current_status = 3
              AND  msn.current_locator_id = :2
            ORDER BY msn.serial_number
        """, [composant, loc_id])
        sn_row = cur.fetchone()
        if sn_row:
            print(f"[OK] SN auto pour {of_number}/op{to_seq} (composant {composant}) : {sn_row[0]}")
            return sn_row[0]
        print(f"[WARN] Aucun SN dispo pour {composant} au locator {loc_id}")
        return None
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════
# AFFICHAGE JOBS_PLANNING
# ══════════════════════════════════════════════════════════════
def afficher_jobs(conn_mysql):
    cur = conn_mysql.cursor()
    cur.execute("""
        SELECT of_number, item_code, operation_code,
               qty_faite, qty_totale, date_besoin, statut
        FROM jobs_planning
        ORDER BY date_besoin ASC, of_number ASC, operation_code ASC
    """)
    rows = cur.fetchall()
    cur.close()

    print(f"\n{'='*90}")
    print(f"  JOBS_PLANNING — {len(rows)} enregistrement(s)")
    print(f"{'='*90}")
    print(f"{'OF':<22} {'ITEM':<14} {'OP':>5}  {'QF':>5}{'QT':>6}  {'DATE BESOIN':<12}  STATUT")
    print("-"*90)
    for r in rows:
        of, item, op, qf, qt, db, st = r
        db_str = db.strftime("%Y-%m-%d") if db else "—"
        print(f"{str(of):<22} {str(item):<14} {str(op):>5}  {str(int(qf or 0)):>5}{str(int(qt or 0)):>6}  {db_str:<12}  {st}")
    print("="*90)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  SYNC ORACLE GLTEST → MySQL rfid_buc")
    print("="*55)

    # Mot de passe Oracle (depuis .env ou saisie)
    password = ORACLE_PASS
    if not password:
        password = getpass.getpass(f"Password Oracle ({ORACLE_USER}) : ")

    try:
        conn_oracle = connecter_oracle(password)
        conn_mysql  = connecter_mysql()

        synchroniser(conn_oracle, conn_mysql)
        afficher_jobs(conn_mysql)

        conn_oracle.close()
        conn_mysql.close()
        print("\n[OK] Sync terminée\n")

    except oracledb.Error as e:
        print(f"\n[ERR Oracle] {e}")
    except mysql.connector.Error as e:
        print(f"\n[ERR MySQL]  {e}")
    except Exception as e:
        print(f"\n[ERR] {e}")
