"""
Serveur Flask — RFID Pristina
Gestion des chariots en temps reel
- Recoit les scans du Pepper C1
- Lit les Jobs Released depuis material_db (SQL Server GE)
- Stocke les donnees dans SQLite local (rfid_pristina.db)
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import sqlite3
import os

# ─── TENTATIVE CONNEXION SQL SERVER ──────────────────────────────────────────
try:
    import pyodbc
    SQL_SERVER_DISPONIBLE = True
except ImportError:
    SQL_SERVER_DISPONIBLE = False
    print("ATTENTION : pyodbc non installe — pip install pyodbc")

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

# SQL Server GE Healthcare (lecture Jobs)
SQL_SERVER  = "dev1facbuc.cqauwe4p6le.eu-west-1.rds.amazonaws.com"
SQL_DB      = "material_db"
SQL_USER    = "TON_LOGIN"        # ← remplace par ton login SSMS
SQL_PASSWORD= "TON_MOT_DE_PASSE" # ← remplace par ton mot de passe

# SQLite local (ecriture donnees RFID)
DB_PATH = os.path.join(os.path.dirname(__file__), "rfid_pristina.db")

app = Flask(__name__)


# ─── SQLITE — INITIALISATION ──────────────────────────────────────────────────

def init_db():
    """Cree les tables SQLite si elles n'existent pas."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Table chariots
    c.execute("""
        CREATE TABLE IF NOT EXISTS chariots (
            chariot_id     TEXT PRIMARY KEY,
            nom            TEXT NOT NULL,
            station        TEXT NOT NULL,
            operation_code TEXT NOT NULL,
            nb_ofs         INTEGER DEFAULT 1,
            actif          INTEGER DEFAULT 1
        )
    """)

    # Table rfid_cards (UID badge → chariot)
    c.execute("""
        CREATE TABLE IF NOT EXISTS rfid_cards (
            uid            TEXT PRIMARY KEY,
            chariot_id     TEXT NOT NULL,
            actif          INTEGER DEFAULT 1,
            enregistre_le  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
    """)

    # Table cart_missions (etat actuel de chaque chariot)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart_missions (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid_uid       TEXT NOT NULL,
            chariot_id     TEXT NOT NULL,
            of_number      TEXT,
            operation_code TEXT NOT NULL,
            statut         TEXT DEFAULT 'EN_APPROCHE',
            ts_scan1       TEXT,
            ts_scan2       TEXT,
            ts_commencer   TEXT,
            ts_terminer    TEXT,
            ws_id          TEXT,
            actif          INTEGER DEFAULT 1,
            cree_le        TEXT DEFAULT (datetime('now'))
        )
    """)

    # Table cart_events (journal complet)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart_events (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id     INTEGER,
            rfid_uid       TEXT,
            chariot_id     TEXT,
            of_number      TEXT,
            operation_code TEXT,
            evenement      TEXT NOT NULL,
            ts             TEXT DEFAULT (datetime('now')),
            scanner_id     TEXT,
            details        TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"  SQLite initialise : {DB_PATH}")


def get_db():
    """Retourne une connexion SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─── SQL SERVER — LECTURE JOBS ────────────────────────────────────────────────

def get_jobs_released(operation=None):
    """
    Lit les Jobs Released depuis material_db (SQL Server GE Healthcare).
    Filtre optionnel par operation (OP20, OP70...).
    """
    if not SQL_SERVER_DISPONIBLE:
        # Mode demo si pas de connexion SQL Server
        return get_jobs_demo()

    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DB};"
            f"UID={SQL_USER};"
            f"PWD={SQL_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        cursor = conn.cursor()

        query = """
            SELECT
                NUM_JOB,
                ORG,
                STATUS,
                ASSEMBLY,
                OPERATION,
                ASSEMBLY_DESCRIPTION,
                USE_DATE
            FROM dbo.JOBS
            WHERE ORG = 'BXD'
            AND STATUS = 'Released'
        """
        params = []
        if operation:
            query += " AND OPERATION = ?"
            params.append(operation)

        query += " ORDER BY USE_DATE"

        cursor.execute(query, params)
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                "num_job"    : row.NUM_JOB,
                "org"        : row.ORG,
                "status"     : row.STATUS,
                "assembly"   : row.ASSEMBLY,
                "operation"  : row.OPERATION,
                "description": row.ASSEMBLY_DESCRIPTION,
                "use_date"   : str(row.USE_DATE) if row.USE_DATE else None,
            })
        conn.close()
        return jobs

    except Exception as e:
        print(f"  ERREUR SQL Server : {e}")
        print("  Utilisation des donnees de demo...")
        return get_jobs_demo()


def get_jobs_demo():
    """Jobs de demo si SQL Server non disponible."""
    return [
        {"num_job": "WO-2026-00141", "org": "BXD", "status": "Released",
         "assembly": "S30381AB", "operation": "OP20",
         "description": "PRISTINA DUETA FULL W/CONTRAST", "use_date": "2026-05-06"},
        {"num_job": "WO-2026-00142", "org": "BXD", "status": "Released",
         "assembly": "S30381AB", "operation": "OP20",
         "description": "PRISTINA DUETA STANDARD", "use_date": "2026-05-07"},
        {"num_job": "WO-2026-00143", "org": "BXD", "status": "Released",
         "assembly": "S30381AB", "operation": "OP70",
         "description": "PRISTINA ESSENTIAL W/CONTRAST", "use_date": "2026-05-07"},
    ]


# ─── ROUTES API ──────────────────────────────────────────────────────────────

@app.route("/api/test", methods=["GET"])
def test_connexion():
    """Tester que Flask tourne."""
    return jsonify({
        "status" : "ok",
        "message": "Serveur Flask RFID Pristina operationnel",
        "db_sqlite"    : os.path.exists(DB_PATH),
        "db_sqlserver" : SQL_SERVER_DISPONIBLE,
    })


@app.route("/api/scan", methods=["POST"])
def recevoir_scan():
    """
    Reçoit un scan du Pepper C1.
    Body JSON : { "uid": "A3F2C1D4", "scanner_id": "SCAN_SUPERMARCHE" }
    """
    data       = request.json or {}
    now        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uid        = data.get("uid", "").strip().upper()
    scanner_id = data.get("scanner_id", "PEPPER_C1")
    type_tag   = data.get("type", "MIFARE")

    print(f"\n{'='*45}")
    print(f"  SCAN RECU — {now}")
    print(f"  UID       : {uid}")
    print(f"  Scanner   : {scanner_id}")
    print(f"{'='*45}")

    if not uid:
        return jsonify({"status": "erreur", "message": "UID vide"}), 400

    # Verifier si le badge est connu
    db   = get_db()
    card = db.execute(
        "SELECT * FROM rfid_cards WHERE uid = ?", (uid,)
    ).fetchone()

    if card:
        chariot = db.execute(
            "SELECT * FROM chariots WHERE chariot_id = ?", (card["chariot_id"],)
        ).fetchone()
        chariot_info = dict(chariot) if chariot else {}
    else:
        chariot_info = {}

    # Enregistrer l'evenement
    db.execute("""
        INSERT INTO cart_events (rfid_uid, evenement, scanner_id)
        VALUES (?, 'SCAN_1_SUPERMARCHE', ?)
    """, (uid, scanner_id))
    db.commit()
    db.close()

    return jsonify({
        "status"   : "ok",
        "uid"      : uid,
        "scanner"  : scanner_id,
        "ts"       : now,
        "badge_connu": card is not None,
        "chariot"  : chariot_info,
        "message"  : f"Scan enregistre a {now}",
    })


@app.route("/api/jobs", methods=["GET"])
def liste_jobs():
    """
    Retourne les Jobs Released depuis material_db.
    Parametre optionnel : ?operation=OP20
    """
    operation = request.args.get("operation")
    jobs = get_jobs_released(operation)
    return jsonify({
        "status" : "ok",
        "total"  : len(jobs),
        "jobs"   : jobs,
    })


@app.route("/api/scans", methods=["GET"])
def voir_scans():
    """Retourne les derniers evenements depuis SQLite."""
    db     = get_db()
    events = db.execute("""
        SELECT * FROM cart_events
        ORDER BY ts DESC
        LIMIT 50
    """).fetchall()
    db.close()
    return jsonify([dict(e) for e in events])


@app.route("/api/reset", methods=["POST"])
def reset():
    """Vider les evenements (pour recommencer un test)."""
    db = get_db()
    db.execute("DELETE FROM cart_events")
    db.execute("DELETE FROM cart_missions")
    db.commit()
    db.close()
    print("\nBase de donnees remise a zero.")
    return jsonify({"status": "ok", "message": "Reset effectue"})


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def dashboard():
    """Dashboard principal."""
    db     = get_db()
    events = db.execute("""
        SELECT * FROM cart_events
        ORDER BY ts DESC LIMIT 20
    """).fetchall()
    nb_events = db.execute("SELECT COUNT(*) FROM cart_events").fetchone()[0]
    db.close()

    jobs = get_jobs_released()

    return render_template_string(DASHBOARD_HTML,
        events=events,
        nb_events=nb_events,
        nb_jobs=len(jobs),
        jobs=jobs[:5],
    )


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <title>RFID Pristina</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif;
               background: #f0f4f8; padding: 20px; }
        h1 { color: #1F3864; font-size: 22px; margin-bottom: 5px; }
        h2 { color: #1F3864; font-size: 16px; margin: 20px 0 10px; }
        .subtitle { color: #666; font-size: 12px; margin-bottom: 20px; }
        .stats { display: flex; gap: 15px; margin-bottom: 20px; }
        .stat-box { background: white; border-radius: 8px;
                    padding: 15px 25px; text-align: center;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
        .stat-box .nb { font-size: 28px; font-weight: bold; color: #1F3864; }
        .stat-box .label { font-size: 11px; color: #888; }
        .card { background: white; border-radius: 8px; padding: 12px 18px;
                margin-bottom: 8px; border-left: 5px solid #4CAF50;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                display: flex; justify-content: space-between; }
        .card.job { border-left-color: #1F7F7F; }
        .card .titre { font-weight: bold; color: #1F3864; font-size: 14px; }
        .card .info { font-size: 11px; color: #888; margin-top: 3px; }
        .card .ts { font-size: 12px; color: #1F7F7F; font-weight: bold; }
        .status-ok { background: #e8f5e9; color: #2e7d32;
                     padding: 5px 12px; border-radius: 20px; font-size: 12px; }
        .header { display: flex; justify-content: space-between;
                  align-items: flex-start; margin-bottom: 20px; }
        .empty { text-align: center; padding: 30px; color: #aaa; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>RFID Pristina — Dashboard</h1>
            <div class="subtitle">Actualisation toutes les 5s</div>
        </div>
        <div class="status-ok">Serveur actif</div>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="nb">{{ nb_events }}</div>
            <div class="label">Scans recus</div>
        </div>
        <div class="stat-box">
            <div class="nb">{{ nb_jobs }}</div>
            <div class="label">Jobs Released</div>
        </div>
    </div>

    <h2>Jobs Released (Oracle)</h2>
    {% if jobs %}
        {% for j in jobs %}
        <div class="card job">
            <div>
                <div class="titre">{{ j.num_job }} — {{ j.operation }}</div>
                <div class="info">{{ j.description }} | {{ j.assembly }}</div>
            </div>
            <div class="ts">{{ j.use_date }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">Aucun job disponible</div>
    {% endif %}

    <h2>Derniers scans RFID</h2>
    {% if events %}
        {% for e in events %}
        <div class="card">
            <div>
                <div class="titre">UID : {{ e.rfid_uid }}</div>
                <div class="info">{{ e.evenement }} | {{ e.scanner_id }}</div>
            </div>
            <div class="ts">{{ e.ts }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">Aucun scan recu — pose un badge sur le Pepper C1</div>
    {% endif %}
</body>
</html>
"""


# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("  SERVEUR FLASK — RFID Pristina")
    print("=" * 45)
    init_db()
    print(f"  Dashboard : http://localhost:5000/")
    print(f"  Jobs      : http://localhost:5000/api/jobs")
    print(f"  Scan      : POST http://localhost:5000/api/scan")
    print("=" * 45 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
