const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; // 13.3" x 7.5"
pres.title = 'Projet RFID - GE Healthcare Buc';
pres.author = 'Stagiaire GE Healthcare Buc';

// ── COULEURS GE ──────────────────────────────────
const GE_BLUE   = '003087';
const GE_TEAL   = '00857C';
const GE_ORANGE = 'E86D1E';
const GE_GRAY   = '64748B';
const GE_LIGHT  = 'F4F6F9';
const GE_WHITE  = 'FFFFFF';
const GE_DARK   = '1C2833';
const GE_GREEN  = '1E8449';
const GE_RED    = 'C0392B';
const GE_PURPLE = '6C3483';

// ── HELPERS ──────────────────────────────────────
const mkShadow = () => ({
  type: 'outer', blur: 8, offset: 3,
  angle: 135, color: '000000', opacity: 0.12
});

// ════════════════════════════════════════════════
// SLIDE 1 — TITRE (fond bleu foncé)
// ════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: GE_BLUE };

  // Bande teal gauche
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });

  // Logo GE HealthCare
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 0.35, w: 2.5, h: 0.6,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL },
    shadow: mkShadow()
  });
  s.addText('GE HealthCare', {
    x: 0.35, y: 0.35, w: 2.5, h: 0.6,
    fontSize: 14, bold: true, color: GE_WHITE,
    align: 'center', valign: 'middle', margin: 0
  });

  // Site
  s.addText('GE Healthcare Buc  |  Ligne Pristina', {
    x: 0.35, y: 1.05, w: 6, h: 0.4,
    fontSize: 11, color: 'AED6F1', align: 'left'
  });

  // Titre principal
  s.addText('Projet RFID', {
    x: 0.35, y: 1.6, w: 9, h: 1.1,
    fontSize: 52, bold: true, color: GE_WHITE,
    align: 'left', fontFace: 'Calibri'
  });

  s.addText('Suivi Chariots & Automatisation Oracle', {
    x: 0.35, y: 2.65, w: 9.5, h: 0.8,
    fontSize: 26, color: GE_TEAL, align: 'left',
    fontFace: 'Calibri'
  });

  // Ligne séparateur
  s.addShape(pres.shapes.LINE, {
    x: 0.35, y: 3.55, w: 12.6, h: 0,
    line: { color: GE_TEAL, width: 2 }
  });

  // Sous-titre
  s.addText('Présentation IT  —  Phase de développement & Architecture finale', {
    x: 0.35, y: 3.75, w: 12.6, h: 0.5,
    fontSize: 16, color: 'BDC3C7', align: 'left'
  });

  // ── 4 cartes stats ──────────────────────────────
  const stats = [
    ['49', 'Chariots\ntotal'],
    ['98', 'Badges\nRFID HF'],
    ['4', 'Types de\nchariots'],
    ['3', 'Phases de\ndéveloppement'],
  ];
  stats.forEach(([num, label], i) => {
    const cx = 0.35 + i * 3.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 4.55, w: 3.0, h: 2.55,
      fill: { color: '0A2560' }, line: { color: GE_TEAL, width: 1.5 },
      shadow: mkShadow()
    });
    // Accent teal top
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: 4.55, w: 3.0, h: 0.07,
      fill: { color: GE_TEAL }, line: { color: GE_TEAL }
    });
    s.addText(num, {
      x: cx, y: 4.7, w: 3.0, h: 1.2,
      fontSize: 60, bold: true, color: GE_WHITE,
      align: 'center', valign: 'middle', margin: 0
    });
    s.addText(label, {
      x: cx, y: 5.85, w: 3.0, h: 1.1,
      fontSize: 13, color: 'AED6F1',
      align: 'center', valign: 'top'
    });
  });

  // Numéro slide
  s.addText('1 / 5', {
    x: 12.5, y: 7.1, w: 0.7, h: 0.3,
    fontSize: 9, color: '5D6D7E', align: 'right'
  });
}

// ════════════════════════════════════════════════
// SLIDE 2 — PHASE DE DÉVELOPPEMENT
// ════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: GE_LIGHT };

  // Header
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 13.3, h: 1.1,
    fill: { color: GE_BLUE }, line: { color: GE_BLUE }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });
  s.addText('GE HealthCare', {
    x: 0.3, y: 0, w: 2.0, h: 1.1,
    fontSize: 11, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });
  s.addText('Phase de Développement  —  Prototype Raspberry Pi', {
    x: 2.5, y: 0, w: 10.5, h: 1.1,
    fontSize: 22, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });

  // ── Colonne gauche : Prototype + Tech ──────────
  // Carte prototype
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 1.3, w: 6.0, h: 1.35,
    fill: { color: GE_WHITE }, line: { color: GE_BLUE, width: 1.5 },
    shadow: mkShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 1.3, w: 0.12, h: 1.35,
    fill: { color: GE_BLUE }, line: { color: GE_BLUE }
  });
  s.addText('Prototype actuel', {
    x: 0.6, y: 1.38, w: 5.6, h: 0.4,
    fontSize: 14, bold: true, color: GE_BLUE, align: 'left'
  });
  s.addText('Développement sur Raspberry Pi  →  réseau WiFi local\nMême code utilisé en production sur serveur Linux GE', {
    x: 0.6, y: 1.78, w: 5.6, h: 0.75,
    fontSize: 11, color: GE_DARK, align: 'left'
  });

  // Carte technologies
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 2.85, w: 6.0, h: 4.3,
    fill: { color: GE_WHITE }, line: { color: GE_TEAL, width: 1.5 },
    shadow: mkShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 2.85, w: 0.12, h: 4.3,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });
  s.addText('Technologies utilisées', {
    x: 0.6, y: 2.93, w: 5.6, h: 0.4,
    fontSize: 14, bold: true, color: GE_TEAL, align: 'left'
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 3.38, w: 5.6, h: 0,
    line: { color: 'E2E8F0', width: 1 }
  });

  const techs = [
    ['Python', 'Flask · Paho-MQTT · MySQL-connector'],
    ['MySQL', 'Base de données rfid_buc (8 tables)'],
    ['Mosquitto', 'Broker MQTT — gestion messages RFID'],
    ['Bootstrap 5', 'Interface responsive tablettes'],
    ['JavaScript', 'Dashboard dynamique temps réel'],
    ['paho-mqtt', 'Communication Pepper C1 → serveur'],
  ];
  techs.forEach(([tech, desc], i) => {
    const ty = 3.52 + i * 0.6;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.6, y: ty, w: 1.2, h: 0.38,
      fill: { color: GE_BLUE }, line: { color: GE_BLUE }
    });
    s.addText(tech, {
      x: 0.6, y: ty, w: 1.2, h: 0.38,
      fontSize: 9, bold: true, color: GE_WHITE,
      align: 'center', valign: 'middle', margin: 0
    });
    s.addText(desc, {
      x: 1.9, y: ty, w: 4.3, h: 0.38,
      fontSize: 10.5, color: GE_DARK, align: 'left', valign: 'middle'
    });
  });

  // ── Colonne droite : 2 couches ─────────────────
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: 1.3, w: 6.15, h: 5.85,
    fill: { color: GE_WHITE }, line: { color: GE_ORANGE, width: 1.5 },
    shadow: mkShadow()
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.8, y: 1.3, w: 0.12, h: 5.85,
    fill: { color: GE_ORANGE }, line: { color: GE_ORANGE }
  });
  s.addText('Architecture 2 couches', {
    x: 7.05, y: 1.38, w: 5.8, h: 0.42,
    fontSize: 14, bold: true, color: GE_ORANGE, align: 'left'
  });
  s.addShape(pres.shapes.LINE, {
    x: 7.05, y: 1.85, w: 5.8, h: 0,
    line: { color: 'E2E8F0', width: 1 }
  });

  // Couche 1
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.05, y: 2.05, w: 5.75, h: 2.2,
    fill: { color: 'EBF5FB' }, line: { color: GE_BLUE, width: 1 }
  });
  s.addText('Couche 1  —  Tracking physique', {
    x: 7.15, y: 2.12, w: 5.55, h: 0.38,
    fontSize: 12, bold: true, color: GE_BLUE, align: 'left'
  });
  s.addText([
    { text: '100% AUTOMATIQUE', options: { bold: true, color: GE_GREEN, breakLine: true } },
    { text: 'Badge START detecte  →  statut EN_ATTENTE', options: { breakLine: true } },
    { text: 'Badge END detecte    →  statut RETOUR', options: { breakLine: true } },
    { text: 'Aucune action humaine requise', options: { color: GE_GRAY } },
  ], {
    x: 7.15, y: 2.55, w: 5.55, h: 1.6,
    fontSize: 11, color: GE_DARK, align: 'left'
  });

  // Couche 2
  s.addShape(pres.shapes.RECTANGLE, {
    x: 7.05, y: 4.45, w: 5.75, h: 2.4,
    fill: { color: 'EAFAF1' }, line: { color: GE_GREEN, width: 1 }
  });
  s.addText('Couche 2  —  Suivi jobs Oracle', {
    x: 7.15, y: 4.52, w: 5.55, h: 0.38,
    fontSize: 12, bold: true, color: GE_GREEN, align: 'left'
  });
  s.addText([
    { text: 'VALIDATION HUMAINE UNIQUE :', options: { bold: true, color: GE_ORANGE, breakLine: true } },
    { text: 'Associer le job au chariot sur tablette WS', options: { breakLine: true } },
    { text: 'Badge START  →  Move Oracle automatique', options: { bold: true, color: GE_GREEN, breakLine: true } },
    { text: 'Badge END    →  Aucune transaction Oracle', options: { color: GE_GRAY } },
  ], {
    x: 7.15, y: 4.95, w: 5.55, h: 1.75,
    fontSize: 11, color: GE_DARK, align: 'left'
  });

  // Footer
  s.addText('2 / 5', {
    x: 12.5, y: 7.1, w: 0.7, h: 0.3,
    fontSize: 9, color: GE_GRAY, align: 'right'
  });
}

// ════════════════════════════════════════════════
// SLIDE 3 — PROTOCOLES
// ════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: GE_LIGHT };

  // Header
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 13.3, h: 1.1,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: GE_BLUE }, line: { color: GE_BLUE }
  });
  s.addText('GE HealthCare', {
    x: 0.3, y: 0, w: 2.0, h: 1.1,
    fontSize: 11, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });
  s.addText('Protocoles Utilisés dans le Développement', {
    x: 2.5, y: 0, w: 10.5, h: 1.1,
    fontSize: 22, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });

  // ── 4 cartes protocoles ─────────────────────────
  const protos = [
    {
      title: 'MQTT / MQTTS',
      subtitle: 'Pepper C1 → Serveur',
      color: GE_RED,
      bg: 'FEF5F5',
      items: [
        'Communication entre le lecteur RFID et le serveur',
        'Prototype  →  port 1883  (sans TLS)',
        'Production →  port 8883  (MQTTS + TLS)',
        'Topic : rfid/buc/#',
        'QoS 1 — livraison garantie'
      ],
      proto: ['Prototype', 'HTTP 1883'],
      prod: ['Production', 'MQTTS 8883']
    },
    {
      title: 'HTTP / HTTPS',
      subtitle: 'Tablettes → Serveur',
      color: GE_BLUE,
      bg: 'EBF5FB',
      items: [
        'Accès dashboard web depuis les tablettes WS',
        'Prototype  →  port 5000  HTTP  (Flask)',
        'Production →  port 443  HTTPS  (Nginx)',
        'Bootstrap 5 + JavaScript',
        'Refresh automatique toutes les 30 secondes'
      ],
      proto: ['Prototype', 'HTTP 5000'],
      prod: ['Production', 'HTTPS 443']
    },
    {
      title: 'Telnet MWA MSCA',
      subtitle: 'Automatisation Oracle',
      color: GE_PURPLE,
      bg: 'F5EEF8',
      items: [
        'Python simule la saisie clavier dans MSCA Oracle',
        'Connexion Telnet → Login → Navigation → Save',
        'Move Transaction WIP sans action humaine',
        'File attente MySQL → traitement asynchrone',
        'Approche validee : Hino GE Healthcare Japon'
      ],
      proto: ['Déclenché par', 'badge START'],
      prod: ['Oracle', 'WIP Move']
    },
    {
      title: 'MySQL + sync_oracle',
      subtitle: 'Données & Synchronisation',
      color: GE_GREEN,
      bg: 'EAFAF1',
      items: [
        'MySQL : stockage missions, chariots, jobs, events',
        'sync_oracle.py : OFs Released → MySQL (periodique)',
        'oracle_move_queue : file attente transactions Oracle',
        'rfid_buc : 8 tables, schéma complet',
        'Connexion Oracle via cx_Oracle (GLTEST/GLPROD)'
      ],
      proto: ['Sync', 'periodique'],
      prod: ['Oracle', 'GLTEST']
    }
  ];

  protos.forEach((p, i) => {
    const col = i < 2 ? i : i;
    const cx = 0.3 + (i % 2) * 6.45;
    const cy = 1.3 + Math.floor(i / 2) * 3.05;
    const cw = 6.2;
    const ch = 2.8;

    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: cw, h: ch,
      fill: { color: p.bg }, line: { color: p.color, width: 1.5 },
      shadow: mkShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: cw, h: 0.55,
      fill: { color: p.color }, line: { color: p.color }
    });
    s.addText(p.title, {
      x: cx + 0.12, y: cy, w: cw - 0.24, h: 0.36,
      fontSize: 13, bold: true, color: GE_WHITE,
      align: 'left', valign: 'bottom', margin: 0
    });
    s.addText(p.subtitle, {
      x: cx + 0.12, y: cy + 0.34, w: cw - 0.24, h: 0.22,
      fontSize: 9.5, color: GE_WHITE, align: 'left',
      valign: 'top', margin: 0
    });

    p.items.forEach((item, j) => {
      s.addText([
        { text: '▸  ', options: { color: p.color, bold: true } },
        { text: item, options: { color: GE_DARK } }
      ], {
        x: cx + 0.15, y: cy + 0.65 + j * 0.41,
        w: cw - 0.3, h: 0.38,
        fontSize: 10.5, align: 'left', valign: 'middle'
      });
    });
  });

  s.addText('3 / 5', {
    x: 12.5, y: 7.1, w: 0.7, h: 0.3,
    fontSize: 9, color: GE_GRAY, align: 'right'
  });
}

// ════════════════════════════════════════════════
// SLIDE 4 — ARCHITECTURE FINALE
// ════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: '0A1628' };

  // Bande teal
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });

  // Logo
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 0.25, w: 2.2, h: 0.5,
    fill: { color: GE_TEAL }, line: { color: GE_TEAL }
  });
  s.addText('GE HealthCare', {
    x: 0.35, y: 0.25, w: 2.2, h: 0.5,
    fontSize: 11, bold: true, color: GE_WHITE,
    align: 'center', valign: 'middle', margin: 0
  });

  // Titre
  s.addText('Architecture Finale', {
    x: 2.8, y: 0.2, w: 7, h: 0.65,
    fontSize: 28, bold: true, color: GE_WHITE, align: 'left'
  });
  s.addText('Serveur Linux GE  |  Sécurité  |  Cloud optionnel', {
    x: 2.8, y: 0.82, w: 10, h: 0.38,
    fontSize: 13, color: GE_TEAL, align: 'left'
  });

  // ── Flux architecture (horizontal) ─────────────
  // Flèche fond
  s.addShape(pres.shapes.LINE, {
    x: 0.35, y: 2.82, w: 12.6, h: 0,
    line: { color: '2D4A6A', width: 1.5 }
  });

  const nodes = [
    { label: 'Pepper C1\nRFID HF', color: GE_RED, x: 0.35, w: 2.0 },
    { label: 'Mosquitto\nMQTTS 8883', color: GE_RED, x: 2.65, w: 2.1 },
    { label: 'rfid_mqtt.py\nFlask + Nginx', color: GE_GREEN, x: 5.05, w: 2.2 },
    { label: 'MySQL\nrfid_buc', color: GE_TEAL, x: 7.55, w: 2.0 },
    { label: 'Oracle MSCA\nMove Auto', color: '8E44AD', x: 9.85, w: 2.1 },
    { label: 'Tablettes\nHTTPS 443', color: GE_ORANGE, x: 12.2, w: 0.9 },
  ];

  nodes.forEach((n, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: n.x, y: 1.5, w: n.w, h: 1.2,
      fill: { color: n.color }, line: { color: n.color },
      shadow: mkShadow()
    });
    s.addText(n.label, {
      x: n.x, y: 1.5, w: n.w, h: 1.2,
      fontSize: 10, bold: true, color: GE_WHITE,
      align: 'center', valign: 'middle'
    });
    if (i < nodes.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: n.x + n.w, y: 2.1, w: 0.2, h: 0,
        line: { color: GE_WHITE, width: 1.5 }
      });
      s.addText('→', {
        x: n.x + n.w, y: 1.88, w: 0.2, h: 0.42,
        fontSize: 14, color: GE_WHITE, align: 'center', valign: 'middle'
      });
    }
  });

  // ── 3 blocs infos ──────────────────────────────
  const blocs = [
    {
      title: 'Serveur Linux GE',
      color: GE_TEAL,
      x: 0.35, y: 3.05, w: 4.0, h: 4.1,
      items: [
        'VM Ubuntu Server 22.04 LTS',
        'IP fixe — reseau usine GE Buc',
        'Mosquitto port 8883 (MQTTS+TLS)',
        'Flask + Nginx port 443 (HTTPS)',
        'MySQL base rfid_buc',
        'Meme code que Raspberry Pi',
        'Juste changer la configuration'
      ]
    },
    {
      title: 'Securite',
      color: GE_RED,
      x: 4.65, y: 3.05, w: 4.0, h: 4.1,
      items: [
        'MQTTS port 8883 — TLS/SSL',
        'HTTPS port 443 — certificat SSL',
        'Username + Password Oracle',
        'VPN GE — acces externe securise',
        'Reseau local usine GE (LAN)',
        'Pas d\'acces Internet requis',
        'Conforme securite GE Healthcare'
      ]
    },
    {
      title: 'Cloud GE (optionnel)',
      color: '1565C0',
      x: 8.95, y: 3.05, w: 4.0, h: 4.1,
      items: [
        'Power BI — dashboard direction',
        'Alertes Microsoft Teams',
        'Sauvegarde MySQL automatique',
        'Acces hors usine (sans VPN)',
        'Monitoring + reporting KPIs',
        'Decision IT + Management',
        'Non requis pour le fonctionnement'
      ]
    }
  ];

  blocs.forEach(b => {
    s.addShape(pres.shapes.RECTANGLE, {
      x: b.x, y: b.y, w: b.w, h: b.h,
      fill: { color: '0D1F38' }, line: { color: b.color, width: 1.5 },
      shadow: mkShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: b.x, y: b.y, w: b.w, h: 0.5,
      fill: { color: b.color }, line: { color: b.color }
    });
    s.addText(b.title, {
      x: b.x + 0.1, y: b.y, w: b.w - 0.2, h: 0.5,
      fontSize: 12, bold: true, color: GE_WHITE,
      align: 'left', valign: 'middle', margin: 0
    });
    b.items.forEach((item, j) => {
      s.addText([
        { text: '▸  ', options: { color: b.color, bold: true } },
        { text: item, options: { color: 'CBD5E0' } }
      ], {
        x: b.x + 0.12, y: b.y + 0.6 + j * 0.49,
        w: b.w - 0.24, h: 0.44,
        fontSize: 10, align: 'left', valign: 'middle'
      });
    });
  });

  s.addText('4 / 5', {
    x: 12.5, y: 7.1, w: 0.7, h: 0.3,
    fontSize: 9, color: '5D6D7E', align: 'right'
  });
}

// ════════════════════════════════════════════════
// SLIDE 5 — BESOINS IT
// ════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: GE_LIGHT };

  // Header
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 13.3, h: 1.1,
    fill: { color: GE_BLUE }, line: { color: GE_BLUE }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 7.5,
    fill: { color: GE_ORANGE }, line: { color: GE_ORANGE }
  });
  s.addText('GE HealthCare', {
    x: 0.3, y: 0, w: 2.0, h: 1.1,
    fontSize: 11, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });
  s.addText('Besoins IT  —  Ce que nous demandons', {
    x: 2.5, y: 0, w: 10.5, h: 1.1,
    fontSize: 22, bold: true, color: GE_WHITE,
    align: 'left', valign: 'middle'
  });

  // Tableau des besoins
  const besoins = [
    { cat: 'SERVEUR', label: 'VM Ubuntu Server 22.04 LTS', detail: 'IP fixe reseau usine GE Buc  —  meme configuration que Raspberry Pi', color: GE_BLUE, priority: 'REQUIS' },
    { cat: 'RESEAU', label: 'Ports 8883 et 443 ouverts', detail: 'MQTTS port 8883 (Pepper C1 → serveur)  |  HTTPS port 443 (tablettes → serveur)', color: GE_TEAL, priority: 'REQUIS' },
    { cat: 'WIFI', label: 'Couverture WiFi industrielle', detail: 'SMK + ligne Pristina complète  —  Pepper C1 + tablettes WS + tablettes opérateurs', color: GE_TEAL, priority: 'REQUIS' },
    { cat: 'ORACLE', label: 'Accès Oracle GLTEST', detail: 'Username + Password MWA MSCA  |  Organisation BUC  —  pour phase de tests', color: GE_ORANGE, priority: 'REQUIS' },
    { cat: 'ORACLE', label: 'Accès Oracle GLPROD', detail: 'Même configuration  —  pour mise en production finale', color: GE_ORANGE, priority: 'REQUIS' },
    { cat: 'SSL', label: 'Certificat SSL', detail: 'Pour HTTPS (Nginx) et MQTTS (Mosquitto)  —  auto-signé ou Let\'s Encrypt', color: GE_RED, priority: 'REQUIS' },
    { cat: 'VPN', label: 'VPN GE Healthcare', detail: 'Acces dashboard depuis hors usine  —  déjà existant dans GE', color: GE_GRAY, priority: 'EXISTANT' },
    { cat: 'CLOUD', label: 'Connecteur Power BI → MySQL', detail: 'Dashboard KPIs pour direction  —  si dashboard externe souhaité', color: '1565C0', priority: 'OPTIONNEL' },
  ];

  besoins.forEach((b, i) => {
    const y = 1.15 + i * 0.70;
    const priorityColor = b.priority === 'REQUIS' ? GE_RED : b.priority === 'EXISTANT' ? GE_GREEN : GE_GRAY;

    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y: y, w: 12.7, h: 0.63,
      fill: { color: GE_WHITE }, line: { color: 'E2E8F0', width: 1 },
      shadow: { type: 'outer', blur: 3, offset: 1, angle: 135, color: '000000', opacity: 0.06 }
    });
    // Barre couleur gauche
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.3, y: y, w: 0.1, h: 0.63,
      fill: { color: b.color }, line: { color: b.color }
    });
    // Badge catégorie
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.55, y: y + 0.12, w: 1.0, h: 0.36,
      fill: { color: b.color }, line: { color: b.color }
    });
    s.addText(b.cat, {
      x: 0.55, y: y + 0.12, w: 1.0, h: 0.36,
      fontSize: 8.5, bold: true, color: GE_WHITE,
      align: 'center', valign: 'middle', margin: 0
    });
    // Label
    s.addText(b.label, {
      x: 1.65, y: y + 0.04, w: 4.5, h: 0.32,
      fontSize: 12, bold: true, color: GE_DARK, align: 'left'
    });
    // Détail
    s.addText(b.detail, {
      x: 1.65, y: y + 0.35, w: 9.5, h: 0.25,
      fontSize: 9.5, color: GE_GRAY, align: 'left'
    });
    // Badge priorité
    s.addShape(pres.shapes.RECTANGLE, {
      x: 11.6, y: y + 0.14, w: 1.3, h: 0.32,
      fill: { color: priorityColor }, line: { color: priorityColor }
    });
    s.addText(b.priority, {
      x: 11.6, y: y + 0.14, w: 1.3, h: 0.32,
      fontSize: 8.5, bold: true, color: GE_WHITE,
      align: 'center', valign: 'middle', margin: 0
    });
  });

  // Footer note
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 6.78, w: 12.7, h: 0.32,
    fill: { color: GE_BLUE }, line: { color: GE_BLUE }
  });
  s.addText('Développement sur Raspberry Pi en cours  —  Migration vers serveur Linux GE dès validation du prototype', {
    x: 0.3, y: 6.78, w: 12.7, h: 0.32,
    fontSize: 9.5, color: GE_WHITE, align: 'center', valign: 'middle', margin: 0
  });
  s.addText('5 / 5', {
    x: 12.5, y: 6.82, w: 0.7, h: 0.3,
    fontSize: 9, color: GE_WHITE, align: 'right'
  });
}

// ════════════════════════════════════════════════
// EXPORT
// ════════════════════════════════════════════════
pres.writeFile({ fileName: 'C:\\Users\\ADMIN\\Desktop\\rfid\\RFID_IT_Presentation.pptx' })
  .then(() => console.log('[OK] RFID_IT_Presentation.pptx cree avec succes'))
  .catch(e => console.error('[ERREUR]', e));
