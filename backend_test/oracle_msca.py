"""
oracle_msca.py — Worker de transactions MSCA (file oracle_move_queue)
GE Healthcare Buc | Ligne Pristina | RFID

UN SEUL worker tourne en arrière-plan. Il prend les moves en file UN PAR UN
(jamais 2 sessions telnet MSCA en même temps → pas de désync) :

    exe_flag :  N = Not done (à traiter)
                P = Pending  (en cours d'exécution telnet)
                D = Done     (succès Oracle)
                E = Error    (échec après tentatives)

Cycle : N → P → do_move() → D (ok) ou E (échec).
Chaque tentative est tracée dans oracle_transaction_logs (OK / RETRY / ERROR).
Quand D : cart_mission_jobs.statut = 'MOVE_DONE' (l'op suivante du job devient prête).

Lancement :  cd ~/backend_test && python3 oracle_msca.py
"""
import os
import time
import traceback
from datetime import datetime

from dotenv import load_dotenv
import mysql.connector

import msca_move
import sync_oracle

# .env du dossier parent (~/.env), comme app.py
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

POLL_SECONDS = 3          # fréquence de scrutation de la file quand elle est vide
MAX_RETRY    = 3          # nb de tentatives avant de marquer E (Error)
MSCA_USER    = os.getenv("MSCA_USER", "250028087")
MSCA_PASS    = os.getenv("MSCA_PASSWORD", "")
MSCA_ORG     = os.getenv("MSCA_ORG", "BXD")
MSCA_DB      = os.getenv("MSCA_DATABASE", "GLTEST")
DRY_RUN      = os.getenv("MSCA_DRY_RUN", "false").lower() == "true"


def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "rfid_app"),
        password=os.getenv("MYSQL_PASSWORD", "rfid_pass"),
        database=os.getenv("MYSQL_DB", "rfid_buc"),
        charset="utf8mb4",
    )


def _op_num(code):
    s = str(code or "").upper().replace("OP", "")
    return int(s) if s.isdigit() else 9999


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def add_log(db, queue_id, status, retry_count, error_message=None):
    """Trace une tentative dans oracle_transaction_logs (OK / RETRY / ERROR)."""
    cur = db.cursor()
    cur.execute("""
        INSERT INTO oracle_transaction_logs
            (queue_id, status, retry_count, error_message, executed_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (queue_id, status, retry_count, (error_message or "")[:2000]))
    db.commit()
    cur.close()


def fetch_next(db):
    """Prend la plus ancienne move en attente (exe_flag='N') et la passe en 'P'.
    Retourne la ligne, ou None si la file est vide."""
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT id, mission_job_id, of_number, operation_code, item_code, qty
        FROM oracle_move_queue
        WHERE exe_flag = 'N'
        ORDER BY cree_le ASC
        LIMIT 1
    """)
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE oracle_move_queue SET exe_flag='P' WHERE id=%s", (row["id"],))
        db.commit()
    cur.close()
    return row


def execute_move(db, row):
    """Exécute UNE move MSCA avec retry. Met à jour exe_flag (D/E) + logs + MOVE_DONE."""
    queue_id  = row["id"]
    of_number = row["of_number"]
    op_code   = row["operation_code"]
    to_seq    = _op_num(op_code)
    qty       = int(row["qty"] or 1)

    log(f"▶️  Move queue#{queue_id} : OF={of_number} op={op_code} (seq={to_seq}) qty={qty}")

    last_error = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            if DRY_RUN:
                res = {"success": True, "message": "Simulé (DRY_RUN)"}
            else:
                # SN auto si l'op est sérialisée (None sinon → move normal)
                # get_sn_for_op se connecte à ORACLE → il prend ORACLE_PASSWORD (.env) tout seul.
                sn = None
                try:
                    sn = sync_oracle.get_sn_for_op(of_number, to_seq)
                except Exception as e:
                    log(f"   [WARN] get_sn_for_op : {e}")
                session = msca_move.MscaTelnet(verbose=True)
                res = msca_move.do_move(
                    session, MSCA_USER, MSCA_PASS, MSCA_ORG,
                    of_number, to_seq, qty, sn, database=MSCA_DB,
                )

            if res.get("success"):
                # ── Succès ───────────────────────────────────
                cur = db.cursor()
                cur.execute("UPDATE oracle_move_queue SET exe_flag='D', erreur=NULL, "
                            "execute_le=NOW() WHERE id=%s", (queue_id,))
                cur.execute("UPDATE cart_mission_jobs SET statut='MOVE_DONE' WHERE id=%s",
                            (row["mission_job_id"],))
                db.commit(); cur.close()
                add_log(db, queue_id, "OK", attempt)
                log(f"✅  Move queue#{queue_id} RÉUSSIE (tentative {attempt}) : {res.get('message','')}")
                return

            # échec « propre » renvoyé par do_move
            last_error = res.get("message") or res.get("error") or "échec inconnu"

        except Exception as e:
            last_error = f"{e}"
            log(f"   [EXC] tentative {attempt} : {e}")
            traceback.print_exc()

        # ── Échec de cette tentative ─────────────────────────
        if attempt < MAX_RETRY:
            add_log(db, queue_id, "RETRY", attempt, last_error)
            log(f"🔁  Échec tentative {attempt} → retry. ({last_error})")
            time.sleep(2)
        else:
            # ── Plus de tentative → Error ────────────────────
            cur = db.cursor()
            cur.execute("UPDATE oracle_move_queue SET exe_flag='E', erreur=%s, "
                        "execute_le=NOW() WHERE id=%s", ((last_error or "")[:2000], queue_id))
            db.commit(); cur.close()
            add_log(db, queue_id, "ERROR", attempt, last_error)
            log(f"❌  Move queue#{queue_id} EN ERREUR après {MAX_RETRY} tentatives : {last_error}")


def main():
    log("=== Worker oracle_msca démarré ===")
    log(f"    org={MSCA_ORG} db={MSCA_DB} dry_run={DRY_RUN} max_retry={MAX_RETRY}")
    while True:
        try:
            db = get_db()
            row = fetch_next(db)
            if row:
                execute_move(db, row)
                db.close()
                continue          # enchaîne tout de suite la suivante (pas d'attente)
            db.close()
        except Exception as e:
            log(f"[ERR boucle] {e}")
            traceback.print_exc()
        time.sleep(POLL_SECONDS)   # file vide → on patiente


if __name__ == "__main__":
    main()
