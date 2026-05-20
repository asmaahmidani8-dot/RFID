# dashboard_ws.py — Dashboard Water Spider (WS)
# Lancer avec : python dashboard_ws.py
# Accès : http://raspberrypi.local:5000

from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ══════════════════════════════════════════════════════════
# CONNEXION BASE DE DONNEES
# ══════════════════════════════════════════════════════════

DB_CONFIG = {
    'host':     'localhost',
    'user':     'rfid_user',
    'password': 'ge@2026',
    'database': 'rfid_buc'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ══════════════════════════════════════════════════════════
# PAGE PRINCIPALE — liste des chariots disponibles
# ══════════════════════════════════════════════════════════

@app.route('/')
def index():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    # Chariots DISPONIBLES (aucune mission active)
    cursor.execute("""
        SELECT c.chariot_id, c.nom, c.location, c.operation_code, c.nb_ofs
        FROM chariots c
        WHERE c.actif = 1
        AND NOT EXISTS (
            SELECT 1 FROM cart_missions cm
            WHERE cm.chariot_id = c.chariot_id
            AND   cm.statut IN ('PREPAREE','EN_COURS','RETOUR')
            AND   cm.actif = 1
        )
        ORDER BY c.chariot_id
    """)
    chariots_dispo = cursor.fetchall()

    # Chariots EN MISSION (info seulement)
    cursor.execute("""
        SELECT c.chariot_id, c.nom, c.location, c.operation_code,
               cm.statut, cm.id AS mission_id, cm.cree_le
        FROM chariots c
        JOIN cart_missions cm ON cm.chariot_id = c.chariot_id
        WHERE c.actif = 1
        AND   cm.statut IN ('PREPAREE','EN_COURS','RETOUR')
        AND   cm.actif = 1
        ORDER BY cm.cree_le DESC
    """)
    chariots_mission = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('ws_index.html',
                           chariots_dispo=chariots_dispo,
                           chariots_mission=chariots_mission)


# ══════════════════════════════════════════════════════════
# DETAIL CHARIOT — jobs disponibles pour ce chariot
# ══════════════════════════════════════════════════════════

@app.route('/chariot/<chariot_id>')
def detail_chariot(chariot_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    # Info chariot
    cursor.execute("SELECT * FROM chariots WHERE chariot_id = %s", (chariot_id,))
    chariot = cursor.fetchone()

    if not chariot:
        cursor.close(); conn.close()
        return "Chariot introuvable", 404

    # OFs disponibles pour ce chariot (pas encore pris)
    cursor.execute("""
        SELECT
            jp.of_number,
            jp.item_code,
            jp.item_desc,
            jp.qty,
            jp.date_besoin,
            pc.gamme
        FROM jobs_planning jp
        JOIN pristina_catalogue pc
            ON jp.item_code = pc.item_code
        JOIN chariots c
            ON pc.feeder_num = REPLACE(c.location, 'FEEDER-', '') + 0
            AND pc.job_type  = c.job_type
        WHERE c.chariot_id = %s
        AND   jp.statut    = 'RELEASED'
        AND NOT EXISTS (
            SELECT 1 FROM cart_mission_jobs cmj
            JOIN  cart_missions cm ON cmj.mission_id = cm.id
            WHERE cmj.of_number = jp.of_number
            AND   cm.statut IN ('PREPAREE','EN_COURS')
            AND   cm.actif = 1
        )
        ORDER BY jp.date_besoin ASC
    """, (chariot_id,))
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('ws_chariot.html', chariot=chariot, jobs=jobs)


# ══════════════════════════════════════════════════════════
# CREER MISSION — WS valide les OFs a charger
# ══════════════════════════════════════════════════════════

@app.route('/mission/creer', methods=['POST'])
def creer_mission():
    chariot_id = request.form.get('chariot_id')
    of_numbers = request.form.getlist('of_numbers')  # cases cochees par WS

    if not chariot_id or not of_numbers:
        return redirect(url_for('index'))

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    # 1. Creer la mission
    cursor.execute("""
        INSERT INTO cart_missions (chariot_id, statut, actif, cree_le)
        VALUES (%s, 'PREPAREE', 1, NOW())
    """, (chariot_id,))
    mission_id = cursor.lastrowid

    # 2. Lier chaque OF a la mission
    for of_number in of_numbers:
        cursor.execute("""
            SELECT item_code, item_desc
            FROM jobs_planning
            WHERE of_number = %s
            LIMIT 1
        """, (of_number,))
        job = cursor.fetchone()
        if job:
            cursor.execute("""
                INSERT INTO cart_mission_jobs
                    (mission_id, of_number, item_code, item_desc, statut)
                VALUES (%s, %s, %s, %s, 'EN_ATTENTE')
            """, (mission_id, of_number, job['item_code'], job['item_desc']))

    # 3. Enregistrer l'evenement
    cursor.execute("""
        INSERT INTO cart_events (mission_id, chariot_id, evenement, ts)
        VALUES (%s, %s, 'MISSION_CREEE', NOW())
    """, (mission_id, chariot_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('mission_detail', mission_id=mission_id))


# ══════════════════════════════════════════════════════════
# DETAIL MISSION — confirmation apres creation
# ══════════════════════════════════════════════════════════

@app.route('/mission/<int:mission_id>')
def mission_detail(mission_id):
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT cm.*, c.nom, c.location, c.operation_code
        FROM cart_missions cm
        JOIN chariots c ON cm.chariot_id = c.chariot_id
        WHERE cm.id = %s
    """, (mission_id,))
    mission = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM cart_mission_jobs WHERE mission_id = %s
    """, (mission_id,))
    jobs = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('ws_mission.html', mission=mission, jobs=jobs)


# ══════════════════════════════════════════════════════════
# API JSON — pour usage futur (mobile, Oracle, etc.)
# ══════════════════════════════════════════════════════════

@app.route('/api/chariots/dispo')
def api_chariots():
    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.chariot_id, c.nom, c.location, c.operation_code
        FROM chariots c
        WHERE c.actif = 1
        AND NOT EXISTS (
            SELECT 1 FROM cart_missions cm
            WHERE cm.chariot_id = c.chariot_id
            AND   cm.statut IN ('PREPAREE','EN_COURS','RETOUR')
            AND   cm.actif = 1
        )
    """)
    data = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify(data)


# ══════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  Dashboard WS — RFID GE HealthCare Buc")
    print("  Acces : http://raspberrypi.local:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
