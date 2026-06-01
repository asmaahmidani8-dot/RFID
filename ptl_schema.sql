-- ══════════════════════════════════════════════════════════════
-- Pick-to-Light Schema — GE Healthcare Buc
-- ══════════════════════════════════════════════════════════════

-- Étagères (1 ESP32 par étagère)
CREATE TABLE IF NOT EXISTS etageres (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    etagere_id  VARCHAR(20) NOT NULL UNIQUE,   -- ex: ETAGERE_1
    nom         VARCHAR(50),
    ip_esp32    VARCHAR(15),                   -- IP de l'ESP32 (info)
    nb_bacs     INT DEFAULT 8,
    actif       TINYINT DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bacs (emplacements physiques)
CREATE TABLE IF NOT EXISTS bacs (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bac_id      VARCHAR(20) NOT NULL UNIQUE,   -- ex: BAC_E1_3
    etagere_id  VARCHAR(20) NOT NULL,
    position    INT NOT NULL,                  -- 0 à 7 sur l'étagère
    item_code   VARCHAR(30),                   -- pièce stockée
    item_desc   VARCHAR(150),
    stock_min   INT DEFAULT 0,
    actif       TINYINT DEFAULT 1,
    FOREIGN KEY (etagere_id) REFERENCES etageres(etagere_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sessions de picking (liées à une mission)
CREATE TABLE IF NOT EXISTS pick_sessions (
    id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    mission_id  INT UNSIGNED NOT NULL,
    bac_id      VARCHAR(20) NOT NULL,
    item_code   VARCHAR(30),
    quantite    INT DEFAULT 1,
    statut      VARCHAR(20) DEFAULT 'EN_ATTENTE',  -- EN_ATTENTE, CONFIRME
    cree_le     DATETIME DEFAULT CURRENT_TIMESTAMP,
    confirme_le DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Données exemple — étagères
INSERT IGNORE INTO etageres (etagere_id, nom, nb_bacs) VALUES
('ETAGERE_1', 'Étagère Supermarché Zone A', 8),
('ETAGERE_2', 'Étagère Supermarché Zone B', 8);

-- Données exemple — bacs (à adapter selon ton supermarché)
INSERT IGNORE INTO bacs (bac_id, etagere_id, position, item_code, item_desc) VALUES
('BAC_E1_0', 'ETAGERE_1', 0, '5920731',  'Senographe Pristina China'),
('BAC_E1_1', 'ETAGERE_1', 1, '5938988',  'Senographe Pristina Athena'),
('BAC_E1_2', 'ETAGERE_1', 2, 'S30371AJ', 'Senographe Pristina Infinity'),
('BAC_E1_3', 'ETAGERE_1', 3, 'S30371AM', 'Senographe Pristina 2D'),
('BAC_E1_4', 'ETAGERE_1', 4, 'S30371FL', 'Senographe Pristina 8.4'),
('BAC_E1_5', 'ETAGERE_1', 5, 'S30371VG', 'Senographe Pristina 8.3 2D'),
('BAC_E1_6', 'ETAGERE_1', 6, 'S30371VH', 'Senographe Pristina 8.3 3D'),
('BAC_E1_7', 'ETAGERE_1', 7, 'S30371WD', 'Senographe Pristina Via');
