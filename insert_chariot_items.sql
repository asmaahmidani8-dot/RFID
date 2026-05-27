-- ============================================================
-- INSERT chariot_items BXD Pristina
-- CH_1_FEEDER2 + CH_2_FEEDER2 + CH_4_POSTE1 → items PRINCIPAL
-- CH_3_FEEDER3 → items FEEDER 3
-- ============================================================

-- ── CH_1_FEEDER2 — PRINCIPAL (partie 1/2) ──────────────────
INSERT INTO chariot_items (chariot_id, ligne_id, item_code, item_desc) VALUES
('CH_1_FEEDER2', 1,  '5920731',   'Senographe Pristina Buc for China only'),
('CH_1_FEEDER2', 2,  '5938988',   'Senographe Pristina Athena & Hygeia - Buc'),
('CH_1_FEEDER2', 3,  'S30371AJ',  'Senographe Pristina (Infinity)'),
('CH_1_FEEDER2', 4,  'S30371AM',  'Senographe Pristina 2D Infinity'),
('CH_1_FEEDER2', 5,  'S30371FL',  'Senographe Pristina 8.4'),
('CH_1_FEEDER2', 6,  'S30371VG',  'Senographe Pristina 8.3 2D'),
('CH_1_FEEDER2', 7,  'S30371VH',  'Senographe Pristina 8.3 3D'),
('CH_1_FEEDER2', 8,  'S30371WD',  'Senographe Pristina Via it9'),
('CH_1_FEEDER2', 9,  'S30371WH',  'Senographe Pristina Duo'),
('CH_1_FEEDER2', 10, 'S30381AA',  'Senographe Pristina it10 Fixed Control station'),
('CH_1_FEEDER2', 11, 'S30381AB',  'Senographe Pristina it10 Ajustable Control Station');

-- ── CH_2_FEEDER2 — PRINCIPAL (partie 2/2) ──────────────────
INSERT INTO chariot_items (chariot_id, ligne_id, item_code, item_desc) VALUES
('CH_2_FEEDER2', 1,  '5920731',   'Senographe Pristina Buc for China only'),
('CH_2_FEEDER2', 2,  '5938988',   'Senographe Pristina Athena & Hygeia - Buc'),
('CH_2_FEEDER2', 3,  'S30371AJ',  'Senographe Pristina (Infinity)'),
('CH_2_FEEDER2', 4,  'S30371AM',  'Senographe Pristina 2D Infinity'),
('CH_2_FEEDER2', 5,  'S30371FL',  'Senographe Pristina 8.4'),
('CH_2_FEEDER2', 6,  'S30371VG',  'Senographe Pristina 8.3 2D'),
('CH_2_FEEDER2', 7,  'S30371VH',  'Senographe Pristina 8.3 3D'),
('CH_2_FEEDER2', 8,  'S30371WD',  'Senographe Pristina Via it9'),
('CH_2_FEEDER2', 9,  'S30371WH',  'Senographe Pristina Duo'),
('CH_2_FEEDER2', 10, 'S30381AA',  'Senographe Pristina it10 Fixed Control station'),
('CH_2_FEEDER2', 11, 'S30381AB',  'Senographe Pristina it10 Ajustable Control Station');

-- ── CH_4_POSTE1 — PRINCIPAL (Poste 1 OP 80) ───────────────
INSERT INTO chariot_items (chariot_id, ligne_id, item_code, item_desc) VALUES
('CH_4_POSTE1', 1,  '5920731',   'Senographe Pristina Buc for China only'),
('CH_4_POSTE1', 2,  '5938988',   'Senographe Pristina Athena & Hygeia - Buc'),
('CH_4_POSTE1', 3,  'S30371AJ',  'Senographe Pristina (Infinity)'),
('CH_4_POSTE1', 4,  'S30371AM',  'Senographe Pristina 2D Infinity'),
('CH_4_POSTE1', 5,  'S30371FL',  'Senographe Pristina 8.4'),
('CH_4_POSTE1', 6,  'S30371VG',  'Senographe Pristina 8.3 2D'),
('CH_4_POSTE1', 7,  'S30371VH',  'Senographe Pristina 8.3 3D'),
('CH_4_POSTE1', 8,  'S30371WD',  'Senographe Pristina Via it9'),
('CH_4_POSTE1', 9,  'S30371WH',  'Senographe Pristina Duo'),
('CH_4_POSTE1', 10, 'S30381AA',  'Senographe Pristina it10 Fixed Control station'),
('CH_4_POSTE1', 11, 'S30381AB',  'Senographe Pristina it10 Ajustable Control Station');

-- ── CH_3_FEEDER3 — FEEDER 3 (2 items par ligne) ───────────
INSERT INTO chariot_items (chariot_id, ligne_id, item_code, item_desc) VALUES
-- PRISTINA 5920731
('CH_3_FEEDER3', 1, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 1, '5719068', 'Locking with cables'),
-- PRISTINA 5938988
('CH_3_FEEDER3', 2, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 2, '5719068', 'Locking with cables'),
-- PRISTINA S30371AJ
('CH_3_FEEDER3', 3, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 3, '5719068', 'Locking with cables'),
-- PRISTINA S30371AM
('CH_3_FEEDER3', 4, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 4, '5719068', 'Locking with cables'),
-- PRISTINA S30371FL
('CH_3_FEEDER3', 5, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 5, '5719068', 'Locking with cables'),
-- PRISTINA S30371VG
('CH_3_FEEDER3', 6, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 6, '5719068', 'Locking with cables'),
-- PRISTINA S30371VH
('CH_3_FEEDER3', 7, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 7, '5719068', 'Locking with cables'),
-- PRISTINA S30371WD
('CH_3_FEEDER3', 8, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 8, '5719068', 'Locking with cables'),
-- PRISTINA S30371WH (item different : 5985933 au lieu de 5719068)
('CH_3_FEEDER3', 9, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 9, '5985933', 'Locking with cables'),
-- PRISTINA S30381AA
('CH_3_FEEDER3', 10, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 10, '5719068', 'Locking with cables'),
-- PRISTINA S30381AB
('CH_3_FEEDER3', 11, '5582884', 'Tube Tilt Assembly'),
('CH_3_FEEDER3', 11, '5719068', 'Locking with cables');
