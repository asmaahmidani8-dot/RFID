"""
mqtt_handler.py — Gestionnaire MQTT securise (MQTTS)
Remplace les endpoints HTTP POST /api/scan par MQTT

Architecture :
  Pepper C1 → MQTTS (port 8883) → Mosquitto Broker → Flask subscriber

Topics MQTT :
  rfid/scan/supermarche   → chariot sort du SMK
  rfid/scan/zone_attente  → chariot arrive au poste
  rfid/scan/retour        → chariot retourne au SMK
  rfid/statut/#           → statuts en temps réel
  rfid/alerte/#           → alertes usine
"""

import json
import ssl
import os
import paho.mqtt.client as mqtt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ─── CONFIGURATION MQTTS ──────────────────────────────────────────────────────
MQTT_BROKER   = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT     = int(os.getenv("MQTT_PORT", "8883"))       # 8883 = MQTTS securise
MQTT_USER     = os.getenv("MQTT_USER", "rfid_user")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "rfid_password")
MQTT_CA_CERT  = os.getenv("MQTT_CA_CERT", "/etc/mosquitto/certs/ca.crt")

# ─── TOPICS ───────────────────────────────────────────────────────────────────
TOPIC_SCAN_SMK      = "rfid/scan/supermarche"
TOPIC_SCAN_ATTENTE  = "rfid/scan/zone_attente"
TOPIC_SCAN_RETOUR   = "rfid/scan/retour"
TOPIC_TOUS_SCANS    = "rfid/scan/#"
TOPIC_STATUT        = "rfid/statut"
TOPIC_ALERTE        = "rfid/alerte"


# ─── CALLBACK : connexion au broker ───────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    codes = {
        0: "Connecte au broker MQTTS",
        1: "Refus : mauvaise version protocole",
        2: "Refus : client ID invalide",
        3: "Refus : serveur indisponible",
        4: "Refus : mauvais username/password",
        5: "Refus : non autorise",
    }
    print(f"MQTT: {codes.get(rc, f'Code erreur {rc}')}")
    if rc == 0:
        # S'abonner a tous les topics de scan
        client.subscribe(TOPIC_TOUS_SCANS, qos=1)
        print(f"MQTT: Abonne a '{TOPIC_TOUS_SCANS}'")


# ─── CALLBACK : message recu ──────────────────────────────────────────────────
def on_message(client, userdata, message):
    """
    Recoit les scans RFID depuis les Pepper C1
    Meme logique que l ancien endpoint HTTP /api/scan
    """
    try:
        topic   = message.topic
        payload = json.loads(message.payload.decode('utf-8'))
        now     = datetime.now()

        print(f"\nMQTT SCAN recu sur '{topic}' :")
        print(f"  Payload : {payload}")

        uid        = payload.get("uid", "")
        scanner_id = payload.get("scanner_id", "")
        timestamp  = payload.get("timestamp", now.isoformat())

        # Determiner le type de scan selon le topic
        if topic == TOPIC_SCAN_SMK:
            type_scan = "SUPERMARCHE"
        elif topic == TOPIC_SCAN_ATTENTE:
            type_scan = "ZONE_ATTENTE"
        elif topic == TOPIC_SCAN_RETOUR:
            type_scan = "RETOUR"
        else:
            type_scan = "INCONNU"

        # Appeler la meme logique que l ancien HTTP scan
        # (importer depuis app.py)
        from app import traiter_scan_rfid
        resultat = traiter_scan_rfid(uid, scanner_id, type_scan, timestamp)

        # Publier le resultat sur le topic statut
        client.publish(
            f"{TOPIC_STATUT}/{uid}",
            json.dumps(resultat),
            qos=1
        )
        print(f"  Resultat publie sur rfid/statut/{uid}")

    except json.JSONDecodeError:
        print(f"MQTT ERREUR: payload non JSON → {message.payload}")
    except Exception as e:
        print(f"MQTT ERREUR traitement : {e}")
        client.publish(
            TOPIC_ALERTE,
            json.dumps({"erreur": str(e), "topic": message.topic}),
            qos=1
        )


# ─── CALLBACK : deconnexion ───────────────────────────────────────────────────
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"MQTT: Deconnecte de facon inattendue (code {rc}) — reconnexion...")


# ─── CREATION CLIENT MQTTS ────────────────────────────────────────────────────
def creer_client_mqtt():
    """
    Cree et configure le client MQTT avec TLS (MQTTS)
    """
    client = mqtt.Client(
        client_id="rfid-pristina-server",
        protocol=mqtt.MQTTv311
    )

    # Authentification username/password
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # TLS/SSL — chiffrement MQTTS port 8883
    client.tls_set(
        ca_certs   = MQTT_CA_CERT,
        tls_version= ssl.PROTOCOL_TLS
    )
    client.tls_insecure_set(False)  # verifier le certificat

    # Callbacks
    client.on_connect    = on_connect
    client.on_message    = on_message
    client.on_disconnect = on_disconnect

    return client


# ─── LANCEMENT ────────────────────────────────────────────────────────────────
def demarrer_mqtt():
    """
    Demarre le client MQTT en arriere-plan
    Appele depuis app.py au demarrage de Flask
    """
    client = creer_client_mqtt()
    try:
        print(f"\nConnexion MQTTS → {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()  # tourne en arriere-plan (thread)
        print("MQTT: Client demarre en arriere-plan")
        return client
    except Exception as e:
        print(f"MQTT ERREUR connexion : {e}")
        return None


# ─── PUBLIER UN MESSAGE ───────────────────────────────────────────────────────
def publier(client, topic, data, qos=1):
    """
    Publier un message vers les abonnes
    Utilise pour notifier le dashboard, Power BI, etc.
    """
    if client and client.is_connected():
        client.publish(topic, json.dumps(data), qos=qos)
    else:
        print(f"MQTT: impossible de publier sur {topic} — client non connecte")


# ─── TEST DIRECT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import time

    print("Test client MQTTS...")
    client = creer_client_mqtt()

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        client.loop_start()
        time.sleep(2)

        # Publier un scan test
        test_payload = {
            "uid": "046D16D24B7780",
            "scanner_id": "SCAN_PRINCIPAL",
            "timestamp": datetime.now().isoformat()
        }
        client.publish(TOPIC_SCAN_SMK, json.dumps(test_payload), qos=1)
        print(f"Message test publie sur {TOPIC_SCAN_SMK}")

        time.sleep(3)
        client.loop_stop()
        client.disconnect()
        print("Test termine")

    except Exception as e:
        print(f"Erreur : {e}")
