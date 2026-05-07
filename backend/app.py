"""
Serveur Flask — RFID Pristina
ETAPE 1 : Trouver les UIDs des badges et l'IP du Pepper C1
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "ok", "message": "Flask operationnel"})


@app.route("/api/scan", methods=["POST"])
def recevoir_scan():
    data      = request.json or {}
    now       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uid       = data.get("uid", "").strip().upper()
    ip_source = request.remote_addr

    print(f"\n{'='*45}")
    print(f"  SCAN RECU — {now}")
    print(f"  UID       : {uid}")
    print(f"  IP source : {ip_source}")
    print(f"{'='*45}")

    if not uid:
        return jsonify({"status": "erreur", "message": "UID vide"}), 400

    return jsonify({
        "status"    : "ok",
        "uid"       : uid,
        "ip_source" : ip_source,
        "ts"        : now,
    })


if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("  FLASK — ETAPE 1 : Trouver UIDs + IP")
    print("  Scan tes badges et note les UIDs !")
    print("=" * 45 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
