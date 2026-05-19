# rfid_mqtt.py — Ecoute les scans du Pepper C1 et traite les tags
# Lancer avec : python rfid_mqtt.py

import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import config

# ══════════════════════════════════════════════════════════
# BASE DE DONNEES SQLITE (simple, pas besoin de MySQL pour prototype)
# ══════════════════════════════════════════════════════════

def init_db():
    """Cree la base de donnees si elle n existe pas"""
    conn = sqlite3.connect("rfid_buc.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS chariots (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            chariot      TEXT NOT NULL,
            statut       TEXT NOT NULL,
            tag_id       TEXT,
            timestamp    TEXT,
            work_order   TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_id       TEXT,
            chariot      TEXT,
            type_tag     TEXT,
            timestamp    TEXT,
            action       TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Base de donnees initialisee")

def update_statut(chariot, statut, tag_id):
    """Met a jour le statut d un chariot"""
    conn = sqlite3.connect("rfid_buc.db")
    c = conn.cursor()
    # Verifie si le chariot existe deja
    c.execute("SELECT id FROM chariots WHERE chariot = ?", (chariot,))
    row = c.fetchone()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row:
        c.execute("""
            UPDATE chariots
            SET statut = ?, tag_id = ?, timestamp = ?
            WHERE chariot = ?
        """, (statut, tag_id, now, chariot))
    else:
        c.execute("""
            INSERT INTO chariots (chariot, statut, tag_id, timestamp)
            VALUES (?, ?, ?, ?)
        """, (chariot, statut, tag_id, now))
    conn.commit()
    conn.close()
    print(f"[DB] {chariot} -> statut : {statut}")

def save_scan(tag_id, chariot, type_tag, action):
    """Enregistre chaque scan dans l historique"""
    conn = sqlite3.connect("rfid_buc.db")
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO scans (tag_id, chariot, type_tag, timestamp, action)
        VALUES (?, ?, ?, ?, ?)
    """, (tag_id, chariot, type_tag, now, action))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
# ORACLE — MOVE TRANSACTION
# ══════════════════════════════════════════════════════════

def trigger_oracle_move(chariot):
    """
    Declenche une Move Transaction dans Oracle GLPROD
    Cette fonction sera implementee quand Oracle est accessible
    """
    print(f"[ORACLE] Move transaction pour {chariot}")
    print(f"[ORACLE] -> WIP_DISCRETE_JOBS mis a jour")
    # TODO : decommenter quand Oracle est connecte
    #
    # import cx_Oracle
    # conn = cx_Oracle.connect(
    #     config.ORACLE_USER,
    #     config.ORACLE_PASS,
    #     f"{config.ORACLE_HOST}:{config.ORACLE_PORT}/{config.ORACLE_SID}"
    # )
    # cursor = conn.cursor()
    # cursor.execute("""
    #     INSERT INTO WIP_MOVE_TRANSACTIONS (...)
    #     VALUES (...)
    # """)
    # conn.commit()
    # conn.close()


# ══════════════════════════════════════════════════════════
# LOGIQUE PRINCIPALE — que faire quand un tag est scanne ?
# ══════════════════════════════════════════════════════════

def traiter_tag(tag_id):
    """Traite un scan RFID recu du Pepper C1"""

    # Tag inconnu ?
    if tag_id not in config.TAGS:
        print(f"[WARN] Tag inconnu : {tag_id}")
        return

    tag_info = config.TAGS[tag_id]
    chariot  = tag_info["chariot"]
    type_tag = tag_info["type"]

    print(f"\n{'='*50}")
    print(f"[SCAN] Tag : {tag_id}")
    print(f"       Chariot : {chariot}")
    print(f"       Type : {type_tag}")
    print(f"       Heure : {datetime.now().strftime('%H:%M:%S')}")

    # ── TAG START — chariot quitte le supermarche ──────────
    if type_tag == "START":
        print(f"[ACTION] {chariot} quitte le SMK -> Zone Attente")
        update_statut(chariot, "EN_TRANSIT", tag_id)
        trigger_oracle_move(chariot)
        save_scan(tag_id, chariot, "START", "QUITTE_SMK -> Oracle Move")
        print(f"[OK] Oracle Move transaction declenchee automatiquement !")

    # ── TAG END — chariot vide, retour SMK ────────────────
    elif type_tag == "END":
        print(f"[ACTION] {chariot} vide -> Retour SMK")
        update_statut(chariot, "VIDE_RETOUR_SMK", tag_id)
        save_scan(tag_id, chariot, "END", "CHARIOT_VIDE -> Retour SMK")
        print(f"[OK] Chariot marque comme vide !")

    print(f"{'='*50}\n")


# ══════════════════════════════════════════════════════════
# MQTT — CONNEXION ET RECEPTION DES MESSAGES PEPPER C1
# ══════════════════════════════════════════════════════════

def on_connect(client, userdata, flags, rc):
    """Appele quand connexion MQTT etablie"""
    if rc == 0:
        print(f"[MQTT] Connecte au broker {config.MQTT_BROKER}:{config.MQTT_PORT}")
        client.subscribe(config.MQTT_TOPIC)
        print(f"[MQTT] En ecoute sur topic : {config.MQTT_TOPIC}")
        print("[MQTT] En attente de scans Pepper C1...\n")
    else:
        print(f"[MQTT] ERREUR connexion, code : {rc}")

def on_message(client, userdata, msg):
    """
    Appele automatiquement a chaque scan Pepper C1
    Le Pepper C1 publie le tag UID quand il detecte un tag
    """
    try:
        payload = msg.payload.decode("utf-8").strip()
        print(f"[MQTT] Message recu sur {msg.topic} : {payload}")

        # Format JSON ? (Pepper C1 firmware recent)
        try:
            data = json.loads(payload)
            # Essayer plusieurs cles possibles selon firmware
            tag_id = (data.get("uid") or
                     data.get("UID") or
                     data.get("tag_id") or
                     data.get("epc") or
                     str(data))
        except json.JSONDecodeError:
            # Format texte simple : juste l UID brut
            tag_id = payload

        tag_id = tag_id.upper().replace(" ", "").replace(":", "")
        traiter_tag(tag_id)

    except Exception as e:
        print(f"[ERROR] Probleme traitement message : {e}")

def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Deconnecte (code {rc}) — reconnexion automatique...")


# ══════════════════════════════════════════════════════════
# LANCEMENT
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  RFID Gate — Pepper C1 MQTT Listener")
    print("  GE HealthCare Buc — Pristina Line")
    print("=" * 50)

    # Initialiser la base de donnees
    init_db()

    # Creer le client MQTT
    client = mqtt.Client(client_id=config.MQTT_CLIENT)
    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    # Connexion au broker
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"[ERROR] Impossible de se connecter au broker MQTT : {e}")
        print(f"        Verifie que Mosquitto tourne sur {config.MQTT_BROKER}")
        exit(1)

    # Boucle infinie — ecoute en permanence
    print("\n[START] Systeme demarre. CTRL+C pour arreter.\n")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Arret du systeme RFID")
        client.disconnect()
