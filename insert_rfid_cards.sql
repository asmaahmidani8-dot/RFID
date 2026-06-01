-- ══════════════════════════════════════════════════════════════
-- INSERT rfid_cards — Badges RFID chariots
-- GE Healthcare Buc | Ligne Pristina
-- ══════════════════════════════════════════════════════════════
-- ⚠️  Vérifier que les chariot_id correspondent bien à ta table chariots

INSERT INTO rfid_cards (uid, chariot_id, badge_type, actif) VALUES

-- ── POSTE 1 ───────────────────────────────────────────────────
('045761D24B7780', 'CH_4_POSTE1', 'START', 1),
('049643D24B7780', 'CH_4_POSTE1', 'END',   1),

-- ── FEEDER 3 ──────────────────────────────────────────────────
('044643D24B7780', 'CH_3_FEEDER3', 'START', 1),
('047772D24B7780', 'CH_3_FEEDER3', 'END',   1),

-- ── FEEDER 2 — Partie 1/2 ────────────────────────────────────
('046D16D24B7780', 'CH_1_FEEDER2', 'START', 1),
('04553BD24B7780', 'CH_1_FEEDER2', 'END',   1),

-- ── FEEDER 2 — Partie 2/2 ────────────────────────────────────
('043234D24B7780', 'CH_2_FEEDER2', 'START', 1),
('04493DD24B7780', 'CH_2_FEEDER2', 'END',   1);
