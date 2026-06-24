import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

fig = plt.figure(figsize=(20, 24), facecolor='#1a1a2e')

# ─────────────────────────────────────────────
# VUE DE DESSUS (Plan View) - TOP
# ─────────────────────────────────────────────
ax1 = fig.add_subplot(3, 1, 1)
ax1.set_facecolor('#1a1a2e')
ax1.set_xlim(-500, 500)
ax1.set_ylim(-50, 350)
ax1.set_aspect('equal')
ax1.axis('off')
ax1.set_title('VUE DE DESSUS — Mat RFID Sol (échelle 1:5)',
              color='white', fontsize=14, fontweight='bold', pad=15)

# MAT HDPE principal (gris foncé)
mat_main = mpatches.FancyBboxPatch((-460, 0), 920, 300,
    boxstyle="round,pad=5",
    linewidth=2, edgecolor='#888888', facecolor='#2d2d3d')
ax1.add_patch(mat_main)

# Extension gauche P70 (légèrement différente)
ext_left = mpatches.Rectangle((-460, 0), 60, 300,
    linewidth=1, edgecolor='#666666', facecolor='#252535', zorder=2)
ax1.add_patch(ext_left)

# Extension droite P70
ext_right = mpatches.Rectangle((400, 0), 60, 300,
    linewidth=1, edgecolor='#666666', facecolor='#252535', zorder=2)
ax1.add_patch(ext_right)

# Passages roues (zones légèrement plus claires)
for x, w in [(-400, 135), (265, 135)]:
    zone = mpatches.Rectangle((x, 0), w, 300,
        linewidth=0, facecolor='#35354a', zorder=2)
    ax1.add_patch(zone)

# ZONE RFID CENTRALE (vert lumineux)
rfid_zone = mpatches.FancyBboxPatch((-35, 75), 70, 150,
    boxstyle="round,pad=3",
    linewidth=2, edgecolor='#00ff88', facecolor='#003d1f', zorder=5)
ax1.add_patch(rfid_zone)

# Effet glow RFID
for alpha, size in [(0.05, 120), (0.08, 90), (0.12, 70)]:
    glow = plt.Circle((0, 150), size, color='#00ff88', alpha=alpha, zorder=4)
    ax1.add_patch(glow)

# Symbole RFID
ax1.text(0, 150, '(((·)))', color='#00ff88', fontsize=16,
         ha='center', va='center', fontweight='bold', zorder=6,
         fontfamily='monospace')
ax1.text(0, 120, 'RFID 70mm', color='#00ff88', fontsize=8,
         ha='center', va='center', zorder=6)

# RAILS INTERNES (jaune, ±265mm)
for x in [-265, 240]:
    rail = mpatches.Rectangle((x, 0), 25, 300,
        linewidth=1, edgecolor='#ffcc00', facecolor='#ffaa00', zorder=7)
    ax1.add_patch(rail)
    # Biseaux
    tri_in = plt.Polygon([[x, 0], [x+25, 0], [x+25, 50]],
                          color='#cc8800', zorder=8)
    tri_out = plt.Polygon([[x, 300], [x+25, 300], [x+25, 250]],
                           color='#cc8800', zorder=8)
    ax1.add_patch(tri_in)
    ax1.add_patch(tri_out)

# RAILS EXTERNES P70 (jaune foncé, ±400mm)
for x in [-400, 375]:
    rail = mpatches.Rectangle((x, 0), 25, 300,
        linewidth=1, edgecolor='#ff8800', facecolor='#cc6600', zorder=7)
    ax1.add_patch(rail)

# BORDS CHANFREINÉS (jaune/noir sécurité)
for start_x in [-460, 400]:
    for i in range(12):
        y_pos = i * 25
        color = '#ffcc00' if i % 2 == 0 else '#1a1a1a'
        stripe = mpatches.Rectangle((start_x, y_pos), 60, 25,
            facecolor=color, linewidth=0, zorder=3)
        ax1.add_patch(stripe)

# CHARIOT T3 (50cm) - exemple - BLEU
cart_width = 265
cart_left = -cart_width//2
cart_right = cart_left + cart_width
chariot = mpatches.FancyBboxPatch((cart_left, 160), cart_width-10, 100,
    boxstyle="round,pad=3",
    linewidth=2, edgecolor='#4488ff', facecolor='#1a3366', alpha=0.85, zorder=9)
ax1.add_patch(chariot)

# Label chariot
ax1.text(0, 210, 'CHARIOT T3 (50cm)', color='#88aaff', fontsize=9,
         ha='center', va='center', fontweight='bold', zorder=10)

# Roues du chariot (cercles rouges)
wheel_y = [170, 250]
wheel_x_left = cart_left + 25
wheel_x_right = cart_right - 35
for wy in wheel_y:
    for wx in [wheel_x_left, wheel_x_right]:
        w = plt.Circle((wx, wy), 12, color='#ff4444', zorder=11, linewidth=1.5,
                       edgecolor='#cc0000')
        ax1.add_patch(w)

# BADGE (point vert sur chariot)
badge = plt.Circle((25, 210), 8, color='#00ff88', zorder=12,
                   linewidth=2, edgecolor='white')
ax1.add_patch(badge)
ax1.text(25, 210, 'B', color='white', fontsize=7, ha='center',
         va='center', fontweight='bold', zorder=13)

# Flèche direction déplacement
ax1.annotate('', xy=(0, 350), xytext=(0, 310),
    arrowprops=dict(arrowstyle='->', color='white', lw=2))
ax1.text(0, 345, 'Sens déplacement', color='white', fontsize=8,
         ha='center', va='bottom')

# COTATIONS
cote_y = -30
ax1.annotate('', xy=(-460, cote_y), xytext=(460, cote_y),
    arrowprops=dict(arrowstyle='<->', color='#aaaaaa', lw=1.5))
ax1.text(0, cote_y-10, '920 mm', color='#aaaaaa', ha='center', va='top', fontsize=9)

# Cote rails internes
ax1.annotate('', xy=(-265, -15), xytext=(265, -15),
    arrowprops=dict(arrowstyle='<->', color='#ffaa00', lw=1.5))
ax1.text(0, -25, '530 mm (channel T1-T6)', color='#ffaa00', ha='center', va='top', fontsize=8)

# Légende vue dessus
legend_elements = [
    mpatches.Patch(color='#2d2d3d', label='Mat HDPE (PETG noir)'),
    mpatches.Patch(color='#ffaa00', label='Rails internes T1-T6 (TPU jaune ±265mm)'),
    mpatches.Patch(color='#cc6600', label='Rails externes P70 (TPU orange ±400mm)'),
    mpatches.Patch(color='#003d1f', label='Zone RFID 70mm (Pepper C1)'),
    mpatches.Patch(color='#1a3366', label='Chariot T3 50cm (exemple)'),
    mpatches.Patch(color='#ff4444', label='Roues ø130mm'),
    mpatches.Patch(color='#00ff88', label='Badge RFID (clip à 265mm roue G)'),
]
ax1.legend(handles=legend_elements, loc='upper right',
           facecolor='#2d2d3d', edgecolor='#555555',
           labelcolor='white', fontsize=8)

# ─────────────────────────────────────────────
# VUE COUPE TRANSVERSALE - MIDDLE
# ─────────────────────────────────────────────
ax2 = fig.add_subplot(3, 1, 2)
ax2.set_facecolor('#1a1a2e')
ax2.set_xlim(-500, 500)
ax2.set_ylim(-20, 120)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.set_title('COUPE TRANSVERSALE — Couches et Dimensions',
              color='white', fontsize=14, fontweight='bold', pad=15)

# Sol (béton)
sol = mpatches.Rectangle((-470, -15), 940, 15,
    facecolor='#444455', edgecolor='#666677', linewidth=1, zorder=1)
ax2.add_patch(sol)
ax2.text(0, -8, 'SOL BÉTON', color='#aaaaaa', ha='center', va='center', fontsize=8)

# MAT PETG principal
mat = mpatches.Rectangle((-460, 0), 920, 15,
    facecolor='#2d2d3d', edgecolor='#888888', linewidth=2, zorder=2)
ax2.add_patch(mat)

# Zone tiroir RFID central
tiroir = mpatches.Rectangle((-75, 0), 150, 27,
    facecolor='#1a3344', edgecolor='#4488aa', linewidth=2, zorder=3)
ax2.add_patch(tiroir)

# Plaque polycarbonate
poly = mpatches.Rectangle((-75, 19), 150, 8,
    facecolor='#aaddff', edgecolor='#88bbdd', linewidth=1, alpha=0.7, zorder=4)
ax2.add_patch(poly)
ax2.text(0, 23, 'Polycarbonate 8mm', color='#1a1a2e', ha='center', va='center',
         fontsize=7, fontweight='bold', zorder=5)

# Antenne C1
ant = mpatches.Rectangle((-35, 17), 70, 2,
    facecolor='#00ff88', edgecolor='#00cc66', linewidth=1, zorder=5)
ax2.add_patch(ant)
ax2.text(0, 18, '── Antenne 70×45mm ──', color='#003311', ha='center', va='center',
         fontsize=6, fontweight='bold', zorder=6)

# Pepper C1 PCB
pcb = mpatches.FancyBboxPatch((-37, 2), 75, 15,
    boxstyle="round,pad=1",
    facecolor='#1a3300', edgecolor='#00aa44', linewidth=1.5, zorder=4)
ax2.add_patch(pcb)
ax2.text(0, 9, 'Pepper C1 PCB\n75×50mm', color='#00ff88', ha='center',
         va='center', fontsize=7, zorder=5)

# RAILS INTERNES TPU (±265mm)
for rx in [-278, 253]:
    rail = mpatches.Rectangle((rx, 0), 25, 15,
        facecolor='#ffaa00', edgecolor='#ffcc00', linewidth=2, zorder=3)
    ax2.add_patch(rail)

# RAILS EXTERNES TPU (±400mm)
for rx in [-413, 388]:
    rail_ext = mpatches.Rectangle((rx, 0), 25, 15,
        facecolor='#cc6600', edgecolor='#ff8800', linewidth=2, zorder=3)
    ax2.add_patch(rail_ext)

# Bords chanfreinés (jaune/noir)
for bx, bw in [(-460, 60), (400, 60)]:
    for i in range(5):
        color = '#ffcc00' if i % 2 == 0 else '#333333'
        s = mpatches.Rectangle((bx + i*12, 0), 12, 15,
            facecolor=color, linewidth=0, zorder=2)
        ax2.add_patch(s)

# CHARIOT (vue de face)
for cx in [-130, 105]:
    axle = mpatches.Rectangle((cx-5, 50), 10, 20,
        facecolor='#888888', edgecolor='#aaaaaa', linewidth=1, zorder=6)
    ax2.add_patch(axle)
    wheel = plt.Circle((cx, 50+37), 37, color='#ff4444', zorder=7,
                        linewidth=2, edgecolor='#cc0000', fill=False)
    ax2.add_patch(wheel)
    wheel_fill = plt.Circle((cx, 50+37), 35, color='#441111', zorder=6, alpha=0.8)
    ax2.add_patch(wheel_fill)

# Châssis chariot
chassis = mpatches.FancyBboxPatch((-135, 87), 275, 20,
    boxstyle="round,pad=2",
    facecolor='#223355', edgecolor='#4466aa', linewidth=2, zorder=6)
ax2.add_patch(chassis)
ax2.text(-10, 97, 'CHASSIS CHARIOT', color='#88aaff', ha='center',
         va='center', fontsize=8, fontweight='bold', zorder=7)

# CLIP BADGE
clip_line = ax2.plot([25, 25], [87, 57], color='#aaaaaa', linewidth=3, zorder=8)
badge_rect = mpatches.Rectangle((15, 47), 20, 10,
    facecolor='white', edgecolor='#00ff88', linewidth=2, zorder=9)
ax2.add_patch(badge_rect)
ax2.text(25, 52, 'BADGE', color='#003311', ha='center', va='center',
         fontsize=6, fontweight='bold', zorder=10)

# Distance badge-antenne
ax2.annotate('', xy=(60, 17), xytext=(60, 47),
    arrowprops=dict(arrowstyle='<->', color='#ff4444', lw=1.5))
ax2.text(75, 32, '<5mm', color='#ff4444', ha='left', va='center', fontsize=9,
         fontweight='bold')

# COTATIONS HAUTEURS
ax2.annotate('', xy=(480, 0), xytext=(480, 15),
    arrowprops=dict(arrowstyle='<->', color='#aaaaaa', lw=1))
ax2.text(490, 7, '15mm', color='#aaaaaa', ha='left', va='center', fontsize=7)

ax2.annotate('', xy=(480, 0), xytext=(480, 27),
    arrowprops=dict(arrowstyle='<->', color='#4488aa', lw=1))
ax2.text(490, 14, '27mm\ntiroir', color='#4488aa', ha='left', va='center', fontsize=7)

# Labels rails
ax2.text(-265, 17, 'Rail G\n±265', color='#ffaa00', ha='center', va='bottom',
         fontsize=7, fontweight='bold')
ax2.text(265, 17, 'Rail D\n±265', color='#ffaa00', ha='center', va='bottom',
         fontsize=7, fontweight='bold')
ax2.text(-400, 17, 'Rail P70\n-400', color='#cc6600', ha='center', va='bottom',
         fontsize=7)
ax2.text(400, 17, 'Rail P70\n+400', color='#cc6600', ha='center', va='bottom',
         fontsize=7)

# ─────────────────────────────────────────────
# VUE ASSEMBLAGE ISOMÉTRIQUE - BOTTOM
# ─────────────────────────────────────────────
ax3 = fig.add_subplot(3, 1, 3)
ax3.set_facecolor('#1a1a2e')
ax3.set_xlim(-600, 600)
ax3.set_ylim(-50, 400)
ax3.axis('off')
ax3.set_title('VUE ISOMÉTRIQUE — Assemblage 3D Imprimé (7 pièces)',
              color='white', fontsize=14, fontweight='bold', pad=15)

# Simulation isométrique simplifiée - perspective
def iso(x, y, z, scale=0.8):
    xi = (x - y) * 0.866 * scale
    yi = (x + y) * 0.5 * scale + z * scale
    return xi, yi

# Base mat (vue perspective)
def draw_box(ax, x0, y0, z0, w, d, h, fc, ec, alpha=1.0, zorder=2):
    pts_top = [iso(x0,y0,z0+h), iso(x0+w,y0,z0+h),
               iso(x0+w,y0+d,z0+h), iso(x0,y0+d,z0+h)]
    pts_front = [iso(x0,y0,z0), iso(x0+w,y0,z0),
                 iso(x0+w,y0,z0+h), iso(x0,y0,z0+h)]
    pts_right = [iso(x0+w,y0,z0), iso(x0+w,y0+d,z0),
                 iso(x0+w,y0+d,z0+h), iso(x0+w,y0,z0+h)]

    for pts, brightness in [(pts_top, 1.0), (pts_front, 0.7), (pts_right, 0.5)]:
        c = [min(1, int(fc[i:i+2],16)/255 * brightness) for i in (0,2,4)]
        poly = plt.Polygon(pts, facecolor=c, edgecolor='#'+ec,
                           linewidth=1, alpha=alpha, zorder=zorder)
        ax.add_patch(poly)

# MAT GAUCHE (PIECE 2) - PETG
draw_box(ax3, 0, 0, 0, 130, 300, 15, '2d2d3d', '888888', zorder=2)
ax3.text(*iso(65, 150, 20), 'PIÈCE 2\nMat G PETG', color='#aaaaaa',
         ha='center', va='bottom', fontsize=7, zorder=10)

# MAT DROIT (PIECE 3)
draw_box(ax3, 275, 0, 0, 130, 300, 15, '2d2d3d', '888888', zorder=2)
ax3.text(*iso(340, 150, 20), 'PIÈCE 3\nMat D PETG', color='#aaaaaa',
         ha='center', va='bottom', fontsize=7, zorder=10)

# TIROIR RFID CENTRAL (PIECE 1)
draw_box(ax3, 130, 75, 0, 145, 150, 27, '1a3344', '4488aa', zorder=5)
ax3.text(*iso(202, 150, 32), 'PIÈCE 1\nTiroir RFID\n(Pepper C1)',
         color='#4488ff', ha='center', va='bottom', fontsize=8, fontweight='bold', zorder=11)

# Polycarbonate (au-dessus tiroir)
draw_box(ax3, 130, 75, 19, 145, 150, 8, 'aaddff', '88bbdd', alpha=0.6, zorder=6)

# RAILS INTERNES GAUCHE (PIECE 4) - TPU
draw_box(ax3, 125, 0, 0, 25, 300, 15, 'ffaa00', 'ffcc00', zorder=7)
ax3.text(*iso(137, 0, 20), 'PIÈCE 4\nRail G TPU', color='#ffaa00',
         ha='center', va='bottom', fontsize=7, zorder=11)

# RAILS INTERNES DROIT (PIECE 5) - TPU
draw_box(ax3, 255, 0, 0, 25, 300, 15, 'ffaa00', 'ffcc00', zorder=7)
ax3.text(*iso(267, 300, 20), 'PIÈCE 5\nRail D TPU', color='#ffaa00',
         ha='center', va='bottom', fontsize=7, zorder=11)

# EXTENSIONS P70 (PIECES 6 & 7)
draw_box(ax3, -70, 0, 0, 70, 300, 15, '252535', '666666', zorder=1)
ax3.text(*iso(-35, 150, 20), 'P6\nExt G', color='#888888',
         ha='center', va='bottom', fontsize=7, zorder=10)

draw_box(ax3, 405, 0, 0, 70, 300, 15, '252535', '666666', zorder=1)
ax3.text(*iso(440, 150, 20), 'P7\nExt D', color='#888888',
         ha='center', va='bottom', fontsize=7, zorder=10)

# CLIP BADGE (au-dessus, flottant)
draw_box(ax3, 175, 120, 80, 30, 25, 3, 'aaaaaa', 'ffffff', zorder=12)
line_top = iso(190, 132, 83)
line_bot = iso(190, 132, 55)
ax3.plot([line_top[0], line_bot[0]], [line_top[1], line_bot[1]],
         color='#888888', linewidth=3, zorder=12)
draw_box(ax3, 180, 125, 45, 20, 15, 5, 'ffffff', '00ff88', zorder=13)
ax3.text(*iso(190, 132, 38), 'BADGE\nRFID', color='#00ff88',
         ha='center', va='top', fontsize=7, fontweight='bold', zorder=14)

# Titre pièces
ax3.text(-550, 380, '7 PIÈCES IMPRESSION 3D :', color='white', fontsize=11,
         fontweight='bold', va='top')
pieces_info = [
    ('■', '#2d2d3d', 'Pièce 1 : Tiroir RFID — PETG'),
    ('■', '#2d2d3d', 'Pièce 2+3 : Mat G/D — PETG noir'),
    ('■', '#ffaa00', 'Pièce 4+5 : Rails internes — TPU 95A jaune'),
    ('■', '#252535', 'Pièce 6+7 : Extensions P70 — PETG'),
    ('■', 'white',   'Clip badge — PETG-CF (×49)'),
    ('□', '#aaddff', 'Polycarbonate 8mm (acheté)'),
]
for i, (sym, col, txt) in enumerate(pieces_info):
    ax3.text(-550, 355-i*28, sym, color=col, fontsize=14, va='top')
    ax3.text(-525, 355-i*28, txt, color='#cccccc', fontsize=9, va='top')

# Signature
fig.text(0.5, 0.01,
         'GE Healthcare Buc — Projet RFID Sol — Ligne Pristina | Design Impression 3D v1.0',
         ha='center', color='#555577', fontsize=9)

plt.tight_layout(pad=2.0)
plt.savefig('C:\\Users\\ADMIN\\Desktop\\rfid\\render_mat_3D.png',
            dpi=150, bbox_inches='tight',
            facecolor='#1a1a2e', edgecolor='none')
print("Render sauvegardé !")
