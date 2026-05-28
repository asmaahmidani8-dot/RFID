"""
app.py — Dashboard Flask Water Spider
GE Healthcare Buc | Ligne Pristina | RFID
"""
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import mysql.connector

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.secret_key = "rfid_buc_ge_2026"

# ── MySQL ─────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "rfid_app"),
        password=os.getenv("MYSQL_PASSWORD", "rfid_pass"),
        database=os.getenv("MYSQL_DB", "rfid_buc"),
        charset="utf8mb4"
    )


# ══════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════

@app.route("/")
def dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT cm.id, cm.statut, cm.ts_preparee,
               c.chariot_id, c.nom, c.type_chariot, c.operation_code,
               COUNT(cmj.id) AS nb_jobs
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        LEFT JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        WHERE cm.actif = 1
        GROUP BY cm.id
        ORDER BY cm.ts_preparee DESC
        LIMIT 20
    """)
    missions = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS total FROM jobs_planning WHERE statut='RELEASED'")
    total_released = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE actif=1 AND statut!='TERMINE'")
    total_actives = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM chariots WHERE actif=1")
    total_chariots = cur.fetchone()["total"]

    cur.close()
    db.close()

    return render_template("dashboard.html",
                           missions=missions,
                           total_released=total_released,
                           total_actives=total_actives,
                           total_chariots=total_chariots)


@app.route("/scan")
def scan():
    session.pop("groupe_scan1", None)
    return render_template("scan.html")


@app.route("/jobs")
def jobs():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT of_number, item_code, item_desc, operation_code,
               qty_faite, qty_totale, date_besoin, statut
        FROM jobs_planning
        WHERE statut = 'RELEASED'
        ORDER BY date_besoin ASC, of_number ASC
        LIMIT 100
    """)
    jobs_list = cur.fetchall()
    cur.close()
    db.close()
    return render_template("jobs.html", jobs=jobs_list)


# ══════════════════════════════════════════════════════════════
# API
# ══════════════════════════════════════════════════════════════

@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json()
    qr_content = data.get("qr_content", "").strip()

    if not qr_content.startswith("CHARIOT:"):
        return jsonify({"error": "QR code invalide"}), 400

    chariot_id = qr_content.replace("CHARIOT:", "").split("|")[0]

    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM chariots WHERE chariot_id=%s AND actif=1", (chariot_id,))
    chariot = cur.fetchone()

    if not chariot:
        cur.close()
        db.close()
        return jsonify({"error": f"Chariot {chariot_id} introuvable"}), 404

    # ── Type B → groupe ───────────────────────────────────────
    if chariot["type_chariot"] == "B":
        scan1 = session.get("groupe_scan1")

        if scan1 is None:
            session["groupe_scan1"] = chariot_id
            cur.close()
            db.close()
            return jsonify({
                "action": "scan_groupe_2",
                "chariot": chariot,
                "message": f"1er chariot scanné : {chariot_id}. Scannez le 2ème chariot."
            })
        else:
            chariot1_id = scan1
            chariot2_id = chariot_id
            session.pop("groupe_scan1", None)

            cur.execute("SELECT * FROM chariots WHERE chariot_id=%s", (chariot1_id,))
            chariot1 = cur.fetchone()

            erreur = None
            if chariot1_id == chariot2_id:
                erreur = "Vous avez scanné le même chariot deux fois !"
            elif chariot["type_chariot"] != "B":
                erreur = f"{chariot2_id} n'est pas un chariot de groupe (Type B)"
            elif chariot["feeder_num"] != chariot1["feeder_num"]:
                erreur = f"Feeders incompatibles : Feeder {chariot1['feeder_num']} ≠ Feeder {chariot['feeder_num']}"
            elif chariot["partie"] == chariot1["partie"]:
                erreur = f"Même partie ({chariot['partie']}) — il faut Partie 1 + Partie 2"

            if erreur:
                return jsonify({"error": erreur, "action": "erreur_groupe"}), 400

            jobs_list = _get_jobs(cur, chariot1_id)
            cur.close()
            db.close()
            return jsonify({
                "action": "groupe_forme",
                "chariot1": chariot1,
                "chariot2": chariot,
                "jobs": jobs_list
            })

    # ── Type A / C / D ────────────────────────────────────────
    jobs_list = _get_jobs(cur, chariot_id)
    cur.close()
    db.close()
    return jsonify({"action": "assigner", "chariot": chariot, "jobs": jobs_list})


def _get_jobs(cur, chariot_id):
    cur.execute("""
        SELECT DISTINCT
            jp.of_number, jp.item_code, jp.item_desc,
            jp.operation_code, jp.qty_totale, jp.date_besoin,
            ci.item_desc AS assembly_name
        FROM jobs_planning jp
        JOIN chariot_items ci ON ci.item_code = jp.item_code AND ci.chariot_id = %s
        JOIN chariots c ON c.chariot_id = %s
        WHERE jp.statut = 'RELEASED'
          AND jp.operation_code = CONCAT('OP', LPAD(c.operation_code, 2, '0'))
          AND jp.of_number NOT IN (
              SELECT cmj.job_number FROM cart_mission_jobs cmj
              JOIN cart_missions cm ON cm.id = cmj.mission_id
              WHERE cm.chariot_id = %s AND cm.actif=1 AND cm.statut != 'TERMINE'
          )
        ORDER BY jp.date_besoin ASC, jp.item_code, jp.of_number
    """, (chariot_id, chariot_id, chariot_id))
    rows = cur.fetchall()
    for r in rows:
        if r.get("date_besoin"):
            r["date_besoin"] = r["date_besoin"].strftime("%d/%m/%Y")
    return rows


@app.route("/api/mission/create", methods=["POST"])
def create_mission():
    data = request.get_json()
    chariot_id  = data.get("chariot_id")
    chariot2_id = data.get("chariot2_id")
    selections  = data.get("selections", [])

    if not chariot_id or not selections:
        return jsonify({"error": "Données manquantes"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)
    now = datetime.now()

    try:
        groupe_id = None
        if chariot2_id:
            cur.execute("INSERT INTO mission_groupes (cree_le) VALUES (%s)", (now,))
            groupe_id = cur.lastrowid

        def creer_mission(cid):
            cur.execute("""
                INSERT INTO cart_missions (statut, ts_preparee, actif, groupe_id, chariot_id)
                VALUES ('PREPAREE', %s, 1, %s, %s)
            """, (now, groupe_id, cid))
            return cur.lastrowid

        mission1_id = creer_mission(chariot_id)
        mission2_id = creer_mission(chariot2_id) if chariot2_id else None

        for sel in selections:
            for mid in filter(None, [mission1_id, mission2_id]):
                cur.execute("""
                    INSERT INTO cart_mission_jobs
                        (item_code, statut, op_code, job_number, mission_id, cree_le)
                    VALUES (%s, 'ASSIGNE', %s, %s, %s, %s)
                """, (sel["item_code"], sel["op_code"], sel["of_number"], mid, now))

            cur.execute("""
                UPDATE jobs_planning SET statut='ASSIGNE'
                WHERE of_number=%s AND item_code=%s
            """, (sel["of_number"], sel["item_code"]))

        db.commit()
        cur.close()
        db.close()
        return jsonify({"success": True, "mission_id": mission1_id})

    except Exception as e:
        db.rollback()
        cur.close()
        db.close()
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def api_stats():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM jobs_planning WHERE statut='RELEASED'")
    released = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM jobs_planning WHERE statut='ASSIGNE'")
    assigned = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM cart_missions WHERE actif=1 AND statut!='TERMINE'")
    actives = cur.fetchone()["n"]
    cur.close()
    db.close()
    return jsonify({"released": released, "assigned": assigned, "actives": actives})


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
