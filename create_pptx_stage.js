const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title  = 'Digitalisation des Flux Logistiques par RFID – GE Healthcare Buc';
pres.author = 'Asmae Hmidani';

// COULEURS
const B  = '003087'; // GE Blue
const T  = '00857C'; // GE Teal
const O  = 'E86D1E'; // Orange
const G  = '64748B'; // Gray
const LG = 'F4F6F9'; // Light gray
const W  = 'FFFFFF';
const D  = '1C2833'; // Dark
const GN = '1E8449'; // Green
const RD = 'C0392B'; // Red
const PU = '6C3483'; // Purple
const NA = '0A1628'; // Navy
const PURPLE_L = 'F3E5F5'; // Purple Light

const mk = () => ({ type:'outer', blur:6, offset:2, angle:135, color:'000000', opacity:0.10 });

// Header helper (slides 2-9)
function header(s, title, accent) {
  s.addShape(pres.shapes.RECTANGLE, { x:0,y:0,w:13.3,h:0.95, fill:{color:accent||B}, line:{color:accent||B} });
  s.addShape(pres.shapes.RECTANGLE, { x:0,y:0,w:0.18,h:7.5,  fill:{color:T},       line:{color:T} });
  s.addShape(pres.shapes.RECTANGLE, { x:0.3,y:0.2,w:2.2,h:0.55, fill:{color:T}, line:{color:T}, shadow:mk() });
  s.addText('GE HealthCare', { x:0.3,y:0.2,w:2.2,h:0.55, fontSize:12,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  s.addText(title, { x:2.7,y:0,w:10.4,h:0.95, fontSize:22,bold:true,color:W,align:'left',valign:'middle' });
}

function pageNum(s, n) {
  s.addText(n+' / 10', { x:12.2,y:7.2,w:0.9,h:0.25, fontSize:8,color:G,align:'right' });
}

// Flux statuts helper — dessine une ligne de statuts avec fleches
function flowLine(s, statuses, colors, y, x0, stepW, h) {
  statuses.forEach((st, i) => {
    s.addShape(pres.shapes.RECTANGLE, { x:x0+i*stepW,y:y,w:stepW-0.15,h:h, fill:{color:colors[i]}, line:{color:colors[i]}, shadow:mk() });
    s.addText(st, { x:x0+i*stepW,y:y,w:stepW-0.15,h:h, fontSize:9,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i < statuses.length-1) {
      s.addShape(pres.shapes.RECTANGLE, { x:x0+i*stepW+stepW-0.2,y:y+h/2-0.04,w:0.22,h:0.08, fill:{color:'CBD5E0'},line:{color:'CBD5E0'} });
    }
  });
}

// ═══════════════════════════════════════════════════════
// SLIDE 1 – TITRE
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: B };

  // Bande teal gauche
  s.addShape(pres.shapes.RECTANGLE, { x:0,y:0,w:0.22,h:7.5, fill:{color:T},line:{color:T} });

  // Bande deco bas
  s.addShape(pres.shapes.RECTANGLE, { x:0,y:6.4,w:13.3,h:1.1, fill:{color:'001F5B'},line:{color:'001F5B'} });
  s.addShape(pres.shapes.RECTANGLE, { x:0,y:6.4,w:4.5,h:1.1, fill:{color:T},line:{color:T} });

  // Logo GE HealthCare
  s.addShape(pres.shapes.RECTANGLE, { x:0.45,y:0.4,w:2.8,h:0.65, fill:{color:T},line:{color:T},shadow:mk() });
  s.addText('GE HealthCare', { x:0.45,y:0.4,w:2.8,h:0.65, fontSize:15,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  // Badge stage
  s.addShape(pres.shapes.RECTANGLE, { x:0.45,y:1.25,w:2.2,h:0.4, fill:{color:'FFFFFF',transparency:80},line:{color:'FFFFFF',transparency:60} });
  s.addText('Rapport de Stage – 2025', { x:0.45,y:1.25,w:2.2,h:0.4, fontSize:9,color:'CADCFC',align:'center',valign:'middle',margin:0 });

  // Titre principal
  s.addText('Digitalisation des Flux', { x:0.5,y:2.0,w:12.5,h:1.0, fontSize:46,bold:true,color:W,align:'left' });
  s.addText('Logistiques par RFID', { x:0.5,y:2.85,w:12.5,h:1.0, fontSize:46,bold:true,color:T,align:'left' });

  // Sous-titre
  s.addShape(pres.shapes.RECTANGLE, { x:0.5,y:4.0,w:6.5,h:0.04, fill:{color:T},line:{color:T} });
  s.addText('Ligne Pristina  |  GE Healthcare Buc', { x:0.5,y:4.15,w:9.0,h:0.45, fontSize:16,color:'CADCFC',align:'left' });

  // Infos auteur
  s.addText('Asmae Hmidani', { x:0.5,y:4.85,w:7.0,h:0.55, fontSize:20,bold:true,color:W,align:'left' });
  s.addText('Ingénierie Électromécanique  —  Digitalisation Industrielle', { x:0.5,y:5.38,w:9.5,h:0.38, fontSize:13,color:'CADCFC',align:'left' });
  s.addText('GE Healthcare Buc', { x:0.5,y:5.72,w:7.0,h:0.35, fontSize:12,color:T,align:'left' });

  // Bas de page
  s.addText('Projet RFID  |  Ligne Pristina  |  2025', { x:4.6,y:6.55,w:8.5,h:0.45, fontSize:11,color:'CADCFC',align:'right' });
}

// ═══════════════════════════════════════════════════════
// SLIDE 2 – CONTEXTE ET PROBLEMATIQUE
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Contexte et Problématique', RD);
  pageNum(s, '2');

  const problems = [
    { txt:'Préparation manuelle des chariots par le Water Spider', c:O },
    { txt:'Peu de visibilité temps réel sur les flux logistiques',  c:RD },
    { txt:'Transactions Oracle parfois retardées ou oubliées',       c:RD },
    { txt:'Pas de synchronisation physique ↔ système Oracle',       c:RD },
    { txt:'Difficulté à mesurer les KPI et le takt time',            c:PU },
  ];

  // Titre section gauche
  s.addText('Situation actuelle', { x:0.5,y:1.1,w:6.5,h:0.42, fontSize:14,bold:true,color:B });
  s.addShape(pres.shapes.RECTANGLE, { x:0.5,y:1.5,w:6.2,h:0.04, fill:{color:T},line:{color:T} });

  problems.forEach((p,i) => {
    const y = 1.65 + i*0.95;
    s.addShape(pres.shapes.RECTANGLE, { x:0.5,y:y,w:6.5,h:0.8, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
    s.addShape(pres.shapes.RECTANGLE, { x:0.5,y:y,w:0.08,h:0.8, fill:{color:p.c},line:{color:p.c} });
    s.addShape(pres.shapes.RECTANGLE, { x:0.7,y:y+0.22,w:0.32,h:0.32, fill:{color:p.c},line:{color:p.c} });
    s.addText('!', { x:0.7,y:y+0.22,w:0.32,h:0.32, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    s.addText(p.txt, { x:1.15,y:y+0.15,w:5.7,h:0.5, fontSize:11.5,color:D,align:'left',valign:'middle' });
  });

  // Schéma flux actuel droite
  s.addShape(pres.shapes.RECTANGLE, { x:7.4,y:1.05,w:5.65,h:5.9, fill:{color:W},line:{color:'CBD5E0',width:1.5},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:7.4,y:1.05,w:5.65,h:0.42, fill:{color:B},line:{color:B} });
  s.addText('Flux actuel — Ligne Pristina', { x:7.4,y:1.05,w:5.65,h:0.42, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  // Noeuds du flux
  const flowNodes = [
    { lbl:'Supermarché (SMK)', c:B,  y2:1.75 },
    { lbl:'Zone Attente',      c:O,  y2:2.95 },
    { lbl:'Poste Assemblage',  c:GN, y2:4.15 },
    { lbl:'Retour vide',       c:G,  y2:5.35 },
  ];
  flowNodes.forEach((n) => {
    s.addShape(pres.shapes.RECTANGLE, { x:8.5,y:n.y2,w:3.5,h:0.65, fill:{color:n.c},line:{color:n.c},shadow:mk() });
    s.addText(n.lbl, { x:8.5,y:n.y2,w:3.5,h:0.65, fontSize:12,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (n.y2 < 5.35) {
      s.addShape(pres.shapes.RECTANGLE, { x:9.95,y:n.y2+0.65,w:0.08,h:0.5, fill:{color:G},line:{color:G} });
    }
  });

  // Nuage "visibilite limitee"
  s.addShape(pres.shapes.RECTANGLE, { x:7.8,y:3.12,w:2.3,h:0.6, fill:{color:'FFF3CD'},line:{color:O,width:1.5} });
  s.addText('? Visibilité\nlimitée', { x:7.8,y:3.12,w:2.3,h:0.6, fontSize:9.5,bold:true,color:O,align:'center',valign:'middle',margin:0 });
  // fleche vers nuage
  s.addShape(pres.shapes.RECTANGLE, { x:10.0,y:3.3,w:0.5,h:0.06, fill:{color:O},line:{color:O} });

  s.addText('Objectif : connecter ces étapes avec RFID', { x:7.6,y:6.55,w:5.3,h:0.32, fontSize:9.5,color:T,align:'center',style:'italic' });
}

// ═══════════════════════════════════════════════════════
// SLIDE 3 – OBJECTIFS
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Objectifs du Projet', T);
  pageNum(s, '3');

  const objs = [
    { txt:'Suivi temps réel des chariots',          detail:'Position et statut à chaque instant',         c:B  },
    { txt:'Automatisation des transactions Oracle',  detail:'Move Transaction WIP sans action manuelle',   c:T  },
    { txt:'Réduction des opérations manuelles',      detail:'Water Spider se concentre sur la valeur ajoutée', c:GN },
    { txt:'Amélioration de la traçabilité',          detail:'Historique complet de chaque chariot/mission', c:O  },
    { txt:'Calcul KPI / temps cycle / takt time',    detail:'Données terrain en temps réel',               c:PU },
    { txt:'Base évolutive Industrie 4.0',            detail:'7 lignes × 16 lecteurs à terme',              c:RD },
  ];

  objs.forEach((o, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * 6.45;
    const y = 1.15 + row * 2.0;

    s.addShape(pres.shapes.RECTANGLE, { x,y,w:6.15,h:1.7, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
    s.addShape(pres.shapes.RECTANGLE, { x,y,w:6.15,h:0.38, fill:{color:o.c},line:{color:o.c} });

    // Check badge
    s.addShape(pres.shapes.RECTANGLE, { x:x+0.15,y:y+0.55,w:0.55,h:0.55, fill:{color:o.c},line:{color:o.c} });
    s.addText('OK', { x:x+0.15,y:y+0.55,w:0.55,h:0.55, fontSize:7.5,bold:true,color:W,align:'center',valign:'middle',margin:0 });

    s.addText(o.txt, { x,y,w:6.15,h:0.38, fontSize:11.5,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    s.addText(o.detail, { x:x+0.85,y:y+0.5,w:5.15,h:0.75, fontSize:12,color:D,align:'left',valign:'middle' });
  });
}

// ═══════════════════════════════════════════════════════
// SLIDE 4 – ARCHITECTURE GLOBALE
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Architecture Globale du Système', B);
  pageNum(s, '4');

  // Flux principal (7 noeuds horizontaux)
  const nodes = [
    { lbl:'Pepper C1\nRFID HF',         c:B  },
    { lbl:'MQTTS\nport 8883',            c:'1565C0' },
    { lbl:'Mosquitto\nBroker',           c:T  },
    { lbl:'Flask\nPython',               c:O  },
    { lbl:'MySQL\nrfid_buc',             c:GN },
    { lbl:'Oracle\nGLPROD',              c:RD },
    { lbl:'Dashboard\nPower BI',         c:PU },
  ];

  const nW = 1.6; const nH = 1.0; const y0 = 2.6; const xStart = 0.4;
  nodes.forEach((n, i) => {
    const x = xStart + i * 1.83;
    s.addShape(pres.shapes.RECTANGLE, { x,y:y0,w:nW,h:nH, fill:{color:n.c},line:{color:n.c},shadow:mk() });
    s.addText(n.lbl, { x,y:y0,w:nW,h:nH, fontSize:9.5,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i < nodes.length-1) {
      // fleche
      s.addShape(pres.shapes.RECTANGLE, { x:x+nW,y:y0+nH/2-0.06,w:0.26,h:0.12, fill:{color:G},line:{color:G} });
    }
  });

  // Labels sous les fleches
  const arrowLabels = ['MQTTS', 'pub/sub', 'handler', 'INSERT', 'cx_Oracle', 'API'];
  arrowLabels.forEach((lbl, i) => {
    const x = xStart + i*1.83 + nW + 0.02;
    s.addText(lbl, { x,y:y0+nH+0.05,w:0.25,h:0.35, fontSize:6.5,color:G,align:'center' });
  });

  // Deux colonnes info bas
  // Colonne RFID
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.05,w:6.0,h:1.35, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.05,w:6.0,h:0.32, fill:{color:B},line:{color:B} });
  s.addText('Couche RFID  —  MQTTS port 8883', { x:0.4,y:4.05,w:6.0,h:0.32, fontSize:10,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  const rfidLines = ['Pepper C1 publie topic rfid/buc/# avec l\'UID du badge lu','QoS 1 — livraison garantie — TLS chiffré','Chaque badge START ou END déclenche la logique Flask'];
  rfidLines.forEach((l,i) => s.addText('• '+l, { x:0.6,y:4.45+i*0.3,w:5.7,h:0.27, fontSize:9.5,color:D,align:'left' }));

  // Colonne WEB
  s.addShape(pres.shapes.RECTANGLE, { x:6.8,y:4.05,w:6.15,h:1.35, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:6.8,y:4.05,w:6.15,h:0.32, fill:{color:T},line:{color:T} });
  s.addText('Couche Web  —  HTTPS port 443', { x:6.8,y:4.05,w:6.15,h:0.32, fontSize:10,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  const webLines = ['Tablettes WS + opérateurs accèdent au dashboard Flask','Nginx en reverse proxy — certificat SSL','QR Code pistolet envoie HTTP POST direct vers Flask'];
  webLines.forEach((l,i) => s.addText('• '+l, { x:7.0,y:4.45+i*0.3,w:5.8,h:0.27, fontSize:9.5,color:D,align:'left' }));

  // Bandeau sync Oracle
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:5.55,w:12.55,h:0.65, fill:{color:'FFF3F3'},line:{color:RD,width:1.2} });
  s.addText('sync_oracle.py — Synchronisation périodique Oracle GLPROD/GLTEST → MySQL   |   oracle_msca_move.py — Move Transaction via Telnet MWA MSCA (approche Hino, validée industriellement)', {
    x:0.6,y:5.55,w:12.3,h:0.65, fontSize:9.5,color:RD,align:'center',valign:'middle'
  });

  s.addText('2 couches indépendantes : Couche 1 = Tracking physique (100% auto)   |   Couche 2 = Oracle jobs (déclenchée par badgeage)', {
    x:0.4,y:6.35,w:12.55,h:0.38, fontSize:9,color:G,align:'center',style:'italic'
  });
}

// ═══════════════════════════════════════════════════════
// SLIDE 5 – PHASE 1
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Phase 1  —  RFID Chariots Type A et B', B);
  pageNum(s, '5');

  // Badge Phase
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.1,w:1.8,h:0.55, fill:{color:B},line:{color:B},shadow:mk() });
  s.addText('PHASE 1', { x:0.4,y:1.1,w:1.8,h:0.55, fontSize:13,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  s.addText('1 Pepper C1  •  Raspberry Pi  •  49 chariots  •  98 badges HF', { x:2.4,y:1.15,w:9.0,h:0.45, fontSize:11,color:G,align:'left',valign:'middle' });

  // Colonne gauche : objectifs
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:4.2,h:2.8, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:4.2,h:0.35, fill:{color:B},line:{color:B} });
  s.addText('Objectifs', { x:0.4,y:1.85,w:4.2,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  const obj1 = ['Tracking sortie SMK (badge START)','Détection retour chariot (badge END)','Oracle Move Transaction automatique','Seule action humaine : associer job sur tablette WS'];
  obj1.forEach((o,i) => {
    s.addShape(pres.shapes.RECTANGLE, { x:0.7,y:2.3+i*0.56,w:0.28,h:0.28, fill:{color:T},line:{color:T} });
    s.addText('>', { x:0.7,y:2.3+i*0.56,w:0.28,h:0.28, fontSize:8,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    s.addText(o, { x:1.1,y:2.28+i*0.56,w:3.4,h:0.32, fontSize:10.5,color:D,align:'left',valign:'middle' });
  });

  // Colonne centre : flux statuts VERTICAL
  s.addShape(pres.shapes.RECTANGLE, { x:4.9,y:1.85,w:3.3,h:2.8, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:4.9,y:1.85,w:3.3,h:0.35, fill:{color:O},line:{color:O} });
  s.addText('Flux Statuts', { x:4.9,y:1.85,w:3.3,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const st1 = [{lbl:'PREPAREE',c:G},{lbl:'EN_ATTENTE',c:B},{lbl:'RETOUR',c:GN}];
  const tr1 = ['badge START lu','badge END lu'];
  st1.forEach((st,i) => {
    const sy = 2.35+i*0.72;
    s.addShape(pres.shapes.RECTANGLE, { x:5.25,y:sy,w:2.6,h:0.42, fill:{color:st.c},line:{color:st.c},shadow:mk() });
    s.addText(st.lbl, { x:5.25,y:sy,w:2.6,h:0.42, fontSize:10,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i<2) {
      s.addShape(pres.shapes.RECTANGLE, { x:5.99,y:sy+0.42,w:0.08,h:0.28, fill:{color:G},line:{color:G} });
      s.addText(tr1[i], { x:5.25,y:sy+0.44,w:2.6,h:0.26, fontSize:8,color:G,align:'center',style:'italic' });
    }
  });

  // Colonne droite : materiel
  s.addShape(pres.shapes.RECTANGLE, { x:8.5,y:1.85,w:4.5,h:2.8, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:8.5,y:1.85,w:4.5,h:0.35, fill:{color:GN},line:{color:GN} });
  s.addText('Matériel & Stack', { x:8.5,y:1.85,w:4.5,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const mat1 = [
    { lbl:'1 × Pepper C1 RFID HF', c:B   },
    { lbl:'Raspberry Pi (prototype)', c:G },
    { lbl:'MySQL  —  rfid_buc',      c:GN },
    { lbl:'Flask + Mosquitto',        c:O  },
    { lbl:'Oracle GLTEST / GLPROD',  c:RD },
  ];
  mat1.forEach((m,i) => {
    s.addShape(pres.shapes.RECTANGLE, { x:8.7,y:2.28+i*0.48,w:4.1,h:0.38, fill:{color:LG},line:{color:'E2E8F0',width:1} });
    s.addShape(pres.shapes.RECTANGLE, { x:8.7,y:2.28+i*0.48,w:0.08,h:0.38, fill:{color:m.c},line:{color:m.c} });
    s.addText(m.lbl, { x:8.9,y:2.28+i*0.48,w:3.8,h:0.38, fontSize:10.5,color:D,align:'left',valign:'middle' });
  });

  // Note Oracle
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.85,w:12.55,h:1.35, fill:{color:'F0FDF4'},line:{color:GN,width:1.2} });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.85,w:0.08,h:1.35, fill:{color:GN},line:{color:GN} });
  s.addText('Oracle Move Transaction — Couche 2', { x:0.7,y:4.9,w:6,h:0.35, fontSize:11,bold:true,color:GN });
  s.addText('Python se connecte via Telnet MWA MSCA et simule la saisie clavier d\'un opérateur.', { x:0.7,y:5.2,w:12.1,h:0.3, fontSize:10,color:D });
  s.addText('Les transactions passent par oracle_move_queue (MySQL) — traitement asynchrone toutes les 10 secondes.', { x:0.7,y:5.48,w:12.1,h:0.3, fontSize:10,color:D });
  s.addText('Approche validée industriellement — référence : Hino / GE Healthcare Japon', { x:0.7,y:5.76,w:12.1,h:0.3, fontSize:10,color:G,style:'italic' });
}

// ═══════════════════════════════════════════════════════
// SLIDE 6 – PHASE 2
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Phase 2  —  Tracking Complet de Bout en Bout', T);
  pageNum(s, '6');

  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.1,w:1.8,h:0.55, fill:{color:T},line:{color:T},shadow:mk() });
  s.addText('PHASE 2', { x:0.4,y:1.1,w:1.8,h:0.55, fontSize:13,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  s.addText('+1 Pepper C1  •  Nouveau statut EN_APPROCHE  •  Visibilité totale', { x:2.4,y:1.15,w:9.5,h:0.45, fontSize:11,color:G,align:'left',valign:'middle' });

  // Ce qui change
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:5.8,h:2.9, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:5.8,h:0.35, fill:{color:T},line:{color:T} });
  s.addText('Nouveauté — Phase 2', { x:0.4,y:1.85,w:5.8,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const news2 = [
    { lbl:'2ème Pepper C1 installé en frontière Zone Attente → Postes', c:T  },
    { lbl:'Détecte le départ du chariot vers le poste assemblage',        c:B  },
    { lbl:'Nouveau statut EN_APPROCHE déclenché automatiquement',         c:O  },
    { lbl:'Opérateur poste sait qu\'un chariot arrive — anticipation',    c:GN },
    { lbl:'Aucune modification du code — seulement configuration MQTT',   c:PU },
  ];
  news2.forEach((n,i) => {
    const y = 2.33+i*0.48;
    s.addShape(pres.shapes.RECTANGLE, { x:0.6,y,w:5.45,h:0.4, fill:{color:LG},line:{color:'E2E8F0',width:1} });
    s.addShape(pres.shapes.RECTANGLE, { x:0.6,y,w:0.08,h:0.4, fill:{color:n.c},line:{color:n.c} });
    s.addText(n.lbl, { x:0.85,y:y+0.05,w:5.1,h:0.3, fontSize:10,color:D,align:'left',valign:'middle' });
  });

  // Flux statuts COMPLET
  s.addShape(pres.shapes.RECTANGLE, { x:6.6,y:1.85,w:6.35,h:2.9, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:6.6,y:1.85,w:6.35,h:0.35, fill:{color:B},line:{color:B} });
  s.addText('Flux Statuts Complet — Type A & B', { x:6.6,y:1.85,w:6.35,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const st2 = [{lbl:'PREPAREE',c:G},{lbl:'EN_ATTENTE',c:B},{lbl:'EN_APPROCHE',c:T},{lbl:'RETOUR',c:GN}];
  const tr2 = ['badge START\n(Pepper C1 #1)','EN_APPROCHE\n(Pepper C1 #2)','badge END\n(Pepper C1 #1)'];
  st2.forEach((st,i) => {
    const sy = 2.33+i*0.62;
    s.addShape(pres.shapes.RECTANGLE, { x:7.8,y:sy,w:3.0,h:0.42, fill:{color:st.c},line:{color:st.c},shadow:mk() });
    s.addText(st.lbl, { x:7.8,y:sy,w:3.0,h:0.42, fontSize:10,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i<3) {
      s.addShape(pres.shapes.RECTANGLE, { x:9.14,y:sy+0.42,w:0.08,h:0.18, fill:{color:G},line:{color:G} });
      s.addText(tr2[i], { x:7.5,y:sy+0.44,w:3.6,h:0.18, fontSize:7.5,color:G,align:'center',style:'italic' });
    }
  });

  // Note EN_APPROCHE
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.9,w:12.55,h:1.3, fill:{color:'E0F7FA'},line:{color:T,width:1.5} });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:4.9,w:0.08,h:1.3, fill:{color:T},line:{color:T} });
  s.addText('Apport de EN_APPROCHE pour la production', { x:0.7,y:4.95,w:6,h:0.35, fontSize:11,bold:true,color:T });
  s.addText('L\'opérateur au poste reçoit une alerte sur sa tablette quand un chariot quitte la zone d\'attente.', { x:0.7,y:5.25,w:12.1,h:0.28, fontSize:10,color:D });
  s.addText('Réduction du temps d\'attente — meilleur takt time — anticipation des mouvements de chariots.', { x:0.7,y:5.52,w:12.1,h:0.28, fontSize:10,color:D });
  s.addText('Phase 1 : Pepper C1 #1 (SMK)   |   Phase 2 : + Pepper C1 #2 (Zone Attente → Postes)', { x:0.7,y:5.8,w:12.1,h:0.28, fontSize:9.5,color:G,style:'italic' });
}

// ═══════════════════════════════════════════════════════
// SLIDE 7 – PHASE 3
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Phase 3  —  Intégration Chariots Lourds et Palettes', PU);
  pageNum(s, '7');

  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.1,w:1.8,h:0.55, fill:{color:PU},line:{color:PU},shadow:mk() });
  s.addText('PHASE 3', { x:0.4,y:1.1,w:1.8,h:0.55, fontSize:13,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  s.addText('QR Code + Pistolet Scanner  •  Type C (P-70)  •  Type D (palettes, box, caisses)', { x:2.4,y:1.15,w:9.5,h:0.45, fontSize:11,color:G,align:'left',valign:'middle' });

  // Gauche : Type C
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:5.9,h:3.1, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:1.85,w:5.9,h:0.35, fill:{color:PU},line:{color:PU} });
  s.addText('Type C  —  Chariots Lourds P-70', { x:0.4,y:1.85,w:5.9,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  // Flux QR Type C
  const qrFlow = [
    {lbl:'QR Code Scanner\n(Pistolet opérateur)',c:PU},
    {lbl:'HTTPS\nport 443',                       c:'1565C0'},
    {lbl:'Flask\nAPI',                             c:O},
    {lbl:'MySQL\nrfid_buc',                        c:GN},
  ];
  qrFlow.forEach((n,i) => {
    const x = 0.6 + i*1.42;
    s.addShape(pres.shapes.RECTANGLE, { x,y:2.35,w:1.25,h:0.65, fill:{color:n.c},line:{color:n.c},shadow:mk() });
    s.addText(n.lbl, { x,y:2.35,w:1.25,h:0.65, fontSize:8,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i<3) s.addShape(pres.shapes.RECTANGLE, { x:x+1.25,y:2.63,w:0.17,h:0.08, fill:{color:G},line:{color:G} });
  });

  s.addText('Pas de badge RFID — Trop lourds pour Pepper C1 standard', { x:0.6,y:3.1,w:5.5,h:0.3, fontSize:9.5,color:G,style:'italic',align:'center' });

  // Statuts Type C
  s.addShape(pres.shapes.RECTANGLE, { x:0.5,y:3.45,w:5.6,h:0.3, fill:{color:B},line:{color:B} });
  s.addText('Flux Statuts Type C / D', { x:0.5,y:3.45,w:5.6,h:0.3, fontSize:9,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const stC = [{lbl:'PREPAREE',c:G},{lbl:'EN_APPROCHE',c:T},{lbl:'RETOUR',c:GN}];
  const trC = ['scan QR entrée poste','scan QR retour vide'];
  let sx3 = 0.62;
  stC.forEach((st,i) => {
    s.addShape(pres.shapes.RECTANGLE, { x:sx3,y:3.85,w:1.6,h:0.4, fill:{color:st.c},line:{color:st.c},shadow:mk() });
    s.addText(st.lbl, { x:sx3,y:3.85,w:1.6,h:0.4, fontSize:8.5,bold:true,color:W,align:'center',valign:'middle',margin:0 });
    if (i<2) {
      s.addShape(pres.shapes.RECTANGLE, { x:sx3+1.6,y:3.99,w:0.18,h:0.1, fill:{color:G},line:{color:G} });
      s.addText(trC[i], { x:sx3+1.6,y:4.28,w:0.2,h:0.25, fontSize:6.5,color:G,align:'center' });
    }
    sx3 += 1.85;
  });

  s.addText('PAS de EN_ATTENTE — Chariot va directement au poste', { x:0.55,y:4.4,w:5.5,h:0.28, fontSize:9,color:RD,bold:true,align:'center' });

  // Droite : Type D
  s.addShape(pres.shapes.RECTANGLE, { x:6.7,y:1.85,w:6.25,h:3.1, fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk() });
  s.addShape(pres.shapes.RECTANGLE, { x:6.7,y:1.85,w:6.25,h:0.35, fill:{color:O},line:{color:O} });
  s.addText('Type D  —  Palettes, Box, Caisses', { x:6.7,y:1.85,w:6.25,h:0.35, fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0 });

  const typeD = [
    { lbl:'Palettes de composants',  detail:'Scannées à l\'entrée du poste — HTTPS POST Flask' },
    { lbl:'Box de pièces',            detail:'QR Code collé sur chaque box — scan pistolet' },
    { lbl:'Caisses réutilisables',    detail:'Même logique que Type C — flux identique' },
  ];
  typeD.forEach((d,i) => {
    const y = 2.35+i*0.72;
    s.addShape(pres.shapes.RECTANGLE, { x:6.9,y,w:5.9,h:0.6, fill:{color:LG},line:{color:'E2E8F0',width:1} });
    s.addShape(pres.shapes.RECTANGLE, { x:6.9,y,w:0.08,h:0.6, fill:{color:O},line:{color:O} });
    s.addText(d.lbl, { x:7.15,y:y+0.05,w:5.5,h:0.26, fontSize:10.5,bold:true,color:D,align:'left' });
    s.addText(d.detail, { x:7.15,y:y+0.3,w:5.5,h:0.24, fontSize:9.5,color:G,align:'left' });
  });

  s.addShape(pres.shapes.RECTANGLE, { x:6.9,y:3.55,w:5.8,h:0.78, fill:{color:'FFF3F3'},line:{color:RD,width:1.2} });
  s.addText('Flux identique Type C — PREPAREE → EN_APPROCHE → RETOUR', { x:7.1,y:3.6,w:5.5,h:0.3, fontSize:10,bold:true,color:RD,align:'center' });
  s.addText('Pas de EN_ATTENTE — Pas de badge RFID — QR Code uniquement', { x:7.1,y:3.88,w:5.5,h:0.28, fontSize:9.5,color:G,align:'center',style:'italic' });

  // Note bas
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:5.15,w:12.55,h:1.08, fill:{color:PURPLE_L||'F3E5F5'},line:{color:PU,width:1.2} });
  s.addShape(pres.shapes.RECTANGLE, { x:0.4,y:5.15,w:0.08,h:1.08, fill:{color:PU},line:{color:PU} });
  s.addText('Comparaison RFID vs QR Code', { x:0.7,y:5.18,w:6,h:0.32, fontSize:10.5,bold:true,color:PU });
  s.addText('RFID (Type A/B) : automatique 100% — le chariot passe devant Pepper C1 → lecture automatique', { x:0.7,y:5.46,w:12.1,h:0.25, fontSize:9.5,color:D });
  s.addText('QR Code (Type C/D) : scan manuel par opérateur → action volontaire — adapté aux chariots hors portée RFID', { x:0.7,y:5.7,w:12.1,h:0.25, fontSize:9.5,color:D });
  s.addText('Les deux flux convergent vers le même MySQL — même dashboard — même Oracle', { x:0.7,y:5.96,w:12.1,h:0.25, fontSize:9,color:G,style:'italic' });
}

// ═══════════════════════════════════════════════════════
// SLIDE 8 – ARCHITECTURE INDUSTRIELLE FINALE
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: NA };

  s.addShape(pres.shapes.RECTANGLE, { x:0,y:0,w:0.22,h:7.5, fill:{color:T},line:{color:T} });
  s.addShape(pres.shapes.RECTANGLE, { x:0.3,y:0.2,w:2.2,h:0.55, fill:{color:T},line:{color:T},shadow:mk() });
  s.addText('GE HealthCare', { x:0.3,y:0.2,w:2.2,h:0.55, fontSize:12,bold:true,color:W,align:'center',valign:'middle',margin:0 });
  s.addText('Industrialisation', { x:2.7,y:0,w:10.0,h:0.95, fontSize:26,bold:true,color:W,align:'left',valign:'middle' });
  s.addText('Architecture Finale  —  Serveur Linux GE + Sécurité', { x:2.7,y:0.62,w:10.0,h:0.38, fontSize:13,color:T,align:'left' });

  pageNum(s, '8');

  // Flux horizontal
  const fnodes = [
    {lbl:'Pepper RFID\n(16 lecteurs)',     c:B     },
    {lbl:'MQTTS\n8883 TLS',               c:'1565C0'},
    {lbl:'Mosquitto\nBroker',              c:T     },
    {lbl:'Flask API\nNginx',               c:O     },
    {lbl:'MySQL\nrfid_buc',               c:GN    },
    {lbl:'Oracle\nGLPROD',               c:RD    },
    {lbl:'Dashboard\nPower BI',           c:PU    },
  ];
  const nw=1.6,nh=0.9,y0=1.2,xs=0.38;
  fnodes.forEach((n,i) => {
    const x=xs+i*1.83;
    s.addShape(pres.shapes.RECTANGLE, {x,y:y0,w:nw,h:nh,fill:{color:n.c},line:{color:n.c},shadow:mk()});
    s.addText(n.lbl, {x,y:y0,w:nw,h:nh,fontSize:9,bold:true,color:W,align:'center',valign:'middle',margin:0});
    if(i<fnodes.length-1) s.addShape(pres.shapes.RECTANGLE,{x:x+nw,y:y0+nh/2-0.05,w:0.26,h:0.1,fill:{color:'4B5563'},line:{color:'4B5563'}});
  });

  // 3 blocs info
  const blocs = [
    { title:'VM Linux GE', c:T, y:2.35, items:['VM Ubuntu Server 22.04 LTS','IP fixe réseau usine GE Buc','Même code que Raspberry Pi','Juste la configuration change'] },
    { title:'Sécurité',    c:RD,y:2.35, items:['MQTTS port 8883  (TLS/SSL)','HTTPS port 443  (Nginx)','Certificat SSL auto-signé / Let\'s Encrypt','VPN GE — accès externe direction','Pas d\'accès Internet requis'] },
    { title:'Infrastructure IT', c:PU,y:2.35, items:['IP fixe + DNS interne','Backup MySQL périodique','Monitoring système Linux','Power BI Gateway local','Extensible 7 lignes × 16 lecteurs'] },
  ];
  blocs.forEach((b,i) => {
    const x=0.4+i*4.3, h2=4.75;
    s.addShape(pres.shapes.RECTANGLE,{x,y:2.38,w:4.1,h:h2,fill:{color:'0F1C33'},line:{color:b.c,width:1.5},shadow:mk()});
    s.addShape(pres.shapes.RECTANGLE,{x,y:2.38,w:4.1,h:0.38,fill:{color:b.c},line:{color:b.c}});
    s.addText(b.title,{x,y:2.38,w:4.1,h:0.38,fontSize:11,bold:true,color:W,align:'center',valign:'middle',margin:0});
    b.items.forEach((it,j) => {
      s.addShape(pres.shapes.RECTANGLE,{x:x+0.2,y:2.9+j*0.62,w:0.25,h:0.25,fill:{color:b.c},line:{color:b.c}});
      s.addText('',{x:x+0.2,y:2.9+j*0.62,w:0.25,h:0.25,fontSize:7,bold:true,color:W,align:'center',valign:'middle',margin:0});
      s.addText(it,{x:x+0.58,y:2.88+j*0.62,w:3.4,h:0.28,fontSize:10,color:'CADCFC',align:'left',valign:'middle'});
    });
  });

  s.addText('Prototype Raspberry Pi  →  Production VM Linux GE  |  Même code — configuration différente', {
    x:0.4,y:7.1,w:12.55,h:0.28, fontSize:9,color:T,align:'center',style:'italic'
  });
}

// ═══════════════════════════════════════════════════════
// SLIDE 9 – KPI ATTENDUS
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: LG };
  header(s, 'Résultats Attendus', GN);
  pageNum(s, '9');

  const kpis = [
    { num:'100%', lbl:'Visibilité\ntemps réel',       detail:'Position et statut de chaque chariot en direct', c:B  },
    { num:'-80%', lbl:'Erreurs\nmanuelles',            detail:'Élimination de la saisie manuelle Oracle',        c:RD },
    { num:'Auto', lbl:'Oracle\nsynchronisé',           detail:'Move Transactions déclenchées par badgeage',      c:O  },
    { num:'Réel', lbl:'Temps cycle\nmesuré',           detail:'Durée réelle de chaque mission chariot',          c:T  },
    { num:'KPI',  lbl:'Tableau de bord\nautomatique',  detail:'Indicateurs production sans saisie manuelle',     c:PU },
    { num:'x7',   lbl:'Base multi-\nlignes',           detail:'Architecture extensible — 7 lignes 16 lecteurs',  c:GN },
  ];

  kpis.forEach((k,i) => {
    const col=i%3, row=Math.floor(i/3);
    const x=0.45+col*4.28, y=1.12+row*2.8;
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:4.0,h:2.55,fill:{color:W},line:{color:'E2E8F0',width:1},shadow:mk()});
    s.addShape(pres.shapes.RECTANGLE,{x,y,w:4.0,h:0.8,fill:{color:k.c},line:{color:k.c}});
    s.addText(k.num,{x,y,w:4.0,h:0.8,fontSize:34,bold:true,color:W,align:'center',valign:'middle',margin:0});
    s.addText(k.lbl,{x,y:y+0.85,w:4.0,h:0.75,fontSize:13,bold:true,color:k.c,align:'center',valign:'middle'});
    s.addText(k.detail,{x:x+0.2,y:y+1.6,w:3.6,h:0.75,fontSize:10,color:G,align:'center',valign:'top'});
  });
}

// ═══════════════════════════════════════════════════════
// SLIDE 10 – CONCLUSION
// ═══════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: B };

  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:0.22,h:7.5,fill:{color:T},line:{color:T}});
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:6.2,w:13.3,h:1.3,fill:{color:'001F5B'},line:{color:'001F5B'}});
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:6.2,w:5.0,h:1.3,fill:{color:T},line:{color:T}});

  s.addShape(pres.shapes.RECTANGLE,{x:0.45,y:0.3,w:2.8,h:0.65,fill:{color:T},line:{color:T},shadow:mk()});
  s.addText('GE HealthCare',{x:0.45,y:0.3,w:2.8,h:0.65,fontSize:15,bold:true,color:W,align:'center',valign:'middle',margin:0});

  s.addText('Conclusion',{x:0.5,y:1.15,w:12.5,h:0.65,fontSize:30,bold:true,color:W,align:'left'});
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:1.78,w:7.0,h:0.05,fill:{color:T},line:{color:T}});

  const pts = [
    { head:'Projet évolutif Industrie 4.0',    body:'Architecture modulaire — Phases 1 → 3 → Production Linux GE',   c:T  },
    { head:'RFID + MQTT + Oracle + Dashboard', body:'Stack technique moderne — protocoles industriels standards',       c:O  },
    { head:'Prototype Raspberry Pi opérationnel',body:'Code Python Flask/MySQL testé sur le terrain — ligne Pristina', c:'CADCFC' },
    { head:'Migration finale vers Linux GE',   body:'Même code — configuration production — sécurité MQTTS/HTTPS',     c:GN },
  ];

  pts.forEach((p,i) => {
    const y=2.0+i*1.08;
    s.addShape(pres.shapes.RECTANGLE,{x:0.5,y,w:0.55,h:0.55,fill:{color:p.c},line:{color:p.c},shadow:mk()});
    s.addText((i+1).toString(),{x:0.5,y,w:0.55,h:0.55,fontSize:18,bold:true,color:B,align:'center',valign:'middle',margin:0});
    s.addText(p.head,{x:1.25,y:y+0.02,w:11.5,h:0.3,fontSize:14,bold:true,color:W,align:'left'});
    s.addText(p.body,{x:1.25,y:y+0.3,w:11.5,h:0.28,fontSize:11,color:'CADCFC',align:'left'});
  });

  s.addText('Asmae Hmidani  —  Ingénierie Électromécanique  —  GE Healthcare Buc  —  2025',{
    x:5.2,y:6.38,w:7.9,h:0.45,fontSize:10,color:W,align:'right',valign:'middle'
  });

  pageNum(s, '10');
}

pres.writeFile({ fileName: 'C:\\Users\\ADMIN\\Desktop\\rfid\\RFID_Stage_Presentation.pptx' })
  .then(() => console.log('[OK] RFID_Stage_Presentation.pptx cree'))
  .catch(e => console.error('[ERREUR]', e));
