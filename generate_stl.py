"""
Generation STL - Support Lateral RFID
GE Healthcare Buc - Ligne Pristina
Pepper+Fuchs C1 sur poteau 25mm fixe
"""

from build123d import *
import os, sys
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

OUTPUT = r"C:\Users\ADMIN\Desktop\rfid\STL"
os.makedirs(OUTPUT, exist_ok=True)

print("=" * 55)
print("  Génération STL — Support RFID Latéral")
print("  GE Healthcare Buc — Pristina")
print("=" * 55)

# ================================================================
# PIECE 1 : COLLIER DE FIXATION
# Serre sur poteau vertical Ø25mm
# Corps : 64mm(X) × 35mm(Y) × 65mm(Z)
# Alésage Ø25.2mm (tube + 0.2mm jeu) — axe Z
# Fente 3mm (de l'alésage vers face avant) — permet serrage
# 2x trous M6 (axe X) pour vis de serrage
# ================================================================
print("\n[1/3] Collier de fixation...")

with BuildPart() as collier:
    # Corps principal
    Box(64, 35, 65)

    # Alésage tube Ø25.2mm (axe Z = vertical)
    with Locations((0, 0, 0)):
        Cylinder(25.2 / 2, 65, mode=Mode.SUBTRACT)

    # Fente de serrage : 3mm large, de l'alésage vers face avant (Y+)
    # Coupe de y=12.6 (bord alésage) à y=17.5 (face avant)
    with Locations((0, 14.55, 0)):
        Box(3.2, 5.5, 65, mode=Mode.SUBTRACT)

    # 2x trous M6 (axe X) traversants, à Z=+20 et Z=-20
    with Locations((0, 14.55, 20), (0, 14.55, -20)):
        Cylinder(3.1, 68, rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    # Logements écrous M6 hexagonaux (SW=10mm) côté gauche (X-)
    # Pour coincer l'écrou : hexagone prof 5mm
    for z_pos in [20, -20]:
        with Locations((-28, 14.55, z_pos)):
            # Hexagone inscrit dans cercle R=6mm (SW=10mm, AF=5.77mm)
            with BuildSketch(Plane.YZ.offset(-28)):
                RegularPolygon(radius=6.0, side_count=6)
            extrude(amount=5, mode=Mode.SUBTRACT)

    # Face de raccordement bras (côté +X droite) : chanfrein léger pour guidage
    # (pas de feature spéciale — la face plate suffit pour la liaison avec bras)

export_stl(collier.part, os.path.join(OUTPUT, "01_collier_fixation.stl"))
print("   [OK] 01_collier_fixation.stl")

# ================================================================
# PIECE 2 : BRAS COULISSANT RÉGLABLE
# Relie collier ①  au support lecteur ③
# Corps : 120mm(X) × 18mm(Y) × 30mm(Z)
# Rainure centrale : 80mm × 8mm (coulissement axe X)
# 5x trous Ø6.5mm espacés 15mm (positions indexées)
# ================================================================
print("\n[2/3] Bras coulissant réglable...")

with BuildPart() as bras:
    # Corps principal
    Box(120, 18, 30)

    # Rainure centrale de coulissement (slot axe X)
    # 80mm de long, 8mm de large, traversante (axe Z)
    with Locations((0, 0, 0)):
        Box(80, 18, 8.5, mode=Mode.SUBTRACT)  # slot through Y

    # 5 trous de réglage Ø6.5mm, axe Z, espacement 15mm
    positions = [(-30, 0, 0), (-15, 0, 0), (0, 0, 0), (15, 0, 0), (30, 0, 0)]
    with Locations(*positions):
        Cylinder(3.25, 30, mode=Mode.SUBTRACT)

    # Trou de fixation côté collier (X-) : trou oblong M6 pour liaison
    with Locations((-55, 0, 0)):
        Cylinder(3.25, 30, mode=Mode.SUBTRACT)

    # Trou de fixation côté support lecteur (X+) : trou oblong M6
    with Locations((55, 0, 0)):
        Cylinder(3.25, 30, mode=Mode.SUBTRACT)

export_stl(bras.part, os.path.join(OUTPUT, "02_bras_coulissant.stl"))
print("   [OK] 02_bras_coulissant.stl")

# ================================================================
# PIECE 3 : SUPPORT LECTEUR PEPPER+FUCHS C1
# Cadre tenant le lecteur avec fenêtre antenne
# Corps extérieur : 90mm(X) × 20mm(Y) × 120mm(Z)
# Fenêtre antenne : 60mm(X) × 100mm(Z) — axe Y traversant
# 4x trous oblongs M4 (réglage fin ±5mm)
# ================================================================
print("\n[3/3] Support lecteur Pepper C1...")

with BuildPart() as support:
    # Cadre extérieur
    Box(90, 20, 120)

    # Fenêtre antenne centrale (Pepper C1 = 70x45mm antenne + jeu)
    with Locations((0, 0, 0)):
        Box(60, 20, 100, mode=Mode.SUBTRACT)

    # 4x trous oblongs M4 (fixation lecteur, réglage fin)
    # Positions aux 4 coins du cadre
    corner_positions = [
        (35,  0,  55),   # haut droite
        (-35, 0,  55),   # haut gauche
        (35,  0, -55),   # bas droite
        (-35, 0, -55),   # bas gauche
    ]
    # Trous oblongs = slot vertical de 8mm long × 4.5mm large
    for pos in corner_positions:
        with Locations(pos):
            # Trou oblong = 2 cercles + rectangle
            Box(4.5, 20, 8, mode=Mode.SUBTRACT)
            with Locations((0, 0, 2)):
                Cylinder(2.25, 20, mode=Mode.SUBTRACT)
            with Locations((0, 0, -2)):
                Cylinder(2.25, 20, mode=Mode.SUBTRACT)

    # Dos plat avec 2 trous M6 pour fixation sur bras coulissant ②
    with Locations((0, -8, 20), (0, -8, -20)):
        Cylinder(3.1, 4, mode=Mode.SUBTRACT)  # trous borgnes M6 côté dos

export_stl(support.part, os.path.join(OUTPUT, "03_support_lecteur.stl"))
print("   [OK] 03_support_lecteur.stl")

# ================================================================
# RÉSUMÉ
# ================================================================
print("\n" + "=" * 55)
print("  Tous les STL generes !")
print(f"  Dossier : {OUTPUT}")
print("=" * 55)
print()
print("  Pieces a imprimer (Bambu Lab PETG) :")
print("  01_collier_fixation.stl   - 1 unite")
print("  02_bras_coulissant.stl    - 1 unite")
print("  03_support_lecteur.stl    - 1 unite")
print()
print("  Reglages Bambu Studio :")
print("  - Filament : PETG")
print("  - Infill   : 40% Gyroid")
print("  - Walls    : 4")
print("  - Support  : Auto")
