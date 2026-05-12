"""
app.py — Serveur Flask RFID Pristina
ÉTAPE 2 : Machine d'état complète avec SQL Server

Flux :
  SCAN_1 (badge START au passage SMK)
    → mission créée (EN_APPROCHE)
    → WS valide (EN_ATTENTE)
  SCAN_2 (badge au passage Zone d'Attente)
    → statut EN_ATTENTE confirmé
    → Opérateur COMMENCER (EN_COURS)
    → Opérateur TERMINER   (VIDE)
  SCAN_3 (badge END retour vers SMK)
    → RETOUR_SUPERMARKET
"""

from flask import Flask, request, jsonify
from datetime import datetime
import pyodbc
import json

app = Flask(__name__)

# ─── CONNEXION SQL SERVER ──────────────────────────────────────────────────────
SERVER  = r"localhost\SQLEXPRESS"
DB_NAME = "rfid_pristina"

CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)


def get_db():
    """Retourne une connexion SQL Server."""
    return pyodbc.connect(CONN_STR)


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
    """Crée une nouvelle mission : chariot quitte le supermarché."""

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

    # Récupérer les N premiers jobs Released pour cette opération
    jobs = c.execute(
        """SELECT TOP(?) of_number, item_code, item_desc, qty, date_besoin
           FROM jobs_planning
           WHERE operation_code = ? AND statut = 'RELEASED'
           ORDER BY date_besoin ASC, of_number ASC""",
        (nb_ofs, operation_code)
    ).fetchall()

    # Créer la mission
    c.execute(
        """INSERT INTO cart_missions
               (rfid_uid, chariot_id, operation_code, statut, ts_scan1, scanner_scan1, cree_le)
           VALUES (?,?,?,'EN_APPROCHE',?,?,?)""",
        (uid, chariot_id, operation_code, now, scanner_id, now)
    )
    mission_id = int(c.execute("SELECT @@IDENTITY").fetchone()[0])

    # Associer les jobs
    jobs_info = []
    for of_number, item_code, item_desc, qty, date_besoin in jobs:
        c.execute(
            """INSERT INTO cart_mission_jobs (mission_id, of_number, item_code, item_desc, statut)
               VALUES (?,?,?,?,'EN_ATTENTE')""",
            (mission_id, of_number, item_code, item_desc)
        )
        c.execute(
            "UPDATE jobs_planning SET statut='ASSIGNE' WHERE of_number=? AND statut='RELEASED'",
            (of_number,)
        )
        jobs_info.append({
            "of_number" : of_number,
            "item_code" : item_code,
            "item_desc" : item_desc,
            "qty"       : qty,
            "date_besoin": str(date_besoin) if date_besoin else None,
        })

    log_event(c, mission_id, uid, chariot_id,
              jobs[0][0] if jobs else None,
              operation_code, None, "SCAN_1_SUPERMARCHE", None, scanner_id,
              {"chariot": nom, "jobs_assignes": len(jobs_info)})

    return {
        "status"         : "ok",
        "action"         : "MISSION_CREEE",
        "mission_id"     : mission_id,
        "chariot_id"     : chariot_id,
        "chariot_nom"    : nom,
        "operation_code" : operation_code,
        "statut"         : "EN_APPROCHE",
        "jobs"           : jobs_info,
        "message"        : f"Mission créée — {len(jobs_info)} job(s) pré-assigné(s)",
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
    app.run(host="0.0.0.0", port=5000, debug=True)
