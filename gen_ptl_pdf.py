"""
Génération PDF — Étude de Cas Pick-to-Light
GE Healthcare Buc | Ligne Pristina
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import KeepTogether

# ── Couleurs GE HealthCare ────────────────────────────────────
GE_BLUE  = colors.HexColor("#003087")
GE_TEAL  = colors.HexColor("#00857C")
GE_LIGHT = colors.HexColor("#E8F4F3")
GE_GRAY  = colors.HexColor("#F5F5F5")
GE_DARK  = colors.HexColor("#333333")
WHITE    = colors.white

# ── Styles ────────────────────────────────────────────────────
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    "Title", fontSize=26, textColor=WHITE,
    fontName="Helvetica-Bold", alignment=TA_CENTER,
    spaceAfter=6, leading=32
)
style_subtitle = ParagraphStyle(
    "Subtitle", fontSize=13, textColor=GE_TEAL,
    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4
)
style_section = ParagraphStyle(
    "Section", fontSize=14, textColor=WHITE,
    fontName="Helvetica-Bold", alignment=TA_LEFT,
    spaceBefore=14, spaceAfter=6, leftIndent=0
)
style_body = ParagraphStyle(
    "Body", fontSize=10, textColor=GE_DARK,
    fontName="Helvetica", alignment=TA_JUSTIFY,
    spaceAfter=5, leading=15
)
style_bullet = ParagraphStyle(
    "Bullet", fontSize=10, textColor=GE_DARK,
    fontName="Helvetica", leftIndent=16,
    spaceAfter=3, leading=14, bulletIndent=6
)
style_step = ParagraphStyle(
    "Step", fontSize=10, textColor=GE_DARK,
    fontName="Helvetica", leftIndent=20,
    spaceAfter=4, leading=14
)
style_caption = ParagraphStyle(
    "Caption", fontSize=9, textColor=colors.HexColor("#666666"),
    fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=8
)
style_kpi = ParagraphStyle(
    "KPI", fontSize=22, textColor=GE_TEAL,
    fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2
)
style_kpi_label = ParagraphStyle(
    "KPILabel", fontSize=9, textColor=GE_DARK,
    fontName="Helvetica", alignment=TA_CENTER, spaceAfter=0
)


def section_header(text):
    """Bloc titre de section fond bleu GE."""
    tbl = Table([[Paragraph(text, style_section)]], colWidths=[17.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GE_BLUE),
        ("ROUNDEDCORNERS", [4,4,4,4]),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
    ]))
    return tbl


def kpi_row(items):
    """Ligne de KPIs en boîtes teal."""
    cells = []
    for val, label in items:
        cell = [Paragraph(val, style_kpi), Paragraph(label, style_kpi_label)]
        cells.append(cell)
    w = 17.5 / len(items)
    tbl = Table([cells], colWidths=[w*cm]*len(items))
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GE_LIGHT),
        ("BOX", (0,0), (-1,-1), 1, GE_TEAL),
        ("INNERGRID", (0,0), (-1,-1), 0.5, GE_TEAL),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    return tbl


def data_table(headers, rows, col_widths=None):
    """Tableau de données stylé GE."""
    data = [[Paragraph(h, ParagraphStyle("TH", fontSize=9,
             fontName="Helvetica-Bold", textColor=WHITE,
             alignment=TA_CENTER)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), ParagraphStyle("TD", fontSize=9,
                     fontName="Helvetica", textColor=GE_DARK,
                     alignment=TA_LEFT)) for c in row])

    if col_widths is None:
        col_widths = [17.5/len(headers)*cm] * len(headers)

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GE_TEAL),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GE_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return tbl


def flux_table():
    """Tableau flux de fonctionnement avec étapes numérotées."""
    steps = [
        ("1", "Scan badge RFID", "Water Spider scanne le badge RFID du chariot (Pepper C1)"),
        ("2", "Identification mission", "Flask app identifie la mission et les items a prelever depuis MySQL"),
        ("3", "Commande MQTT", "Flask publie les commandes vers les ESP32 des zones concernees"),
        ("4", "Activation PTL", "LEDs vertes s'allument + afficheurs TM1637 affichent les quantites"),
        ("5", "Prelevement", "Water Spider preleve la piece indiquee dans la bonne quantite"),
        ("6", "Confirmation", "WS appuie sur le bouton → LED s'eteint → MQTT confirm publie"),
        ("7", "Mise a jour base", "Flask reçoit la confirmation → MySQL mis a jour → mission TERMINEE"),
    ]
    data = [[
        Paragraph("#", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Etape", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Description", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
    ]]
    for num, title, desc in steps:
        data.append([
            Paragraph(num, ParagraphStyle("N", fontSize=11, fontName="Helvetica-Bold", textColor=GE_TEAL, alignment=TA_CENTER)),
            Paragraph(title, ParagraphStyle("T", fontSize=9, fontName="Helvetica-Bold", textColor=GE_DARK)),
            Paragraph(desc, ParagraphStyle("D", fontSize=9, fontName="Helvetica", textColor=GE_DARK)),
        ])
    tbl = Table(data, colWidths=[1.2*cm, 4.5*cm, 11.8*cm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GE_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GE_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return tbl


# ══════════════════════════════════════════════════════════════
# CONSTRUCTION DU DOCUMENT
# ══════════════════════════════════════════════════════════════
def build():
    output = r"C:\Users\ADMIN\Desktop\rfid\Etude_Cas_Pick_to_Light.pdf"
    doc = SimpleDocTemplate(
        output, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # ── PAGE DE COUVERTURE ────────────────────────────────────
    cover = Table(
        [[Paragraph("Étude de Cas", style_title)],
         [Paragraph("Système Pick-to-Light IoT", style_title)],
         [Spacer(1, 0.3*cm)],
         [Paragraph("GE Healthcare Buc  |  Ligne Pristina  |  Supermarché Industriel", style_subtitle)],
         [Spacer(1, 0.5*cm)],
         [HRFlowable(width="100%", thickness=2, color=GE_TEAL)],
         [Spacer(1, 0.5*cm)],
         [Paragraph("Digitalisation du processus de picking par technologie IoT", style_body)],
        ],
        colWidths=[17.5*cm]
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,3), GE_BLUE),
        ("TOPPADDING", (0,0), (-1,3), 12),
        ("BOTTOMPADDING", (0,0), (-1,3), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 16),
    ]))
    story.append(cover)
    story.append(Spacer(1, 0.4*cm))

    # KPIs titre
    story.append(kpi_row([
        ("-60%", "Réduction temps\nde picking"),
        ("-90%", "Réduction erreurs\nde picking"),
        ("~6€", "Coût par bac\n(vs 200€ industriel)"),
        ("96%", "Économie vs solutions\ncommerciales"),
    ]))
    story.append(Spacer(1, 0.6*cm))

    # ── SECTION 1 — CONTEXTE ─────────────────────────────────
    story.append(section_header("1.  Contexte et Problématique"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "GE Healthcare Buc fabrique des équipements médicaux d'imagerie (Senographe Pristina) "
        "sur la ligne Pristina. Le supermarché interne stocke environ 200 références de pièces "
        "détachées et consommables. Les Water Spiders (opérateurs logistiques) ont pour mission "
        "de préparer les chariots de pièces destinés aux postes de montage.",
        style_body
    ))
    story.append(Spacer(1, 0.2*cm))

    prob_data = [
        ["Problème", "Impact terrain"],
        ["Recherche visuelle des pièces dans les rayons", "Perte de 2-5 min par préparation"],
        ["Absence de guidage vers les bons emplacements", "Erreurs de picking fréquentes"],
        ["Quantités à prélever sur papier ou mémoire", "Risque de sous/sur-prélèvement"],
        ["Aucune traçabilité des prélèvements", "Impossibilité d'audit et de contrôle"],
        ["Stress opérateur lors des périodes de pointe", "Turnover et fatigue accrus"],
    ]
    story.append(data_table(
        ["Problème", "Impact terrain"],
        [r[1:] for r in prob_data[1:]],
        col_widths=[9*cm, 8.5*cm]
    ))
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 2 — SOLUTION ─────────────────────────────────
    story.append(section_header("2.  Solution Pick-to-Light IoT"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "La solution proposée repose sur un système Pick-to-Light (PTL) entièrement développé "
        "en interne, basé sur des composants IoT grand public et intégré à l'infrastructure "
        "RFID et Oracle déjà en place à GE Healthcare Buc.",
        style_body
    ))
    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph("<b>Composants principaux :</b>", style_body))
    for item in [
        "ESP32 DevKit V1 Type-C — microcontrôleur WiFi/MQTT — 1 unité par zone de 7 bacs",
        "WS2812B LED RGB — 1 LED par bac — vert = prendre ici, éteinte = terminé",
        "TM1637 Afficheur 7 segments 4 chiffres — affiche la quantité à prélever",
        "Bouton poussoir 12mm étanche RUNCCI-YUN — confirmation du pick par l'opérateur",
        "Broker MQTT Mosquitto — déjà installé sur le Raspberry Pi du projet RFID",
        "Flask/MySQL — déjà en place, aucune infrastructure supplémentaire requise",
    ]:
        story.append(Paragraph(f"• {item}", style_bullet))
    story.append(Spacer(1, 0.35*cm))

    story.append(Paragraph("<b>Flux de fonctionnement — 7 étapes :</b>", style_body))
    story.append(Spacer(1, 0.15*cm))
    story.append(flux_table())
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 3 — ARCHITECTURE HARDWARE ────────────────────
    story.append(section_header("3.  Architecture Hardware par Zone (7 bacs)"))
    story.append(Spacer(1, 0.3*cm))

    hw_rows = [
        ["ESP32 DevKit V1 Type-C", "1", "Contrôleur WiFi/MQTT central", "GPIO21-27, GPIO5, GPIO4..."],
        ["TM1637 4 digits 0.56\"", "7", "Affichage quantité à prendre", "CLK + DIO (2 GPIO par module)"],
        ["WS2812B LED RGB", "7", "Indication visuelle bac actif", "Data chaîné — 1 GPIO total"],
        ["Bouton 12mm étanche", "7", "Confirmation pick opérateur", "1 GPIO par bouton + GND"],
        ["Résistance 330 Ohm", "1", "Protection signal WS2812B", "Série sur data GPIO5"],
        ["Résistance 10k Ohm", "1", "Pull-up GPIO34 (bouton 7)", "GPIO34 vers 3.3V"],
        ["Condensateur 100µF", "1", "Protection alimentation LEDs", "Entre 5V et GND"],
        ["Alimentation USB 5V/1A", "1", "Alimentation zone complète", "Via port USB-C ESP32"],
    ]
    story.append(data_table(
        ["Composant", "Qté", "Rôle", "Connexion"],
        hw_rows,
        col_widths=[5*cm, 1.5*cm, 6*cm, 5*cm]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Bilan GPIO ESP32 pour 7 bacs :</b>", style_body))
    gpio_rows = [
        ["7 × TM1637 (CLK + DIO)", "14 GPIO", "GPIO21,22 / 18,19 / 16,17 / 14,13 / 26,25 / 27,23 / 5,?"],
        ["7 × WS2812B chaîne", "1 GPIO", "GPIO5 (data unique pour toute la chaîne)"],
        ["7 × Bouton", "7 GPIO", "GPIO4 / 15 / 2 / 33 / 32 / 23 / 34"],
        ["TOTAL utilisé", "22 GPIO", "Sur 34 GPIO disponibles (64% utilisé)"],
    ]
    story.append(data_table(
        ["Périphérique", "GPIO utilisés", "Pins ESP32"],
        gpio_rows,
        col_widths=[5*cm, 3*cm, 9.5*cm]
    ))
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 4 — INTÉGRATION RFID ─────────────────────────
    story.append(section_header("4.  Intégration avec le Système RFID Existant"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Le système Pick-to-Light s'intègre nativement dans l'infrastructure RFID déjà déployée "
        "à GE Healthcare Buc. Aucun serveur supplémentaire, aucun nouveau broker — tout repose "
        "sur la même pile technologique.",
        style_body
    ))
    story.append(Spacer(1, 0.25*cm))

    integ_rows = [
        ["Broker MQTT", "Mosquitto (Raspberry Pi)", "Déjà installé et configuré", "✓ Réutilisé"],
        ["Serveur applicatif", "Flask Python", "Déjà en place", "✓ Étendu"],
        ["Base de données", "MySQL rfid_buc", "Tables existantes", "✓ Étendu"],
        ["Sync Oracle", "sync_oracle.py", "OFs Released GLPROD", "✓ Réutilisé"],
        ["Réseau", "WiFi usine GE", "Déjà disponible", "✓ Réutilisé"],
    ]
    story.append(data_table(
        ["Composant", "Technologie", "État actuel", "Action"],
        integ_rows,
        col_widths=[4*cm, 4.5*cm, 5.5*cm, 3.5*cm]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Topics MQTT Pick-to-Light :</b>", style_body))
    mqtt_rows = [
        ["Activation bac", "rfid/zone-A/bac-1", '{"qty": 3, "color": "green"}', "Flask → ESP32"],
        ["Confirmation pick", "rfid/zone-A/bac-1/confirm", '{"picked": true}', "ESP32 → Flask"],
        ["Tout éteindre zone", "rfid/zone-A/reset", '{"reset": true}', "Flask → ESP32"],
    ]
    story.append(data_table(
        ["Action", "Topic MQTT", "Payload JSON", "Direction"],
        mqtt_rows,
        col_widths=[3.5*cm, 5*cm, 6*cm, 3*cm]
    ))
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 5 — BUDGET ET ROI ─────────────────────────────
    story.append(section_header("5.  Budget et Retour sur Investissement"))
    story.append(Spacer(1, 0.3*cm))

    budget_rows = [
        ["ESP32 DevKit V1 Type-C", "1", "10.00 €", "10.00 €"],
        ["TM1637 Afficheur 7 segments", "7", "1.00 €", "7.00 €"],
        ["WS2812B LED RGB module", "7", "0.40 €", "2.80 €"],
        ["Boutons RUNCCI-YUN 12mm (pack 5)", "2", "7.99 €", "15.98 €"],
        ["Résistances + condensateur", "—", "—", "2.00 €"],
        ["Fils, connecteurs, PCB proto", "—", "—", "3.00 €"],
        ["TOTAL par zone (7 bacs)", "", "", "~41 €"],
    ]
    story.append(data_table(
        ["Composant", "Qté", "Prix unitaire", "Total"],
        budget_rows,
        col_widths=[8*cm, 2.5*cm, 3.5*cm, 3.5*cm]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Comparaison avec solutions PTL industrielles :</b>", style_body))
    comp_rows = [
        ["Solution IoT proposée", "~6 €/bac", "41 €/zone", "Développement interne, IoT"],
        ["PTL industriel standard", "150-300 €/bac", "1 050-2 100 €/zone", "Systèmes Zetes, SSI Schaefer"],
        ["Économie réalisée", "-96 à -98%", "-1 000 à -2 060 €/zone", "✓ ROI immédiat"],
    ]
    story.append(data_table(
        ["Solution", "Coût/bac", "Coût/zone (7 bacs)", "Remarque"],
        comp_rows,
        col_widths=[5*cm, 3*cm, 4.5*cm, 5*cm]
    ))
    story.append(Spacer(1, 0.4*cm))

    story.append(kpi_row([
        ("~6€", "Coût / bac"),
        ("-60%", "Temps de picking"),
        ("-90%", "Erreurs picking"),
        ("< 1 mois", "ROI"),
    ]))
    story.append(Spacer(1, 0.5*cm))

    # ── SECTION 6 — PLAN D'IMPLÉMENTATION ────────────────────
    story.append(section_header("6.  Plan d'Implémentation"))
    story.append(Spacer(1, 0.3*cm))

    plan_rows = [
        ["Phase 1", "Semaines 1-2", "• Commande matériel (Amazon/AliExpress)\n• Montage prototype 1 zone (7 bacs)\n• Développement firmware ESP32\n• Tests unitaires sur banc"],
        ["Phase 2", "Semaine 3", "• Déploiement test en supermarché\n• Validation avec Water Spiders réels\n• Ajustements firmware et application Flask\n• Mesure des gains de performance"],
        ["Phase 3", "Semaine 4", "• Déploiement toutes zones supermarché\n• Intégration complète RFID + PTL\n• Tests end-to-end complets\n• Documentation technique"],
        ["Phase 4", "Mois 2", "• Formation des opérateurs WS\n• Mise en production officielle\n• Monitoring et maintenance\n• Rapport de performance"],
    ]

    tbl_data = [[
        Paragraph("Phase", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Calendrier", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("Activités", ParagraphStyle("TH", fontSize=9, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
    ]]
    phase_colors = [GE_TEAL, colors.HexColor("#006B63"), GE_BLUE, colors.HexColor("#002266")]
    for i, (ph, cal, act) in enumerate(plan_rows):
        tbl_data.append([
            Paragraph(ph, ParagraphStyle("P", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
            Paragraph(cal, ParagraphStyle("C", fontSize=9, fontName="Helvetica", textColor=GE_DARK)),
            Paragraph(act.replace("\n", "<br/>"), ParagraphStyle("A", fontSize=9, fontName="Helvetica", textColor=GE_DARK, leading=14)),
        ])

    plan_tbl = Table(tbl_data, colWidths=[3*cm, 3.5*cm, 11*cm], repeatRows=1)
    plan_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GE_BLUE),
        ("BACKGROUND", (0,1), (0,1), GE_TEAL),
        ("BACKGROUND", (0,2), (0,2), colors.HexColor("#006B63")),
        ("BACKGROUND", (0,3), (0,3), GE_BLUE),
        ("BACKGROUND", (0,4), (0,4), colors.HexColor("#002266")),
        ("ROWBACKGROUNDS", (1,1), (-1,-1), [WHITE, GE_GRAY]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("FONTCOLOR", (0,1), (0,-1), WHITE),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(plan_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ── FOOTER ────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1.5, color=GE_TEAL))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "GE Healthcare Buc — Projet RFID & Pick-to-Light | Ligne Pristina | Document confidentiel interne",
        style_caption
    ))

    doc.build(story)
    print(f"[OK] PDF généré : {output}")


build()
