"""
app.py — Serveur Flask RFID Pristina

Architecture industrielle :
  Oracle EBS   : source officielle des jobs Released
  jobs_planning : copie locale rapide (sync toutes 30s)
  cart_missions : suivi RFID réel (SQL Server)

Flux scan :
  Scan START
    1. Cherche job dans jobs_planning local  (rapide)
    2. Si absent → Oracle direct fallback    (1-2s)
    3. Si Oracle indisponible → erreur + mission en attente
    → Crée mission dans cart_missions

  Scan END
    → Clôture mission dans cart_missions
"""

from flask import Flask, request, jsonify, send_from_directory
import os
from datetime import datetime
import pyodbc
import json
import threading

# APScheduler pour sync automatique
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_OK = True
except ImportError:
    SCHEDULER_OK = False
    print("⚠ APScheduler non installé — lance : pip install apscheduler")

# Oracle
try:
    import oracledb
    ORACLE_OK = True
except ImportError:
    ORACLE_OK = False
    print("⚠ oracledb non installé — sync Oracle désactivée")

app = Flask(__name__)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/ws')
def page_ws():
    return send_from_directory(FRONTEND_DIR, 'ws.html')

@app.route('/dashboard')
def page_dashboard():
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

# ─── CONNEXION SQL SERVER ──────────────────────────────────────────────────────
SERVER  = r"localhost\SQLEXPRESS"
DB_NAME = "rfid_pristina"

# ─── CONNEXION ORACLE ──────────────────────────────────────────────────────────
ORACLE_USER     = "TON_USERNAME"       # ← ton username
ORACLE_PASSWORD = "TON_PASSWORD"       # ← ton mot de passe
ORACLE_HOST     = "qahceaexa-scan.ge-healthcare.net"
ORACLE_PORT     = 1521
ORACLE_SERVICE  = "ebs_gltest"
ORGANIZATION_ID = "1731"

def get_oracle():
    """Connexion Oracle directe — temps réel."""
    if not ORACLE_OK:
        return None
    try:
        dsn = oracledb.makedsn(ORACLE_HOST, ORACLE_PORT, service_name=ORACLE_SERVICE)
        return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=dsn)
    except Exception as e:
        print(f"  ⚠ Oracle connexion échouée : {e}")
        return None


def jobs_released_oracle(operation_code, nb_ofs, deja_assignes):
    """
    Interroge Oracle directement pour les jobs Released d'une opération.
    Exclut les OFs déjà assignés dans SQL Server (deja_assignes = liste of_number).
    Retourne une liste de dicts.
    """
    conn_ora = get_oracle()
    if not conn_ora:
        return []

    try:
        # Construire la clause d'exclusion
        exclusions = ""
        if deja_assignes:
            liste = ",".join(f"'{x}'" for x in deja_assignes)
            exclusions = f"AND wen.WIP_ENTITY_NAME NOT IN ({liste})"

        sql = f"""
            SELECT wen.WIP_ENTITY_NAME, ite.SEGMENT1,
                   SUBSTR(ite.DESCRIPTION,1,150), wdj.START_QUANTITY,
                   wdj.SCHEDULED_COMPLETION_DATE,
                   'OP' || wop.OPERATION_SEQ_NUM
            FROM   apps.WIP_DISCRETE_JOBS   wdj,
                   apps.WIP_ENTITIES        wen,
                   apps.MTL_SYSTEM_ITEMS_B  ite,
                   apps.WIP_OPERATIONS      wop
            WHERE  wdj.WIP_ENTITY_ID    = wen.WIP_ENTITY_ID
              AND  wdj.PRIMARY_ITEM_ID  = ite.INVENTORY_ITEM_ID
              AND  wdj.ORGANIZATION_ID  = ite.ORGANIZATION_ID
              AND  wdj.WIP_ENTITY_ID    = wop.WIP_ENTITY_ID
              AND  wdj.STATUS_TYPE      = 3
              AND  wdj.ORGANIZATION_ID  = '{ORGANIZATION_ID}'
              AND  'OP' || wop.OPERATION_SEQ_NUM = '{operation_code}'
              AND  NVL(wop.QUANTITY_COMPLETED,0) < wdj.START_QUANTITY
              {exclusions}
            ORDER BY wdj.SCHEDULED_COMPLETION_DATE ASC, wen.WIP_ENTITY_NAME ASC
            FETCH FIRST {nb_ofs} ROWS ONLY
        """
        c    = conn_ora.cursor()
        rows = c.execute(sql).fetchall()
        conn_ora.close()

        return [{
            "of_number"  : str(r[0]),
            "item_code"  : str(r[1]),
            "item_desc"  : str(r[2] or ""),
            "qty"        : int(r[3]) if r[3] else 1,
            "date_besoin": str(r[4].date()) if r[4] else None,
            "operation_code": str(r[5]),
        } for r in rows]

    except Exception as e:
        print(f"  ⚠ Erreur Oracle query : {e}")
        if conn_ora:
            conn_ora.close()
        return []

CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)


def get_db():
    """
    Retourne une connexion SQL Server.
    pyodbc gère automatiquement un pool de connexions
    → plusieurs scans simultanés = pas de problème
    """
    return pyodbc.connect(CONN_STR, autocommit=False)


# ─── UTILITAIRES ──────────────────────────────────────────────────────────────

def get_scanner_by_ip(c, ip_address):
    """Identifie le scanner par son IP (retourne (scanner_id, type_scan) ou None)."""
    return c.execute(
        "SELECT scanner_id, type_scan FROM rfid_scanners WHERE ip_address = ? AND actif = 1",
        (ip_address,)
    ).fetchone()


def get_card_info(c, uid):
    """Retourne les infos du badge + chariot associé (ou None si inconnu)."""
    return c.execute(
        """SELECT rc.chariot_id, rc.badge_type, ch.nom, ch.station,
                  ch.operation_code, ch.nb_ofs, ch.type_chariot
           FROM rfid_cards rc
           JOIN chariots ch ON ch.chariot_id = rc.chariot_id
           WHERE rc.uid = ? AND rc.actif = 1""",
        (uid,)
    ).fetchone()


def get_mission_active(c, chariot_id):
    """Retourne la mission active (non clôturée) d'un chariot, ou None."""
    return c.execute(
        """SELECT id, statut, of_number, item_code, operation_code, poste_id
           FROM cart_missions
           WHERE chariot_id = ? AND actif = 1
             AND statut NOT IN ('VIDE', 'RETOUR_SUPERMARKET')
           ORDER BY cree_le DESC""",
        (chariot_id,)
    ).fetchone()


def log_event(c, mission_id, rfid_uid, chariot_id, of_number,
              operation_code, poste_id, evenement, fait_par, scanner_id, details=None):
    """Enregistre un événement dans cart_events."""
    c.execute(
        """INSERT INTO cart_events
               (mission_id, rfid_uid, chariot_id, of_number, operation_code,
                poste_id, evenement, fait_par, scanner_id, details)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (mission_id, rfid_uid, chariot_id, of_number, operation_code,
         poste_id, evenement, fait_par, scanner_id,
         json.dumps(details, ensure_ascii=False) if details else None)
    )


# ─── ENDPOINT PRINCIPAL : SCAN RFID ──────────────────────────────────────────

@app.route("/api/scan", methods=["POST"])
def recevoir_scan():
    data      = request.json or {}
    uid       = data.get("uid", "").strip().upper()
    ip_source = request.remote_addr
    now       = datetime.now()

    print(f"\n{'='*55}")
    print(f"  SCAN  {now.strftime('%H:%M:%S')}  UID={uid}  IP={ip_source}")

    if not uid:
        return jsonify({"status": "erreur", "message": "UID vide"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()

        # 1. Identifier le scanner par son IP
        scanner = get_scanner_by_ip(c, ip_source)
        if not scanner:
            print(f"  ⚠ Scanner inconnu pour IP {ip_source}")
            conn.close()
            return jsonify({
                "status" : "erreur",
                "message": f"Scanner non reconnu (IP {ip_source}). Enregistrez-le dans rfid_scanners.",
            }), 404

        scanner_id, type_scan = scanner
        print(f"  Scanner : {scanner_id} ({type_scan})")

        # 2. Identifier le badge
        card = get_card_info(c, uid)
        if not card:
            print(f"  ⚠ Badge inconnu : {uid}")
            conn.close()
            return jsonify({
                "status" : "erreur",
                "message": f"Badge RFID non enregistré ({uid})",
            }), 404

        chariot_id, badge_type, nom, station, operation_code, nb_ofs, type_chariot = card
        print(f"  Chariot : {chariot_id} ({nom})  badge={badge_type}")

        # 3. Router selon le type de scanner
        if type_scan == "SUPERMARCHE":
            result = traiter_scan_supermarche(
                c, uid, chariot_id, badge_type, nom, station,
                operation_code, nb_ofs, type_chariot, scanner_id, now
            )
        elif type_scan == "ZONE_ATTENTE":
            result = traiter_scan_zone_attente(
                c, uid, chariot_id, badge_type, scanner_id, now
            )
        elif type_scan == "RETOUR":
            result = traiter_scan_retour(c, uid, chariot_id, badge_type, scanner_id, now)
        else:
            result = {"status": "erreur", "message": f"Type scan inconnu: {type_scan}"}

        conn.commit()
        conn.close()
        print(f"  → {result.get('action', result.get('status', '?'))}")
        return jsonify(result)

    except Exception as e:
        print(f"  ERREUR : {e}")
        import traceback; traceback.print_exc()
        return jsonify({"status": "erreur", "message": str(e)}), 500


# ─── SYNC ORACLE → jobs_planning (toutes les 30 sec) ────────────────────────

def sync_oracle_background():
    """
    Sync automatique Oracle → jobs_planning.
    Tourne en arrière-plan toutes les 30 secondes.
    """
    if not ORACLE_OK:
        return
    try:
        conn_ora = get_oracle()
        if not conn_ora:
            return

        sql = f"""
            SELECT wen.WIP_ENTITY_NAME, ite.SEGMENT1,
                   SUBSTR(ite.DESCRIPTION,1,150),
                   'OP' || wop.OPERATION_SEQ_NUM,
                   wdj.START_QUANTITY,
                   wdj.SCHEDULED_COMPLETION_DATE
            FROM   apps.WIP_DISCRETE_JOBS   wdj,
                   apps.WIP_ENTITIES        wen,
                   apps.MTL_SYSTEM_ITEMS_B  ite,
                   apps.WIP_OPERATIONS      wop
            WHERE  wdj.WIP_ENTITY_ID   = wen.WIP_ENTITY_ID
              AND  wdj.PRIMARY_ITEM_ID = ite.INVENTORY_ITEM_ID
              AND  wdj.ORGANIZATION_ID = ite.ORGANIZATION_ID
              AND  wdj.WIP_ENTITY_ID   = wop.WIP_ENTITY_ID
              AND  wdj.STATUS_TYPE     = 3
              AND  wdj.ORGANIZATION_ID = '{ORGANIZATION_ID}'
              AND  NVL(wop.QUANTITY_COMPLETED,0) < wdj.START_QUANTITY
            ORDER BY wdj.SCHEDULED_COMPLETION_DATE ASC
        """
        rows = conn_ora.cursor().execute(sql).fetchall()
        conn_ora.close()

        conn_sql = get_db()
        c        = conn_sql.cursor()
        now      = datetime.now()
        nb_new   = 0

        for r in rows:
            of_number      = str(r[0])
            item_code      = str(r[1])
            item_desc      = str(r[2] or "")[:150]
            operation_code = str(r[3])
            qty            = int(r[4]) if r[4] else 1
            date_besoin    = str(r[5].date()) if r[5] else None

            existe = c.execute(
                "SELECT statut FROM jobs_planning WHERE of_number=? AND operation_code=?",
                (of_number, operation_code)
            ).fetchone()

            if not existe:
                c.execute(
                    """INSERT INTO jobs_planning
                           (of_number, operation_code, item_code, item_desc,
                            statut, qty, date_besoin, date_import)
                       VALUES (?,?,?,?,'RELEASED',?,?,?)""",
                    (of_number, operation_code, item_code, item_desc, qty, date_besoin, now)
                )
                nb_new += 1
            elif existe[0] == "RELEASED":
                c.execute(
                    """UPDATE jobs_planning
                       SET item_desc=?, qty=?, date_besoin=?
                       WHERE of_number=? AND operation_code=? AND statut='RELEASED'""",
                    (item_desc, qty, date_besoin, of_number, operation_code)
                )

        conn_sql.commit()
        conn_sql.close()
        if nb_new > 0:
            print(f"  [Sync Oracle] {nb_new} nouveaux jobs — total Oracle: {len(rows)}")

    except Exception as e:
        print(f"  [Sync Oracle] Erreur : {e}")


# ─── CHERCHER JOBS RELEASED (3 niveaux) ──────────────────────────────────────

def chercher_jobs_released(c, operation_code, nb_ofs, deja_assignes):
    """
    3 niveaux de recherche :
      1. jobs_planning local       → rapide (10ms)
      2. Oracle direct fallback    → si absent localement
      3. Si Oracle indispo         → retourne [] + source='indisponible'
    """
    exclusions_sql = ""
    if deja_assignes:
        placeholders = ",".join(["?" for _ in deja_assignes])
        exclusions_sql = f"AND of_number NOT IN ({placeholders})"

    # ── NIVEAU 1 : jobs_planning local ───────────────────────────────────────
    query = f"""
        SELECT TOP(?) of_number, item_code, item_desc, qty, date_besoin
        FROM jobs_planning
        WHERE operation_code=? AND statut='RELEASED'
        {exclusions_sql}
        ORDER BY date_besoin ASC, of_number ASC
    """
    params = [nb_ofs + 10, operation_code] + deja_assignes
    jobs_local = c.execute(query, params).fetchall()

    if jobs_local:
        print(f"  [Jobs] {len(jobs_local)} trouvé(s) localement pour {operation_code}")
        return [{
            "of_number"     : j[0],
            "item_code"     : j[1],
            "item_desc"     : j[2] or "",
            "qty"           : j[3] or 1,
            "date_besoin"   : str(j[4]) if j[4] else None,
            "operation_code": operation_code,
        } for j in jobs_local], "local"

    # ── NIVEAU 2 : Oracle direct fallback ────────────────────────────────────
    print(f"  [Jobs] Rien localement pour {operation_code} → Oracle direct...")
    jobs_oracle = jobs_released_oracle(operation_code, nb_ofs + 10, deja_assignes)

    if jobs_oracle:
        print(f"  [Jobs] {len(jobs_oracle)} trouvé(s) dans Oracle pour {operation_code}")
        # Sauvegarder dans jobs_planning pour les prochains scans
        now = datetime.now()
        for j in jobs_oracle:
            existe = c.execute(
                "SELECT statut FROM jobs_planning WHERE of_number=? AND operation_code=?",
                (j["of_number"], j["operation_code"])
            ).fetchone()
            if not existe:
                c.execute(
                    """INSERT INTO jobs_planning
                           (of_number, operation_code, item_code, item_desc,
                            statut, qty, date_besoin, date_import)
                       VALUES (?,?,?,?,'RELEASED',?,?,?)""",
                    (j["of_number"], j["operation_code"], j["item_code"],
                     j["item_desc"], j["qty"], j["date_besoin"], now)
                )
        return jobs_oracle, "oracle_direct"

    # ── NIVEAU 3 : rien trouvé nulle part ────────────────────────────────────
    print(f"  [Jobs] Aucun job disponible pour {operation_code}")
    return [], "indisponible"


# ─── HELPERS JOBS ────────────────────────────────────────────────────────────

def _inserer_job_mission(c, mission_id, job):
    """Insère un job dans cart_mission_jobs et le marque ASSIGNE dans jobs_planning."""
    c.execute(
        "INSERT INTO cart_mission_jobs (mission_id, of_number, item_code, item_desc, statut) VALUES (?,?,?,?,'EN_ATTENTE')",
        (mission_id, job["of_number"], job["item_code"], job["item_desc"])
    )
    _upsert_job_planning(c, job, statut="ASSIGNE")


def _upsert_job_planning(c, job, statut="RELEASED"):
    """Insère ou met à jour un job dans jobs_planning (cache local Oracle)."""
    existe = c.execute(
        "SELECT statut FROM jobs_planning WHERE of_number=? AND operation_code=?",
        (job["of_number"], job["operation_code"])
    ).fetchone()
    if not existe:
        c.execute(
            """INSERT INTO jobs_planning (of_number, operation_code, item_code, item_desc, statut, qty, date_besoin)
               VALUES (?,?,?,?,?,?,?)""",
            (job["of_number"], job["operation_code"], job["item_code"],
             job["item_desc"], statut, job["qty"], job["date_besoin"])
        )
    elif existe[0] == "RELEASED" and statut != "RELEASED":
        c.execute(
            "UPDATE jobs_planning SET statut=? WHERE of_number=? AND operation_code=?",
            (statut, job["of_number"], job["operation_code"])
        )


# ─── API SYNC ORACLE MANUELLE ────────────────────────────────────────────────

@app.route("/api/sync-oracle", methods=["POST"])
def sync_oracle_manuel():
    """Déclenche une sync Oracle manuelle (bouton dashboard ou cron)."""
    try:
        conn = get_db()
        c    = conn.cursor()
        now  = datetime.now()
        nb   = 0

        conn_ora = get_oracle()
        if not conn_ora:
            conn.close()
            return jsonify({"status": "erreur", "message": "Oracle non accessible"}), 503

        sql = f"""
            SELECT wen.WIP_ENTITY_NAME, ite.SEGMENT1,
                   SUBSTR(ite.DESCRIPTION,1,150),
                   'OP' || wop.OPERATION_SEQ_NUM,
                   wdj.START_QUANTITY, wdj.SCHEDULED_COMPLETION_DATE
            FROM   apps.WIP_DISCRETE_JOBS   wdj,
                   apps.WIP_ENTITIES        wen,
                   apps.MTL_SYSTEM_ITEMS_B  ite,
                   apps.WIP_OPERATIONS      wop
            WHERE  wdj.WIP_ENTITY_ID   = wen.WIP_ENTITY_ID
              AND  wdj.PRIMARY_ITEM_ID = ite.INVENTORY_ITEM_ID
              AND  wdj.ORGANIZATION_ID = ite.ORGANIZATION_ID
              AND  wdj.WIP_ENTITY_ID   = wop.WIP_ENTITY_ID
              AND  wdj.STATUS_TYPE     = 3
              AND  wdj.ORGANIZATION_ID = '{ORGANIZATION_ID}'
              AND  NVL(wop.QUANTITY_COMPLETED,0) < wdj.START_QUANTITY
            ORDER BY wdj.SCHEDULED_COMPLETION_DATE ASC
        """
        rows = conn_ora.cursor().execute(sql).fetchall()
        conn_ora.close()

        for r in rows:
            job = {
                "of_number"     : str(r[0]),
                "item_code"     : str(r[1]),
                "item_desc"     : str(r[2] or "")[:150],
                "operation_code": str(r[3]),
                "qty"           : int(r[4]) if r[4] else 1,
                "date_besoin"   : str(r[5].date()) if r[5] else None,
            }
            existe = c.execute(
                "SELECT statut FROM jobs_planning WHERE of_number=? AND operation_code=?",
                (job["of_number"], job["operation_code"])
            ).fetchone()
            if not existe:
                c.execute(
                    "INSERT INTO jobs_planning (of_number, operation_code, item_code, item_desc, statut, qty, date_besoin, date_import) VALUES (?,?,?,?,'RELEASED',?,?,?)",
                    (job["of_number"], job["operation_code"], job["item_code"],
                     job["item_desc"], job["qty"], job["date_besoin"], now)
                )
                nb += 1
            elif existe[0] == "RELEASED":
                c.execute(
                    "UPDATE jobs_planning SET item_desc=?, qty=?, date_besoin=? WHERE of_number=? AND operation_code=? AND statut='RELEASED'",
                    (job["item_desc"], job["qty"], job["date_besoin"], job["of_number"], job["operation_code"])
                )

        conn.commit()
        conn.close()
        print(f"  Sync Oracle : {len(rows)} rows, {nb} nouveaux")
        return jsonify({"status": "ok", "total_oracle": len(rows), "nouveaux": nb, "ts": str(now)})

    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


# ─── SCAN 1 : SORTIE SUPERMARCHÉ ─────────────────────────────────────────────
#   badge START → chariot part vers la ligne  → créer mission
#   badge END   → chariot revient au SMK       → clore mission (= Scan 3)

def traiter_scan_supermarche(c, uid, chariot_id, badge_type, nom, station,
                              operation_code, nb_ofs, type_chariot, scanner_id, now):
    if badge_type == "START":
        return creer_mission(c, uid, chariot_id, nom, station,
                             operation_code, nb_ofs, type_chariot, scanner_id, now)
    else:
        return traiter_scan_retour(c, uid, chariot_id, badge_type, scanner_id, now)


def creer_mission(c, uid, chariot_id, nom, station, operation_code,
                  nb_ofs, type_chariot, scanner_id, now):
    """
    Crée une nouvelle mission quand le chariot quitte le supermarché.

    Logique d'assignation des jobs :
      0 job  RELEASED → mission sans OF  → WS assigne manuellement
      1 job  RELEASED → auto-assigné     → WS confirme juste
      2+ jobs RELEASED → WS choisit dans la liste
    """

    # Déjà une mission active ?
    mission_active = get_mission_active(c, chariot_id)
    if mission_active:
        mission_id, statut = mission_active[0], mission_active[1]
        return {
            "status"     : "avertissement",
            "action"     : "MISSION_DEJA_ACTIVE",
            "mission_id" : mission_id,
            "statut"     : statut,
            "message"    : f"Chariot {chariot_id} a déjà une mission active (statut={statut})",
        }

    # OFs déjà assignés (à exclure)
    deja_assignes = [r[0] for r in c.execute(
        "SELECT of_number FROM jobs_planning WHERE operation_code=? AND statut IN ('ASSIGNE','EN_ATTENTE','EN_COURS')",
        (operation_code,)
    ).fetchall()]

    # ── Chercher jobs Released (local → Oracle → indisponible) ───────────────
    jobs_oracle, source = chercher_jobs_released(c, operation_code, nb_ofs, deja_assignes)
    nb_disponibles = len(jobs_oracle)
    print(f"  → {nb_disponibles} job(s) disponible(s) [source={source}]")

    # Créer la mission
    c.execute(
        """INSERT INTO cart_missions
               (rfid_uid, chariot_id, operation_code, statut, ts_scan1, scanner_scan1, cree_le)
           VALUES (?,?,?,'EN_APPROCHE',?,?,?)""",
        (uid, chariot_id, operation_code, now, scanner_id, now)
    )
    mission_id = int(c.execute("SELECT @@IDENTITY").fetchone()[0])

    jobs_info        = []
    mode_assignation = None

    if nb_disponibles == 0:
        # ── CAS 0 : aucun job dans Oracle → WS assigne manuellement ──────────
        mode_assignation = "MANUEL"
        log_event(c, mission_id, uid, chariot_id, None,
                  operation_code, None, "SCAN_1_SUPERMARCHE", None, scanner_id,
                  {"chariot": nom, "mode": "SANS_JOB"})

    elif nb_disponibles == 1:
        # ── CAS 1 : 1 seul job Oracle → auto-assigné ─────────────────────────
        mode_assignation = "AUTO"
        job = jobs_oracle[0]
        _inserer_job_mission(c, mission_id, job)
        jobs_info.append(job)
        log_event(c, mission_id, uid, chariot_id, job["of_number"],
                  operation_code, None, "SCAN_1_SUPERMARCHE", None, scanner_id,
                  {"chariot": nom, "mode": "AUTO", "of": job["of_number"]})

    else:
        # ── CAS 2+ : plusieurs jobs Oracle → WS choisit ──────────────────────
        mode_assignation = "CHOIX_WS"
        # Mettre en cache les jobs Oracle dans jobs_planning pour que le WS les voie
        for job in jobs_oracle:
            _upsert_job_planning(c, job)
        log_event(c, mission_id, uid, chariot_id, None,
                  operation_code, None, "SCAN_1_SUPERMARCHE", None, scanner_id,
                  {"chariot": nom, "mode": "CHOIX_WS", "nb_jobs": nb_disponibles})

    # ── Message et action selon le mode ──────────────────────────────────────
    actions = {
        "AUTO"    : ("MISSION_AUTO",   f"1 job auto-assigné — WS confirme"),
        "CHOIX_WS": ("MISSION_CHOIX",  f"{nb_disponibles} jobs disponibles — WS choisit"),
        "MANUEL"  : ("MISSION_VIDE",   "Aucun job disponible — WS assigne manuellement"),
    }
    action, message = actions[mode_assignation]

    return {
        "status"          : "ok",
        "action"          : action,
        "mode_assignation": mode_assignation,
        "mission_id"      : mission_id,
        "chariot_id"      : chariot_id,
        "chariot_nom"     : nom,
        "operation_code"  : operation_code,
        "statut"          : "EN_APPROCHE",
        "jobs"            : jobs_info,
        "nb_jobs_dispo"   : nb_disponibles,
        "message"         : message,
    }


# ─── SCAN 2 : ARRIVÉE ZONE D'ATTENTE ─────────────────────────────────────────

def traiter_scan_zone_attente(c, uid, chariot_id, badge_type, scanner_id, now):
    """Chariot détecté à l'entrée de la zone d'attente devant les postes."""
    mission = get_mission_active(c, chariot_id)
    if not mission:
        return {
            "status"  : "erreur",
            "action"  : "PAS_DE_MISSION",
            "message" : f"Aucune mission active pour {chariot_id}",
        }

    mission_id, statut, of_number, item_code, operation_code, poste_id = mission

    if statut not in ("EN_APPROCHE", "EN_ATTENTE"):
        return {
            "status"     : "avertissement",
            "action"     : "STATUT_INATTENDU",
            "mission_id" : mission_id,
            "statut"     : statut,
            "message"    : f"Scan 2 reçu mais statut={statut}",
        }

    c.execute(
        "UPDATE cart_missions SET statut='EN_ATTENTE', ts_scan2=?, scanner_scan2=? WHERE id=?",
        (now, scanner_id, mission_id)
    )

    jobs = c.execute(
        """SELECT cmj.of_number, cmj.item_code, cmj.item_desc, cmj.statut,
                  jp.qty, jp.date_besoin
           FROM cart_mission_jobs cmj
           LEFT JOIN jobs_planning jp ON jp.of_number = cmj.of_number
           WHERE cmj.mission_id = ?
           ORDER BY cmj.id""",
        (mission_id,)
    ).fetchall()

    log_event(c, mission_id, uid, chariot_id, None,
              operation_code, poste_id, "SCAN_2_ZONE_ATTENTE", None, scanner_id)

    return {
        "status"     : "ok",
        "action"     : "EN_ATTENTE",
        "mission_id" : mission_id,
        "chariot_id" : chariot_id,
        "statut"     : "EN_ATTENTE",
        "jobs"       : [{
            "of_number"  : j[0],
            "item_code"  : j[1],
            "item_desc"  : j[2],
            "statut"     : j[3],
            "qty"        : j[4],
            "date_besoin": str(j[5]) if j[5] else None,
        } for j in jobs],
        "message" : "Chariot en zone d'attente — en attente de validation WS",
    }


# ─── SCAN 3 : RETOUR SUPERMARCHÉ ─────────────────────────────────────────────

def traiter_scan_retour(c, uid, chariot_id, badge_type, scanner_id, now):
    """Chariot retourne au SMK (badge END détecté)."""
    mission = c.execute(
        """SELECT id, statut, of_number, operation_code
           FROM cart_missions
           WHERE chariot_id = ? AND actif = 1
             AND statut IN ('VIDE','EN_COURS','EN_ATTENTE','EN_APPROCHE')
           ORDER BY cree_le DESC""",
        (chariot_id,)
    ).fetchone()

    if not mission:
        return {
            "status"  : "avertissement",
            "action"  : "PAS_DE_MISSION_RETOUR",
            "message" : f"Aucune mission à clore pour {chariot_id}",
        }

    mission_id, statut, of_number, operation_code = mission

    c.execute(
        "UPDATE cart_missions SET statut='RETOUR_SUPERMARKET', ts_scan3=? WHERE id=?",
        (now, mission_id)
    )

    log_event(c, mission_id, uid, chariot_id, of_number,
              operation_code, None, "SCAN_3_RETOUR", None, scanner_id)

    return {
        "status"     : "ok",
        "action"     : "RETOUR_SMK",
        "mission_id" : mission_id,
        "chariot_id" : chariot_id,
        "statut"     : "RETOUR_SUPERMARKET",
        "message"    : "Chariot de retour au supermarché",
    }


# ─── API TABLETTES WS ─────────────────────────────────────────────────────────

@app.route("/api/ws/jobs-disponibles", methods=["GET"])
def ws_jobs_disponibles():
    """
    Retourne les jobs RELEASED pour une opération donnée.
    Utilisé par le WS quand il y a plusieurs jobs à choisir.
    Param : ?operation_code=OP10
    """
    operation_code = request.args.get("operation_code")
    if not operation_code:
        return jsonify({"status": "erreur", "message": "operation_code requis"}), 400
    try:
        conn = get_db()
        c    = conn.cursor()
        jobs = c.execute(
            """SELECT of_number, item_code, item_desc, qty, date_besoin
               FROM jobs_planning
               WHERE operation_code=? AND statut='RELEASED'
               ORDER BY date_besoin ASC, of_number ASC""",
            (operation_code,)
        ).fetchall()
        conn.close()
        return jsonify({
            "status"         : "ok",
            "operation_code" : operation_code,
            "jobs"           : [{
                "of_number"  : j[0],
                "item_code"  : j[1],
                "item_desc"  : j[2],
                "qty"        : j[3],
                "date_besoin": str(j[4]) if j[4] else None,
            } for j in jobs],
            "count" : len(jobs),
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/ws/assigner-job", methods=["POST"])
def ws_assigner_job():
    """
    WS assigne manuellement un OF à une mission (cas 0 ou 2+ jobs).
    Body JSON : { mission_id, of_number, ws_id }
    """
    data       = request.json or {}
    mission_id = data.get("mission_id")
    of_number  = data.get("of_number")
    ws_id      = data.get("ws_id")

    if not all([mission_id, of_number]):
        return jsonify({"status": "erreur", "message": "mission_id et of_number requis"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()

        # Vérifier que la mission existe et est EN_APPROCHE
        mission = c.execute(
            "SELECT id, statut, chariot_id, operation_code FROM cart_missions WHERE id=?",
            (mission_id,)
        ).fetchone()

        if not mission or mission[1] != "EN_APPROCHE":
            conn.close()
            return jsonify({
                "status" : "erreur",
                "message": f"Mission non en approche (statut={mission[1] if mission else 'introuvable'})",
            }), 400

        _, _, chariot_id, operation_code = mission

        # Vérifier que le job est bien RELEASED
        job = c.execute(
            "SELECT of_number, item_code, item_desc, qty FROM jobs_planning WHERE of_number=? AND operation_code=? AND statut='RELEASED'",
            (of_number, operation_code)
        ).fetchone()

        if not job:
            conn.close()
            return jsonify({
                "status" : "erreur",
                "message": f"OF {of_number} non disponible (déjà assigné ou introuvable)",
            }), 400

        of_number, item_code, item_desc, qty = job

        # Insérer dans cart_mission_jobs
        c.execute(
            "INSERT INTO cart_mission_jobs (mission_id, of_number, item_code, item_desc, statut) VALUES (?,?,?,?,'EN_ATTENTE')",
            (mission_id, of_number, item_code, item_desc)
        )

        # Marquer le job comme assigné
        c.execute(
            "UPDATE jobs_planning SET statut='ASSIGNE' WHERE of_number=? AND operation_code=? AND statut='RELEASED'",
            (of_number, operation_code)
        )

        log_event(c, mission_id, None, chariot_id, of_number,
                  operation_code, None, "JOB_SELECTIONNE", ws_id, None,
                  {"of_number": of_number, "mode": "WS_MANUEL"})

        conn.commit()
        conn.close()
        return jsonify({
            "status"     : "ok",
            "action"     : "JOB_ASSIGNE",
            "mission_id" : mission_id,
            "of_number"  : of_number,
            "item_code"  : item_code,
            "message"    : f"OF {of_number} assigné au chariot",
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/ws/missions-en-attente", methods=["GET"])
def ws_missions_en_attente():
    """Écran WS : liste les chariots EN_APPROCHE + EN_ATTENTE."""
    try:
        conn = get_db()
        c    = conn.cursor()

        missions = c.execute(
            """SELECT cm.id, cm.chariot_id, ch.nom, cm.statut,
                      cm.operation_code, cm.ts_scan1, cm.ts_scan2,
                      cm.poste_id, cm.emplacement, cm.operateur_id
               FROM cart_missions cm
               JOIN chariots ch ON ch.chariot_id = cm.chariot_id
               WHERE cm.actif = 1
                 AND cm.statut IN ('EN_APPROCHE','EN_ATTENTE')
               ORDER BY cm.ts_scan1 ASC"""
        ).fetchall()

        result = []
        for m in missions:
            mid  = m[0]
            jobs = c.execute(
                "SELECT of_number, item_code, item_desc, statut FROM cart_mission_jobs WHERE mission_id=? ORDER BY id",
                (mid,)
            ).fetchall()
            result.append({
                "mission_id"     : mid,
                "chariot_id"     : m[1],
                "chariot_nom"    : m[2],
                "statut"         : m[3],
                "operation_code" : m[4],
                "ts_scan1"       : str(m[5]) if m[5] else None,
                "ts_scan2"       : str(m[6]) if m[6] else None,
                "poste_id"       : m[7],
                "emplacement"    : m[8],
                "operateur_id"   : m[9],
                "jobs"           : [{"of_number":j[0],"item_code":j[1],"item_desc":j[2],"statut":j[3]} for j in jobs],
            })

        conn.close()
        return jsonify({"status": "ok", "missions": result, "count": len(result)})
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/ws/valider", methods=["POST"])
def ws_valider_mission():
    """
    WS valide la mission : assigne poste + emplacement + opérateur.
    Body JSON : { mission_id, poste_id, emplacement, operateur_id, ws_id }
    """
    data        = request.json or {}
    mission_id  = data.get("mission_id")
    poste_id    = data.get("poste_id")
    emplacement = data.get("emplacement")
    operateur   = data.get("operateur_id")
    ws_id       = data.get("ws_id")

    if not all([mission_id, poste_id]):
        return jsonify({"status": "erreur", "message": "mission_id et poste_id requis"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()
        now  = datetime.now()

        mission = c.execute(
            "SELECT id, statut, chariot_id, operation_code FROM cart_missions WHERE id=?",
            (mission_id,)
        ).fetchone()

        if not mission:
            conn.close()
            return jsonify({"status": "erreur", "message": "Mission introuvable"}), 404

        _, statut, chariot_id, operation_code = mission

        if statut not in ("EN_APPROCHE", "EN_ATTENTE"):
            conn.close()
            return jsonify({
                "status" : "erreur",
                "message": f"Impossible de valider : statut={statut}",
            }), 400

        c.execute(
            """UPDATE cart_missions
               SET poste_id=?, emplacement=?, operateur_id=?, ws_id=?,
                   ts_validation=?, statut='EN_ATTENTE'
               WHERE id=?""",
            (poste_id, emplacement, operateur, ws_id, now, mission_id)
        )

        # jobs_planning → EN_ATTENTE
        c.execute(
            """UPDATE jobs_planning SET statut='EN_ATTENTE'
               WHERE of_number IN (SELECT of_number FROM cart_mission_jobs WHERE mission_id=?)
                 AND statut='ASSIGNE'""",
            (mission_id,)
        )

        log_event(c, mission_id, None, chariot_id, None,
                  operation_code, poste_id, "JOB_VALIDE",
                  operateur or ws_id, None,
                  {"poste_id": poste_id, "emplacement": emplacement, "ws_id": ws_id})

        conn.commit()
        conn.close()
        return jsonify({
            "status"     : "ok",
            "action"     : "VALIDE",
            "mission_id" : mission_id,
            "poste_id"   : poste_id,
            "emplacement": emplacement,
            "message"    : f"Mission assignée au poste {poste_id}",
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


# ─── API OPÉRATEURS ───────────────────────────────────────────────────────────

@app.route("/api/op/mes-chariots", methods=["GET"])
def op_mes_chariots():
    """
    Chariots EN_ATTENTE + EN_COURS pour un poste donné.
    Param : ?poste_id=WS01
    """
    poste_id = request.args.get("poste_id")
    if not poste_id:
        return jsonify({"status": "erreur", "message": "poste_id requis"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()

        missions = c.execute(
            """SELECT cm.id, cm.chariot_id, ch.nom, cm.statut,
                      cm.emplacement, cm.ts_validation, cm.ts_commencer
               FROM cart_missions cm
               JOIN chariots ch ON ch.chariot_id = cm.chariot_id
               WHERE cm.actif = 1
                 AND cm.poste_id = ?
                 AND cm.statut IN ('EN_ATTENTE','EN_COURS')
               ORDER BY cm.emplacement ASC""",
            (poste_id,)
        ).fetchall()

        result = []
        for m in missions:
            mid  = m[0]
            jobs = c.execute(
                "SELECT of_number, item_code, item_desc, statut FROM cart_mission_jobs WHERE mission_id=? ORDER BY id",
                (mid,)
            ).fetchall()
            result.append({
                "mission_id"   : mid,
                "chariot_id"   : m[1],
                "chariot_nom"  : m[2],
                "statut"       : m[3],
                "emplacement"  : m[4],
                "ts_validation": str(m[5]) if m[5] else None,
                "ts_commencer" : str(m[6]) if m[6] else None,
                "jobs"         : [{"of_number":j[0],"item_code":j[1],"item_desc":j[2],"statut":j[3]} for j in jobs],
            })

        conn.close()
        return jsonify({"status": "ok", "chariots": result, "poste_id": poste_id})
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/op/commencer", methods=["POST"])
def op_commencer():
    """
    Opérateur démarre la consommation du chariot.
    Body JSON : { mission_id, operateur_id }
    """
    data       = request.json or {}
    mission_id = data.get("mission_id")
    operateur  = data.get("operateur_id")

    if not mission_id:
        return jsonify({"status": "erreur", "message": "mission_id requis"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()
        now  = datetime.now()

        mission = c.execute(
            "SELECT id, statut, chariot_id, operation_code, poste_id FROM cart_missions WHERE id=?",
            (mission_id,)
        ).fetchone()

        if not mission or mission[1] != "EN_ATTENTE":
            conn.close()
            statut_actuel = mission[1] if mission else "introuvable"
            return jsonify({
                "status" : "erreur",
                "message": f"Mission non en attente (statut={statut_actuel})",
            }), 400

        _, _, chariot_id, operation_code, poste_id = mission

        c.execute(
            "UPDATE cart_missions SET statut='EN_COURS', ts_commencer=? WHERE id=?",
            (now, mission_id)
        )

        # Premier job → EN_COURS
        premier_of = c.execute(
            "SELECT TOP(1) of_number FROM cart_mission_jobs WHERE mission_id=? AND statut='EN_ATTENTE' ORDER BY id",
            (mission_id,)
        ).fetchone()
        if premier_of:
            c.execute(
                "UPDATE cart_mission_jobs SET statut='EN_COURS' WHERE mission_id=? AND of_number=?",
                (mission_id, premier_of[0])
            )
            c.execute(
                "UPDATE jobs_planning SET statut='EN_COURS' WHERE of_number=?",
                (premier_of[0],)
            )

        log_event(c, mission_id, None, chariot_id, premier_of[0] if premier_of else None,
                  operation_code, poste_id, "COMMENCER", operateur, None)

        conn.commit()
        conn.close()
        return jsonify({
            "status"     : "ok",
            "action"     : "EN_COURS",
            "mission_id" : mission_id,
            "message"    : "Production démarrée",
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/op/terminer", methods=["POST"])
def op_terminer():
    """
    Opérateur termine un OF (ou tous les OFs si of_number absent).
    Body JSON : { mission_id, of_number (optionnel), operateur_id }
    """
    data       = request.json or {}
    mission_id = data.get("mission_id")
    of_number  = data.get("of_number")   # optionnel : terminer un OF spécifique
    operateur  = data.get("operateur_id")

    if not mission_id:
        return jsonify({"status": "erreur", "message": "mission_id requis"}), 400

    try:
        conn = get_db()
        c    = conn.cursor()
        now  = datetime.now()

        mission = c.execute(
            "SELECT id, statut, chariot_id, operation_code, poste_id FROM cart_missions WHERE id=?",
            (mission_id,)
        ).fetchone()

        if not mission or mission[1] != "EN_COURS":
            conn.close()
            statut_actuel = mission[1] if mission else "introuvable"
            return jsonify({
                "status" : "erreur",
                "message": f"Mission non en cours (statut={statut_actuel})",
            }), 400

        _, _, chariot_id, operation_code, poste_id = mission

        if of_number:
            # ── Terminer un OF spécifique ──────────────────────────────────
            c.execute(
                "UPDATE cart_mission_jobs SET statut='TERMINE' WHERE mission_id=? AND of_number=?",
                (mission_id, of_number)
            )
            c.execute(
                "UPDATE jobs_planning SET statut='TERMINE' WHERE of_number=?",
                (of_number,)
            )
            # Passer au job suivant
            suivant = c.execute(
                "SELECT TOP(1) of_number FROM cart_mission_jobs WHERE mission_id=? AND statut='EN_ATTENTE' ORDER BY id",
                (mission_id,)
            ).fetchone()
            if suivant:
                c.execute(
                    "UPDATE cart_mission_jobs SET statut='EN_COURS' WHERE mission_id=? AND of_number=?",
                    (mission_id, suivant[0])
                )
                c.execute(
                    "UPDATE jobs_planning SET statut='EN_COURS' WHERE of_number=?",
                    (suivant[0],)
                )

            # Vérifier si tous les jobs sont terminés
            nb_restant = c.execute(
                "SELECT COUNT(*) FROM cart_mission_jobs WHERE mission_id=? AND statut!='TERMINE'",
                (mission_id,)
            ).fetchone()[0]

            if nb_restant == 0:
                c.execute(
                    "UPDATE cart_missions SET statut='VIDE', ts_terminer=? WHERE id=?",
                    (now, mission_id)
                )
                action  = "VIDE"
                message = "Chariot vide — retour au supermarché"
            else:
                action  = "JOB_TERMINE"
                message = f"OF {of_number} terminé — {nb_restant} job(s) restant(s)"
        else:
            # ── Terminer tous les OFs d'un coup ───────────────────────────
            c.execute(
                "UPDATE cart_mission_jobs SET statut='TERMINE' WHERE mission_id=?",
                (mission_id,)
            )
            c.execute(
                """UPDATE jobs_planning SET statut='TERMINE'
                   WHERE of_number IN (SELECT of_number FROM cart_mission_jobs WHERE mission_id=?)""",
                (mission_id,)
            )
            c.execute(
                "UPDATE cart_missions SET statut='VIDE', ts_terminer=? WHERE id=?",
                (now, mission_id)
            )
            action  = "VIDE"
            message = "Chariot vide — retour au supermarché"

        log_event(c, mission_id, None, chariot_id, of_number,
                  operation_code, poste_id, "TERMINER", operateur, None,
                  {"of_number": of_number, "action": action})

        conn.commit()
        conn.close()
        return jsonify({
            "status"     : "ok",
            "action"     : action,
            "mission_id" : mission_id,
            "message"    : message,
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


# ─── API DASHBOARD ────────────────────────────────────────────────────────────

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    """Vue globale de la ligne : tous les chariots actifs + stats."""
    try:
        conn = get_db()
        c    = conn.cursor()

        missions = c.execute(
            """SELECT cm.id, cm.chariot_id, ch.nom, ch.station, cm.statut,
                      cm.operation_code, cm.poste_id, cm.emplacement, cm.operateur_id,
                      cm.ts_scan1, cm.ts_validation, cm.ts_scan2,
                      cm.ts_commencer, cm.ts_terminer, cm.ts_scan3
               FROM cart_missions cm
               JOIN chariots ch ON ch.chariot_id = cm.chariot_id
               WHERE cm.actif = 1
                 AND cm.statut != 'RETOUR_SUPERMARKET'
               ORDER BY cm.statut, cm.ts_scan1 ASC"""
        ).fetchall()

        result = []
        for m in missions:
            mid  = m[0]
            jobs = c.execute(
                "SELECT of_number, item_code, statut FROM cart_mission_jobs WHERE mission_id=?",
                (mid,)
            ).fetchall()
            result.append({
                "mission_id"    : mid,
                "chariot_id"    : m[1],
                "chariot_nom"   : m[2],
                "station"       : m[3],
                "statut"        : m[4],
                "operation_code": m[5],
                "poste_id"      : m[6],
                "emplacement"   : m[7],
                "operateur_id"  : m[8],
                "ts_scan1"      : str(m[9])  if m[9]  else None,
                "ts_validation" : str(m[10]) if m[10] else None,
                "ts_scan2"      : str(m[11]) if m[11] else None,
                "ts_commencer"  : str(m[12]) if m[12] else None,
                "ts_terminer"   : str(m[13]) if m[13] else None,
                "ts_scan3"      : str(m[14]) if m[14] else None,
                "jobs"          : [{"of_number":j[0],"item_code":j[1],"statut":j[2]} for j in jobs],
            })

        stats_rows = c.execute(
            """SELECT statut, COUNT(*) FROM cart_missions
               WHERE actif=1 AND statut!='RETOUR_SUPERMARKET'
               GROUP BY statut"""
        ).fetchall()

        conn.close()
        return jsonify({
            "status"   : "ok",
            "missions" : result,
            "stats"    : {s[0]: s[1] for s in stats_rows},
            "total"    : len(result),
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/historique", methods=["GET"])
def historique():
    """Historique des 50 derniers événements (paramètre ?limit=N)."""
    try:
        conn  = get_db()
        c     = conn.cursor()
        limit = int(request.args.get("limit", 50))
        events = c.execute(
            """SELECT TOP(?) id, mission_id, chariot_id, evenement, ts, fait_par, details
               FROM cart_events ORDER BY ts DESC""",
            (limit,)
        ).fetchall()
        conn.close()
        return jsonify({
            "status": "ok",
            "events": [{
                "id"        : e[0],
                "mission_id": e[1],
                "chariot_id": e[2],
                "evenement" : e[3],
                "ts"        : str(e[4]),
                "fait_par"  : e[5],
                "details"   : e[6],
            } for e in events],
        })
    except Exception as e:
        return jsonify({"status": "erreur", "message": str(e)}), 500


@app.route("/api/test", methods=["GET"])
def test():
    """Health-check : vérifie la connexion SQL Server."""
    try:
        conn = get_db()
        c    = conn.cursor()
        nb   = c.execute("SELECT COUNT(*) FROM chariots").fetchone()[0]
        conn.close()
        return jsonify({
            "status"      : "ok",
            "message"     : "Flask + SQL Server opérationnel",
            "nb_chariots" : nb,
        })
    except Exception as e:
        return jsonify({"status": "erreur", "db_erreur": str(e)}), 500


# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  FLASK RFID PRISTINA — ÉTAPE 2")
    print(f"  Base : {SERVER} / {DB_NAME}")
    print("  ─────────────────────────────────────────")
    print("  Lecteurs RFID (Pepper C1) :")
    print("    POST  /api/scan")
    print("  Tablettes Water Spider :")
    print("    GET   /api/ws/missions-en-attente")
    print("    POST  /api/ws/valider")
    print("  Tablettes Opérateurs :")
    print("    GET   /api/op/mes-chariots?poste_id=WS01")
    print("    POST  /api/op/commencer")
    print("    POST  /api/op/terminer")
    print("  Dashboard & Historique :")
    print("    GET   /api/dashboard")
    print("    GET   /api/historique")
    print("    GET   /api/test")
    print("=" * 55 + "\n")
    # ── Sync Oracle automatique toutes les 30 secondes ───────────────────────
    if SCHEDULER_OK and ORACLE_OK:
        scheduler = BackgroundScheduler()
        scheduler.add_job(sync_oracle_background, 'interval', seconds=30)
        scheduler.start()
        print("  [Sync Oracle] Actif — toutes les 30 secondes")
    else:
        print("  [Sync Oracle] Désactivé (APScheduler ou oracledb manquant)")

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
