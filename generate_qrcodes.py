"""
generate_qrcodes.py — Génère les QR codes pour chaque chariot (Windows)
Contenu simple : CHARIOT:<chariot_id>
Les infos (TYPE, OP, FEEDER, PARTIE) viennent du JOIN avec la table chariots
"""
import qrcode
import os

CHARIOTS = [
    ("CH_1_FEEDER2", "Feeder 2 Partie 1/2 OP10"),
    ("CH_2_FEEDER2", "Feeder 2 Partie 2/2 OP10"),
    ("CH_3_FEEDER3", "Feeder 3 OP10"),
    ("CH_4_POSTE1",  "Poste 1 OP80"),
]

OUTPUT_DIR = r"C:\Users\ADMIN\Desktop\rfid\qrcodes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 55)
print("  Génération QR codes — GE Healthcare Buc RFID")
print("=" * 55)

sql_lines = ["USE rfid_buc;"]

for chariot_id, nom in CHARIOTS:
    content = f"CHARIOT:{chariot_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    path = os.path.join(OUTPUT_DIR, f"{chariot_id}.png")
    img.save(path)
    print(f"[OK] {chariot_id:<20} → {content}")

    sql_lines.append(
        f"INSERT INTO qr_codes (chariot_id, qr_content) VALUES ('{chariot_id}', '{content}') "
        f"ON DUPLICATE KEY UPDATE qr_content='{content}';"
    )

sql_path = os.path.join(OUTPUT_DIR, "insert_qrcodes.sql")
with open(sql_path, "w") as f:
    f.write("\n".join(sql_lines))

print(f"\n[OK] PNG → {OUTPUT_DIR}")
print(f"[OK] SQL → {sql_path}")
