"""
rfid_mqtt.py — Handler MQTT pour lecteurs RFID Pepper C1
GE Healthcare Buc | Ligne Pristina

Flux :
  Badge scanné → Pepper C1 → MQTT → ce script → MySQL
  → Enregistre l'événement
  → Met à jour la mission (START = en cours, END = terminée)

Audio :
  Piezo buzzer branché sur GPIO 18 (pin 12) + GND (pin 14) du Raspberry Pi
  Le Pepper C1 n'a PAS de sortie audio/speaker — uniquement LED RGB intégrée
  START → 1 bip court (200ms)
  END   → 2 bips longs (400ms + 400ms)
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

MQTT_HOST   = "localhost"
MQTT_PORT   = 1883
COOLDOWN_S  = 5   # Ignorer le même badge pendant 5 secondes

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
    # ── Anti-doublon ─────────────────────────────────────────
    maintenant = time.time()
    cle        = f"{scanner_id}:{uid}"
    if cle in _derniers_scans:
        elapsed = maintenant - _derniers_scans[cle]
        if elapsed < COOLDOWN_S:
            print(f"[RFID] UID={uid} ignoré (doublon, {elapsed:.1f}s < {COOLDOWN_S}s)")
            return
    _derniers_scans[cle] = maintenant

    print(f"\n[RFID] Scanner={scanner_id} | Badge UID={uid}")

    db = get_db()
    cur = db.cursor(dictionary=True)

    # 1. Identifier le badge → chariot + type (START/END)
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
    badge_type   = card["badge_type"]   # START ou END
    chariot_nom  = card["nom"]
    print(f"[RFID] Chariot={chariot_id} | Type badge={badge_type} | {chariot_nom}")

    now = datetime.now()

    # 2. Trouver la mission active AVANT d'insérer l'événement
    cur.execute("""
        SELECT id FROM cart_missions
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
        if badge_type == "START":
            nouveau_statut = "EN_ATTENTE"
            cur.execute("""
                UPDATE cart_missions
                SET statut = 'EN_ATTENTE', ts_en_attente = %s
                WHERE id = %s
            """, (now, mission_id))
            print(f"[RFID] Mission #{mission_id} → EN_ATTENTE ✅")
            jouer_bip("start")

        elif badge_type == "END":
            nouveau_statut = "TERMINEE"
            cur.execute("""
                UPDATE cart_missions
                SET statut = 'TERMINEE', ts_terminee = %s
                WHERE id = %s
            """, (now, mission_id))
            print(f"[RFID] Mission #{mission_id} → TERMINÉE ✅")
            jouer_bip("end")
            # TODO: déclencher Oracle Move Transaction ici

        else:
            nouveau_statut = None

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

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "rfid_handler_pi")
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
