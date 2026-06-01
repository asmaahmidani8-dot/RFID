"""
ptl.py — Pick-to-Light routes & MQTT handler
GE Healthcare Buc | Ligne Pristina
"""
import json
import threading
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template
import mysql.connector
import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as mqtt_pub

ptl_bp = Blueprint("ptl", __name__)

MQTT_HOST = "localhost"
MQTT_PORT = 1883

# ── DB helper ─────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "rfid_app"),
        password=os.getenv("MYSQL_PASSWORD", "rfid_pass"),
        database=os.getenv("MYSQL_DB", "rfid_buc"),
        charset="utf8mb4"
    )

# ── MQTT publish helper ───────────────────────────────────────
def ptl_publish(etagere_id, payload: dict):
    try:
        mqtt_pub.single(
            topic   = f"rfid/ptl/{etagere_id}",
            payload = json.dumps(payload),
            hostname= MQTT_HOST,
            port    = MQTT_PORT
        )
    except Exception as e:
        print(f"[PTL MQTT] Erreur publish : {e}")

# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

@ptl_bp.route("/ptl")
def ptl_page():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM etageres WHERE actif=1")
    etageres = cur.fetchall()
    cur.execute("""
        SELECT ps.*, b.etagere_id, b.position, b.item_desc AS bac_desc
        FROM pick_sessions ps
        JOIN bacs b ON b.bac_id = ps.bac_id
        WHERE ps.statut = 'EN_ATTENTE'
        ORDER BY ps.cree_le DESC
    """)
    sessions = cur.fetchall()
    cur.close(); db.close()
    return render_template("ptl.html", etageres=etageres, sessions=sessions)

# ══════════════════════════════════════════════════════════════
# API
# ══════════════════════════════════════════════════════════════

@ptl_bp.route("/api/ptl/start", methods=["POST"])
def ptl_start():
    """Démarre le picking pour une mission — allume les bacs concernés."""
    data       = request.get_json()
    mission_id = data.get("mission_id")
    item_code  = data.get("item_code")   # item de l'OF assigné
    quantite   = data.get("quantite", 1)

    if not mission_id or not item_code:
        return jsonify({"error": "mission_id et item_code requis"}), 400

    db = get_db(); cur = db.cursor(dictionary=True)

    # Trouver les bacs contenant cet item
    cur.execute("""
        SELECT b.*, e.etagere_id AS et_id
        FROM bacs b
        JOIN etageres e ON e.etagere_id = b.etagere_id
        WHERE b.item_code = %s AND b.actif = 1
    """, (item_code,))
    bacs = cur.fetchall()

    if not bacs:
        cur.close(); db.close()
        return jsonify({"error": f"Aucun bac trouvé pour {item_code}"}), 404

    sessions_crees = []
    now = datetime.now()

    for bac in bacs:
        # Créer session picking
        cur.execute("""
            INSERT INTO pick_sessions (mission_id, bac_id, item_code, quantite, statut, cree_le)
            VALUES (%s, %s, %s, %s, 'EN_ATTENTE', %s)
        """, (mission_id, bac["bac_id"], item_code, quantite, now))

        # Allumer le bac via MQTT
        ptl_publish(bac["etagere_id"], {
            "action":   "allumer",
            "position": bac["position"],
            "bac_id":   bac["bac_id"],
            "quantite": quantite,
            "item":     bac["item_desc"] or item_code
        })
        sessions_crees.append(bac["bac_id"])

    db.commit(); cur.close(); db.close()
    return jsonify({"success": True, "bacs_allumes": sessions_crees})


@ptl_bp.route("/api/ptl/confirm", methods=["POST"])
def ptl_confirm():
    """Confirme un bac (depuis tablette ou bouton ESP32)."""
    data   = request.get_json()
    bac_id = data.get("bac_id")

    if not bac_id:
        return jsonify({"error": "bac_id requis"}), 400

    db = get_db(); cur = db.cursor(dictionary=True)

    # Marquer la session comme confirmée
    cur.execute("""
        UPDATE pick_sessions
        SET statut='CONFIRME', confirme_le=NOW()
        WHERE bac_id=%s AND statut='EN_ATTENTE'
    """, (bac_id,))

    # Trouver l'étagère pour éteindre la LED
    cur.execute("SELECT etagere_id, position FROM bacs WHERE bac_id=%s", (bac_id,))
    bac = cur.fetchone()

    if bac:
        ptl_publish(bac["etagere_id"], {
            "action":   "eteindre",
            "position": bac["position"],
            "bac_id":   bac_id
        })

    db.commit(); cur.close(); db.close()
    return jsonify({"success": True})


@ptl_bp.route("/api/ptl/status/<int:mission_id>")
def ptl_status(mission_id):
    """Retourne l'état de picking d'une mission."""
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT ps.*, b.position, b.item_desc AS bac_desc, b.etagere_id
        FROM pick_sessions ps
        JOIN bacs b ON b.bac_id = ps.bac_id
        WHERE ps.mission_id = %s
        ORDER BY ps.bac_id
    """, (mission_id,))
    sessions = cur.fetchall()
    for s in sessions:
        if s.get("cree_le"): s["cree_le"] = s["cree_le"].strftime("%H:%M")
        if s.get("confirme_le"): s["confirme_le"] = s["confirme_le"].strftime("%H:%M")
    cur.close(); db.close()

    total     = len(sessions)
    confirmes = sum(1 for s in sessions if s["statut"] == "CONFIRME")
    return jsonify({
        "sessions": sessions,
        "total": total,
        "confirmes": confirmes,
        "termine": total > 0 and confirmes == total
    })


@ptl_bp.route("/api/ptl/eteindre_tout", methods=["POST"])
def ptl_eteindre_tout():
    """Éteint toutes les LEDs de toutes les étagères."""
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT etagere_id FROM etageres WHERE actif=1")
    etageres = cur.fetchall()
    cur.close(); db.close()

    for e in etageres:
        ptl_publish(e["etagere_id"], {"action": "eteindre_tout"})

    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════════
# MQTT SUBSCRIBER — confirmations depuis ESP32
# ══════════════════════════════════════════════════════════════

def on_esp32_confirm(client, userdata, msg):
    """Reçoit la confirmation bouton OK depuis l'ESP32."""
    try:
        data   = json.loads(msg.payload)
        bac_id = data.get("bac_id")
        if bac_id:
            db = get_db(); cur = db.cursor()
            cur.execute("""
                UPDATE pick_sessions
                SET statut='CONFIRME', confirme_le=NOW()
                WHERE bac_id=%s AND statut='EN_ATTENTE'
            """, (bac_id,))
            db.commit(); cur.close(); db.close()
            print(f"[PTL] Bac {bac_id} confirmé par bouton ESP32")
    except Exception as e:
        print(f"[PTL] Erreur confirmation ESP32 : {e}")


def start_ptl_mqtt_listener():
    """Lance le subscriber MQTT en background thread."""
    client = mqtt_client.Client("flask_ptl_listener")
    client.on_message = on_esp32_confirm
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        client.subscribe("rfid/ptl/+/confirm")
        print("[PTL MQTT] Listener démarré — rfid/ptl/+/confirm")
        client.loop_forever()
    except Exception as e:
        print(f"[PTL MQTT] Impossible de démarrer : {e}")


def init_ptl(app):
    """Appeler depuis app.py pour initialiser le module PTL."""
    app.register_blueprint(ptl_bp)
    t = threading.Thread(target=start_ptl_mqtt_listener, daemon=True)
    t.start()
