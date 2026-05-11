"""
setup_sqlserver.py — Création automatique de la base rfid_pristina
sur SQL Server local (localhost\SQLEXPRESS, Windows Authentication)

"""

import sys

try:
    import pyodbc
except ImportError:
    print("ERREUR : pyodbc non installé")
    print("  Lance : pip install pyodbc")
    sys.exit(1)

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
SERVER  = r"localhost\SQLEXPRESS"
DB_NAME = "rfid_pristina"

CONN_MASTER = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE=master;"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)
CONN_RFID = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DB_NAME};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)


# ─── UTILITAIRE : ajouter une colonne si elle n'existe pas ───────────────────

def ajouter_colonne(c, table, colonne, definition):
    """Ajoute une colonne à une table si elle n'existe pas déjà."""
    c.execute(f"""
        IF NOT EXISTS (
            SELECT * FROM sys.columns
            WHERE name = '{colonne}'
            AND object_id = OBJECT_ID('{table}')
        )
        ALTER TABLE {table} ADD {colonne} {definition}
    """)


# ─── ÉTAPE 1 : créer la base ─────────────────────────────────────────────────

def creer_base(conn_master):
    conn_master.autocommit = True
    c = conn_master.cursor()
    existe = c.execute(
        "SELECT COUNT(*) FROM sys.databases WHERE name = ?", (DB_NAME,)
    ).fetchone()[0]
    if existe:
        print(f"  ✓ Base '{DB_NAME}' déjà existante")
    else:
        c.execute(f"CREATE DATABASE [{DB_NAME}]")
        print(f"  ✓ Base '{DB_NAME}' créée")
    conn_master.autocommit = False


# ─── ÉTAPE 2 : créer les tables ──────────────────────────────────────────────

def creer_tables(conn):
    c = conn.cursor()
    print("\nCréation des tables...")

    tables = [

        # ── TABLE 1 : chariots ──────────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='chariots')
        CREATE TABLE chariots (
            chariot_id      VARCHAR(20)  NOT NULL PRIMARY KEY,
            nom             VARCHAR(50)  NOT NULL,
            station         VARCHAR(20)  NOT NULL,
            operation_code  VARCHAR(10)  NOT NULL,
            nb_ofs          INT          DEFAULT 1,
            type_chariot    VARCHAR(10)  DEFAULT 'RM'
                            CHECK (type_chariot IN ('RM','RIP')),
            actif           BIT          DEFAULT 1
        )
        """, "chariots"),

        # ── TABLE 2 : rfid_cards ────────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='rfid_cards')
        CREATE TABLE rfid_cards (
            uid             VARCHAR(30)  NOT NULL PRIMARY KEY,
            chariot_id      VARCHAR(20)  NOT NULL,
            badge_type      VARCHAR(5)   NOT NULL DEFAULT 'START'
                            CHECK (badge_type IN ('START','END')),
            actif           BIT          DEFAULT 1,
            enregistre_le   DATETIME     DEFAULT GETDATE(),
            enregistre_par  VARCHAR(30),
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
        """, "rfid_cards"),

        # ── TABLE 3 : rfid_scanners ─────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='rfid_scanners')
        CREATE TABLE rfid_scanners (
            scanner_id      VARCHAR(30)  NOT NULL PRIMARY KEY,
            type_scan       VARCHAR(20)  NOT NULL
                            CHECK (type_scan IN ('SUPERMARCHE','ZONE_ATTENTE','RETOUR')),
            poste_id        VARCHAR(10),
            ip_address      VARCHAR(15),
            localisation    VARCHAR(50),
            actif           BIT          DEFAULT 1,
            last_seen       DATETIME
        )
        """, "rfid_scanners"),

        # ── TABLE 4 : jobs_planning ─────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='jobs_planning')
        CREATE TABLE jobs_planning (
            of_number       VARCHAR(30)  NOT NULL PRIMARY KEY,
            item_code       VARCHAR(30)  NOT NULL,
            item_desc       VARCHAR(150) NOT NULL,
            organisation    VARCHAR(10)  DEFAULT 'BXD',
            ligne           VARCHAR(20)  DEFAULT 'PRISTINA',
            operation_code  VARCHAR(10)  NOT NULL,
            statut          VARCHAR(20)  DEFAULT 'RELEASED'
                            CHECK (statut IN (
                                'RELEASED','ASSIGNE','EN_APPROCHE',
                                'EN_ATTENTE','EN_COURS','TERMINE','ANNULE'
                            )),
            qty             INT          DEFAULT 1,
            date_besoin     DATE,
            date_import     DATETIME     DEFAULT GETDATE()
        )
        """, "jobs_planning"),

        # ── TABLE 5 : cart_missions ─────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='cart_missions')
        CREATE TABLE cart_missions (
            id              INT          NOT NULL IDENTITY(1,1) PRIMARY KEY,
            rfid_uid        VARCHAR(30)  NOT NULL,
            chariot_id      VARCHAR(20)  NOT NULL,
            of_number       VARCHAR(30),
            item_code       VARCHAR(30),
            item_desc       VARCHAR(150),
            operation_code  VARCHAR(10)  NOT NULL,
            poste_id        VARCHAR(10),
            emplacement     INT,
            statut          VARCHAR(25)  NOT NULL DEFAULT 'EN_APPROCHE'
                            CHECK (statut IN (
                                'EN_APPROCHE','EN_ATTENTE','EN_COURS',
                                'VIDE','RETOUR_SUPERMARKET'
                            )),
            ts_scan1        DATETIME,
            ts_validation   DATETIME,
            ts_scan2        DATETIME,
            ts_commencer    DATETIME,
            ts_terminer     DATETIME,
            ts_scan3        DATETIME,
            ws_id           VARCHAR(20),
            operateur_id    VARCHAR(20),
            scanner_scan1   VARCHAR(30),
            scanner_scan2   VARCHAR(30),
            actif           BIT          DEFAULT 1,
            cree_le         DATETIME     DEFAULT GETDATE(),
            FOREIGN KEY (rfid_uid)   REFERENCES rfid_cards(uid),
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
        """, "cart_missions"),

        # ── TABLE 6 : cart_mission_jobs ─────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='cart_mission_jobs')
        CREATE TABLE cart_mission_jobs (
            id          INT         NOT NULL IDENTITY(1,1) PRIMARY KEY,
            mission_id  INT         NOT NULL,
            of_number   VARCHAR(30) NOT NULL,
            item_code   VARCHAR(30),
            item_desc   VARCHAR(150),
            statut      VARCHAR(15) DEFAULT 'EN_ATTENTE'
                        CHECK (statut IN ('EN_ATTENTE','EN_COURS','TERMINE')),
            FOREIGN KEY (mission_id) REFERENCES cart_missions(id),
            UNIQUE (mission_id, of_number)
        )
        """, "cart_mission_jobs"),

        # ── TABLE 7 : cart_events ───────────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='cart_events')
        CREATE TABLE cart_events (
            id              INT         NOT NULL IDENTITY(1,1) PRIMARY KEY,
            mission_id      INT,
            rfid_uid        VARCHAR(30),
            chariot_id      VARCHAR(20),
            of_number       VARCHAR(30),
            operation_code  VARCHAR(10),
            poste_id        VARCHAR(10),
            evenement       VARCHAR(25) NOT NULL
                            CHECK (evenement IN (
                                'SCAN_1_SUPERMARCHE','JOB_SELECTIONNE','JOB_VALIDE',
                                'SCAN_2_ZONE_ATTENTE','COMMENCER','TERMINER',
                                'SCAN_3_RETOUR','ERREUR_SCAN','ANNULATION'
                            )),
            ts              DATETIME    DEFAULT GETDATE(),
            fait_par        VARCHAR(20),
            scanner_id      VARCHAR(30),
            details         NVARCHAR(MAX)
        )
        """, "cart_events"),

        # ── TABLE 8 : chariot_groupes ───────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='chariot_groupes')
        CREATE TABLE chariot_groupes (
            groupe_id   INT         NOT NULL IDENTITY(1,1) PRIMARY KEY,
            chariot_id  VARCHAR(20) NOT NULL,
            nom_groupe  VARCHAR(50),
            statut      VARCHAR(15) DEFAULT 'EN_ATTENTE',
            cree_le     DATETIME    DEFAULT GETDATE(),
            cree_par    VARCHAR(30),
            FOREIGN KEY (chariot_id) REFERENCES chariots(chariot_id)
        )
        """, "chariot_groupes"),

        # ── TABLE 9 : chariot_groupe_ofs ────────────────────────────────────
        ("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='chariot_groupe_ofs')
        CREATE TABLE chariot_groupe_ofs (
            id          INT         NOT NULL IDENTITY(1,1) PRIMARY KEY,
            groupe_id   INT         NOT NULL,
            of_number   VARCHAR(30) NOT NULL,
            ordre       INT         DEFAULT 1,
            statut      VARCHAR(15) DEFAULT 'EN_ATTENTE',
            FOREIGN KEY (groupe_id) REFERENCES chariot_groupes(groupe_id),
            UNIQUE (groupe_id, of_number)
        )
        """, "chariot_groupe_ofs"),
    ]

    for sql, nom in tables:
        try:
            c.execute(sql)
            print(f"  ✓ {nom}")
        except Exception as e:
            print(f"  ERREUR {nom} : {e}")

    conn.commit()
    print("Tables créées ✓")


# ─── ÉTAPE 3 : mettre à jour les tables (ajouter nouvelles colonnes) ─────────

def mettre_a_jour_tables(conn):
    """
    Ajoute les nouvelles colonnes si elles n'existent pas.
    Ne supprime jamais de données.
    → Ajoute ici tes nouvelles colonnes quand tu modifies le schéma.
    """
    c = conn.cursor()
    print("\nMise à jour des tables...")

    mises_a_jour = [
        # Format : (table, colonne, définition SQL)
        ("chariots",    "type_chariot", "VARCHAR(10) DEFAULT 'RM' CHECK (type_chariot IN ('RM','RIP'))"),
        ("rfid_cards",  "badge_type",   "VARCHAR(5) NOT NULL DEFAULT 'START' CHECK (badge_type IN ('START','END'))"),
    ]

    if not mises_a_jour:
        print("  ✓ Aucune mise à jour nécessaire")
        return

    for table, colonne, definition in mises_a_jour:
        try:
            ajouter_colonne(c, table, colonne, definition)
            print(f"  ✓ {table}.{colonne} ajoutée")
        except Exception as e:
            print(f"  ERREUR {table}.{colonne} : {e}")

    conn.commit()
    print("Mise à jour terminée ✓")


# ─── ÉTAPE 4 : insérer les données réelles ───────────────────────────────────

def inserer_donnees(conn):
    c = conn.cursor()
    print("\nInsertion des données...")

    # ── CHARIOTS ──────────────────────────────────────────────────────────────
    chariots = [
        ("CHR-F1-OP20-1", "Feeder 1 OP20 #1", "Feeder 1", "OP20", 1, "RM"),
        ("CHR-F2-OP10-1", "Feeder 2 OP10 #1", "Feeder 2", "OP10", 1, "RM"),
        ("CHR-F2-OP10-2", "Feeder 2 OP10 #2", "Feeder 2", "OP10", 1, "RM"),
        ("CHR-F5-1",      "Feeder 5 #1",       "Feeder 5", "OP10", 7, "RM"),
    ]
    for row in chariots:
        try:
            c.execute("""
                IF NOT EXISTS (SELECT 1 FROM chariots WHERE chariot_id=?)
                INSERT INTO chariots (chariot_id,nom,station,operation_code,nb_ofs,type_chariot)
                VALUES (?,?,?,?,?,?)
            """, (row[0], *row))
            print(f"  ✓ chariot {row[0]}")
        except Exception as e:
            print(f"  ERREUR chariot {row[0]} : {e}")

    # ── SCANNER ───────────────────────────────────────────────────────────────
    try:
        c.execute("""
            IF NOT EXISTS (SELECT 1 FROM rfid_scanners WHERE scanner_id='SCAN_PRINCIPAL')
            INSERT INTO rfid_scanners (scanner_id, type_scan, ip_address, localisation)
            VALUES ('SCAN_PRINCIPAL','SUPERMARCHE','172.20.10.5','Passage principal SMK vers ligne')
        """)
        print("  ✓ scanner SCAN_PRINCIPAL")
    except Exception as e:
        print(f"  ERREUR scanner : {e}")

    # ── BADGES RFID (4 START + 4 END) ─────────────────────────────────────────
    # START = badge avant du chariot (vers ligne)
    # END   = badge arrière du chariot (vers SMK)
    badges = [
        # (uid,              chariot_id,       badge_type)
        ("046D16D24B7780", "CHR-F1-OP20-1", "START"),
        ("04493DD24B7780", "CHR-F1-OP20-1", "END"),
        ("043234D24B7780", "CHR-F2-OP10-1", "START"),
        ("047772D24B7780", "CHR-F2-OP10-1", "END"),
        ("044643D24B7780", "CHR-F2-OP10-2", "START"),
        ("049643D24B7780", "CHR-F2-OP10-2", "END"),
        ("045761D24B7780", "CHR-F5-1",      "START"),
        ("04553BD24B7780", "CHR-F5-1",      "END"),
    ]
    for uid, chariot_id, badge_type in badges:
        try:
            c.execute("""
                IF NOT EXISTS (SELECT 1 FROM rfid_cards WHERE uid=?)
                INSERT INTO rfid_cards (uid, chariot_id, badge_type)
                VALUES (?,?,?)
            """, (uid, uid, chariot_id, badge_type))
            print(f"  ✓ badge {badge_type} {uid} → {chariot_id}")
        except Exception as e:
            print(f"  ERREUR badge {uid} : {e}")

    conn.commit()
    print("Données insérées ✓")


# ─── RÉSUMÉ ───────────────────────────────────────────────────────────────────

def afficher_resume(conn):
    c = conn.cursor()
    print("\n" + "=" * 45)
    print("  RÉSUMÉ BASE DE DONNÉES")
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


# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 45)
    print("  SETUP SQL SERVER — rfid_pristina")
    print(f"  Serveur : {SERVER}")
    print("=" * 45 + "\n")

    print("Connexion à master...")
    try:
        conn_master = pyodbc.connect(CONN_MASTER)
        print("  ✓ Connecté à master")
    except Exception as e:
        print(f"  ERREUR connexion : {e}")
        print("\n  1. SQL Server Express démarré ?")
        print("     → Services Windows → 'SQL Server (SQLEXPRESS)'")
        print("  2. ODBC Driver 17 installé ?")
        print("     → https://aka.ms/odbc17")
        sys.exit(1)

    creer_base(conn_master)
    conn_master.close()

    print(f"\nConnexion à {DB_NAME}...")
    try:
        conn = pyodbc.connect(CONN_RFID)
        print(f"  ✓ Connecté à {DB_NAME}")
    except Exception as e:
        print(f"  ERREUR : {e}")
        sys.exit(1)

    creer_tables(conn)
    mettre_a_jour_tables(conn)
    inserer_donnees(conn)
    afficher_resume(conn)

    conn.close()
    print(f"\nBase '{DB_NAME}' prête !")
    print("Lance maintenant : python backend/app.py\n")
