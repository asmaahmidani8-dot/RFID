"""
test_serials.py — Numéros de série dispos d'un composant (GLTEST)
GE Healthcare Buc | Ligne Pristina | RFID

Valide la requête des SN AVANT de coder le backflush série (op 110).
Le worker piochera 1 SN dispo dans cette liste pour le saisir dans MSCA.

Lancer (sur le Pi, réseau usine) :
   cd ~/backend_test
   python3 test_serials.py
"""

import os
import sys
import getpass
import platform
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── Oracle Instant Client ─────────────────────────────────────
try:
    import oracledb
    if platform.system() == "Linux":
        try:
            oracledb.init_oracle_client(lib_dir="/home/ge/instantclient_23_26")
        except Exception as e:
            print(f"[WARN] init_oracle_client : {e}")
    elif platform.system() == "Windows":
        try:
            oracledb.init_oracle_client(
                lib_dir=r"C:\Users\250028087\Downloads\instantclient-basic-windows.x64-23.26.1.0.0\instantclient_23_0"
            )
        except Exception:
            pass
except ImportError:
    print("[ERR] oracledb non installé → pip install oracledb")
    sys.exit(1)

# ── Config Oracle (depuis .env) ───────────────────────────────
ORACLE_HOST    = os.getenv("ORACLE_HOST",    "qahceaexa-scan.ge-healthcare.net")
ORACLE_PORT    = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "ebs_gltest")
ORACLE_USER    = os.getenv("ORACLE_USER",    "SSO250028087")
ORACLE_PASS    = os.getenv("ORACLE_PASSWORD", "")

# Valeurs vues sur l'écran MSCA (op 110, job 29434470)
DEFAULT_COMPOSANT = "5589000-P"
DEFAULT_SOUS_INV  = "RM"
DEFAULT_ORG       = "BXD"

# current_status : 3 = Resident (en stock, dispo)
STATUT = {1: "Défini (pas en stock)", 3: "EN STOCK (dispo)", 4: "Sorti", 5: "Intransit"}


def main():
    print("=" * 70)
    print("  SN DISPOS D'UN COMPOSANT — Oracle GLTEST")
    print("=" * 70)

    composant = input(f"\nComposant [{DEFAULT_COMPOSANT}] : ").strip() or DEFAULT_COMPOSANT
    org       = input(f"Org Code [{DEFAULT_ORG}] : ").strip() or DEFAULT_ORG
    sous_inv  = input(f"Sous-inventaire (% = tous) [{DEFAULT_SOUS_INV}] : ").strip() or DEFAULT_SOUS_INV

    pwd = ORACLE_PASS or getpass.getpass(f"Password Oracle ({ORACLE_USER}) : ")
    dsn = f"{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}"

    # Jointure sur l'ORG (msi.organization_id = msn.current_organization_id)
    # → supprime les doublons (l'item est défini dans plusieurs orgs).
    # Filtre org BXD via mtl_parameters.organization_code.
    sql = """
        SELECT msn.serial_number              AS sn,
               msn.current_subinventory_code  AS sous_inv,
               msn.current_locator_id         AS loc_id,
               msn.current_status             AS statut
        FROM   apps.mtl_serial_numbers msn
        JOIN   apps.mtl_system_items_b msi
               ON msi.inventory_item_id = msn.inventory_item_id
              AND msi.organization_id   = msn.current_organization_id
        JOIN   apps.mtl_parameters mp
               ON mp.organization_id = msn.current_organization_id
        WHERE  msi.segment1 = :comp
          AND  msn.current_status = 3
          AND  msn.current_subinventory_code LIKE :sub
          AND  mp.organization_code = :org
        ORDER BY msn.serial_number
    """

    print(f"\n[..] Connexion {ORACLE_HOST}/{ORACLE_SERVICE} ...")
    conn = oracledb.connect(user=ORACLE_USER, password=pwd, dsn=dsn)
    cur = conn.cursor()
    print("[OK] Connecté\n")

    cur.execute(sql, {"comp": composant, "sub": sous_inv, "org": org})
    rows = cur.fetchall()

    print("=" * 70)
    print(f"  {composant}  |  org {org}  |  sous-inv {sous_inv}  |  {len(rows)} SN dispo(s)")
    print("=" * 70)
    print(f"  {'N° SÉRIE':<24} {'SOUS-INV':<10} {'LOC_ID':<10} STATUT")
    print("  " + "-" * 60)
    for sn, sub, loc_id, statut in rows:
        print(f"  {str(sn):<24} {str(sub):<10} {str(loc_id or ''):<10} {STATUT.get(statut, statut)}")
    print("=" * 70)
    print(f"\n  → {len(rows)} numéro(s) de série disponible(s) en org {org}.")
    print("    (Le worker en piochera 1 par unité à backflusher.)\n")

    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        main()
    except oracledb.Error as e:
        print(f"\n[ERR Oracle] {e}")
    except Exception as e:
        print(f"\n[ERR] {e}")
