"""
check_pending.py — Diagnostic : pourquoi les moves MSCA restent PENDING
GE Healthcare Buc | Ligne Pristina | RFID

Interroge Oracle GLTEST (LECTURE SEULE) pour montrer :
  1. Les moves en attente / erreur dans l'interface (WIP_MOVE_TXN_INTERFACE)
  2. L'état du concurrent manager Oracle qui doit les traiter

Lancer sur le Pi (connecté au réseau usine) :
  python3 check_pending.py
"""

import os
import getpass
import platform

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import oracledb
if platform.system() == "Linux":
    try:
        oracledb.init_oracle_client(lib_dir="/home/ge/instantclient_23_26")
    except Exception:
        pass

ORACLE_HOST    = os.getenv("ORACLE_HOST",    "qahceaexa-scan.ge-healthcare.net")
ORACLE_PORT    = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "ebs_gltest")
ORACLE_USER    = os.getenv("ORACLE_USER",    "SSO250028087")
ORACLE_PASS    = os.getenv("ORACLE_PASSWORD", "")

STATUS = {1: "PENDING (attend le manager)", 2: "RUNNING", 3: "ERROR"}
PHASE  = {1: "Validation", 2: "Move", 3: "Backflush", 4: "Completed"}

# 1. Les moves coincés dans l'interface
SQL_INTERFACE = """
    SELECT mti.transaction_id,
           we.wip_entity_name        AS job,
           mti.organization_id,
           mti.fm_operation_seq_num  AS from_op,
           mti.to_operation_seq_num  AS to_op,
           mti.transaction_quantity  AS qty,
           mti.process_status,
           mti.process_phase,
           mti.group_id,
           mti.request_id
    FROM apps.wip_move_txn_interface mti
    LEFT JOIN apps.wip_entities we ON we.wip_entity_id = mti.wip_entity_id
    ORDER BY mti.last_update_date DESC
"""

# 2. L'état des concurrent managers (Move / Cost / Material)
SQL_MANAGER = """
    SELECT cq.user_concurrent_queue_name AS manager,
           cq.max_processes,
           cq.running_processes,
           cq.enabled_flag,
           cq.control_code
    FROM apps.fnd_concurrent_queues_vl cq
    WHERE upper(cq.user_concurrent_queue_name) LIKE '%MOVE%'
       OR upper(cq.user_concurrent_queue_name) LIKE '%COST%'
       OR upper(cq.user_concurrent_queue_name) LIKE '%MATERIAL%'
       OR upper(cq.user_concurrent_queue_name) LIKE '%WIP%'
    ORDER BY cq.user_concurrent_queue_name
"""


def main():
    print("=" * 70)
    print("  DIAGNOSTIC PENDING — Oracle", ORACLE_SERVICE)
    print("=" * 70)

    pwd = ORACLE_PASS or getpass.getpass(f"Password Oracle ({ORACLE_USER}) : ")
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"
    print(f"[..] Connexion {ORACLE_HOST}/{ORACLE_SERVICE} ...")
    conn = oracledb.connect(user=ORACLE_USER, password=pwd, dsn=dsn)
    cur = conn.cursor()
    print("[OK] Connecté\n")

    # ── 1. Interface des moves ────────────────────────────────
    print("=" * 70)
    print("  1. MOVES DANS L'INTERFACE (WIP_MOVE_TXN_INTERFACE)")
    print("=" * 70)
    try:
        cur.execute(SQL_INTERFACE)
        rows = cur.fetchall()
        if not rows:
            print("  (vide) — aucun move en attente : soit déjà traités, soit table non accessible.")
        for r in rows:
            txn, job, org, fop, top, qty, st, ph, gid, rid = r
            print(f"\n  Txn {txn} | Job {job} | op {fop} -> {top} | qty {qty} | org {org}")
            print(f"    Statut : {STATUS.get(st, st)}    Phase : {PHASE.get(ph, ph)}")
            print(f"    group_id : {gid}   request_id : {rid}")
            if st == 3:
                print("    ⚠️ Statut ERROR -> voir bouton 'Errors' (desktop) ou apps.wip_txn_interface_errors")
        print(f"\n  Total dans l'interface : {len(rows)}")
    except Exception as e:
        print(f"  [INFO] Lecture impossible : {e}")

    # ── 2. État des managers ──────────────────────────────────
    print("\n" + "=" * 70)
    print("  2. CONCURRENT MANAGERS (Move / Cost / Material / WIP)")
    print("=" * 70)
    try:
        cur.execute(SQL_MANAGER)
        mrows = cur.fetchall()
        if not mrows:
            print("  (aucun manager trouvé avec ce filtre)")
        for m in mrows:
            name, maxp, runp, enabled, ctrl = m
            actif = "✅ ACTIF" if (runp and runp > 0) else "❌ A L'ARRET"
            print(f"  {actif:<14} {name:<42} actifs={runp}/{maxp} enabled={enabled} ctrl={ctrl}")
    except Exception as e:
        print(f"  [INFO] Pas d'accès aux managers (fnd_concurrent_queues) : {e}")
        print("  -> demande à l'Apps DBA de vérifier le WIP Move Transaction Manager")

    cur.close()
    conn.close()
    print("\n[OK] Diagnostic terminé.\n")
    print("Lecture :")
    print("  - Statut PENDING + manager A L'ARRET  -> le manager ne tourne pas (cause confirmée)")
    print("  - Statut ERROR + message              -> il y a une vraie erreur de validation")


if __name__ == "__main__":
    main()
