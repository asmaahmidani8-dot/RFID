"""
Initialisation de la base de donnees SQLite
rfid_pristina.db — RFID Pristina GE Healthcare Buc

Lance ce fichier UNE SEULE FOIS pour creer les tables
et inserer les donnees de depart.

Commande : python backend/init_db.py
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "rfid_pristina.db")


def creer_tables(conn):
    c = conn.cursor()
    print("Creation des tables...")

    # ─── TABLE 1 : chariots ───────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS chariots (
            chariot_id      TEXT    PRIMARY KEY,
            nom             TEXT    NOT NULL,
            station         TEXT    NOT NULL,
            operation_code  TEXT    NOT NULL,
            nb_ofs          INTEGER DEFAULT 1,
            actif           INTEGER DEFAULT 1
        )
    """)
    print("  ✓ chariots")

    # ─── TABLE 2 : rfid_cards ─────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS rfid_cards (
            uid             TEXT    PRIMARY KEY,
            chariot_id      TEXT    NOT NULL,
            actif           INTEGER DEFAULT 1,
            enregistre_le   TEXT    DEFAULT (datetime('now')),
            enregistre_par  TEXT,
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
    """)
    print("  ✓ rfid_cards")

    # ─── TABLE 3 : rfid_scanners ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS rfid_scanners (
            scanner_id      TEXT    PRIMARY KEY,
            type_scan       TEXT    NOT NULL,
            operation_code  TEXT,
            poste_id        TEXT,
            ip_address      TEXT,
            localisation    TEXT,
            actif           INTEGER DEFAULT 1,
            last_seen       TEXT
        )
    """)
    print("  ✓ rfid_scanners")

    # ─── TABLE 4 : jobs_planning ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs_planning (
            of_number       TEXT    PRIMARY KEY,
            item_code       TEXT    NOT NULL,
            item_desc       TEXT    NOT NULL,
            organisation    TEXT    DEFAULT 'BXD',
            ligne           TEXT    DEFAULT 'PRISTINA',
            operation_code  TEXT    NOT NULL,
            statut          TEXT    DEFAULT 'RELEASED',
            qty             INTEGER DEFAULT 1,
            date_besoin     TEXT,
            date_import     TEXT    DEFAULT (datetime('now'))
        )
    """)
    print("  jobs_planning")

    # ─── TABLE 5 : cart_missions ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart_missions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            rfid_uid        TEXT    NOT NULL,
            chariot_id      TEXT    NOT NULL,
            of_number       TEXT,
            item_code       TEXT,
            item_desc       TEXT,
            operation_code  TEXT    NOT NULL,
            poste_id        TEXT,
            emplacement     INTEGER,
            statut          TEXT    DEFAULT 'EN_APPROCHE',
            ts_scan1        TEXT,
            ts_validation   TEXT,
            ts_scan2        TEXT,
            ts_commencer    TEXT,
            ts_terminer     TEXT,
            ts_scan3        TEXT,
            ws_id           TEXT,
            operateur_id    TEXT,
            scanner_scan1   TEXT,
            scanner_scan2   TEXT,
            actif           INTEGER DEFAULT 1,
            cree_le         TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (rfid_uid)   REFERENCES rfid_cards(uid),
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
    """)
    print("  ✓ cart_missions")

    # ─── TABLE 6 : cart_mission_jobs ──────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart_mission_jobs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id  INTEGER NOT NULL,
            of_number   TEXT    NOT NULL,
            item_code   TEXT,
            item_desc   TEXT,
            statut      TEXT    DEFAULT 'EN_ATTENTE',
            FOREIGN KEY (mission_id) REFERENCES cart_missions(id),
            UNIQUE (mission_id, of_number)
        )
    """)
    print("  ✓ cart_mission_jobs")

    # ─── TABLE 7 : cart_events ────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS cart_events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id      INTEGER,
            rfid_uid        TEXT,
            chariot_id      TEXT,
            of_number       TEXT,
            operation_code  TEXT,
            poste_id        TEXT,
            evenement       TEXT    NOT NULL,
            ts              TEXT    DEFAULT (datetime('now')),
            fait_par        TEXT,
            scanner_id      TEXT,
            details         TEXT
        )
    """)
    print("  ✓ cart_events")

    # ─── TABLE 8 : chariot_groupes ────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS chariot_groupes (
            groupe_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            chariot_id  TEXT    NOT NULL,
            nom_groupe  TEXT,
            statut      TEXT    DEFAULT 'EN_ATTENTE',
            cree_le     TEXT    DEFAULT (datetime('now')),
            cree_par    TEXT,
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
    """)
    print("  ✓ chariot_groupes")

    # ─── TABLE 9 : chariot_groupe_ofs ─────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS chariot_groupe_ofs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            groupe_id   INTEGER NOT NULL,
            of_number   TEXT    NOT NULL,
            ordre       INTEGER DEFAULT 1,
            statut      TEXT    DEFAULT 'EN_ATTENTE',
            FOREIGN KEY (groupe_id) REFERENCES chariot_groupes(groupe_id),
            UNIQUE (groupe_id, of_number)
        )
    """)
    print("  ✓ chariot_groupe_ofs")

    conn.commit()
    print("\nToutes les tables creees ✓")


def inserer_donnees_depart(conn):
    c = conn.cursor()
    print("\nInsertion des donnees de depart...")
    conn.execute("PRAGMA foreign_keys = OFF")

    # ─── LECTEURS RFID ────────────────────────────────────────────────────────
    scanners = [
        ("SCAN_SUPERMARCHE", "SUPERMARCHE", None,    None,      "Comptoir sortie supermarche"),
        ("SCAN_ZONE_OP10",   "ZONE_ATTENTE","OP10",  "FEEDER2", "Zone attente Feeder 2"),
        ("SCAN_ZONE_OP20",   "ZONE_ATTENTE","OP20",  "FEEDER1", "Zone attente Feeder 1 OP20"),
        ("SCAN_ZONE_OP25",   "ZONE_ATTENTE","OP25",  "FEEDER1", "Zone attente Feeder 1 OP25"),
        ("SCAN_ZONE_OP70",   "ZONE_ATTENTE","OP70",  "POSTE1",  "Zone attente Poste 1"),
        ("SCAN_ZONE_OP80",   "ZONE_ATTENTE","OP80",  "POSTE1",  "Zone attente Poste 1"),
        ("SCAN_ZONE_OP90",   "ZONE_ATTENTE","OP90",  "POSTE2",  "Zone attente Poste 2"),
        ("SCAN_ZONE_OP100",  "ZONE_ATTENTE","OP100", "POSTE3",  "Zone attente Poste 3"),
        ("SCAN_ZONE_OP130",  "ZONE_ATTENTE","OP130", "POSTE67", "Zone attente Poste 6/7"),
    ]
    try:
        c.executemany("""
            INSERT OR IGNORE INTO rfid_scanners
            (scanner_id, type_scan, operation_code, poste_id, localisation)
            VALUES (?, ?, ?, ?, ?)
        """, scanners)
        conn.commit()
        print(f"  ✓ {len(scanners)} lecteurs RFID")
    except Exception as e:
        print(f"  ERREUR scanners : {e}")

    # ─── CHARIOTS PHYSIQUES ───────────────────────────────────────────────────
    chariots = [
        ("CHR-F2-OP10-1",  "Feeder 2 OP10 #1",   "Feeder 2",  "OP10",  1),
        ("CHR-F2-OP10-2",  "Feeder 2 OP10 #2",   "Feeder 2",  "OP10",  1),
        ("CHR-F2-OP10-3",  "Feeder 2 OP10 #3",   "Feeder 2",  "OP10",  1),
        ("CHR-F1-OP20-1",  "Feeder 1 OP20 #1",   "Feeder 1",  "OP20",  1),
        ("CHR-F1-OP20-2",  "Feeder 1 OP20 #2",   "Feeder 1",  "OP20",  1),
        ("CHR-F1-OP20-3",  "Feeder 1 OP20 #3",   "Feeder 1",  "OP20",  1),
        ("CHR-F1-OP25-1",  "Feeder 1 OP25 #1",   "Feeder 1",  "OP25",  1),
        ("CHR-F1-OP25-2",  "Feeder 1 OP25 #2",   "Feeder 1",  "OP25",  1),
        ("CHR-F1-OP25-3",  "Feeder 1 OP25 #3",   "Feeder 1",  "OP25",  1),
        ("CHR-F3-1",       "Feeder 3 #1",         "Feeder 3",  "OP20",  2),
        ("CHR-F4-1",       "Feeder 4 #1",         "Feeder 4",  "OP25",  1),
        ("CHR-F5-1",       "Feeder 5 #1",         "Feeder 5",  "OP70",  7),
        ("CHR-P1-OP70-1",  "Poste 1 OP70 #1",    "Poste 1",   "OP70",  1),
        ("CHR-P1-OP70-2",  "Poste 1 OP70 #2",    "Poste 1",   "OP70",  1),
        ("CHR-P1-OP70-3",  "Poste 1 OP70 #3",    "Poste 1",   "OP70",  1),
        ("CHR-P1-OP80-1",  "Poste 1 OP80 #1",    "Poste 1",   "OP80",  1),
        ("CHR-P1-OP80-2",  "Poste 1 OP80 #2",    "Poste 1",   "OP80",  1),
        ("CHR-P2-OP90-1",  "Poste 2 OP90 #1",    "Poste 2",   "OP90",  1),
        ("CHR-P2-OP90-2",  "Poste 2 OP90 #2",    "Poste 2",   "OP90",  1),
        ("CHR-P3-OP100-1", "Poste 3 OP100 #1",   "Poste 3",   "OP100", 1),
        ("CHR-P67-OP130-1","Poste6/7 OP130 #1",  "Poste 6/7", "OP130", 1),
        ("CHR-P67-OP130-2","Poste6/7 OP130 #2",  "Poste 6/7", "OP130", 1),
        ("CHR-P67-OP130-3","Poste6/7 OP130 #3",  "Poste 6/7", "OP130", 1),
    ]
    try:
        c.executemany("""
            INSERT OR IGNORE INTO chariots
            (chariot_id, nom, station, operation_code, nb_ofs)
            VALUES (?, ?, ?, ?, ?)
        """, chariots)
        conn.commit()
        nb = c.execute("SELECT COUNT(*) FROM chariots").fetchone()[0]
        print(f"  ✓ {nb} chariots dans la base")
    except Exception as e:
        print(f"  ERREUR chariots : {e}")

    # ─── BADGES RFID (EXEMPLES — remplacer par les vrais UIDs) ───────────────
    badges = [
        ("A3F2C1D4", "CHR-F1-OP20-1"),  # ← remplace par le vrai UID du badge
        ("B7E4A2F1", "CHR-F1-OP20-2"),
        ("C1D9B3E8", "CHR-F1-OP25-1"),
        ("D4A1C7B2", "CHR-P1-OP70-1"),
    ]
    try:
        c.executemany("""
            INSERT OR IGNORE INTO rfid_cards (uid, chariot_id)
            VALUES (?, ?)
        """, badges)
        conn.commit()
        nb = c.execute("SELECT COUNT(*) FROM rfid_cards").fetchone()[0]
        print(f"  ✓ {nb} badges RFID dans la base")
    except Exception as e:
        print(f"  ERREUR badges : {e}")

    # ─── JOBS DE DEMO ─────────────────────────────────────────────────────────
    jobs = [
        ("WO-2026-00141","5440867-2-H","PRISTINA DUETA FULL W/CONTRAST","OP20",1,"2026-05-06"),
        ("WO-2026-00142","5440867-2-H","PRISTINA DUETA FULL W/CONTRAST","OP20",1,"2026-05-07"),
        ("WO-2026-00143","5440867-1-H","PRISTINA DUETA STANDARD",       "OP20",1,"2026-05-08"),
        ("WO-2026-00144","5440860-2-H","PRISTINA ESSENTIAL W/CONTRAST", "OP70",1,"2026-05-06"),
        ("WO-2026-00145","5440867-2-H","PRISTINA DUETA FULL W/CONTRAST","OP90",1,"2026-05-07"),
    ]
    try:
        c.executemany("""
            INSERT OR IGNORE INTO jobs_planning
            (of_number, item_code, item_desc, operation_code, qty, date_besoin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, jobs)
        conn.commit()
        nb = c.execute("SELECT COUNT(*) FROM jobs_planning").fetchone()[0]
        print(f"  ✓ {nb} jobs dans la base")
    except Exception as e:
        print(f"  ERREUR jobs : {e}")

    print("\nDonnees de depart inserees ✓")


def afficher_resume(conn):
    c = conn.cursor()
    print("\n" + "=" * 45)
    print("  RESUME BASE DE DONNEES")
    print("=" * 45)
    tables = [
        "chariots", "rfid_cards", "rfid_scanners",
        "jobs_planning", "cart_missions", "cart_mission_jobs",
        "cart_events", "chariot_groupes", "chariot_groupe_ofs"
    ]
    for t in tables:
        nb = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<25} : {nb} ligne(s)")
    print("=" * 45)


if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("  INIT BASE DE DONNEES RFID PRISTINA")
    print("=" * 45)
    print(f"  Fichier : {DB_PATH}\n")

    conn = sqlite3.connect(DB_PATH)

    creer_tables(conn)
    inserer_donnees_depart(conn)
    afficher_resume(conn)

    conn.close()
    print(f"\nBase de donnees prete !")
    print(f"Lance maintenant : python backend/app.py\n")
