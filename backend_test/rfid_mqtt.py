"""
rfid_mqtt.py — Handler MQTT pour lecteurs RFID Pepper C1
GE Healthcare Buc | Ligne Pristina

Flux :
  Badge scanné → Pepper C1 → MQTT → ce script → MySQL
  → Enregistre l'événement
  → Met à jour la mission selon le TIMING (pas selon le badge) :
      1er scan → EN_ATTENTE + Oracle Move  |  re-scan > 30 min → TERMINEE
  Les 2 badges d'un chariot (gauche / droite) sont équivalents.

Audio :
  Piezo buzzer branché sur GPIO 18 (pin 12) + GND (pin 14) du Raspberry Pi
  Le Pepper C1 n'a PAS de sortie audio/speaker — uniquement LED RGB intégrée
  Passage EN_ATTENTE → 1 bip court (200ms)
  Passage TERMINEE   → 2 bips longs (400ms + 400ms)
"""

import os
import json
import time
import mysql.connector
import paho.mqtt.client as mqtt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Audio — Haut-parleur Mylar via jack 3.5mm Pi ──────────────
# Câblage : Jack Amphenol T(Tip)=rouge  S(Sleeve)=noir
# Générer les fichiers : voir README ou generate_beeps.py
import subprocess

BIP_START = os.path.expanduser("~/bip_start.wav")
BIP_END   = os.path.expanduser("~/bip_end.wav")

def jouer_bip(type_bip="start"):
    """Joue un fichier WAV via aplay (sortie jack 3.5mm Pi)."""
    fichier = BIP_START if type_bip == "start" else BIP_END
    if not os.path.exists(fichier):
        return  # Pas de fichier = silencieux, non bloquant
    try:
        subprocess.Popen(
            ['aplay', '-q', fichier],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass  # Pas de son = pas bloquant

MQTT_HOST        = "localhost"
MQTT_PORT        = 1883
COOLDOWN_S       = 5    # Anti-rebond matériel : 2 scans du même chariot < 5 s = ignoré
MIN_TRIP_MIN     = 7    # Re-scan < 7 min (n'importe quel badge) = doublon → ignoré
END_TRIGGER_MIN  = 30   # Re-scan > 30 min = chariot revenu vide → TERMINEE

# Cache anti-doublon : { uid: timestamp_dernier_scan }
_derniers_scans = {}

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

# ── Traitement d'un scan RFID ─────────────────────────────────
def traiter_scan(scanner_id, uid, timestamp=None):
    maintenant = time.time()
    print(f"\n[RFID] Scanner={scanner_id} | Badge UID={uid}")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # 1. Identifier le badge → chariot
    #    Le type START/END est conservé pour l'historique mais n'a AUCUN
    #    effet sur la logique : les 2 badges d'un chariot sont équivalents.
    cur.execute("""
        SELECT rc.*, c.chariot_id, c.nom, c.type_chariot, c.operation_code
        FROM rfid_cards rc
        JOIN chariots c ON c.chariot_id = rc.chariot_id
        WHERE rc.uid = %s AND rc.actif = 1
    """, (uid,))
    card = cur.fetchone()

    if not card:
        print(f"[RFID] Badge UID={uid} inconnu — ignoré")
        cur.close(); db.close()
        return

    chariot_id   = card["chariot_id"]
    badge_type   = card["badge_type"]   # gardé seulement pour cart_events (historique)
    chariot_nom  = card["nom"]
    print(f"[RFID] Chariot={chariot_id} | Badge={badge_type} | {chariot_nom}")

    # ── Anti-rebond matériel — clé par CHARIOT (pas par badge) ───
    #    Scanner le badge gauche puis le badge droite du même chariot
    #    en quelques secondes = un seul scan logique.
    cle = f"{scanner_id}:{chariot_id}"
    if cle in _derniers_scans:
        elapsed = maintenant - _derniers_scans[cle]
        if elapsed < COOLDOWN_S:
            print(f"[RFID] Chariot={chariot_id} ignoré (doublon {elapsed:.1f}s < {COOLDOWN_S}s)")
            cur.close(); db.close()
            return
    _derniers_scans[cle] = maintenant

    now = datetime.now()

    # 2. Trouver la mission active AVANT d'insérer l'événement
    cur.execute("""
        SELECT id, statut, ts_en_attente FROM cart_missions
        WHERE chariot_id = %s AND actif = 1 AND statut NOT IN ('TERMINEE')
        ORDER BY ts_preparee DESC LIMIT 1
    """, (chariot_id,))

    mission     = cur.fetchone()
    mission_id  = mission["id"] if mission else None

    # 3. Enregistrer le scan badge dans cart_events (avec mission_id)
    cur.execute("""
        INSERT INTO cart_events (mission_id, chariot_id, scanner_id, rfid_uid, evenement, ts)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (mission_id, chariot_id, scanner_id, uid, badge_type, now))

    # 4. Mettre à jour la mission et enregistrer le changement de statut
    if mission_id:
        statut_actuel = mission["statut"]
        nouveau_statut = None

        # ── PREPAREE : 1er scan (peu importe le badge) → EN_ATTENTE ──
        if statut_actuel == "PREPAREE":
            nouveau_statut = "EN_ATTENTE"
            cur.execute("""
                UPDATE cart_missions
                SET statut='EN_ATTENTE', ts_en_attente=%s, msca_status='EN_ATTENTE'
                WHERE id=%s
            """, (now, mission_id))
            print(f"[RFID] Mission #{mission_id} → EN_ATTENTE (Oracle Move à déclencher)")
            jouer_bip("start")
            # TODO: déclencher Oracle Move Transaction ici (dès accès MSCA)

        # ── EN_ATTENTE : logique timing ───────────────────────
        elif statut_actuel == "EN_ATTENTE":
            ts_start    = mission.get("ts_en_attente")
            elapsed_min = 0
            if ts_start:
                elapsed_min = (now - ts_start).total_seconds() / 60

            # ── CONDITION B : chariot marqué VIDE par opérateur ──
            cur.execute("SELECT is_vide FROM chariots WHERE chariot_id=%s", (chariot_id,))
            ch = cur.fetchone()
            is_vide = ch and ch.get("is_vide", 0)

            if is_vide:
                # Chariot confirmé vide par opérateur → TERMINEE immédiat
                nouveau_statut = "TERMINEE"
                cur.execute("""
                    UPDATE cart_missions SET statut='TERMINEE', ts_terminee=%s WHERE id=%s
                """, (now, mission_id))
                cur.execute("UPDATE chariots SET is_vide=0 WHERE chariot_id=%s", (chariot_id,))
                print(f"[RFID] Mission #{mission_id} → TERMINEE (VIDE confirmé par opérateur) ✅")
                jouer_bip("end")

            elif elapsed_min < MIN_TRIP_MIN:
                print(f"[RFID] Scan ignoré — doublon ({elapsed_min:.1f} min < {MIN_TRIP_MIN} min)")
                cur.close(); db.close()
                return

            elif elapsed_min < END_TRIGGER_MIN:
                print(f"[RFID] Scan ignoré — chariot encore au poste ({elapsed_min:.1f} min)")
                cur.close(); db.close()
                return

            else:
                # ── CONDITION A : > 30 min → TERMINEE ────────────
                nouveau_statut = "TERMINEE"
                cur.execute("""
                    UPDATE cart_missions SET statut='TERMINEE', ts_terminee=%s WHERE id=%s
                """, (now, mission_id))
                print(f"[RFID] Mission #{mission_id} → TERMINEE ({elapsed_min:.0f} min) ✅")
                jouer_bip("end")

        # ── VIDE : WS scanne → TERMINEE ──────────────────────
        elif statut_actuel == "VIDE":
            nouveau_statut = "TERMINEE"
            cur.execute("""
                UPDATE cart_missions SET statut='TERMINEE', ts_terminee=%s WHERE id=%s
            """, (now, mission_id))
            cur.execute("UPDATE chariots SET is_vide=0 WHERE chariot_id=%s", (chariot_id,))
            print(f"[RFID] Mission #{mission_id} → TERMINEE (WS a récupéré chariot VIDE) ✅")
            jouer_bip("end")

        # ── TERMINEE : ignorer ────────────────────────────────
        elif statut_actuel == "TERMINEE":
            print(f"[RFID] Mission #{mission_id} déjà terminée → ignoré")
            cur.close(); db.close()
            return

        # Enregistrer le changement de statut comme événement séparé
        if nouveau_statut:
            cur.execute("""
                INSERT INTO cart_events (mission_id, chariot_id, scanner_id, rfid_uid, evenement, ts)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (mission_id, chariot_id, scanner_id, uid, nouveau_statut, now))

    else:
        print(f"[RFID] Aucune mission active pour {chariot_id}")

    db.commit()
    cur.close()
    db.close()

# ── Callback MQTT — message reçu ─────────────────────────────
def on_message(client, userdata, msg):
    try:
        topic   = msg.topic
        payload = json.loads(msg.payload.decode())
        print(f"[MQTT] Topic={topic} | Payload={payload}")

        # Format Pepper C1 : {"uid": "ABCD1234", "rssi": -60, ...}
        uid        = payload.get("uid") or payload.get("epc") or payload.get("tag_id")
        scanner_id = topic.split("/")[-1]  # ex: rfid/scanner/SCANNER_1 → SCANNER_1

        if uid:
            traiter_scan(scanner_id, uid.upper())
        else:
            print(f"[MQTT] Payload sans UID : {payload}")

    except Exception as e:
        print(f"[MQTT] Erreur traitement : {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connecté au broker Mosquitto ✅")
        client.subscribe("rfid/scanner/#")
        print("[MQTT] Abonné à : rfid/scanner/#")
    else:
        print(f"[MQTT] Erreur connexion : code {rc}")

def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Déconnecté (code={rc}) — reconnexion dans 5s...")

# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  RFID MQTT Handler — GE Healthcare Buc")
    print("=" * 50)

    import uuid
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, f"rfid_handler_{uuid.uuid4().hex[:8]}")
    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as e:
            print(f"[MQTT] Connexion échouée : {e} — retry dans 10s")
            time.sleep(10)
