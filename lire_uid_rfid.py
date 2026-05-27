"""
Lecture UIDs RFID — Pepper C1 via MQTT
Scanne un badge → affiche l'UID
"""

import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "raspberrypi.local"
PORT   = 1883
TOPIC  = "#"   # ecoute tous les topics pour trouver le bon

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[OK] Connecte au broker MQTT ({BROKER}:{PORT})")
        print(f"[..] En ecoute sur tous les topics...")
        print("-" * 50)
        client.subscribe(TOPIC)
    else:
        print(f"[ERR] Connexion refusee — code {rc}")

def on_message(client, userdata, msg):
    ts    = datetime.now().strftime("%H:%M:%S")
    topic = msg.topic
    data  = msg.payload.decode("utf-8", errors="replace")
    print(f"[{ts}] TOPIC: {topic}")
    print(f"       UID  : {data}")
    print("-" * 50)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connexion a {BROKER}:{PORT} ...")
try:
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[STOP] Arret par l'utilisateur")
except Exception as e:
    print(f"[ERR] {e}")
