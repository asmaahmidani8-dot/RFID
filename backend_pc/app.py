"""
app.py — Dashboard Flask Water Spider
GE Healthcare Buc | Ligne Pristina | RFID
"""
import os
import sys
import subprocess
import threading
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template, request, jsonify, session, send_file, Response
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


def _find_active_mission(cur, chariot_ids):
    ids = sorted({cid for cid in chariot_ids if cid})
    if not ids:
        return None
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(f"""
        SELECT id, chariot_id, statut
        FROM cart_missions
        WHERE actif = 1
          AND COALESCE(statut, '') NOT IN ('TERMINEE', 'ANNULE', 'ANNULEE')
          AND chariot_id IN ({placeholders})
        ORDER BY ts_preparee DESC, id DESC
        LIMIT 1
    """, tuple(ids))
    return cur.fetchone()


def _fetch_routing_background(of_numbers):
    try:
        import sync_oracle
        sync_oracle.fetch_routing_for_of(of_numbers)
    except Exception as e:
        print(f"[WARN] routing non recupere en arriere-plan : {e}")


# ── Favicon (évite le 500 dans les logs : le navigateur le demande tout seul) ──
@app.route("/favicon.ico")
def favicon():
    return "", 204


# ── QR code généré côté SERVEUR (zéro dépendance internet/CDN) ──
@app.route("/api/qr")
def api_qr():
    """Génère un QR PNG sur le Pi. Usage : /api/qr?text=29434505"""
    text = request.args.get("text", "") or " "
    try:
        import io
        import qrcode
        img = qrcode.make(text)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except ImportError:
        return Response("qrcode non installe : pip3 install 'qrcode[pil]'", status=500)


# ── Code-barres CODE 128 généré côté SERVEUR (comme la vraie étiquette GE) ──
@app.route("/api/barcode")
def api_barcode():
    """Génère un code-barres CODE 128 PNG (horizontal). Usage : /api/barcode?text=29434505"""
    text = request.args.get("text", "") or " "
    try:
        import io
        from barcode import Code128
        from barcode.writer import ImageWriter
        buf = io.BytesIO()
        Code128(str(text), writer=ImageWriter()).write(
            buf,
            options={
                "write_text": False,   # pas de texte sous le code (on l'affiche nous-mêmes)
                "module_height": 12.0,
                "module_width": 0.30,
                "quiet_zone": 2.0,
            },
        )
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except ImportError:
        return Response(
            "python-barcode non installe : sudo apt install python3-barcode "
            "(ou pip3 install python-barcode --break-system-packages)",
            status=500,
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


def _op_num(code):
    """'OP10' / '10' -> 10 (numéro d'op). 9999 si invalide."""
    s = str(code or "").upper().replace("OP", "")
    return int(s) if s.isdigit() else 9999


@app.route("/transactions")
def transactions():
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Chariots EN_ATTENTE + leur job/op/assembly/desc + statut du move (MOVE_DONE ?)
    cur.execute("""
        SELECT cm.id AS mission_id, cm.ts_en_attente,
               c.chariot_id, c.nom AS chariot_nom,
               cmj.id AS job_id, cmj.of_number, cmj.operation_code,
               cmj.item_code, cmj.statut AS job_statut,
               jp.item_desc,
               (SELECT MIN(pt.route) FROM postes_travail pt
                 WHERE pt.operation_code = c.operation_code
                   AND pt.numero = COALESCE(CAST(c.feeder_num AS CHAR), c.poste)
                   AND pt.type = CASE WHEN c.feeder_num IS NOT NULL THEN 'feeder' ELSE 'poste' END
               ) AS route
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
                                  AND jp.operation_code = cmj.operation_code
        WHERE cm.statut IN ('EN_ATTENTE', 'EN_COURS') AND cm.actif = 1
        ORDER BY cmj.of_number, cmj.operation_code
    """)
    rows = cur.fetchall()

    # ── État de la file MSCA (oracle_move_queue) par job ──────────
    # On garde la DERNIÈRE demande par job (exe_flag : N=en file, P=en cours, D=fait, E=erreur)
    queue_by_job = {}
    job_ids = [r["job_id"] for r in rows]
    if job_ids:
        fmt = ",".join(["%s"] * len(job_ids))
        cur.execute(f"""
            SELECT q.mission_job_id, q.exe_flag, q.erreur
            FROM oracle_move_queue q
            JOIN (SELECT mission_job_id, MAX(id) AS mid
                  FROM oracle_move_queue
                  WHERE mission_job_id IN ({fmt})
                  GROUP BY mission_job_id) last
              ON last.mid = q.id
        """, tuple(job_ids))
        for q in cur.fetchall():
            queue_by_job[q["mission_job_id"]] = q

    # Pour CHAQUE job : l'op la plus PETITE encore non-movéé = celle qui est PRÊTE.
    # (l'ordre des moves suit le routing = op croissant : OP10 → OP20 → OP25 ...)
    min_pending = {}   # of_number -> plus petit op non-movéé
    for r in rows:
        if r["job_statut"] != 'MOVE_DONE':
            n = _op_num(r["operation_code"])
            of = r["of_number"]
            if of not in min_pending or n < min_pending[of]:
                min_pending[of] = n

    for r in rows:
        r["op_num"] = _op_num(r["operation_code"])
        r["moved"]  = (r["job_statut"] == 'MOVE_DONE')
        # État de la file MSCA pour ce job : None / N / P / D / E
        q = queue_by_job.get(r["job_id"])
        r["queue_flag"]   = q["exe_flag"] if q else None
        r["queue_erreur"] = (q["erreur"] if q else None) or ""
        # Condition 1 (EN_ATTENTE) = déjà filtrée par la requête.
        # Condition 2 (ordre) : prêt = pas movéé ET c'est l'op min non-movéé de son job.
        r["ready"]  = (not r["moved"]) and (min_pending.get(r["of_number"]) == r["op_num"])

    # ── GROUPAGE PAR CHARIOT (1 ligne = 1 chariot, 1 Move = tous ses jobs) ──
    carts = {}   # mission_id -> chariot + ses jobs
    for r in rows:
        c = carts.get(r["mission_id"])
        if not c:
            c = carts[r["mission_id"]] = {
                "mission_id": r["mission_id"],
                "chariot_id": r["chariot_id"],
                "chariot_nom": r["chariot_nom"],
                "route": r.get("route"),
                "jobs": [],
            }
        c["jobs"].append(r)

    carts = list(carts.values())
    for c in carts:
        jobs = c["jobs"]
        c["nb_jobs"]     = len(jobs)
        c["ready_jobs"]  = [j for j in jobs if j["ready"]]
        flags = [j["queue_flag"] for j in jobs]
        # Statut du chariot (priorité) : done < error < in_progress < in_queue < ready < waiting
        if all(j["moved"] for j in jobs):
            c["status"] = "done"
        elif "P" in flags:
            c["status"] = "in_progress"
        elif "N" in flags:
            c["status"] = "in_queue"
        elif "E" in flags:
            c["status"] = "error"
            c["erreur"] = next((j["queue_erreur"] for j in jobs if j["queue_flag"] == "E"), "")
        elif c["ready_jobs"]:
            c["status"] = "ready"
        else:
            c["status"] = "waiting"
        # résumé jobs movéés
        c["n_done"] = sum(1 for j in jobs if j["moved"])

    stats = {
        "tous":    len(carts),
        "ready":   sum(1 for c in carts if c["status"] == "ready"),
        "waiting": sum(1 for c in carts if c["status"] == "waiting"),
        "encours": sum(1 for c in carts if c["status"] in ("in_queue", "in_progress")),
        "done":    sum(1 for c in carts if c["status"] == "done"),
        "error":   sum(1 for c in carts if c["status"] == "error"),
        "route1":  sum(1 for c in carts if c.get("route") == 1),
        "route2":  sum(1 for c in carts if c.get("route") == 2),
    }

    cur.close(); db.close()
    return render_template("transactions.html", carts=carts, stats=stats)


def _ensure_worker_running():
    """Lance le worker oracle_msca.py en arrière-plan S'IL NE TOURNE PAS DÉJÀ.
    Idempotent : un seul worker à la fois (jamais 2 telnet MSCA en parallèle).
    → l'opérateur n'a plus besoin d'ouvrir un 2e terminal."""
    try:
        out = subprocess.run(["pgrep", "-f", "oracle_msca.py"],
                             capture_output=True, text=True)
        if out.stdout.strip():
            return False   # déjà en cours
    except Exception:
        pass
    here = os.path.dirname(__file__)
    logf = open(os.path.join(here, "worker.log"), "a")
    subprocess.Popen(
        ["python3", os.path.join(here, "oracle_msca.py")],
        stdout=logf, stderr=subprocess.STDOUT,
        start_new_session=True,   # détaché : survit même si Flask redémarre
    )
    print("[WORKER] oracle_msca.py lancé automatiquement")
    return True


def _enqueue_job(cur, job):
    """Empile UN job dans oracle_move_queue (exe_flag='N') avec protection doublon Type B.
    `job` = dict {id, of_number, operation_code, item_code, statut}.
    Retourne (queued: bool, message: str). Ne commit PAS (l'appelant commit)."""
    if job["statut"] == 'MOVE_DONE':
        return False, "déjà movéé"

    # Protection doublon Type B : move N/P/D déjà existante pour ce of+op → SKIP
    cur.execute("""
        SELECT COUNT(*) AS n
        FROM oracle_move_queue omq
        JOIN cart_mission_jobs cmj ON cmj.id = omq.mission_job_id
        WHERE cmj.of_number = %s AND cmj.operation_code = %s
          AND omq.exe_flag IN ('N','P','D')
    """, (job["of_number"], job["operation_code"]))
    if cur.fetchone()["n"] > 0:
        return False, "doublon ignoré"

    cur.execute("""
        INSERT INTO oracle_move_queue
            (mission_job_id, of_number, operation_code, item_code, qty, exe_flag)
        VALUES (%s, %s, %s, %s, 1, 'N')
    """, (job["id"], job["of_number"], job["operation_code"], job.get("item_code")))
    return True, "ajoutée à la file"


@app.route("/api/transactions/move", methods=["POST"])
def api_transaction_move():
    """Move d'UN job (job_id) : empile dans la file + lance le worker auto.
    Le worker traite UN PAR UN → pas de désync. Doublon Type B géré."""
    data = request.get_json() or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"success": False, "error": "job_id manquant"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("""SELECT id, of_number, operation_code, item_code, statut
                       FROM cart_mission_jobs WHERE id=%s""", (job_id,))
        job = cur.fetchone()
        if not job:
            return jsonify({"success": False, "error": "job introuvable"}), 404

        queued, msg = _enqueue_job(cur, job)
        db.commit()
        if queued:
            _ensure_worker_running()
        return jsonify({"success": True, "queued": queued, "message": msg})
    finally:
        cur.close(); db.close()


@app.route("/api/transactions/move-chariot", methods=["POST"])
def api_transaction_move_chariot():
    """Move d'un CHARIOT (mission_id) : empile TOUS ses jobs PRÊTS d'un coup
    (respecte l'ordre des op = on n'empile que l'op la plus basse non-movéé de chaque OF),
    puis lance le worker auto. 1 clic = nb_jobs moves."""
    data = request.get_json() or {}
    mission_id = data.get("mission_id")
    if not mission_id:
        return jsonify({"success": False, "error": "mission_id manquant"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        # Tous les jobs du chariot (cette mission)
        cur.execute("""SELECT id, of_number, operation_code, item_code, statut
                       FROM cart_mission_jobs WHERE mission_id=%s""", (mission_id,))
        jobs = cur.fetchall()
        if not jobs:
            return jsonify({"success": False, "error": "aucun job pour ce chariot"}), 404

        # Op la plus basse non-movéé par OF (= l'op PRÊTE de chaque job)
        min_pending = {}
        for j in jobs:
            if j["statut"] != 'MOVE_DONE':
                n = _op_num(j["operation_code"])
                of = j["of_number"]
                if of not in min_pending or n < min_pending[of]:
                    min_pending[of] = n

        # On empile seulement les jobs PRÊTS (op == op min non-movéé de leur OF)
        n_queued = 0
        for j in jobs:
            if j["statut"] == 'MOVE_DONE':
                continue
            if _op_num(j["operation_code"]) != min_pending.get(j["of_number"]):
                continue   # pas encore son tour (ordre du routing)
            queued, _msg = _enqueue_job(cur, j)
            if queued:
                n_queued += 1
        db.commit()

        if n_queued:
            _ensure_worker_running()
        return jsonify({"success": True, "queued": n_queued > 0, "n_queued": n_queued,
                        "message": f"{n_queued} job(s) ajouté(s) à la file"})
    finally:
        cur.close(); db.close()


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

    # 1 ligne = 1 JOB (la consommation se suit job par job via conso_statut).
    cur.execute(f"""
        SELECT cm.id AS mission_id, cm.statut AS mission_statut, cm.ts_en_attente,
               c.chariot_id, c.nom AS chariot_nom, c.feeder_num, c.poste,
               cmj.id AS job_id, cmj.of_number, cmj.item_code,
               cmj.operation_code AS operation_code,
               COALESCE(cmj.conso_statut, 'EN_ATTENTE') AS conso_statut,
               jp.item_desc, jp.qty_totale
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
                                  AND jp.operation_code = cmj.operation_code
        WHERE cm.statut IN ('EN_ATTENTE', 'EN_COURS')
          AND cm.actif = 1
          AND {condition}
          -- Un JOB n'apparaît à l'opérateur QUE si SON move est fait...
          AND cmj.statut = 'MOVE_DONE'
          -- ...et tant qu'il n'est pas encore vidé (consommé)
          AND COALESCE(cmj.conso_statut, 'EN_ATTENTE') <> 'VIDE'
        ORDER BY cm.ts_en_attente ASC, cmj.operation_code ASC
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


@app.route("/api/operateur/encours", methods=["POST"])
def api_operateur_encours():
    """L'opérateur COMMENCE à consommer le chariot → statut EN_COURS."""
    data = request.get_json()
    mission_id = data.get("mission_id")
    if not mission_id:
        return jsonify({"ok": False, "error": "mission_id manquant"}), 400
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("UPDATE cart_missions SET statut='EN_COURS' WHERE id=%s", (mission_id,))
    db.commit()
    cur.close(); db.close()
    return jsonify({"ok": True})


# ── Consommation PAR JOB (chariot multi-jobs : chaque job se traite séparément) ──
@app.route("/api/operateur/job/encours", methods=["POST"])
def api_operateur_job_encours():
    """Un JOB précis passe EN COURS de consommation (conso_statut='EN_COURS').
    La mission passe EN_COURS dès qu'au moins un job est en consommation."""
    data = request.get_json() or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"ok": False, "error": "job_id manquant"}), 400
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("UPDATE cart_mission_jobs SET conso_statut='EN_COURS' WHERE id=%s", (job_id,))
    cur.execute("SELECT mission_id FROM cart_mission_jobs WHERE id=%s", (job_id,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE cart_missions SET statut='EN_COURS' "
                    "WHERE id=%s AND statut='EN_ATTENTE'", (row["mission_id"],))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True})


@app.route("/api/operateur/job/vide", methods=["POST"])
def api_operateur_job_vide():
    """Un JOB précis est consommé (conso_statut='VIDE').
    Quand TOUS les jobs du chariot sont VIDE → la mission passe VIDE + chariot.is_vide=1."""
    data = request.get_json() or {}
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"ok": False, "error": "job_id manquant"}), 400
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("UPDATE cart_mission_jobs SET conso_statut='VIDE' WHERE id=%s", (job_id,))
    cur.execute("SELECT mission_id FROM cart_mission_jobs WHERE id=%s", (job_id,))
    row = cur.fetchone()
    mission_vide = False
    if row:
        mission_id = row["mission_id"]
        # reste-t-il un job non vidé sur ce chariot ?
        cur.execute("""SELECT COUNT(*) AS reste FROM cart_mission_jobs
                       WHERE mission_id=%s
                         AND COALESCE(conso_statut,'EN_ATTENTE') <> 'VIDE'""", (mission_id,))
        if cur.fetchone()["reste"] == 0:
            cur.execute("SELECT chariot_id FROM cart_missions WHERE id=%s", (mission_id,))
            m = cur.fetchone()
            cur.execute("UPDATE cart_missions SET statut='VIDE' WHERE id=%s", (mission_id,))
            if m:
                cur.execute("UPDATE chariots SET is_vide=1 WHERE chariot_id=%s",
                            (m["chariot_id"],))
            mission_vide = True
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True, "mission_vide": mission_vide})


# ══════════════════════════════════════════════════════════════
# PILOTAGE WATER SPIDER — ordres de réapprovisionnement (V1)
# Réserve d'une OP = nb d'unités EN_ATTENTE (Type B = 1 unité par groupe).
# Manque = objectif − réserve. Objectif configurable par (poste, OP), défaut 3.
# ══════════════════════════════════════════════════════════════
OBJECTIF_RESERVE_DEFAUT = 3

@app.route("/ws-ordres")
def ws_ordres():
    return render_template("ws_ordres.html")


def _pkey(type_p, numero, partie, op):
    """Clé d'un poste : (type, numero, partie, op). partie peut être None."""
    return (type_p, str(numero), (int(partie) if partie is not None else None), str(op))


@app.route("/api/ws/ordres")
def api_ws_ordres():
    db = get_db(); cur = db.cursor(dictionary=True)

    # 1) Les POSTES (source de vérité = postes_travail) : 1 ligne = poste(+partie) + objectif
    postes = []
    try:
        cur.execute("""SELECT type, numero, partie, operation_code, objectif_reserve, nom
                       FROM postes_travail WHERE actif = 1""")
        postes = cur.fetchall()
    except Exception:
        postes = []   # table absente → pas d'ordres (rien à piloter)

    # 2) Réserve réelle = nb chariots EN_ATTENTE par (type, numero, partie, OP)
    cur.execute("""
        SELECT CASE WHEN c.feeder_num IS NOT NULL THEN 'feeder' ELSE 'poste' END AS type,
               COALESCE(CAST(c.feeder_num AS CHAR), c.poste) AS numero,
               c.partie, c.operation_code, COUNT(*) AS n
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        WHERE cm.actif = 1 AND cm.statut = 'EN_ATTENTE'
        GROUP BY 1, 2, 3, 4
    """)
    reserve = {}
    for r in cur.fetchall():
        reserve[_pkey(r["type"], r["numero"], r["partie"], r["operation_code"])] = r["n"]

    # 3) FIFO : plus ancien VIDE par (type, numero, partie, OP)
    cur.execute("""
        SELECT CASE WHEN c.feeder_num IS NOT NULL THEN 'feeder' ELSE 'poste' END AS type,
               COALESCE(CAST(c.feeder_num AS CHAR), c.poste) AS numero,
               c.partie, c.operation_code, MIN(cm.ts_terminee) AS depuis
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        WHERE cm.actif = 1 AND cm.statut = 'VIDE'
        GROUP BY 1, 2, 3, 4
    """)
    fifo = {}
    for r in cur.fetchall():
        fifo[_pkey(r["type"], r["numero"], r["partie"], r["operation_code"])] = r["depuis"]

    # 4) Construire les ordres (uniquement là où il manque des chariots)
    now = datetime.now()
    ordres = []
    for p in postes:
        key      = _pkey(p["type"], p["numero"], p["partie"], p["operation_code"])
        objectif = p["objectif_reserve"]
        res      = reserve.get(key, 0)
        manque   = objectif - res
        if manque <= 0:
            continue
        niveau = "critique" if res == 0 else ("urgent" if res == 1 else "normal")
        depuis = fifo.get(key)
        depuis_min = int((now - depuis).total_seconds() // 60) if depuis else None
        label = p["nom"] or (("Feeder " if p["type"] == "feeder" else "Poste ") + str(p["numero"]))
        ordres.append({
            "label": label, "operation_code": str(p["operation_code"]),
            "partie": p["partie"], "objectif": objectif, "reserve": res, "manque": manque,
            "niveau": niveau, "depuis_min": depuis_min,
            "_sort_depuis": depuis.timestamp() if depuis else now.timestamp(),
        })

    # 5) Tri : réserve la plus basse d'abord, puis FIFO (manque le plus ancien)
    ordres.sort(key=lambda o: (o["reserve"], o["_sort_depuis"]))
    for o in ordres:
        o.pop("_sort_depuis", None)

    cur.close(); db.close()
    return jsonify(ordres)


@app.route("/etiquette")
def etiquette():
    """Page : le WS scanne un chariot → voit son étiquette."""
    return render_template("etiquette.html")


def _etiquette_data(cur, chariot_id):
    """Données d'étiquette d'un chariot (sa mission active + job). None si aucune."""
    cur.execute("""
        SELECT cm.id AS mission_id, cm.statut, cm.groupe_id,
               c.chariot_id, c.nom, c.type_chariot, c.partie,
               c.operation_code AS chariot_op,
               cmj.of_number, cmj.item_code, cmj.operation_code AS job_op,
               jp.item_desc, jp.qty_totale
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        LEFT JOIN cart_mission_jobs cmj ON cmj.mission_id = cm.id
        LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
                                  AND jp.operation_code = cmj.operation_code
        WHERE c.chariot_id = %s AND cm.actif = 1 AND cm.statut != 'TERMINEE'
        ORDER BY cm.ts_preparee DESC
        LIMIT 1
    """, (chariot_id,))
    row = cur.fetchone()
    if not row:
        return None
    row["operation_code"] = row.get("job_op") or row.get("chariot_op")
    row["org"] = "BXD"
    return row


@app.route("/api/chariot/etiquette")
def api_chariot_etiquette():
    """Étiquette d'un chariot = sa mission active + job. Si Type B groupé → + binôme."""
    chariot_id = request.args.get("chariot_id", "").strip()
    if not chariot_id:
        return jsonify({"error": "chariot_id manquant"}), 400
    db = get_db()
    cur = db.cursor(dictionary=True)
    row = _etiquette_data(cur, chariot_id)
    if not row:
        cur.close(); db.close()
        return jsonify({"error": f"Aucune mission active pour {chariot_id}"}), 404

    # Binôme : si Type B + groupe → l'autre chariot du même groupe
    binome = None
    if row.get("type_chariot") == "B" and row.get("groupe_id"):
        cur.execute("""
            SELECT c.chariot_id FROM cart_missions cm
            JOIN chariots c ON c.chariot_id = cm.chariot_id
            WHERE cm.groupe_id = %s AND cm.actif = 1 AND cm.statut != 'TERMINEE'
              AND c.chariot_id <> %s
            LIMIT 1
        """, (row["groupe_id"], chariot_id))
        b = cur.fetchone()
        if b:
            binome = _etiquette_data(cur, b["chariot_id"])
    cur.close(); db.close()
    row["binome"] = binome
    return jsonify(row)


@app.route("/api/chariots-en-mission")
def api_chariots_en_mission():
    """Liste des chariots ayant une mission active (pour le menu 'Choisir')."""
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT DISTINCT c.chariot_id, c.nom, c.type_chariot
        FROM cart_missions cm
        JOIN chariots c ON c.chariot_id = cm.chariot_id
        WHERE cm.actif = 1 AND cm.statut != 'TERMINEE'
        ORDER BY c.chariot_id
    """)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


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
    mission_active = _find_active_mission(cur, [chariot_id])
    if mission_active:
        cur.close()
        db.close()
        return jsonify({
            "action": "mission_active",
            "error": f"Ce chariot est deja en mission #{mission_active['id']} ({mission_active['statut']}). Terminez la mission avant de rescanner.",
            "chariot_id": mission_active["chariot_id"],
            "mission_id": mission_active["id"],
            "statut": mission_active["statut"]
        })

    # ── Type B → 1 scan + CHOIX du partenaire (l'autre partie, libre) ──
    #    Pool : on scanne 1 chariot, puis on TAPE la partie 2 présente
    #    dans la liste des chariots de l'AUTRE partie, même feeder/op, LIBRES.
    if chariot["type_chariot"] == "B":
        autre_partie = 2 if chariot.get("partie") == 1 else 1
        cur.execute("""
            SELECT c.chariot_id, c.nom, c.partie, c.operation_code, c.feeder_num
            FROM chariots c
            WHERE c.actif = 1 AND c.type_chariot = 'B'
              AND c.feeder_num = %s AND c.operation_code = %s
              AND c.partie = %s
              AND c.chariot_id <> %s
              AND NOT EXISTS (
                  SELECT 1 FROM cart_missions cm
                  WHERE cm.chariot_id = c.chariot_id AND cm.actif = 1
                    AND cm.statut NOT IN ('TERMINEE', 'ANNULE', 'ANNULEE')
              )
            ORDER BY c.chariot_id
        """, (chariot["feeder_num"], chariot["operation_code"], autre_partie, chariot_id))
        partenaires = cur.fetchall()
        cur.close(); db.close()
        return jsonify({
            "action": "choisir_partenaire",
            "chariot": chariot,
            "autre_partie": autre_partie,
            "partenaires": partenaires
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
    chariot2_id = data.get("chariot2_id")

    if not chariot_id:
        return jsonify({"error": "chariot_id manquant"}), 400

    # Avant Oracle : si un des chariots est deja en mission, reponse immediate.
    db = get_db()
    cur = db.cursor(dictionary=True)
    mission_active = _find_active_mission(cur, [chariot_id, chariot2_id])
    cur.close()
    db.close()
    if mission_active:
        return jsonify({
            "action": "mission_active",
            "error": f"Le chariot {mission_active['chariot_id']} est deja en mission #{mission_active['id']} ({mission_active['statut']}).",
            "chariot_id": mission_active["chariot_id"],
            "mission_id": mission_active["id"],
            "statut": mission_active["statut"]
        })

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


def _release_locks(cur, lock_names):
    """Libère les verrous MySQL EN CONSOMMANT le résultat de chaque SELECT
    RELEASE_LOCK (sinon le connecteur lève 'Unread result found' au execute/close suivant)."""
    for ln in reversed(lock_names):
        cur.execute("SELECT RELEASE_LOCK(%s)", (ln,))
        cur.fetchall()


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
    lock_names = []

    try:
        chariot_ids = [cid for cid in [chariot_id, chariot2_id] if cid]
        for cid in sorted(set(chariot_ids)):
            lock_name = f"mission_create:{cid}"
            cur.execute("SELECT GET_LOCK(%s, 5) AS locked", (lock_name,))
            locked = cur.fetchone()["locked"]
            if locked != 1:
                _release_locks(cur, lock_names)
                cur.close()
                db.close()
                return jsonify({
                    "success": False,
                    "error": f"Creation mission deja en cours pour {cid}"
                }), 409
            lock_names.append(lock_name)

        placeholders = ",".join(["%s"] * len(chariot_ids))
        cur.execute(f"""
            SELECT id, chariot_id, statut
            FROM cart_missions
            WHERE actif = 1
              AND statut NOT IN ('TERMINEE', 'ANNULE')
              AND chariot_id IN ({placeholders})
            ORDER BY ts_preparee DESC, id DESC
        """, tuple(chariot_ids))
        missions_actives = cur.fetchall()
        if missions_actives:
            details = ", ".join(
                f"{m['chariot_id']} mission #{m['id']} ({m['statut']})"
                for m in missions_actives
            )
            _release_locks(cur, lock_names)
            cur.close()
            db.close()
            return jsonify({
                "success": False,
                "error": f"Mission active deja existante : {details}"
            }), 409

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
        _release_locks(cur, lock_names)
        lock_names = []

        # Non bloquant : la page repond tout de suite, Oracle continue en arriere-plan.
        if os.getenv("ORACLE_SYNC", "true").lower() == "true":
            ofs = list({s["of_number"] for s in selections})
            threading.Thread(
                target=_fetch_routing_background,
                args=(ofs,),
                daemon=True
            ).start()

        cur.close()
        db.close()
        return jsonify({"success": True, "mission_id": mission1_id})

    except Exception as e:
        db.rollback()
        try:
            _release_locks(cur, lock_names)
        except Exception:
            pass
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


# ══════════════════════════════════════════════════════════════
# PARAMÈTRES — configuration & dépannage (sans SQL manuel)
# ══════════════════════════════════════════════════════════════
@app.route("/parametres")
def parametres():
    return render_template("parametres.html")


# ── CHARIOTS : liste + état (en mission ?) ────────────────────
@app.route("/api/params/chariots")
def api_params_chariots():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT c.chariot_id, c.nom, c.type_chariot, c.operation_code,
               c.nb_jobs, c.feeder_num, c.partie, c.poste, c.actif, c.is_vide,
               cm.id AS mission_id, cm.statut AS mission_statut
        FROM chariots c
        LEFT JOIN cart_missions cm
               ON cm.chariot_id = c.chariot_id AND cm.actif = 1 AND cm.statut <> 'TERMINEE'
        ORDER BY c.chariot_id
    """)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/params/chariot/save", methods=["POST"])
def api_params_chariot_save():
    d = request.get_json() or {}
    cid = (d.get("chariot_id") or "").strip()
    if not cid:
        return jsonify({"ok": False, "error": "chariot_id manquant"}), 400
    db = get_db(); cur = db.cursor()
    cur.execute("""
        INSERT INTO chariots (chariot_id, nom, type_chariot, operation_code,
                              nb_jobs, feeder_num, partie, poste, actif)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1)
        ON DUPLICATE KEY UPDATE
            nom=VALUES(nom), type_chariot=VALUES(type_chariot),
            operation_code=VALUES(operation_code), nb_jobs=VALUES(nb_jobs),
            feeder_num=VALUES(feeder_num), partie=VALUES(partie), poste=VALUES(poste)
    """, (cid, d.get("nom"), (d.get("type_chariot") or "A"), (d.get("operation_code") or "10"),
          d.get("nb_jobs") or 1, d.get("feeder_num") or None,
          d.get("partie") or None, d.get("poste") or None))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True})


@app.route("/api/params/chariot/toggle", methods=["POST"])
def api_params_chariot_toggle():
    cid = (request.get_json() or {}).get("chariot_id")
    if not cid:
        return jsonify({"ok": False, "error": "chariot_id manquant"}), 400
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE chariots SET actif = 1 - actif WHERE chariot_id=%s", (cid,))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True})


@app.route("/api/params/chariot/debloquer", methods=["POST"])
def api_params_chariot_debloquer():
    """Sort un chariot d'une mission coincée : désactive ses missions actives
    (hors TERMINEE) + remet is_vide=0. Le chariot redevient libre."""
    cid = (request.get_json() or {}).get("chariot_id")
    if not cid:
        return jsonify({"ok": False, "error": "chariot_id manquant"}), 400
    db = get_db(); cur = db.cursor()
    cur.execute("""UPDATE cart_missions SET actif=0
                   WHERE chariot_id=%s AND actif=1 AND statut <> 'TERMINEE'""", (cid,))
    n = cur.rowcount
    cur.execute("UPDATE chariots SET is_vide=0 WHERE chariot_id=%s", (cid,))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True, "missions_liberees": n})


# ── BADGES RFID : association UID ↔ chariot ───────────────────
@app.route("/api/params/badges")
def api_params_badges():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT rc.uid, rc.chariot_id, rc.badge_type, rc.actif, c.nom
        FROM rfid_cards rc
        LEFT JOIN chariots c ON c.chariot_id = rc.chariot_id
        ORDER BY rc.chariot_id, rc.badge_type
    """)
    rows = cur.fetchall()
    cur.close(); db.close()
    return jsonify(rows)


@app.route("/api/params/badge/save", methods=["POST"])
def api_params_badge_save():
    d = request.get_json() or {}
    uid = (d.get("uid") or "").strip()
    cid = (d.get("chariot_id") or "").strip()
    btype = (d.get("badge_type") or "START").strip().upper()
    if not uid or not cid:
        return jsonify({"ok": False, "error": "uid et chariot_id requis"}), 400
    db = get_db(); cur = db.cursor()
    cur.execute("""
        INSERT INTO rfid_cards (uid, chariot_id, badge_type, actif)
        VALUES (%s,%s,%s,1)
        ON DUPLICATE KEY UPDATE chariot_id=VALUES(chariot_id),
            badge_type=VALUES(badge_type), actif=1
    """, (uid, cid, btype))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True})


@app.route("/api/params/badge/toggle", methods=["POST"])
def api_params_badge_toggle():
    uid = (request.get_json() or {}).get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "uid manquant"}), 400
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE rfid_cards SET actif = 1 - actif WHERE uid=%s", (uid,))
    db.commit(); cur.close(); db.close()
    return jsonify({"ok": True})


# ── RÉSERVE (objectif par OP) ─────────────────────────────────
@app.route("/api/params/reserve")
def api_params_reserve():
    db = get_db(); cur = db.cursor(dictionary=True)
    rows = []
    try:
        # 1 ligne = 1 poste (feeder/poste) + OP + partie. Pas de redondance par chariot.
        cur.execute("""SELECT id, type, numero, partie, operation_code, objectif_reserve, nom
                       FROM postes_travail ORDER BY type, numero, partie""")
        rows = cur.fetchall()
    except Exception:
        rows = []   # table pas encore créée
    cur.close(); db.close()
    return jsonify({"defaut": OBJECTIF_RESERVE_DEFAUT, "config": rows})


@app.route("/api/params/reserve/save", methods=["POST"])
def api_params_reserve_save():
    """Met à jour l'objectif de réserve d'un poste (par id de postes_travail)."""
    d = request.get_json() or {}
    pid = d.get("id")
    obj = int(d.get("objectif") or 3)
    if not pid:
        return jsonify({"ok": False, "error": "id du poste manquant"}), 400
    db = get_db(); cur = db.cursor()
    try:
        cur.execute("UPDATE postes_travail SET objectif_reserve=%s WHERE id=%s", (obj, pid))
        db.commit()
    except Exception as e:
        cur.close(); db.close()
        return jsonify({"ok": False, "error": f"Table postes_travail absente ? ({e})"}), 500
    cur.close(); db.close()
    return jsonify({"ok": True})


# ── DÉPANNAGE : relancer / vider la file de moves ─────────────
@app.route("/api/params/moves/retry", methods=["POST"])
def api_params_moves_retry():
    """Remet toutes les moves en ERREUR (E) à traiter (N) + relance le worker."""
    db = get_db(); cur = db.cursor()
    cur.execute("UPDATE oracle_move_queue SET exe_flag='N', erreur=NULL WHERE exe_flag='E'")
    n = cur.rowcount
    db.commit(); cur.close(); db.close()
    if n:
        _ensure_worker_running()
    return jsonify({"ok": True, "relancees": n})


# ── SUPERVISION : chiffres clés ───────────────────────────────
@app.route("/api/params/sante")
def api_params_sante():
    db = get_db(); cur = db.cursor(dictionary=True)
    def one(q):
        cur.execute(q); return cur.fetchone()["n"]
    data = {
        "chariots_actifs":  one("SELECT COUNT(*) n FROM chariots WHERE actif=1"),
        "missions_actives": one("SELECT COUNT(*) n FROM cart_missions WHERE actif=1 AND statut<>'TERMINEE'"),
        "file_attente":     one("SELECT COUNT(*) n FROM oracle_move_queue WHERE exe_flag='N'"),
        "file_encours":     one("SELECT COUNT(*) n FROM oracle_move_queue WHERE exe_flag='P'"),
        "file_erreur":      one("SELECT COUNT(*) n FROM oracle_move_queue WHERE exe_flag='E'"),
        "badges_actifs":    one("SELECT COUNT(*) n FROM rfid_cards WHERE actif=1"),
    }
    # worker en vie ?
    try:
        out = subprocess.run(["pgrep", "-f", "oracle_msca.py"], capture_output=True, text=True)
        data["worker_actif"] = bool(out.stdout.strip())
    except Exception:
        data["worker_actif"] = None
    cur.close(); db.close()
    return jsonify(data)


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
    here = os.path.dirname(os.path.abspath(__file__))
    cert = os.path.join(here, "cert.pem")
    key  = os.path.join(here, "key.pem")
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # HTTPS : 1) certs fournis (cert.pem/key.pem dans le dossier) sinon
    #         2) "adhoc" = certificat auto-signé généré par Flask (pip install pyopenssl)
    if os.path.exists(cert) and os.path.exists(key):
        ssl_ctx = (cert, key)
    else:
        ssl_ctx = "adhoc"

    try:
        app.run(host="0.0.0.0", port=5001, debug=debug, use_reloader=False, ssl_context=ssl_ctx)
    except Exception as e:
        print(f"[WARN] HTTPS indisponible ({e}) → bascule en HTTP. "
              f"Pour HTTPS : pip install pyopenssl")
        app.run(host="0.0.0.0", port=5001, debug=debug, use_reloader=False)
