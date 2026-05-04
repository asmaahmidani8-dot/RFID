"""
Serveur Flask — Test RFID Pristina
PC joue le role du serveur usine
"""

from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Stockage en memoire (pas de base de donnees pour les tests)
scans = []

# ─── TEMPLATE DASHBOARD ─────────────────────────────────────────────────────

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2">
    <title>RFID Pristina — Test</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f0f4f8;
            padding: 20px;
        }
        h1 {
            color: #1F3864;
            font-size: 24px;
            margin-bottom: 5px;
        }
        .subtitle {
            color: #666;
            font-size: 13px;
            margin-bottom: 20px;
        }
        .stats {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-box {
            background: white;
            border-radius: 8px;
            padding: 15px 25px;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }
        .stat-box .nb {
            font-size: 32px;
            font-weight: bold;
            color: #1F3864;
        }
        .stat-box .label {
            font-size: 12px;
            color: #888;
        }
        .scan-card {
            background: white;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-left: 5px solid #4CAF50;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .scan-card .uid {
            font-size: 18px;
            font-weight: bold;
            color: #1F3864;
            font-family: monospace;
        }
        .scan-card .info {
            font-size: 12px;
            color: #888;
            margin-top: 4px;
        }
        .scan-card .ts {
            font-size: 13px;
            color: #1F7F7F;
            font-weight: bold;
        }
        .empty {
            text-align: center;
            padding: 40px;
            color: #aaa;
            font-size: 16px;
        }
        .refresh {
            font-size: 11px;
            color: #bbb;
            margin-top: 15px;
            text-align: right;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        .status-ok {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>RFID Pristina — Test Materiel</h1>
            <div class="subtitle">
                Serveur Flask sur localhost:5000 |
                API : POST /api/scan
            </div>
        </div>
        <div class="status-ok">Serveur actif</div>
    </div>

    <div class="stats">
        <div class="stat-box">
            <div class="nb">{{ nb_scans }}</div>
            <div class="label">Scans recus</div>
        </div>
        <div class="stat-box">
            <div class="nb">{{ nb_uids }}</div>
            <div class="label">Badges differents</div>
        </div>
        <div class="stat-box">
            <div class="nb">{{ dernier_ts }}</div>
            <div class="label">Dernier scan</div>
        </div>
    </div>

    {% if scans %}
        {% for s in scans %}
        <div class="scan-card">
            <div>
                <div class="uid">UID : {{ s.uid }}</div>
                <div class="info">
                    Scanner : {{ s.scanner_id }} |
                    Type : {{ s.type }}
                </div>
            </div>
            <div class="ts">{{ s.ts }}</div>
        </div>
        {% endfor %}
    {% else %}
        <div class="empty">
            Aucun scan recu<br>
            <small>Pose un badge sur le Pepper C1...</small>
        </div>
    {% endif %}

    <div class="refresh">Actualisation automatique toutes les 2s</div>
</body>
</html>
"""


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def dashboard():
    """Dashboard principal."""
    uids_uniques = set(s["uid"] for s in scans)
    dernier = scans[-1]["ts"] if scans else "--:--:--"

    return render_template_string(
        DASHBOARD_HTML,
        scans=list(reversed(scans)),
        nb_scans=len(scans),
        nb_uids=len(uids_uniques),
        dernier_ts=dernier,
    )


@app.route("/api/scan", methods=["POST"])
def recevoir_scan():
    """
    Point d'entree principal — Pepper C1 envoie ici les UIDs.
    Body JSON attendu :
        { "uid": "A3F2C1D4", "scanner_id": "TEST", "type": "MIFARE_CLASSIC" }
    """
    data = request.json or {}
    now  = datetime.now().strftime("%H:%M:%S")

    uid        = data.get("uid", "").strip().upper()
    scanner_id = data.get("scanner_id", "PEPPER_C1")
    type_tag   = data.get("type", "MIFARE")

    # Log console
    print(f"\n{'='*45}")
    print(f"  SCAN RECU — {now}")
    print(f"  UID       : {uid}")
    print(f"  Scanner   : {scanner_id}")
    print(f"  Type      : {type_tag}")
    print(f"{'='*45}")

    # Validation basique
    if not uid:
        return jsonify({"status": "erreur", "message": "UID vide"}), 400

    # Enregistrer
    scans.append({
        "uid"       : uid,
        "scanner_id": scanner_id,
        "type"      : type_tag,
        "ts"        : now,
    })

    return jsonify({
        "status" : "ok",
        "uid"    : uid,
        "message": f"Scan enregistre a {now}",
        "total"  : len(scans),
    })


@app.route("/api/scans", methods=["GET"])
def voir_scans():
    """Retourne tous les scans en JSON."""
    return jsonify(scans)


@app.route("/api/reset", methods=["POST"])
def reset():
    """Vider la liste des scans (pour recommencer un test)."""
    scans.clear()
    print("\nListe des scans remise a zero.")
    return jsonify({"status": "ok", "message": "Reset effectue"})


@app.route("/api/test", methods=["GET"])
def test_connexion():
    """Tester que Flask tourne — appeler depuis navigateur ou curl."""
    return jsonify({
        "status" : "ok",
        "message": "Serveur Flask operationnel",
        "url_scan": "POST http://localhost:5000/api/scan",
    })


# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("  SERVEUR FLASK — RFID Pristina Test")
    print("=" * 45)
    print(f"  Dashboard : http://localhost:5000/")
    print(f"  API scan  : POST http://localhost:5000/api/scan")
    print(f"  Reset     : POST http://localhost:5000/api/reset")
    print("=" * 45)
    print("  En attente de scans...\n")

    app.run(host="0.0.0.0", port=5000, debug=True)
