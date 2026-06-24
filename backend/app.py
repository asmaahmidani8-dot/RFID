"""
app.py — Dashboard Flask Water Spider
GE Healthcare Buc | Ligne Pristina | RFID
"""
import os
import sys
import subprocess
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template, request, jsonify, session
from flask.json.provider import DefaultJSONProvider
from dotenv import load_dotenv
import mysql.connector

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
app.secret_key = "rfid_buc_ge_2026"

# ── Encodeur JSON — gère Decimal et date MySQL ────────────────
class RFIDJsonProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj == int(obj) else float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.strftime("%d/%m/%Y")
        return super().default(obj)

app.json_provider_class = RFIDJsonProvider
app.json = RFIDJsonProvider(app)

# ── Gestionnaire erreurs → toujours retourner JSON ───────────
@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

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
def accueil():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM jobs_planning WHERE statut='RELEASED'")
    total_released = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE actif=1 AND statut!='TERMINEE'")
    total_actives = cur.fetchone()["total"]
    try:
        cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE msca_status='EN_ATTENTE'")
        total_msca_pending = cur.fetchone()["total"]
    except Exception:
        total_msca_pending = 0
    cur.close(); db.close()
    return render_template("accueil.html",
                           total_released=total_released,
                           total_actives=total_actives,
                           total_msca_pending=total_msca_pending)


@app.route("/ws")
def water_spider():
    session.pop("groupe_scan1", None)
    session.pop("depart_scan1", None)
    return render_template("scan.html")


@app.route("/transactions")
def transactions():
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT
            cm.id, cm.statut, cm.ts_preparee, cm.ts_en_attente, cm.ts_terminee,
            COALESCE(cm.msca_status, 'EN_ATTENTE') AS msca_status,
            c.chariot_id, c.nom AS chariot_nom,
            cmj.of_number, cmj.item_code, cmj.operation_code,
            jp.item_desc,
            TIMESTAMPDIFF(MINUTE, cm.ts_en_attente, cm.ts_terminee) AS duree_min
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        LEFT JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
                                  AND jp.operation_code = cmj.operation_code
        ORDER BY cm.ts_preparee DESC
        LIMIT 100
    """)
    transactions = cur.fetchall()

    # Calcul next_op pour chaque transaction
    op_sequence = [10,11,13,14,15,16,17,18,20,25,30,70,80,90]
    for t in transactions:
        op = t.get("operation_code")
        # operation_code peut être 'OP10' ou '10' → extraire le numéro
        op_num = None
        if op:
            op_str = str(op).upper().replace("OP", "")
            if op_str.isdigit():
                op_num = int(op_str)
        if op_num is not None and op_num in op_sequence:
            idx = op_sequence.index(op_num)
            t["next_op"] = op_sequence[idx+1] if idx+1 < len(op_sequence) else None
        else:
            t["next_op"] = None

    cur.execute("SELECT COUNT(*) AS total FROM cart_missions")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE statut='EN_ATTENTE'")
    en_attente = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE statut='TERMINEE'")
    terminees = cur.fetchone()["total"]
    try:
        cur.execute("SELECT COUNT(*) AS total FROM cart_missions WHERE COALESCE(msca_status,'EN_ATTENTE')='EN_ATTENTE'")
        msca_pending = cur.fetchone()["total"]
    except Exception:
        msca_pending = 0

    cur.close(); db.close()
    return render_template("transactions.html",
                           transactions=transactions,
                           stats={"total": total, "en_attente": en_attente,
                                  "terminees": terminees, "msca_pending": msca_pending})


@app.route("/operateur")
def operateur():
    # Hardcodé pour la phase de développement
    # À enrichir quand tous les chariots seront ajoutés
    feeders = [
        {"feeder_num": 1, "operation_code": "10"},
        {"feeder_num": 2, "operation_code": "10"},
        {"feeder_num": 3, "operation_code": "10"},
        {"feeder_num": 4, "operation_code": "10"},
        {"feeder_num": 5, "operation_code": "11"},
        {"feeder_num": 6, "operation_code": "11"},
    ]
    postes = [
        {"poste": "1", "operation_code": "13"},
        {"poste": "2", "operation_code": "14"},
        {"poste": "3", "operation_code": "15"},
        {"poste": "6", "operation_code": "17"},
    ]
    return render_template("operateur.html", feeders=feeders, postes=postes)


@app.route("/api/operateur/chariots")
def api_operateur_chariots():
    type_ = request.args.get("type")  # feeder ou poste
    val   = request.args.get("val")
    db = get_db()
    cur = db.cursor(dictionary=True)

    if type_ == "feeder":
        condition = "c.feeder_num = %s"
    else:
        condition = "c.poste = %s"

    cur.execute(f"""
        SELECT cm.id AS mission_id, cm.statut, cm.ts_en_attente,
               c.chariot_id, c.operation_code, c.feeder_num, c.poste,
               cmj.of_number, cmj.item_code,
               jp.item_desc, jp.qty_totale
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        LEFT JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
                                  AND jp.operation_code = cmj.operation_code
        WHERE cm.statut = 'EN_ATTENTE'
          AND cm.actif = 1
          AND {condition}
        ORDER BY cm.ts_en_attente ASC
    """, (val,))
    results = cur.fetchall()
    cur.close(); db.close()
    return jsonify(results)


@app.route("/api/operateur/vide", methods=["POST"])
def api_operateur_vide():
    data       = request.get_json()
    mission_id = data.get("mission_id")
    if not mission_id:
        return jsonify({"ok": False, "error": "mission_id manquant"}), 400
    db = get_db()
    cur = db.cursor(dictionary=True)
    # Récupérer le chariot_id de cette mission
    cur.execute("SELECT chariot_id FROM cart_missions WHERE id=%s", (mission_id,))
    mission = cur.fetchone()
    if mission:
        # Mission → statut VIDE + chariot.is_vide = 1
        cur.execute("""
            UPDATE cart_missions SET statut='VIDE' WHERE id=%s
        """, (mission_id,))
        cur.execute("UPDATE chariots SET is_vide=1 WHERE chariot_id=%s",
                    (mission["chariot_id"],))
    db.commit()
    cur.close(); db.close()
    return jsonify({"ok": True})


@app.route("/scan")
def scan():
    session.pop("groupe_scan1", None)
    session.pop("depart_scan1", None)
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
# API WATER SPIDER
# ══════════════════════════════════════════════════════════════

@app.route("/api/ws/search")
def ws_search():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT id, of_number, item_code, item_desc, operation_code,
               qty_totale, date_besoin
        FROM jobs_planning
        WHERE statut='RELEASED'
          AND (of_number LIKE %s OR item_code LIKE %s OR item_desc LIKE %s)
        ORDER BY date_besoin ASC
        LIMIT 20
    """, (f"%{q}%", f"%{q}%", f"%{q}%"))
    results = cur.fetchall()
    cur.close(); db.close()
    return jsonify(results)


@app.route("/api/ws/associer", methods=["POST"])
def ws_associer():
    data = request.get_json()
    chariot_id     = data.get("chariot_id", "").strip()
    of_number      = data.get("of_number", "").strip()
    operation_code = data.get("operation_code")

    if not chariot_id or not of_number:
        return jsonify({"ok": False, "error": "chariot_id et of_number requis"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Récupérer le job_id
    cur.execute("SELECT id FROM jobs_planning WHERE of_number=%s AND operation_code=%s LIMIT 1",
                (of_number, operation_code))
    job = cur.fetchone()
    job_id = job["id"] if job else None

    # Créer ou mettre à jour la mission
    cur.execute("""
        INSERT INTO cart_missions (chariot_id, statut, actif, ts_preparee, msca_status)
        VALUES (%s, 'PREPAREE', 1, NOW(), 'EN_ATTENTE')
    """, (chariot_id,))
    mission_id = cur.lastrowid

    # Associer le job à la mission
    if job_id:
        cur.execute("""
            INSERT IGNORE INTO cart_mission_jobs (mission_id, job_id)
            VALUES (%s, %s)
        """, (mission_id, job_id))

    db.commit()
    cur.close(); db.close()
    return jsonify({"ok": True, "mission_id": mission_id})


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

    # ── Vérifier mission active → bloquer le rescan ───────────
    cur.execute("""
        SELECT id, statut FROM cart_missions
        WHERE chariot_id = %s AND actif = 1 AND statut NOT IN ('TERMINEE')
        LIMIT 1
    """, (chariot_id,))
    mission_active = cur.fetchone()
    if mission_active:
        cur.close()
        db.close()
        return jsonify({
            "action": "mission_active",
            "error": f"Ce chariot est déjà en mission #{mission_active['id']} ({mission_active['statut']}). Terminez la mission avant de rescanner.",
            "mission_id": mission_active["id"],
            "statut": mission_active["statut"]
        }), 409

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

            cur.close()
            db.close()
            return jsonify({
                "action": "groupe_forme",
                "chariot1": chariot1,
                "chariot2": chariot
            })

    # ── Type A / C / D ────────────────────────────────────────
    cur.close()
    db.close()
    return jsonify({"action": "chariot_identifie", "chariot": chariot})


def _get_jobs(cur, chariot_id):
    cur.execute("""
        SELECT DISTINCT
            jp.of_number, jp.item_code, jp.item_desc,
            jp.operation_code, jp.qty_totale, jp.date_besoin
        FROM jobs_planning jp
        JOIN chariots c ON c.chariot_id = %s
        JOIN chariot_items ci ON ci.chariot_id = %s
                              AND ci.item_code = jp.item_code
        WHERE jp.statut = 'RELEASED'
          AND jp.operation_code = CONCAT('OP', LPAD(c.operation_code, 2, '0'))
        ORDER BY jp.date_besoin ASC, jp.item_code, jp.of_number
    """, (chariot_id, chariot_id))
    rows = cur.fetchall()
    for r in rows:
        if r.get("date_besoin"):
            r["date_besoin"] = r["date_besoin"].strftime("%d/%m/%Y")
    return rows


@app.route("/api/jobs", methods=["POST"])
def api_jobs():
    """Sync Oracle puis retourne les OFs compatibles avec le chariot."""
    data = request.get_json()
    chariot_id = data.get("chariot_id")

    if not chariot_id:
        return jsonify({"error": "chariot_id manquant"}), 400

    # ── Sync Oracle (désactivable via ORACLE_SYNC=false dans .env)
    sync_ok = False
    if os.getenv("ORACLE_SYNC", "true").lower() == "true":
        try:
            sync_script = os.path.join(os.path.dirname(__file__), "sync_oracle.py")
            env = {**os.environ}
            ic_path = "/home/ge/instantclient_23_26"
            if os.path.exists(ic_path):
                env["LD_LIBRARY_PATH"] = ic_path + ":" + env.get("LD_LIBRARY_PATH", "")
            result = subprocess.run(
                [sys.executable, sync_script],
                timeout=10,
                env=env,
                capture_output=True
            )
            sync_ok = (result.returncode == 0)
        except Exception:
            pass  # Sync échouée → données en cache MySQL

    # ── Requête jobs ──────────────────────────────────────────
    db = get_db()
    cur = db.cursor(dictionary=True)
    jobs_list = _get_jobs(cur, chariot_id)
    cur.close()
    db.close()

    return jsonify({"jobs": jobs_list, "sync_ok": sync_ok})


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
                        (of_number, operation_code, item_code, statut, mission_id, cree_le)
                    VALUES (%s, %s, %s, 'ASSIGNE', %s, %s)
                """, (sel["of_number"], sel["op_code"], sel["item_code"], mid, now))

            cur.execute("""
                UPDATE jobs_planning SET statut='ASSIGNE'
                WHERE of_number=%s AND operation_code=%s
            """, (sel["of_number"], sel["op_code"]))

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
    cur.execute("SELECT COUNT(*) AS n FROM cart_missions WHERE actif=1 AND statut!='TERMINEE'")
    actives = cur.fetchone()["n"]
    cur.close()
    db.close()
    return jsonify({"released": released, "assigned": assigned, "actives": actives})


@app.route("/chariots-vides")
def chariots_vides():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT cm.id AS mission_id, c.chariot_id, c.nom,
               c.type_chariot, c.operation_code, c.feeder_num, c.poste,
               cm.ts_en_attente
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        WHERE cm.statut = 'VIDE' AND cm.actif = 1
        ORDER BY cm.ts_en_attente ASC
    """)
    chariots_list = cur.fetchall()
    cur.close(); db.close()
    return render_template("chariots_vides.html", chariots=chariots_list)


@app.route("/api/chariots-vides")
def api_chariots_vides():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT cm.id AS mission_id, c.chariot_id, c.nom,
               c.type_chariot, c.operation_code, c.feeder_num, c.poste
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        WHERE cm.statut = 'VIDE' AND cm.actif = 1
        ORDER BY cm.ts_en_attente ASC
    """)
    chariots = cur.fetchall()
    cur.close(); db.close()
    return jsonify(chariots)


# ── Pick-to-Light (désactivé) ─────────────────────────────────
# from ptl import init_ptl
# init_ptl(app)

if __name__ == "__main__":
    cert = os.path.expanduser("~/cert.pem")
    key  = os.path.expanduser("~/key.pem")
    ssl_ctx = (cert, key) if os.path.exists(cert) else None
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_ctx)
