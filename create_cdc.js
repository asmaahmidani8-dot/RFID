const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, TableOfContents, LevelFormat
} = require('C:\\Users\\ADMIN\\AppData\\Roaming\\npm\\node_modules\\docx');
const fs = require('fs');

const BLUE = "003087";
const TEAL = "00857C";
const LIGHT_BLUE = "D5E8F0";
const LIGHT_TEAL = "D5EDE9";
const WHITE = "FFFFFF";
const GREY = "F5F5F5";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 32, color: WHITE, font: "Arial" })],
    shading: { fill: BLUE, type: ShadingType.CLEAR },
    spacing: { before: 300, after: 150 },
    indent: { left: 120 }
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 26, color: WHITE, font: "Arial" })],
    shading: { fill: TEAL, type: ShadingType.CLEAR },
    spacing: { before: 200, after: 100 },
    indent: { left: 120 }
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, size: 22, color: BLUE, font: "Arial" })],
    spacing: { before: 150, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: TEAL } }
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: 20, font: "Arial", ...opts })],
    spacing: { after: 80 }
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 20, font: "Arial" })],
    spacing: { after: 60 }
  });
}

function makeTable(headers, rows, headerColor = BLUE) {
  const totalWidth = 9026;
  const colCount = headers.length;
  const colWidth = Math.floor(totalWidth / colCount);
  const colWidths = headers.map((_, i) => i === headers.length - 1 ? totalWidth - colWidth * (colCount - 1) : colWidth);

  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: headerColor, type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 120, right: 120 },
      verticalAlign: VerticalAlign.CENTER,
      children: [new Paragraph({
        children: [new TextRun({ text: h, bold: true, color: WHITE, size: 18, font: "Arial" })],
        alignment: AlignmentType.CENTER
      })]
    }))
  });

  const dataRows = rows.map((row, ri) => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: ri % 2 === 0 ? WHITE : GREY, type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({
        children: [new TextRun({ text: String(cell), size: 18, font: "Arial" })]
      })]
    }))
  }));

  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
    margins: { top: 100, bottom: 100 }
  });
}

function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 120 } });
}

const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: WHITE },
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: WHITE },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 }
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 150, after: 80 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "GE HealthCare — Cahier des Charges RFID Sol — Ligne Pristina", bold: true, size: 16, color: BLUE, font: "Arial" }),
            new TextRun({ text: "\t\tVersion 1.0 | 2026-06-04", size: 16, color: "888888", font: "Arial" })
          ],
          tabStops: [{ type: "right", position: 9026 }],
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL } }
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "GE Healthcare Buc | Confidentiel | Page ", size: 16, color: "888888", font: "Arial" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: BLUE, font: "Arial" })
          ],
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: TEAL } }
        })]
      })
    },
    children: [
      // TITLE PAGE
      spacer(), spacer(),
      new Paragraph({
        children: [new TextRun({ text: "GE HealthCare", bold: true, size: 56, color: BLUE, font: "Arial" })],
        alignment: AlignmentType.CENTER, spacing: { after: 100 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "CAHIER DES CHARGES", bold: true, size: 48, color: TEAL, font: "Arial" })],
        alignment: AlignmentType.CENTER, spacing: { after: 100 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "Mise en Installation Systeme RFID Sol", bold: true, size: 32, color: BLUE, font: "Arial" })],
        alignment: AlignmentType.CENTER, spacing: { after: 60 }
      }),
      new Paragraph({
        children: [new TextRun({ text: "GE Healthcare Buc — Ligne Pristina — Suivi Chariots", size: 24, color: "555555", font: "Arial" })],
        alignment: AlignmentType.CENTER, spacing: { after: 400 }
      }),
      makeTable(
        ["Parametre", "Valeur"],
        [
          ["Document", "CDC_Installation_RFID_GE_Healthcare"],
          ["Version", "1.0"],
          ["Date", "2026-06-04"],
          ["Statut", "En cours de validation"],
          ["Redige par", "Stagiaire Digitalisation"],
          ["Site", "GE Healthcare Buc, France"],
          ["Ligne", "Pristina"]
        ]
      ),
      spacer(), spacer(),

      // TOC
      new Paragraph({ children: [new TextRun({ text: "TABLE DES MATIERES", bold: true, size: 28, color: BLUE, font: "Arial" })], spacing: { before: 200, after: 200 } }),
      new TableOfContents("Table des matieres", { hyperlink: true, headingStyleRange: "1-3" }),
      new Paragraph({ children: [], pageBreakBefore: true }),

      // SECTION 1
      heading1("1. OBJET ET CONTEXTE"),
      heading2("1.1 Objet du document"),
      para("Ce document definit les specifications techniques et fonctionnelles pour la mise en installation du systeme RFID de suivi des chariots sur la ligne Pristina de GE Healthcare Buc."),
      spacer(),
      heading2("1.2 Contexte"),
      bullet("Site : GE Healthcare Buc, France"),
      bullet("Ligne : Pristina (ligne d'assemblage)"),
      bullet("Problematique actuelle : suivi manuel par etiquettes papier, desynchronisation Oracle, erreurs de tracabilite"),
      bullet("Solution : Systeme RFID sol automatique + automatisation Move Transactions Oracle"),
      spacer(),
      heading2("1.3 Objectifs"),
      bullet("Remplacer etiquettes papier par detection RFID automatique"),
      bullet("Tracking temps reel des chariots en entree/sortie supermarche"),
      bullet("Automatisation des Move Transactions Oracle (WIP) sans intervention manuelle"),
      bullet("Reduction des erreurs de tracabilite a zero"),
      spacer(),

      // SECTION 2
      heading1("2. PERIMETRE DU PROJET"),
      heading2("2.1 Types de chariots concernes"),
      makeTable(
        ["Type", "Designation", "Largeur", "Technologie", "Statut"],
        [
          ["T1", "Chariot standard", "46 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["T2", "Chariot standard", "48 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["T3", "Chariot standard", "50 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["T4", "Chariot standard", "51 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["T5", "Chariot standard", "52 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["T6", "Chariot standard", "53 cm", "Badge RFID + Mat sol", "Couvert CDC"],
          ["P70", "Chariot lourd palette", "80 cm", "QR Code + Pistolet scanner", "Hors CDC"]
        ]
      ),
      spacer(),
      heading2("2.2 Zones d'installation"),
      bullet("Entree supermarche ligne Pristina (badge START)"),
      bullet("Sortie supermarche ligne Pristina (badge END)"),
      bullet("Total : 2 mats RFID a installer"),
      spacer(),

      // SECTION 3
      heading1("3. EXIGENCES FONCTIONNELLES"),
      heading2("3.1 Detection automatique"),
      makeTable(
        ["Ref", "Exigence"],
        [
          ["EF-01", "Le systeme doit detecter automatiquement le passage de tout chariot T1 a T6"],
          ["EF-02", "La detection doit s'effectuer sans aucune intervention de l'operateur"],
          ["EF-03", "Le taux de detection doit etre >= 95% sur l'ensemble des types de chariots"],
          ["EF-04", "Le badge doit etre identifie en moins de 200ms apres passage"]
        ]
      ),
      spacer(),
      heading2("3.2 Identification"),
      makeTable(
        ["Ref", "Exigence"],
        [
          ["EF-05", "Chaque badge RFID identifie un chariot specifique (ID unique)"],
          ["EF-06", "Le systeme distingue badge START et badge END pour chaque chariot"],
          ["EF-07", "En cas de non-detection : alerte visuelle sur tablette WS"]
        ]
      ),
      spacer(),
      heading2("3.3 Integration Oracle"),
      makeTable(
        ["Ref", "Exigence"],
        [
          ["EF-08", "Chaque detection declenche automatiquement un Move Transaction Oracle"],
          ["EF-09", "Synchronisation OFs Released depuis Oracle GLPROD vers MySQL (periodique)"],
          ["EF-10", "Seule action humaine autorisee : association job/chariot sur tablette WS"]
        ]
      ),
      spacer(),

      // SECTION 4
      heading1("4. SPECIFICATIONS TECHNIQUES — MAT RFID SOL"),
      heading2("4.1 Lecteur RFID"),
      makeTable(
        ["Parametre", "Specification"],
        [
          ["Modele", "Pepper C1 Standard"],
          ["Frequence", "HF 13.56 MHz"],
          ["Dimensions PCB", "75 mm x 50 mm"],
          ["Dimensions antenne interne", "70 mm x 45 mm"],
          ["Communication", "WiFi 802.11 b/g/n + MQTT natif"],
          ["Alimentation", "USB 5V"],
          ["Temperature fonctionnement", "-25 degC a +85 degC"],
          ["Quantite", "2 unites (1 entree + 1 sortie)"]
        ]
      ),
      spacer(),
      heading2("4.2 Zone de lecture RFID"),
      makeTable(
        ["Parametre", "Valeur"],
        [
          ["Largeur zone", "70 mm (antenne reelle C1)"],
          ["Tolerance badge (+/-)", "+/- 35 mm depuis centre"],
          ["Distance badge-antenne", "< 5 mm (garantie par clip)"],
          ["Reference position", "Centre lecteur = 0 mm"]
        ]
      ),
      spacer(),
      heading2("4.3 Dimensions mat RFID"),
      makeTable(
        ["Element", "Position", "Dimension"],
        [
          ["Largeur totale mat", "—", "920 mm"],
          ["Zone RFID centrale", "0 mm (centre)", "70 mm"],
          ["Rail interne gauche", "-265 mm", "25 x 15 mm"],
          ["Rail interne droit", "+265 mm", "25 x 15 mm"],
          ["Rail externe gauche (P70)", "-400 mm", "25 x 15 mm"],
          ["Rail externe droit (P70)", "+400 mm", "25 x 15 mm"],
          ["Longueur mat (sens deplacement)", "—", "600 mm minimum"],
          ["Hauteur totale mat", "—", "15 mm maximum"]
        ]
      ),
      spacer(),
      heading2("4.4 Structure tiroir RFID central"),
      makeTable(
        ["Couche", "Materiau", "Epaisseur"],
        [
          ["Couvercle protection", "Polycarbonate (transparent HF)", "8 mm"],
          ["Antenne C1", "Integree PCB", "2 mm"],
          ["Electronique Pepper C1", "PCB 75x50mm", "15 mm"],
          ["Base tiroir", "Acier inox", "2 mm"],
          ["TOTAL", "—", "~27 mm"]
        ]
      ),
      spacer(),
      para("Note : Le tiroir est AMOVIBLE sans outils (rails coulissants) pour maintenance.", { bold: true, color: TEAL }),
      spacer(),
      heading2("4.5 Rails de guidage"),
      makeTable(
        ["Parametre", "Valeur"],
        [
          ["Materiau", "Caoutchouc dur industriel ou HDPE"],
          ["Section", "25 mm x 15 mm"],
          ["Biseautage entree", "45 degres, longueur 50 mm"],
          ["Biseautage sortie", "45 degres, longueur 50 mm"],
          ["Fixation", "Vis inox M4 tous les 150 mm"],
          ["Couleur", "Jaune (signalisation)"]
        ]
      ),
      spacer(),

      // SECTION 5
      heading1("5. SPECIFICATIONS CLIP BADGE"),
      heading2("5.1 Principe de centrage"),
      para("Le badge n'est PAS positionne au centre geometrique du chariot. La position du clip est calculee de sorte que le badge soit toujours centre sur l'antenne (position 0 mm) lorsque la roue gauche du chariot est en contact avec le rail interne gauche."),
      spacer(),
      para("Formule : Distance clip = Distance rail gauche au centre", { bold: true }),
      bullet("Groupe A (T1-T6) : clip = 265 mm depuis centre roue gauche"),
      bullet("Groupe B (P70)   : clip = 400 mm depuis centre roue gauche"),
      spacer(),
      heading2("5.2 Position clip par groupe"),
      makeTable(
        ["Groupe", "Chariots", "Distance clip depuis roue gauche"],
        [
          ["Groupe A", "T1 a T6 (46-53 cm)", "265 mm"],
          ["Groupe B", "P70 (80 cm)", "400 mm"]
        ]
      ),
      spacer(),
      heading2("5.3 Position clip par type de chariot"),
      makeTable(
        ["Type", "Largeur", "Demi-track", "Offset clip / centre chariot"],
        [
          ["T1", "46 cm", "220 mm", "+45 mm (droite du centre)"],
          ["T2", "48 cm", "230 mm", "+35 mm (droite du centre)"],
          ["T3", "50 cm", "240 mm", "+25 mm (droite du centre)"],
          ["T4", "51 cm", "245 mm", "+20 mm (droite du centre)"],
          ["T5", "52 cm", "250 mm", "+15 mm (droite du centre)"],
          ["T6", "53 cm", "255 mm", "+10 mm (droite du centre)"]
        ]
      ),
      spacer(),
      heading2("5.4 Dimensions clip badge"),
      makeTable(
        ["Parametre", "Valeur"],
        [
          ["Plaque fixation chassis", "60 x 40 x 3 mm (acier inox)"],
          ["Tige de descente", "Longueur 30 mm, diametre 6 mm (inox)"],
          ["Fixation sur chariot", "2 x boulon M6"],
          ["Orientation badge", "Face RFID vers le bas"],
          ["Distance badge / antenne", "<= 5 mm (verifiee apres installation)"],
          ["Reglage", "Vis de reglage hauteur +/- 5 mm"]
        ]
      ),
      spacer(),

      // SECTION 6
      heading1("6. SPECIFICATIONS ELECTRIQUES"),
      heading2("6.1 Alimentation Pepper C1"),
      makeTable(
        ["Parametre", "Valeur"],
        [
          ["Tension", "5V DC (USB standard)"],
          ["Courant nominal", "150 mA (WiFi ON, RF ON)"],
          ["Source", "Prise 230V -> adaptateur USB 5V 1A"],
          ["Cable USB", "Longueur 2-3 m, gaine de protection"],
          ["Protection cable", "Gaine encastree dans mat ou passe-cable mural"]
        ]
      ),
      spacer(),
      heading2("6.2 Puissance totale installation"),
      makeTable(
        ["Element", "Puissance"],
        [
          ["Pepper C1 x 2", "2 x 0.75W = 1.5W"],
          ["Raspberry Pi (serveur proto)", "5W"],
          ["Switch WiFi (si necessaire)", "5W"],
          ["TOTAL", "< 15W"]
        ]
      ),
      spacer(),

      // SECTION 7
      heading1("7. SPECIFICATIONS RESEAU ET LOGICIEL"),
      heading2("7.1 Architecture reseau"),
      makeTable(
        ["Composant", "Protocole", "Port", "Note"],
        [
          ["Pepper C1 -> Serveur", "MQTT", "1883 (proto) / 8883 (prod)", "TLS en production"],
          ["Tablettes WS -> Serveur", "HTTP/HTTPS", "5000 (proto) / 443 (prod)", "Nginx en production"],
          ["Serveur -> Oracle", "Telnet MWA MSCA", "Standard", "Move Transaction auto"],
          ["Sync Oracle -> MySQL", "cx_Oracle", "Standard", "OFs Released"]
        ]
      ),
      spacer(),
      heading2("7.2 Stack logiciel"),
      makeTable(
        ["Couche", "Technologie"],
        [
          ["Backend", "Python Flask"],
          ["Broker MQTT", "Mosquitto"],
          ["Base de donnees", "MySQL — rfid_buc"],
          ["Frontend tablettes", "HTML/JS + Bootstrap 5"],
          ["Oracle interface", "python-oracledb / Telnet MWA"],
          ["Serveur prototype", "Raspberry Pi 4"],
          ["Serveur production", "VM Ubuntu Server 22.04 LTS"]
        ]
      ),
      spacer(),
      heading2("7.3 Topics MQTT"),
      makeTable(
        ["Topic", "Declencheur", "Donnees"],
        [
          ["rfid/pristina/start", "Badge START detecte", "{badge_id, chariot_id, timestamp}"],
          ["rfid/pristina/end", "Badge END detecte", "{badge_id, chariot_id, timestamp}"],
          ["rfid/pristina/alert", "Non-detection timeout", "{chariot_id, zone, timestamp}"]
        ]
      ),
      spacer(),

      // SECTION 8
      heading1("8. CONTRAINTES D'INSTALLATION"),
      heading2("8.1 Contraintes physiques"),
      makeTable(
        ["Contrainte", "Exigence"],
        [
          ["Hauteur mat", "<= 15 mm (surface du sol au dessus)"],
          ["Largeur couloir libre", ">= 920 mm (largeur mat)"],
          ["Longueur zone detection", ">= 600 mm (sens deplacement chariot)"],
          ["Fixation mat", "Vis au sol ou bandes adhesives double-face industrielles"],
          ["Cable alimentation", "Encastre ou gaine, hors passage pieton"]
        ]
      ),
      spacer(),
      heading2("8.2 Contraintes environnementales"),
      makeTable(
        ["Parametre", "Exigence"],
        [
          ["Temperature ambiante", "15-35 degC (usine GE Buc)"],
          ["Humidite", "< 80% non-condensant"],
          ["Poussiere", "Protection IP54 minimum"],
          ["Vibrations", "Resistant passages chariots"],
          ["Produits chimiques", "Resistance huiles legeres (HDPE / inox)"]
        ]
      ),
      spacer(),
      heading2("8.3 Contraintes WiFi"),
      makeTable(
        ["Parametre", "Exigence"],
        [
          ["Couverture", "Signal WiFi >= -70 dBm au niveau mat"],
          ["Bande", "2.4 GHz (Pepper C1)"],
          ["SSID", "Reseau usine GE Buc"],
          ["Authentification", "WPA2-Enterprise ou PSK"],
          ["Debit minimum", "1 Mbps (tres faible trafic)"]
        ]
      ),
      spacer(),

      // SECTION 9
      heading1("9. EXIGENCES SECURITE (EHS)"),
      makeTable(
        ["Exigence", "Solution", "Norme"],
        [
          ["Risque trebuchement", "Hauteur mat <= 15 mm + biseaux 45 degres", "GE EHS"],
          ["Risque glissade", "Revetement antiderapant R11", "EN 13893"],
          ["Visibilite", "Bandes jaune/noir sur bords", "EN ISO 11684"],
          ["Cables", "Aucun cable apparent au sol", "GE EHS"],
          ["Maintenance", "Tiroir amovible sans outils", "—"],
          ["Signalisation", "Pictogramme RFID au sol", "—"],
          ["Masse mat", "< 10 kg (manutention 1 personne)", "—"]
        ]
      ),
      spacer(),

      // SECTION 10
      heading1("10. PLAN DE VALIDATION ET TESTS"),
      heading2("10.1 Tests unitaires"),
      makeTable(
        ["Test", "Methode", "Critere succes"],
        [
          ["T-01 : Detection badge", "Passer badge a <= 5mm antenne", "Lecture en < 200ms"],
          ["T-02 : Distance clip", "Mesure badge/antenne", "< 5mm pour tous chariots"],
          ["T-03 : Centrage badge", "Passer chaque type chariot", "Badge dans zone +/- 35mm"],
          ["T-04 : WiFi MQTT", "Verifier message broker", "Message recu < 500ms"],
          ["T-05 : Oracle Move", "Declencher Move Transaction", "Transaction confirmee Oracle"]
        ]
      ),
      spacer(),
      heading2("10.2 Tests de charge"),
      makeTable(
        ["Test", "Methode", "Critere succes"],
        [
          ["T-06 : Taux detection", "100 passages par type", ">= 95% detections"],
          ["T-07 : Passage operateur", "Operateur marche sur mat", "Aucun inconfort / incident"],
          ["T-08 : Poids chariot charge", "Chariot plein passe sur mat", "Aucune deformation"],
          ["T-09 : Duree", "8h de fonctionnement continu", "Aucune interruption"]
        ]
      ),
      spacer(),
      heading2("10.3 Criteres de recette"),
      bullet("Taux detection >= 95% sur 100 passages de chaque type de chariot"),
      bullet("Zero incident EHS lors des tests operateur"),
      bullet("Latence MQTT < 1 seconde"),
      bullet("Move Transaction Oracle confirmee a 100% des detections"),
      spacer(),

      // SECTION 11
      heading1("11. PLANNING D'INSTALLATION"),
      makeTable(
        ["Phase", "Description", "Duree estimee"],
        [
          ["Phase 1", "Fabrication mat RFID (HDPE + rails)", "1-2 semaines"],
          ["Phase 2", "Fabrication clips badge x 49 chariots", "1 semaine"],
          ["Phase 3", "Installation mat + cablage", "1 jour"],
          ["Phase 4", "Installation clips sur chariots", "1-2 jours"],
          ["Phase 5", "Configuration Pepper C1 (WiFi, MQTT)", "0.5 jour"],
          ["Phase 6", "Tests unitaires", "1 jour"],
          ["Phase 7", "Tests de charge + recette", "2 jours"],
          ["Phase 8", "Formation operateurs", "0.5 jour"],
          ["TOTAL", "—", "~4-5 semaines"]
        ]
      ),
      spacer(),

      // SECTION 12
      heading1("12. RESPONSABILITES"),
      makeTable(
        ["Tache", "Responsable"],
        [
          ["Fabrication mat RFID", "Atelier GE Buc / Sous-traitant"],
          ["Fabrication clips badge", "Atelier GE Buc / Impression 3D"],
          ["Installation physique mat", "Maintenance GE Buc"],
          ["Configuration reseau WiFi", "IT GE Buc"],
          ["Ouverture ports MQTT/HTTPS", "IT GE Buc"],
          ["Acces Oracle GLTEST/GLPROD", "IT GE Buc / Oracle Admin"],
          ["Developpement logiciel", "Stagiaire Digitalisation"],
          ["Tests et validation", "Stagiaire + Responsable Ligne"],
          ["Formation operateurs", "Stagiaire + Chef d'equipe"]
        ]
      ),
      spacer(),

      // SECTION 13
      heading1("13. BESOINS IT — ACTIONS REQUISES"),
      makeTable(
        ["Besoin", "Detail", "Priorite"],
        [
          ["VM Ubuntu Server 22.04", "IP fixe reseau usine, 2 CPU, 4GB RAM, 50GB", "HAUTE"],
          ["Port 8883 ouvert", "MQTTS (production) reseau usine", "HAUTE"],
          ["Port 443 ouvert", "HTTPS dashboard tablettes", "HAUTE"],
          ["WiFi industriel", "Couverture SMK + Pristina, signal >= -70dBm", "HAUTE"],
          ["Acces Oracle GLTEST", "Username/password MWA MSCA, org BUC", "HAUTE"],
          ["Acces Oracle GLPROD", "Pour production finale", "MOYENNE"],
          ["Certificat SSL", "Pour HTTPS Nginx + MQTTS Mosquitto", "MOYENNE"],
          ["VPN GE", "Acces externe dashboard direction", "BASSE"]
        ]
      ),
      spacer(),

      // SECTION 14
      heading1("14. ANNEXES"),
      heading2("A. Schema architecture systeme"),
      makeTable(
        ["Composant", "Role", "Connexion"],
        [
          ["Badge RFID (sous chariot)", "Identification chariot", "Inductif HF < 5mm"],
          ["Pepper C1 Standard", "Lecture badge + emission MQTT", "WiFi -> Broker"],
          ["Mosquitto Broker", "Routage messages MQTT", "Port 1883/8883"],
          ["rfid_mqtt.py (Flask)", "Traitement evenements RFID", "MySQL"],
          ["MySQL rfid_buc", "Stockage missions/chariots/jobs", "cx_Oracle"],
          ["Tablette WS", "Association job/chariot operateur", "HTTPS port 443"],
          ["oracle_msca_move.py", "Move Transaction automatique", "Telnet MWA MSCA"],
          ["Oracle GLPROD", "ERP GE Healthcare", "Telnet MWA"]
        ]
      ),
      spacer(),
      heading2("B. Schema mat RFID — Vue de dessus (Dimensions en mm)"),
      makeTable(
        ["Element", "Position", "Largeur", "Role"],
        [
          ["Bord gauche", "-460 mm", "60 mm", "Marge securite"],
          ["Rail externe G (P70)", "-400 mm", "25 mm", "Guidage chariots 80cm"],
          ["Passage roue P70", "-400 a -265 mm", "135 mm", "Zone roues larges"],
          ["Rail interne G (T1-T6)", "-265 mm", "25 mm", "Guidage chariots 46-53cm"],
          ["Passage roue T1-T6", "-265 a -35 mm", "230 mm", "Zone roues standard"],
          ["ZONE RFID CENTRALE", "-35 a +35 mm", "70 mm", "DETECTION BADGE"],
          ["Passage roue T1-T6", "+35 a +265 mm", "230 mm", "Zone roues standard"],
          ["Rail interne D (T1-T6)", "+265 mm", "25 mm", "Guidage chariots 46-53cm"],
          ["Passage roue P70", "+265 a +400 mm", "135 mm", "Zone roues larges"],
          ["Rail externe D (P70)", "+400 mm", "25 mm", "Guidage chariots 80cm"],
          ["Bord droit", "+460 mm", "60 mm", "Marge securite"]
        ]
      ),
      spacer(),
      heading2("C. Documents de reference"),
      bullet("Pepper C1 User Manual V2.19 — Eccel Technology"),
      bullet("Oracle MSCA MWA Configuration Guide — GE Healthcare"),
      bullet("GE Healthcare EHS Floor Safety Standards"),
      bullet("Projet RFID — Architecture Technique V1.0"),
      spacer(),
      new Paragraph({
        children: [new TextRun({ text: "— FIN DU DOCUMENT —", bold: true, size: 22, color: BLUE, font: "Arial" })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 400 }
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\ADMIN\\Desktop\\rfid\\CDC_Installation_RFID_GE_Healthcare.docx", buffer);
  console.log("✅ Document cree avec succes !");
  console.log("📄 C:\\Users\\ADMIN\\Desktop\\rfid\\CDC_Installation_RFID_GE_Healthcare.docx");
}).catch(err => {
  console.error("❌ Erreur:", err.message);
});
