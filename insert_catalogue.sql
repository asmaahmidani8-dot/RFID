USE rfid_buc;

CREATE TABLE IF NOT EXISTS pristina_catalogue (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    gamme       VARCHAR(30)  NOT NULL,
    item_code   VARCHAR(30)  NOT NULL,
    item_desc   VARCHAR(150) NOT NULL,
    feeder_num  INT,
    job_type    VARCHAR(10)  NOT NULL,
    actif       TINYINT(1)   DEFAULT 1,
    UNIQUE (gamme, item_code)
);

DELETE FROM pristina_catalogue;

INSERT INTO pristina_catalogue (gamme, item_code, item_desc, feeder_num, job_type) VALUES
-- ── PRISTINA 5920731 ────────────────────────────────────────
('PRISTINA 5920731','5582304-2',    '|CACC| 2D Faceshield',              NULL, 'CACC'),
('PRISTINA 5920731','5920731',      'Senographe Pristina Buc for China', NULL, 'PRINCIPAL'),
('PRISTINA 5920731','5582884',      '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA 5920731','5719068',      '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA 5920731','5599407-2-C3', '|FEEDER 4| Control Station Equipped',4,  'FEEDER'),
('PRISTINA 5920731','5567822',      '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA 5920731','5573306',      '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA 5920731','5582772',      '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA 5920731','5717903-2',    '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA 5920731','5718540',      '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA 5920731','5726638',      '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA 5920731','5726640',      '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA 5938988 ────────────────────────────────────────
('PRISTINA 5938988','5938988',      'Senographe Pristina Athena & Hygeia',NULL,'PRINCIPAL'),
('PRISTINA 5938988','5582884',      '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA 5938988','5719068',      '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA 5938988','5599407-9',    '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA 5938988','5567822',      '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA 5938988','5573306',      '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA 5938988','5582772',      '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA 5938988','5717903-2',    '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA 5938988','5718540',      '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA 5938988','5726638',      '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA 5938988','5726640',      '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371AJ ───────────────────────────────────────
('PRISTINA S30371AJ','S30371AJ',    'Senographe Pristina (Infinity)',     NULL, 'PRINCIPAL'),
('PRISTINA S30371AJ','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371AJ','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371AJ','5599407-3',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371AJ','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371AJ','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371AJ','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371AJ','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371AJ','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371AJ','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371AJ','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371AM ───────────────────────────────────────
('PRISTINA S30371AM','S30371AM',    'Senographe Pristina 2D Infinity',   NULL, 'PRINCIPAL'),
('PRISTINA S30371AM','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371AM','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371AM','5599407-4',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371AM','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371AM','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371AM','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371AM','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371AM','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371AM','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371AM','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371FL ───────────────────────────────────────
('PRISTINA S30371FL','S30371FL',    'Senographe Pristina 8.4',           NULL, 'PRINCIPAL'),
('PRISTINA S30371FL','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371FL','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371FL','5599407-9',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371FL','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371FL','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371FL','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371FL','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371FL','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371FL','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371FL','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371VG ───────────────────────────────────────
('PRISTINA S30371VG','S30371VG',    'Senographe Pristina 8.3 2D',        NULL, 'PRINCIPAL'),
('PRISTINA S30371VG','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371VG','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371VG','5599407-7',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371VG','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371VG','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371VG','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371VG','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371VG','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371VG','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371VG','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371VH ───────────────────────────────────────
('PRISTINA S30371VH','S30371VH',    'Senographe Pristina 8.3 3D',        NULL, 'PRINCIPAL'),
('PRISTINA S30371VH','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371VH','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371VH','5599407-8',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371VH','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371VH','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371VH','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371VH','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371VH','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371VH','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371VH','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371WD ───────────────────────────────────────
('PRISTINA S30371WD','S30371WD',    'Senographe Pristina Via it9',       NULL, 'PRINCIPAL'),
('PRISTINA S30371WD','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371WD','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371WD','5599407-10',  '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371WD','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371WD','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371WD','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371WD','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371WD','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371WD','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30371WD','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30371WH ───────────────────────────────────────
('PRISTINA S30371WH','S30371WH',    'Senographe Pristina Duo',           NULL, 'PRINCIPAL'),
('PRISTINA S30371WH','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30371WH','5985933',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30371WH','5974479',     '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30371WH','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30371WH','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30371WH','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30371WH','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30371WH','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30371WH','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),
('PRISTINA S30371WH','5985944',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),

-- ── PRISTINA S30381AA ───────────────────────────────────────
('PRISTINA S30381AA','S30381AA',    'Senographe Pristina it10 Fixed Control station',NULL,'PRINCIPAL'),
('PRISTINA S30381AA','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30381AA','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30381AA','5599407-11',  '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30381AA','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30381AA','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30381AA','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30381AA','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30381AA','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30381AA','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30381AA','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER'),

-- ── PRISTINA S30381AB ───────────────────────────────────────
('PRISTINA S30381AB','S30381AB',    'Senographe Pristina it10 Ajustable Control Station',NULL,'PRINCIPAL'),
('PRISTINA S30381AB','5582884',     '|FEEDER 3| Tube Tilt Assembly',     3,    'FEEDER'),
('PRISTINA S30381AB','5719068',     '|FEEDER 3| Locking with cables',    3,    'FEEDER'),
('PRISTINA S30381AB','5958835-3',   '|FEEDER 4| Control Station Equipped',4,   'FEEDER'),
('PRISTINA S30381AB','5567822',     '|FEEDER 5| GAS SPRING ASSY',        5,    'FEEDER'),
('PRISTINA S30381AB','5573306',     '|FEEDER 5| CPU EQUIPPED',           5,    'FEEDER'),
('PRISTINA S30381AB','5582772',     '|FEEDER 5| EMC CASED GPS ASSY',     5,    'FEEDER'),
('PRISTINA S30381AB','5717903-2',   '|FEEDER 5| LIFT SCREW ASSY WITH MOTOR',5,'FEEDER'),
('PRISTINA S30381AB','5718540',     '|FEEDER 5| LIFT ENCODER ASSEMBLY',  5,    'FEEDER'),
('PRISTINA S30381AB','5726638',     '|FEEDER 5| Lift Board Assembly',    5,    'FEEDER'),
('PRISTINA S30381AB','5726640',     '|FEEDER 5| Rotation Board Assembly',5,    'FEEDER');

-- Vérification
SELECT job_type, COUNT(*) as total FROM pristina_catalogue GROUP BY job_type;
SELECT gamme, COUNT(*) as nb_items FROM pristina_catalogue GROUP BY gamme ORDER BY gamme;
