/**
 * RFID GE Healthcare Buc — Présentation IT
 * Génère RFID_IT_Presentation.pptx via PptxGenJS
 */
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";
pres.author  = "GE Healthcare Buc — RFID Project";
pres.title   = "Projet RFID — Suivi Chariots & Automatisation Oracle";

// ── Palette ──────────────────────────────────────────────────
const NAVY   = "003087";   // GE HealthCare primary blue
const TEAL   = "00857C";   // GE HealthCare teal
const WHITE  = "FFFFFF";
const LGRAY  = "F4F6F9";   // slide background
const DGRAY  = "374151";   // body text
const MGRAY  = "6B7280";   // muted text
const LTEAL  = "E6F4F2";   // teal tint
const LNAVY  = "E8EDF6";   // navy tint

// Slide dimensions (LAYOUT_16x9 = 10 × 5.625 in)
const W = 10;
const H = 5.625;

// ── Helper: GE logo badge (top-left) ─────────────────────────
function addGELogo(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.25, y: 0.18, w: 1.55, h: 0.38,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("GE HealthCare", {
    x: 0.25, y: 0.18, w: 1.55, h: 0.38,
    fontSize: 10, bold: true, color: WHITE,
    align: "center", valign: "middle", margin: 0
  });
}

// ── Helper: slide top bar ─────────────────────────────────────
function addTopBar(slide, color, title, textColor) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: W, h: 0.72,
    fill: { color: color }, line: { color: color }
  });
  slide.addText(title, {
    x: 1.95, y: 0, w: 7.6, h: 0.72,
    fontSize: 20, bold: true, color: textColor || WHITE,
    align: "left", valign: "middle", margin: 0
  });
  addGELogo(slide);
}

// ── Helper: teal accent left border for a card ───────────────
function addCard(slide, x, y, w, h, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: color || LGRAY },
    shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.10 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.055, h,
    fill: { color: TEAL }, line: { color: TEAL }
  });
}

// ════════════════════════════════════════════════════════════
// SLIDE 1 — Title (dark navy background)
// ════════════════════════════════════════════════════════════
(function() {
  const s = pres.addSlide();
  s.background = { color: NAVY };

  // Right teal accent panel
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: 0, w: 3.2, h: H,
    fill: { color: TEAL }, line: { color: TEAL }
  });

  // Diagonal accent
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 0, w: 0.5, h: H,
    fill: { color: "005F73" }, line: { color: "005F73" }
  });

  // GE logo badge
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 0.3, w: 1.8, h: 0.45,
    fill: { color: WHITE }, line: { color: WHITE }
  });
  s.addText("GE HealthCare", {
    x: 0.35, y: 0.3, w: 1.8, h: 0.45,
    fontSize: 12, bold: true, color: NAVY,
    align: "center", valign: "middle", margin: 0
  });

  // Main title
  s.addText("Projet RFID", {
    x: 0.35, y: 1.05, w: 5.8, h: 0.75,
    fontSize: 38, bold: true, color: WHITE, align: "left", margin: 0
  });
  s.addText("Suivi Chariots &\nAutomatisation Oracle", {
    x: 0.35, y: 1.75, w: 5.8, h: 1.1,
    fontSize: 24, bold: false, color: "CADCFC",
    align: "left", margin: 0
  });

  // Subtitle bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 2.95, w: 5.8, h: 0.005,
    fill: { color: TEAL }, line: { color: TEAL }
  });
  s.addText("GE Healthcare Buc  |  Ligne Pristina  |  Présentation IT", {
    x: 0.35, y: 3.05, w: 5.8, h: 0.35,
    fontSize: 13, color: "CADCFC", align: "left", margin: 0
  });

  // Key points on left
  const bullets = [
    "Remplacer les étiquettes papier par un tracking RFID digital",
    "Suivi temps réel des 49 chariots — ligne Pristina",
    "Automatisation Move Transactions Oracle WIP sans saisie manuelle",
    "2 technologies : RFID HF (Pepper C1) + QR Code (Pistolet)"
  ];
  bullets.forEach((b, i) => {
    s.addShape(pres.shapes.OVAL, {
      x: 0.35, y: 3.6 + i * 0.4, w: 0.16, h: 0.16,
      fill: { color: TEAL }, line: { color: TEAL }
    });
    s.addText(b, {
      x: 0.58, y: 3.55 + i * 0.4, w: 5.6, h: 0.35,
      fontSize: 11, color: "E0E8F4", align: "left", margin: 0
    });
  });

  // Right panel content
  s.addText("49 chariots", {
    x: 6.85, y: 0.9, w: 3.0, h: 0.6,
    fontSize: 34, bold: true, color: WHITE, align: "center", margin: 0
  });
  s.addText("98 badges RFID", {
    x: 6.85, y: 1.45, w: 3.0, h: 0.35,
    fontSize: 15, color: "E0F0EE", align: "center", margin: 0
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: 7.1, y: 1.9, w: 2.5, h: 0,
    line: { color: WHITE, width: 1 }
  });

  const typeLines = [
    ["Type A/B", "Pepper C1 RFID HF"],
    ["Type C/D", "QR Code + Pistolet"]
  ];
  typeLines.forEach(([type, tech], i) => {
    s.addText(type, {
      x: 6.85, y: 2.1 + i * 0.65, w: 1.4, h: 0.3,
      fontSize: 12, bold: true, color: WHITE, align: "center", margin: 0
    });
    s.addText(tech, {
      x: 6.85, y: 2.37 + i * 0.65, w: 3.0, h: 0.28,
      fontSize: 11, color: "D1F0ED", align: "center", margin: 0
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.85, y: 3.55, w: 2.95, h: 1.6,
    fill: { color: "00715F" }, line: { color: "00715F" }
  });
  s.addText("49 START + 49 END\n\nOP 10, OP 20, OP 40\nOP 60, OP 80", {
    x: 6.85, y: 3.55, w: 2.95, h: 1.6,
    fontSize: 12, color: WHITE, align: "center", valign: "middle", margin: 0
  });
})();

// ════════════════════════════════════════════════════════════
// SLIDE 2 — Phase Développement Raspberry Pi
// ════════════════════════════════════════════════════════════
(function() {
  const s = pres.addSlide();
  s.background = { color: LGRAY };

  addTopBar(s, TEAL, "Phase de Développement — Prototype Raspberry Pi");

  // LEFT COLUMN — Tech stack
  addCard(s, 0.28, 0.85, 4.2, 4.5, WHITE);

  s.addText("Technologies utilisées", {
    x: 0.42, y: 0.95, w: 3.95, h: 0.35,
    fontSize: 13, bold: true, color: NAVY, margin: 0
  });

  const techItems = [
    { cat: "Backend",   items: "Python — Flask, Paho-MQTT, MySQL-connector" },
    { cat: "Base de données", items: "MySQL / MariaDB — rfid_buc" },
    { cat: "Messagerie",items: "Mosquitto — Broker MQTT (port 1883)" },
    { cat: "Frontend",  items: "JavaScript + Bootstrap 5 — tablettes opérateurs" },
    { cat: "Hardware",  items: "Raspberry Pi 4 (prototype) · Pepper C1 (lecteur RFID)" }
  ];

  techItems.forEach((t, i) => {
    const y = 1.42 + i * 0.6;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.42, y, w: 3.95, h: 0.52,
      fill: { color: i % 2 === 0 ? LGRAY : "EBF2F8" }, line: { color: "D1D8E0" }
    });
    s.addText(t.cat, {
      x: 0.5, y: y + 0.04, w: 1.4, h: 0.22,
      fontSize: 10, bold: true, color: TEAL, margin: 0
    });
    s.addText(t.items, {
      x: 0.5, y: y + 0.24, w: 3.8, h: 0.22,
      fontSize: 10, color: DGRAY, margin: 0
    });
  });

  // RIGHT COLUMN — 2 layers
  addCard(s, 4.72, 0.85, 5.0, 2.1, WHITE);
  s.addText("Couche 1 — Tracking physique (100% automatique)", {
    x: 4.88, y: 0.95, w: 4.7, h: 0.38,
    fontSize: 12, bold: true, color: TEAL, margin: 0
  });
  const c1 = [
    "Badge RFID scanné → MQTT → Python → MySQL",
    "Mise à jour statut chariot en temps réel",
    "Événement horodaté dans cart_events"
  ];
  c1.forEach((line, i) => {
    s.addText("→  " + line, {
      x: 4.88, y: 1.38 + i * 0.36, w: 4.7, h: 0.3,
      fontSize: 11, color: DGRAY, margin: 0
    });
  });

  addCard(s, 4.72, 3.1, 5.0, 2.25, WHITE);
  s.addText("Couche 2 — Suivi jobs Oracle + Move Transaction", {
    x: 4.88, y: 3.2, w: 4.7, h: 0.38,
    fontSize: 12, bold: true, color: NAVY, margin: 0
  });
  const c2 = [
    "sync_oracle.py → OFs Released → MySQL jobs_planning",
    "Tablette WS : associer le job Oracle au chariot",
    "Badge END → oracle_msca.py → Move Transaction auto"
  ];
  c2.forEach((line, i) => {
    s.addText("→  " + line, {
      x: 4.88, y: 3.63 + i * 0.36, w: 4.7, h: 0.3,
      fontSize: 11, color: DGRAY, margin: 0
    });
  });

  // Badge accent
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.0, y: 2.15, w: 2.6, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  s.addText("✓ Seule action humaine : associer le job au chariot", {
    x: 7.02, y: 2.15, w: 2.58, h: 0.55,
    fontSize: 10, color: WHITE, align: "center", valign: "middle", margin: 4
  });
})();

// ════════════════════════════════════════════════════════════
// SLIDE 3 — Protocoles
// ════════════════════════════════════════════════════════════
(function() {
  const s = pres.addSlide();
  s.background = { color: LGRAY };

  addTopBar(s, NAVY, "Protocoles Utilisés — Développement → Production");

  const protocols = [
    {
      title: "MQTT / MQTTS",
      subtitle: "Pepper C1 → Serveur",
      dev:  "Port 1883 — sans TLS (prototype)",
      prod: "Port 8883 — MQTTS + TLS (production)",
      note: "Broker Mosquitto sur Raspberry Pi / VM Ubuntu",
      color: TEAL
    },
    {
      title: "HTTP / HTTPS",
      subtitle: "Dashboard tablettes",
      dev:  "Port 5000 — HTTP Flask (prototype)",
      prod: "Port 443 — HTTPS Nginx + Flask (production)",
      note: "Interface Bootstrap 5 — responsive tablettes",
      color: NAVY
    },
    {
      title: "Telnet MWA (MSCA)",
      subtitle: "Move Transaction Oracle",
      dev:  "ebsmwaexp…:10400 (GLTEST pour tests)",
      prod: "ebsmwaexpglprod…:10400 (GLPROD — production)",
      note: "Python simule saisie MSCA — approche validée GE Hino Japan",
      color: "005F73"
    },
    {
      title: "MySQL / MariaDB",
      subtitle: "Base de données locale",
      dev:  "MariaDB 11 sur Raspberry Pi — rfid_buc",
      prod: "MySQL sur VM Ubuntu — même schéma 14 tables",
      note: "14 tables : chariots, missions, jobs, événements, queue Oracle",
      color: "6D28D9"
    }
  ];

  protocols.forEach((p, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.28 + col * 4.87;
    const y = 0.88 + row * 2.35;
    const w = 4.62;
    const h = 2.12;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: WHITE },
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.10 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.06,
      fill: { color: p.color }, line: { color: p.color }
    });

    s.addText(p.title, {
      x: x + 0.2, y: y + 0.14, w: w - 0.3, h: 0.35,
      fontSize: 14, bold: true, color: p.color, margin: 0
    });
    s.addText(p.subtitle, {
      x: x + 0.2, y: y + 0.46, w: w - 0.3, h: 0.25,
      fontSize: 11, color: MGRAY, italic: true, margin: 0
    });

    s.addShape(pres.shapes.LINE, {
      x: x + 0.2, y: y + 0.76, w: w - 0.45, h: 0,
      line: { color: "D1D8E0", width: 1 }
    });

    const devProdItems = [
      { label: "Prototype", text: p.dev,  bg: LGRAY  },
      { label: "Production", text: p.prod, bg: LTEAL }
    ];
    devProdItems.forEach((item, j) => {
      const iy = y + 0.88 + j * 0.42;
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + 0.18, y: iy, w: w - 0.38, h: 0.35,
        fill: { color: item.bg }, line: { color: "D1D8E0" }
      });
      s.addText(item.label + ": ", {
        x: x + 0.24, y: iy + 0.04, w: 0.82, h: 0.28,
        fontSize: 9, bold: true, color: DGRAY, margin: 0
      });
      s.addText(item.text, {
        x: x + 1.02, y: iy + 0.04, w: w - 1.25, h: 0.28,
        fontSize: 9, color: DGRAY, margin: 0
      });
    });

    s.addText("ℹ " + p.note, {
      x: x + 0.2, y: y + 1.77, w: w - 0.35, h: 0.27,
      fontSize: 9, color: MGRAY, italic: true, margin: 0
    });
  });
})();

// ════════════════════════════════════════════════════════════
// SLIDE 4 — Architecture Finale
// ════════════════════════════════════════════════════════════
(function() {
  const s = pres.addSlide();
  s.background = { color: "0D1B38" };   // very dark navy

  addTopBar(s, TEAL, "Architecture Finale — Serveur Linux GE + Sécurité");

  // Sub-title
  s.addText("Raspberry Pi → VM Ubuntu Server 22.04 LTS | Même code source — seulement la configuration change", {
    x: 0.28, y: 0.8, w: 9.44, h: 0.3,
    fontSize: 10.5, color: "A0B4D0", italic: true, margin: 0
  });

  // Architecture flow boxes
  const flows = [
    { label: "Pepper C1\n(RFID HF)", sub: "WiFi usine", color: TEAL,   x: 0.15, y: 1.25 },
    { label: "MQTTS\nport 8883\n(TLS)", sub: "Chiffré", color: "005F73", x: 1.85, y: 1.25 },
    { label: "Mosquitto\n+ rfid_mqtt.py",sub:"VM Ubuntu", color: NAVY,   x: 3.55, y: 1.25 },
    { label: "MySQL\nrfid_buc",  sub: "14 tables", color: "2D3B8E", x: 5.25, y: 1.25 },
    { label: "Flask\n+ Nginx",  sub: "HTTPS 443", color: "6D28D9", x: 6.95, y: 1.25 },
    { label: "Tablettes WS\n+ Opérateurs",sub:"Dashboard", color: "0A6159", x: 8.65, y: 1.25 }
  ];

  flows.forEach((f, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: f.x, y: f.y, w: 1.55, h: 1.0,
      fill: { color: f.color }, line: { color: f.color }
    });
    s.addText(f.label, {
      x: f.x, y: f.y + 0.1, w: 1.55, h: 0.65,
      fontSize: 10, bold: true, color: WHITE,
      align: "center", valign: "middle", margin: 2
    });
    s.addText(f.sub, {
      x: f.x, y: f.y + 0.73, w: 1.55, h: 0.24,
      fontSize: 8, color: "D1ECE9", align: "center", margin: 0
    });
    if (i < flows.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: f.x + 1.55, y: f.y + 0.5, w: 0.3, h: 0,
        line: { color: TEAL, width: 2 }
      });
    }
  });

  // Oracle row
  const oracleFlows = [
    { label: "sync_oracle.py",  sub: "OFs Released",   color: "8B3A0F", x: 0.15 },
    { label: "Oracle GLPROD\n(DB 1521)",  sub: "apps.WIP_*", color: "A04010", x: 2.05 },
    { label: "jobs_planning\nMySQL",  sub: "OFs synchronisés", color: "2D3B8E", x: 3.95 },
    { label: "oracle_msca.py", sub: "Move Transaction", color: "8B3A0F", x: 5.85 },
    { label: "MWA MSCA\nport 10400",  sub: "Telnet sécurisé",  color: "A04010", x: 7.75 }
  ];

  s.addText("Synchronisation Oracle", {
    x: 0.15, y: 2.55, w: 2.5, h: 0.25,
    fontSize: 9, color: "A0B4D0", bold: true, margin: 0
  });

  oracleFlows.forEach((f, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: f.x, y: 2.82, w: 1.75, h: 0.85,
      fill: { color: f.color }, line: { color: f.color }
    });
    s.addText(f.label, {
      x: f.x, y: 2.84, w: 1.75, h: 0.55,
      fontSize: 10, bold: true, color: WHITE, align: "center", valign: "middle", margin: 2
    });
    s.addText(f.sub, {
      x: f.x, y: 3.37, w: 1.75, h: 0.24,
      fontSize: 8, color: "FECBA8", align: "center", margin: 0
    });
    if (i < oracleFlows.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: f.x + 1.75, y: 3.24, w: 0.3, h: 0,
        line: { color: "FCA869", width: 2 }
      });
    }
  });

  // Cloud/Optional row
  const optItems = [
    "Power BI → MySQL (dashboard direction)",
    "Alertes Teams (missions critiques)",
    "VPN GE existant → accès externe direction",
    "Sauvegarde automatique VM"
  ];
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.15, y: 3.88, w: 9.68, h: 1.5,
    fill: { color: "0A1E35" }, line: { color: TEAL, width: 1 }
  });
  s.addText("Optionnel — Cloud GE / Intégrations", {
    x: 0.28, y: 3.95, w: 4.0, h: 0.3,
    fontSize: 10, bold: true, color: TEAL, margin: 0
  });
  optItems.forEach((item, i) => {
    const col = i % 2;
    const row2 = Math.floor(i / 2);
    s.addText("◆  " + item, {
      x: 0.35 + col * 4.9, y: 4.3 + row2 * 0.37, w: 4.7, h: 0.3,
      fontSize: 10, color: "8AB4D0", margin: 0
    });
  });
})();

// ════════════════════════════════════════════════════════════
// SLIDE 5 — Besoins IT
// ════════════════════════════════════════════════════════════
(function() {
  const s = pres.addSlide();
  s.background = { color: LGRAY };

  addTopBar(s, NAVY, "Besoins IT — Ce que nous demandons");

  const needs = [
    {
      icon: "SERVER",
      title: "Serveur",
      detail: "VM Ubuntu Server 22.04 LTS\nIP fixe réseau usine GE Buc",
      color: NAVY
    },
    {
      icon: "NETWORK",
      title: "Réseau / Firewall",
      detail: "Ports 8883 (MQTTS) et 443 (HTTPS)\nouverture sur réseau usine",
      color: TEAL
    },
    {
      icon: "WIFI",
      title: "WiFi Industriel",
      detail: "Couverture complète SMK + Pristina\nPepper C1 + tablettes (2.4 GHz / 5 GHz)",
      color: "005F73"
    },
    {
      icon: "DB",
      title: "Oracle GLTEST",
      detail: "Accès username/password MWA MSCA\nOrg BUC — pour les tests préalables",
      color: "6D28D9"
    },
    {
      icon: "ORACLE",
      title: "Oracle GLPROD",
      detail: "Accès identique pour la production finale\nMove Transactions WIP sur OFs Released",
      color: "8B3A0F"
    },
    {
      icon: "SSL",
      title: "Certificat SSL",
      detail: "Pour HTTPS (Nginx) et MQTTS (Mosquitto)\nCertificat GE ou Let's Encrypt",
      color: "0A6159"
    }
  ];

  needs.forEach((n, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.22 + col * 3.28;
    const y = 0.85 + row * 2.35;
    const w = 3.12;
    const h = 2.15;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h,
      fill: { color: WHITE },
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 135, opacity: 0.10 }
    });
    // Top accent
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w, h: 0.07,
      fill: { color: n.color }, line: { color: n.color }
    });
    // Icon circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.15, y: y + 0.18, w: 0.5, h: 0.5,
      fill: { color: n.color }, line: { color: n.color }
    });
    s.addText(n.icon[0], {
      x: x + 0.15, y: y + 0.18, w: 0.5, h: 0.5,
      fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0
    });
    // Title
    s.addText(n.title, {
      x: x + 0.73, y: y + 0.2, w: w - 0.85, h: 0.42,
      fontSize: 13, bold: true, color: n.color, margin: 0
    });
    // Divider
    s.addShape(pres.shapes.LINE, {
      x: x + 0.15, y: y + 0.78, w: w - 0.3, h: 0,
      line: { color: "E2E8F0", width: 1 }
    });
    // Detail
    s.addText(n.detail, {
      x: x + 0.15, y: y + 0.9, w: w - 0.3, h: 1.12,
      fontSize: 10.5, color: DGRAY, margin: 0
    });
  });

  // Optionnel footer
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.22, y: 5.22, w: 9.56, h: 0.3,
    fill: { color: LGRAY }, line: { color: LGRAY }
  });
  s.addText("Optionnel : connecteur Power BI → MySQL (dashboard direction) · VPN GE existant → accès externe direction", {
    x: 0.25, y: 5.23, w: 9.5, h: 0.28,
    fontSize: 9, color: MGRAY, align: "center", margin: 0
  });
})();

// ════════════════════════════════════════════════════════════
// WRITE FILE
// ════════════════════════════════════════════════════════════
pres.writeFile({ fileName: "C:\\Users\\ADMIN\\Desktop\\rfid\\RFID_IT_Presentation.pptx" })
  .then(() => console.log("[OK] Fichier cree : RFID_IT_Presentation.pptx"))
  .catch(err => console.error("[ERR]", err));
