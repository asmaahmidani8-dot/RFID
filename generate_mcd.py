import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(22, 15))
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis('off')
fig.patch.set_facecolor('#EEF2F7')
ax.set_facecolor('#EEF2F7')

C_ENT   = '#1C3D6E'
C_ASS   = '#E86D1E'
C_CARD  = '#C0392B'
C_WHITE = '#FFFFFF'
C_LINE  = '#34495E'
C_PK    = '#FFD700'
C_FK    = '#90CAF9'

# ─────────────────────────────────────────────
def draw_entity(x, y, w, h, name, attrs):
    # En-tete
    head = FancyBboxPatch((x, y+h-0.55), w, 0.55,
                           boxstyle="round,pad=0.0",
                           facecolor=C_ENT, edgecolor='#0D2B45', lw=2, zorder=3)
    ax.add_patch(head)
    ax.text(x+w/2, y+h-0.27, name, ha='center', va='center',
            fontsize=10, fontweight='bold', color=C_WHITE, zorder=4)
    # Corps
    body = FancyBboxPatch((x, y), w, h-0.55,
                           boxstyle="round,pad=0.0",
                           facecolor='#D6E4F0', edgecolor='#0D2B45', lw=2, zorder=3)
    ax.add_patch(body)
    # Attributs
    row_h = (h-0.65) / max(len(attrs), 1)
    for i, (attr, atype) in enumerate(attrs):
        yi = y + h - 0.65 - i*row_h - row_h/2
        if atype == 'PK':
            color = '#1C3D6E'
            prefix = '🔑 '
            fw = 'bold'
        elif atype == 'FK':
            color = '#1565C0'
            prefix = '⚿  '
            fw = 'bold'
        else:
            color = '#1A1A1A'
            prefix = '   '
            fw = 'normal'
        ax.text(x+0.18, yi, prefix+attr, ha='left', va='center',
                fontsize=8, color=color, fontweight=fw,
                fontfamily='monospace', zorder=4)

def draw_assoc(x, y, w, h, name):
    r = FancyBboxPatch((x, y), w, h,
                        boxstyle="round,pad=0.08",
                        facecolor=C_ASS, edgecolor='#A04000', lw=2, zorder=5)
    ax.add_patch(r)
    ax.text(x+w/2, y+h/2, name, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=C_WHITE, zorder=6)

def draw_link(x1, y1, x2, y2, c1, c2, c1_off=(0,0.15), c2_off=(0,0.15)):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='-', color=C_LINE, lw=1.8), zorder=2)
    ax.text(x1+c1_off[0], y1+c1_off[1], c1,
            ha='center', va='center', fontsize=9,
            fontweight='bold', color=C_CARD, zorder=7)
    ax.text(x2+c2_off[0], y2+c2_off[1], c2,
            ha='center', va='center', fontsize=9,
            fontweight='bold', color=C_CARD, zorder=7)

# ═══════════════════════════════════════════════════
# ENTITES
# ═══════════════════════════════════════════════════

# CHARIOT  — centre haut
draw_entity(8.0, 9.8, 5.5, 3.8, 'CHARIOT', [
    ('chariot_id', 'PK'),
    ('nom',        ''),
    ('poste_id',   ''),
    ('actif',      ''),
])

# RFID_CARD  — droite haut
draw_entity(15.5, 9.8, 5.8, 3.8, 'RFID_CARD', [
    ('uid',          'PK'),
    ('chariot_id',   'FK'),
    ('badge_type',   ''),
    ('actif',        ''),
    ('enregistre_le',''),
])

# RFID_SCANNER  — gauche haut
draw_entity(0.5, 9.8, 5.8, 3.8, 'RFID_SCANNER', [
    ('scanner_id',  'PK'),
    ('type_scan',   ''),
    ('localisation',''),
    ('ip_address',  ''),
    ('actif',       ''),
    ('last_seen',   ''),
])

# CART_MISSION  — centre milieu
draw_entity(7.5, 3.8, 6.5, 5.2, 'CART_MISSION', [
    ('id',           'PK'),
    ('chariot_id',   'FK'),
    ('rfid_uid',     'FK'),
    ('statut',       ''),
    ('ts_scan1',     ''),
    ('ts_scan2',     ''),
    ('ts_commencer', ''),
    ('ts_terminer',  ''),
    ('ts_scan3',     ''),
    ('cree_le',      ''),
])

# JOBS_PLANNING  — droite milieu
draw_entity(15.5, 3.8, 5.8, 5.2, 'JOBS_PLANNING', [
    ('id',             'PK'),
    ('of_number',      ''),
    ('operation_code', ''),
    ('item_code',      ''),
    ('item_desc',      ''),
    ('statut',         ''),
    ('qty',            ''),
    ('date_besoin',    ''),
])

# CART_EVENTS  — gauche bas
draw_entity(0.5, 0.5, 5.8, 4.8, 'CART_EVENTS', [
    ('id',         'PK'),
    ('mission_id', 'FK'),
    ('rfid_uid',   ''),
    ('chariot_id', ''),
    ('evenement',  ''),
    ('ts',         ''),
    ('scanner_id', ''),
    ('details',    ''),
])

# CART_MISSION_JOBS  — droite bas
draw_entity(15.5, 0.5, 5.8, 3.0, 'CART_MISSION_JOBS', [
    ('id',         'PK'),
    ('mission_id', 'FK'),
    ('of_number',  'FK'),
    ('statut',     ''),
])

# ═══════════════════════════════════════════════════
# ASSOCIATIONS
# ═══════════════════════════════════════════════════

draw_assoc(13.2, 10.8, 2.1, 0.6, 'POSSEDE')
draw_assoc(9.8,  8.8,  2.1, 0.6, 'EFFECTUE')
draw_assoc(4.2,  8.0,  2.1, 0.6, 'DETECTE')
draw_assoc(4.2,  4.5,  2.1, 0.6, 'GENERE')
draw_assoc(13.2, 5.2,  2.1, 0.6, 'CONTIENT')

# ═══════════════════════════════════════════════════
# LIENS + CARDINALITES
# ═══════════════════════════════════════════════════

# CHARIOT ── POSSEDE ── RFID_CARD
ax.plot([13.5, 13.2], [11.1, 11.1], color=C_LINE, lw=1.8, zorder=2)
ax.plot([15.3, 15.5], [11.1, 11.1], color=C_LINE, lw=1.8, zorder=2)
ax.text(12.8, 11.35, '1,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
ax.text(15.7, 11.35, '1,1', ha='center', fontsize=9, fontweight='bold', color=C_CARD)

# CHARIOT ── EFFECTUE ── CART_MISSION
ax.plot([10.75, 10.75], [9.8,  9.4], color=C_LINE, lw=1.8, zorder=2)
ax.plot([10.75, 10.75], [8.8,  6.0], color=C_LINE, lw=1.8, zorder=2)  # was 9.0 -> 6.0 (bottom of CART_MISSION top area) - this goes to cart_mission top area
ax.plot([10.75, 10.75], [8.8,  8.85], color=C_LINE, lw=1.8, zorder=2)
ax.text(10.3,  9.6,  '1,1', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
ax.text(10.3,  8.65, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
# Connect EFFECTUE bottom to CART_MISSION top
ax.plot([10.75, 10.75], [8.8, 9.0], color=C_LINE, lw=1.8, zorder=2)
ax.plot([10.75, 10.75], [9.4, 9.8], color=C_LINE, lw=1.8, zorder=2)

# Draw the actual connection for EFFECTUE
ax.annotate('', xy=(10.75, 9.8),  xytext=(10.75, 9.4),
            arrowprops=dict(arrowstyle='-', color=C_LINE, lw=1.8), zorder=2)
ax.annotate('', xy=(10.75, 9.0),  xytext=(10.75, 8.8),
            arrowprops=dict(arrowstyle='-', color=C_LINE, lw=1.8), zorder=2)

# RFID_SCANNER ── DETECTE ── CART_MISSION
ax.plot([3.4, 4.2],   [9.0, 8.3],  color=C_LINE, lw=1.8, zorder=2)
ax.plot([6.3, 7.5],   [8.3, 7.5],  color=C_LINE, lw=1.8, zorder=2)
ax.text(3.0, 8.8, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
ax.text(7.2, 7.3, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)

# CART_MISSION ── GENERE ── CART_EVENTS
ax.plot([7.5, 6.3],   [4.8, 4.8],  color=C_LINE, lw=1.8, zorder=2)
ax.plot([4.2, 3.4],   [4.8, 5.3],  color=C_LINE, lw=1.8, zorder=2)
ax.text(7.8, 5.0, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
ax.text(3.0, 5.0, '0,1', ha='center', fontsize=9, fontweight='bold', color=C_CARD)

# CART_MISSION ── CONTIENT ── JOBS_PLANNING
ax.plot([14.0, 13.2],  [5.5, 5.5],  color=C_LINE, lw=1.8, zorder=2)
ax.plot([15.3, 15.5],  [5.5, 5.5],  color=C_LINE, lw=1.8, zorder=2)
ax.text(14.7, 5.8, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)
ax.text(15.8, 5.8, '0,N', ha='center', fontsize=9, fontweight='bold', color=C_CARD)

# CART_MISSION_JOBS — table d'association (pointilles)
ax.plot([16.5, 14.3], [3.5, 5.5], color='#888888', lw=1.2, ls='--', zorder=2)
ax.plot([16.5, 10.75],[3.5, 3.8], color='#888888', lw=1.2, ls='--', zorder=2)
ax.text(13.5, 4.2, '(table\nd\'association)', ha='center',
        fontsize=7.5, color='#666666', style='italic')

# ═══════════════════════════════════════════════════
# TITRE
# ═══════════════════════════════════════════════════
ax.text(11, 14.5, 'MCD — Système RFID Suivi Chariots',
        ha='center', fontsize=17, fontweight='bold', color=C_ENT)
ax.text(11, 14.0, 'GE HealthCare Buc  •  Ligne Pristina  •  Méthode Merise',
        ha='center', fontsize=11, color='#444444')

# Légende
lx, ly = 8.0, 1.2
draw_entity(lx, ly, 2.2, 0.6, '', [])
rect_l = FancyBboxPatch((lx, ly), 2.2, 0.6, boxstyle="round,pad=0.0",
                         facecolor=C_ENT, edgecolor='#0D2B45', lw=2, zorder=3)
ax.add_patch(rect_l)
ax.text(lx+1.1, ly+0.3, 'Entité', ha='center', va='center',
        fontsize=8, color=C_WHITE, fontweight='bold', zorder=4)

draw_assoc(lx+2.6, ly, 2.2, 0.6, 'Association')

ax.text(lx+5.4, ly+0.3, '0,N  /  1,1  /  1,N  =  Cardinalités',
        ha='left', va='center', fontsize=8.5, color=C_CARD, fontweight='bold')

ax.text(lx, ly-0.4, '🔑 PK = Clé Primaire    ⚿  FK = Clé Étrangère',
        ha='left', va='center', fontsize=8.5, color='#333333')

plt.tight_layout(pad=0.5)
out = r'C:\Users\ADMIN\Desktop\rfid\MCD_RFID_GE.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#EEF2F7')
print(f"[OK] MCD genere : {out}")
plt.show()
