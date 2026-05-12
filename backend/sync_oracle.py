"""
sync_oracle.py — Synchronisation Oracle GLTEST → SQL Server rfid_pristina
Importe les Work Orders Released (STATUS_TYPE=3) dans jobs_planning

Connexion Oracle :
  Host    : qahceaexa-scan.ge-healthcare.net
  Port    : 1521
  Service : ebs_gltest
  Org     : BXD (ORGANIZATION_ID = 1731)
"""

import sys
from datetime import datetime

# ─── DÉPENDANCES ──────────────────────────────────────────────────────────────
try:
    import oracledb
except ImportError:
    print("ERREUR : oracledb non installé")
    print("  Lance : pip install oracledb")
    sys.exit(1)

try:
    import pyodbc
except ImportError:
    print("ERREUR : pyodbc non installé")
    print("  Lance : pip install pyodbc")
    sys.exit(1)


# ─── CONFIGURATION ORACLE ─────────────────────────────────────────────────────
ORACLE_USER     = "TON_USERNAME"      # ← remplace par ton username SSO/Oracle
ORACLE_PASSWORD = "TON_PASSWORD"      # ← remplace par ton mot de passe
ORACLE_HOST     = "qahceaexa-scan.ge-healthcare.net"
ORACLE_PORT     = 1521
ORACLE_SERVICE  = "ebs_gltest"

ORACLE_DSN = oracledb.makedsn(
    host    = ORACLE_HOST,
    port    = ORACLE_PORT,
    service_name = ORACLE_SERVICE,
)

# ─── CONFIGURATION SQL SERVER ─────────────────────────────────────────────────
SQLSERVER_CONN = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=rfid_pristina;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# ─── ORGANISATION ─────────────────────────────────────────────────────────────
ORGANIZATION_ID  = "1731"   # BXD — ligne Pristina
JOURS_HISTORIQUE = 90       # Chercher les OFs créés dans les 90 derniers jours


# ─── REQUÊTE ORACLE ───────────────────────────────────────────────────────────
# 1 ligne par (OF × opération ouverte)
# COMPLETION_QUANTITY < START_QUANTITY = opération pas encore terminée

REQUETE_ORACLE = f"""
    SELECT
        wen.WIP_ENTITY_NAME                             AS of_number,
        ite.SEGMENT1                                    AS item_code,
        SUBSTR(ite.DESCRIPTION, 1, 150)                 AS item_desc,
        'OP' || LPAD(wop.OPERATION_SEQ_NUM, 2, '0')    AS operation_code,
        wop.OPERATION_SEQ_NUM                           AS operation_seq,
        wdj.START_QUANTITY                              AS qty_totale,
        wdj.SCHEDULED_COMPLETION_DATE                   AS date_besoin
    FROM
        apps.WIP_DISCRETE_JOBS  wdj,
        apps.WIP_ENTITIES       wen,
        apps.MTL_SYSTEM_ITEMS_B ite,
        apps.WIP_OPERATIONS     wop
    WHERE
        wdj.WIP_ENTITY_ID    = wen.WIP_ENTITY_ID
        AND wdj.PRIMARY_ITEM_ID  = ite.INVENTORY_ITEM_ID
        AND wdj.ORGANIZATION_ID  = ite.ORGANIZATION_ID
        AND wdj.WIP_ENTITY_ID    = wop.WIP_ENTITY_ID
        AND wdj.STATUS_TYPE      = 3
        AND wdj.ORGANIZATION_ID  = '{ORGANIZATION_ID}'
        AND wdj.CREATION_DATE    > SYSDATE - {JOURS_HISTORIQUE}
        AND NVL(wop.QUANTITY_COMPLETED, 0) < wdj.START_QUANTITY   -- opération pas finie
    ORDER BY
        wdj.SCHEDULED_COMPLETION_DATE ASC,
        wen.WIP_ENTITY_NAME ASC,
        wop.OPERATION_SEQ_NUM ASC
"""


# ─── REQUÊTE SIMPLIFIÉE (si WIP_OPERATIONS inaccessible) ─────────────────────

REQUETE_SIMPLE = f"""
    SELECT
        wen.WIP_ENTITY_NAME                         AS of_number,
        ite.SEGMENT1                                AS item_code,
        SUBSTR(ite.DESCRIPTION, 1, 150)             AS item_desc,
        wdj.START_QUANTITY                          AS qty,
        wdj.SCHEDULED_COMPLETION_DATE               AS date_besoin
    FROM
        apps.WIP_DISCRETE_JOBS  wdj,
        apps.WIP_ENTITIES       wen,
        apps.MTL_SYSTEM_ITEMS_B ite
    WHERE
        wdj.WIP_ENTITY_ID    = wen.WIP_ENTITY_ID
        AND wdj.PRIMARY_ITEM_ID  = ite.INVENTORY_ITEM_ID
        AND wdj.ORGANIZATION_ID  = ite.ORGANIZATION_ID
        AND wdj.STATUS_TYPE      = 3
        AND wdj.ORGANIZATION_ID  = '{ORGANIZATION_ID}'
        AND wdj.CREATION_DATE    > SYSDATE - {JOURS_HISTORIQUE}
    ORDER BY
        wdj.SCHEDULED_COMPLETION_DATE ASC
"""


# ─── CONNEXIONS ───────────────────────────────────────────────────────────────

def connecter_oracle():
    print(f"Connexion Oracle → {ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")
    try:
        conn = oracledb.connect(
            user     = ORACLE_USER,
            password = ORACLE_PASSWORD,
            dsn      = ORACLE_DSN,
        )
        print("  ✓ Connecté à Oracle GLTEST")
        return conn
    except Exception as e:
        print(f"  ERREUR Oracle : {e}")
        sys.exit(1)


def connecter_sqlserver():
    print("Connexion SQL Server → rfid_pristina")
    try:
        conn = pyodbc.connect(SQLSERVER_CONN)
        print("  ✓ Connecté à SQL Server")
        return conn
    except Exception as e:
        print(f"  ERREUR SQL Server : {e}")
        sys.exit(1)


# ─── SYNC PRINCIPALE ──────────────────────────────────────────────────────────

def synchroniser(conn_oracle, conn_sql):
    c_oracle = conn_oracle.cursor()
    c_sql    = conn_sql.cursor()
    now      = datetime.now()

    print(f"\nLancement sync — {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Récupérer les OFs + toutes leurs opérations ouvertes ─────────────────
    print("Récupération des Work Orders Released + opérations depuis Oracle...")
    try:
        c_oracle.execute(REQUETE_ORACLE)
        rows = c_oracle.fetchall()
        mode = "complet"
        print(f"  ✓ {len(rows)} ligne(s) (OF × opération) trouvée(s)")
    except Exception as e:
        print(f"  ⚠ Requête complète échouée : {e}")
        print("  → Utilisation requête simplifiée (sans WIP_OPERATIONS)...")
        c_oracle.execute(REQUETE_SIMPLE)
        rows = c_oracle.fetchall()
        mode = "simple"
        print(f"  ✓ {len(rows)} Work Order(s) trouvé(s) (mode simplifié)")

    # ── Insérer / mettre à jour dans SQL Server ───────────────────────────────
    nb_nouveaux = 0
    nb_maj      = 0
    nb_ignores  = 0

    for row in rows:
        if mode == "complet":
            # of_number, item_code, item_desc, operation_code, op_seq, qty, date_besoin
            of_number, item_code, item_desc, operation_code, op_seq, qty, date_besoin = row  # qty = START_QUANTITY
        else:
            # Mode simple : pas d'opération connue → on écrit OP00 (inconnu)
            of_number, item_code, item_desc, qty, date_besoin = row
            operation_code = "OP00"

        qty_val        = int(qty) if qty else 1
        item_desc_str  = str(item_desc or "")[:150]
        operation_code = str(operation_code)[:10]

        try:
            # Vérifier si la combinaison (OF, opération) existe déjà
            existe = c_sql.execute(
                "SELECT statut FROM jobs_planning WHERE of_number=? AND operation_code=?",
                (str(of_number), operation_code)
            ).fetchone()

            if not existe:
                # Nouveau → INSERT statut RELEASED
                c_sql.execute(
                    """INSERT INTO jobs_planning
                           (of_number, operation_code, item_code, item_desc,
                            statut, qty, date_besoin, date_import)
                       VALUES (?,?,?,?,'RELEASED',?,?,?)""",
                    (str(of_number), operation_code,
                     str(item_code), item_desc_str,
                     qty_val,
                     date_besoin.date() if date_besoin else None,
                     now)
                )
                nb_nouveaux += 1
                print(f"  + {of_number} / {operation_code} ({item_code})  [NOUVEAU]")

            elif existe[0] == "RELEASED":
                # Déjà RELEASED → mise à jour qty/date uniquement
                c_sql.execute(
                    """UPDATE jobs_planning
                       SET item_desc=?, qty=?, date_besoin=?
                       WHERE of_number=? AND operation_code=? AND statut='RELEASED'""",
                    (item_desc_str, qty_val,
                     date_besoin.date() if date_besoin else None,
                     str(of_number), operation_code)
                )
                nb_maj += 1
            else:
                # ASSIGNE / EN_COURS / TERMINE → on ne touche pas
                nb_ignores += 1

        except Exception as e:
            print(f"  ERREUR {of_number}/{operation_code} : {e}")

    conn_sql.commit()
    print(f"\n  Résultat sync :")
    print(f"    Nouveaux OFs insérés  : {nb_nouveaux}")
    print(f"    OFs mis à jour        : {nb_maj}")
    print(f"    OFs ignorés           : {nb_ignores}")
    print(f"    Total Oracle          : {len(rows)}")


# ─── RÉSUMÉ JOBS_PLANNING ─────────────────────────────────────────────────────

def afficher_resume(conn_sql):
    c = conn_sql.cursor()
    print("\n" + "=" * 50)
    print("  JOBS_PLANNING — État actuel")
    print("=" * 50)
    stats = c.execute(
        "SELECT statut, operation_code, COUNT(*) FROM jobs_planning GROUP BY statut, operation_code ORDER BY statut, operation_code"
    ).fetchall()
    for s in stats:
        print(f"  {s[0]:<15} {s[1]:<8} : {s[2]} job(s)")
    print("=" * 50)


# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  SYNC ORACLE → SQL SERVER")
    print(f"  Oracle  : {ORACLE_HOST}/{ORACLE_SERVICE}")
    print(f"  Org     : BXD ({ORGANIZATION_ID})")
    print(f"  Historique : {JOURS_HISTORIQUE} jours")
    print("=" * 50 + "\n")

    conn_oracle = connecter_oracle()
    conn_sql    = connecter_sqlserver()

    synchroniser(conn_oracle, conn_sql)
    afficher_resume(conn_sql)

    conn_oracle.close()
    conn_sql.close()
    print("\nSync terminée ✓")
    print("Lance maintenant : python backend/app.py\n")
