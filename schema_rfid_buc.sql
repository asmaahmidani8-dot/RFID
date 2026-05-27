-- ============================================================
-- RFID_BUC — Schema MySQL/MariaDB
-- Raspberry Pi prototype | GE Healthcare Buc
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS system_health;
DROP TABLE IF EXISTS oracle_transaction_logs;
DROP TABLE IF EXISTS oracle_move_queue;
DROP TABLE IF EXISTS cart_events;
DROP TABLE IF EXISTS cart_mission_jobs;
DROP TABLE IF EXISTS cart_missions;
DROP TABLE IF EXISTS mission_groupes;
DROP TABLE IF EXISTS jobs_planning;
DROP TABLE IF EXISTS rfid_cards;
DROP TABLE IF EXISTS rfid_scanners;
DROP TABLE IF EXISTS chariot_items;
DROP TABLE IF EXISTS chariots;
DROP TABLE IF EXISTS lignes;
DROP TABLE IF EXISTS organisations;

SET FOREIGN_KEY_CHECKS = 1;

-- 1. ORGANISATIONS
CREATE TABLE organisations (
    id      TINYINT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    code    VARCHAR(10)         NOT NULL UNIQUE,
    label   VARCHAR(60)         NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO organisations (code, label) VALUES
    ('BXD', 'GE Healthcare Buc — Pristina'),
    ('BXV', 'GE Healthcare Buc — Vasculaire');

-- 2. LIGNES
CREATE TABLE lignes (
    id              SMALLINT UNSIGNED   AUTO_INCREMENT PRIMARY KEY,
    organisation_id TINYINT UNSIGNED    NOT NULL,
    code            VARCHAR(30)         NOT NULL,
    label           VARCHAR(80),
    CONSTRAINT fk_lignes_org FOREIGN KEY (organisation_id)
        REFERENCES organisations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. CHARIOTS
CREATE TABLE chariots (
    chariot_id      VARCHAR(20)         PRIMARY KEY,
    ligne_id        SMALLINT UNSIGNED   NOT NULL,
    type_chariot    CHAR(1)             NOT NULL,
    operation_code  VARCHAR(10)         NOT NULL,
    feeder_num      TINYINT             DEFAULT NULL,
    partie          TINYINT             DEFAULT NULL,
    poste           VARCHAR(20)         DEFAULT NULL,
    actif           TINYINT(1)          DEFAULT 1,
    cree_le         DATETIME            DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chariots_lignes FOREIGN KEY (ligne_id)
        REFERENCES lignes(id),
    CONSTRAINT chk_type_chariot CHECK (type_chariot IN ('A','B','C','D'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. CHARIOT_ITEMS
CREATE TABLE chariot_items (
    id          INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    chariot_id  VARCHAR(20)     NOT NULL,
    item_code   VARCHAR(30)     NOT NULL,
    item_desc   VARCHAR(150),
    CONSTRAINT fk_items_chariot FOREIGN KEY (chariot_id)
        REFERENCES chariots(chariot_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. RFID_CARDS
CREATE TABLE rfid_cards (
    uid         VARCHAR(20)     PRIMARY KEY,
    chariot_id  VARCHAR(20)     NOT NULL,
    badge_type  VARCHAR(5)      NOT NULL,
    actif       TINYINT(1)      DEFAULT 1,
    cree_le     DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cards_chariot FOREIGN KEY (chariot_id)
        REFERENCES chariots(chariot_id),
    CONSTRAINT chk_badge_type CHECK (badge_type IN ('START','END'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. RFID_SCANNERS
CREATE TABLE rfid_scanners (
    scanner_id      VARCHAR(20)     PRIMARY KEY,
    nom             VARCHAR(60),
    localisation    VARCHAR(80),
    ip_address      VARCHAR(15),
    type_scan       VARCHAR(5)      NOT NULL,
    actif           TINYINT(1)      DEFAULT 1,
    cree_le         DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_type_scan CHECK (type_scan IN ('SMK','WS'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. JOBS_PLANNING
CREATE TABLE jobs_planning (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    organisation    VARCHAR(10),
    of_number       VARCHAR(20)     NOT NULL,
    operation_code  VARCHAR(10)     NOT NULL,
    item_code       VARCHAR(30),
    item_desc       VARCHAR(150),
    statut          VARCHAR(20),
    qty_totale      DECIMAL(10,2),
    qty_faite       DECIMAL(10,2)   DEFAULT 0,
    date_besoin     DATE,
    synced_le       DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_jobs UNIQUE (of_number, operation_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. MISSION_GROUPES
CREATE TABLE mission_groupes (
    id      INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    cree_le DATETIME        DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. CART_MISSIONS
CREATE TABLE cart_missions (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    chariot_id      VARCHAR(20)     NOT NULL,
    groupe_id       INT UNSIGNED    DEFAULT NULL,
    statut          VARCHAR(15)     NOT NULL DEFAULT 'PREPAREE',
    ts_preparee     DATETIME        DEFAULT CURRENT_TIMESTAMP,
    ts_en_attente   DATETIME        DEFAULT NULL,
    ts_en_approche  DATETIME        DEFAULT NULL,
    ts_terminee     DATETIME        DEFAULT NULL,
    actif           TINYINT(1)      DEFAULT 1,
    CONSTRAINT fk_missions_chariot FOREIGN KEY (chariot_id)
        REFERENCES chariots(chariot_id),
    CONSTRAINT fk_missions_groupe FOREIGN KEY (groupe_id)
        REFERENCES mission_groupes(id),
    CONSTRAINT chk_mission_statut CHECK (
        statut IN ('PREPAREE','EN_ATTENTE','EN_APPROCHE','TERMINEE')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. CART_MISSION_JOBS
CREATE TABLE cart_mission_jobs (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    mission_id      INT UNSIGNED    NOT NULL,
    of_number       VARCHAR(20)     NOT NULL,
    operation_code  VARCHAR(10)     NOT NULL,
    item_code       VARCHAR(30),
    statut          VARCHAR(15)     DEFAULT 'ASSIGNE',
    cree_le         DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cmj_mission FOREIGN KEY (mission_id)
        REFERENCES cart_missions(id),
    CONSTRAINT fk_cmj_jobs FOREIGN KEY (of_number, operation_code)
        REFERENCES jobs_planning(of_number, operation_code),
    CONSTRAINT chk_cmj_statut CHECK (
        statut IN ('ASSIGNE','MOVE_PENDING','MOVE_DONE','ANNULE')
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. ORACLE_MOVE_QUEUE
CREATE TABLE oracle_move_queue (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    mission_job_id  INT UNSIGNED    NOT NULL,
    of_number       VARCHAR(20)     NOT NULL,
    operation_code  VARCHAR(10)     NOT NULL,
    item_code       VARCHAR(30),
    qty             DECIMAL(10,2),
    exe_flag        CHAR(1)         DEFAULT 'N',
    erreur          TEXT,
    cree_le         DATETIME        DEFAULT CURRENT_TIMESTAMP,
    execute_le      DATETIME        DEFAULT NULL,
    CONSTRAINT fk_queue_job FOREIGN KEY (mission_job_id)
        REFERENCES cart_mission_jobs(id),
    CONSTRAINT chk_exe_flag CHECK (exe_flag IN ('N','P','D','E'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. ORACLE_TRANSACTION_LOGS
CREATE TABLE oracle_transaction_logs (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    queue_id        INT UNSIGNED    NOT NULL,
    status          VARCHAR(10)     NOT NULL,
    retry_count     TINYINT         DEFAULT 0,
    error_message   TEXT,
    executed_at     DATETIME,
    cree_le         DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_queue FOREIGN KEY (queue_id)
        REFERENCES oracle_move_queue(id),
    CONSTRAINT chk_log_status CHECK (status IN ('OK','ERROR','RETRY'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. CART_EVENTS
CREATE TABLE cart_events (
    id          INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    mission_id  INT UNSIGNED    DEFAULT NULL,
    chariot_id  VARCHAR(20)     NOT NULL,
    scanner_id  VARCHAR(20)     NOT NULL,
    evenement   VARCHAR(30)     NOT NULL,
    rfid_uid    VARCHAR(20),
    ts          DATETIME        DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_events_mission FOREIGN KEY (mission_id)
        REFERENCES cart_missions(id),
    CONSTRAINT fk_events_chariot FOREIGN KEY (chariot_id)
        REFERENCES chariots(chariot_id),
    CONSTRAINT fk_events_scanner FOREIGN KEY (scanner_id)
        REFERENCES rfid_scanners(scanner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. SYSTEM_HEALTH
CREATE TABLE system_health (
    id              INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    service_name    VARCHAR(40)     NOT NULL UNIQUE,
    status          VARCHAR(10)     DEFAULT 'UNKNOWN',
    last_seen       DATETIME,
    error_message   TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO system_health (service_name, status) VALUES
    ('rfid_mqtt',     'UNKNOWN'),
    ('flask_app',     'UNKNOWN'),
    ('sync_oracle',   'UNKNOWN'),
    ('oracle_msca',   'UNKNOWN');
