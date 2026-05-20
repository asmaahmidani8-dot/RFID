import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

fig = plt.figure(figsize=(10, 16), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 16)
ax.axis('off')

PURPLE   = '#5B2D8E'; PURPLE_L = '#EDE9FE'
BLUE     = '#1E3A6E'; BLUE_L   = '#DBEAFE'
GREEN    = '#166534'; GREEN_L  = '#DCFCE7'
ORANGE   = '#C05621'; ORANGE_L = '#FED7AA'
TEAL     = '#0F766E'; TEAL_L   = '#CCFBF1'
RED      = '#B91C1C'; RED_L    = '#FEE2E2'
GRAY     = '#4B5563'; GRAY_L   = '#F3F4F6'
GE_BLUE  = '#003087'
WHITE    = '#FFFFFF'; DARK = '#1C1C1C'

def rbox(x, y, w, h, fc='white', ec='gray', lw=1.5, r=0.15, zorder=2):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.02,rounding_size="+str(r),
                         facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder)
    ax.add_patch(box)

def txt(x, y, s, fs=9, fw='normal', color=DARK, ha='center', va='center',
        style='normal', zorder=3, bbox=None):
    ax.text(x, y, s, fontsize=fs, fontweight=fw, color=color,
            ha=ha, va=va, fontstyle=style, zorder=zorder, bbox=bbox)

def arrow(x1, y1, x2, y2, color=GRAY, lw=1.8, head=12):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                mutation_scale=head), zorder=4)

def lbl(x, y, s, fc=GRAY, fs=7.5):
    ax.text(x, y, s, fontsize=fs, color=WHITE, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor=fc, edgecolor='none'),
            zorder=5)

# ============================================================
# GE LOGO TOP RIGHT
# ============================================================
rbox(7.6, 15.35, 2.2, 0.52, fc=GE_BLUE, ec=GE_BLUE, r=0.1)
txt(8.7, 15.61, 'GE HealthCare', fs=11, fw='bold', color=WHITE)

# ============================================================
# TITRE
# ============================================================
rbox(0.2, 14.52, 9.6, 0.72, fc=PURPLE, ec=PURPLE, r=0.2)
txt(5.0, 14.88, 'PHASE 3  -  MIXED (A/B RFID + C/D QR)', fs=14, fw='bold', color=WHITE)
txt(5.0, 14.35, 'Add Type C & D (QR Code)  -  Architecture Corrigee',
    fs=9, color=PURPLE, style='italic')

# ============================================================
# FIELD LAYER GAUCHE - RFID Type A + B
# ============================================================
rbox(0.2, 11.15, 4.3, 3.0, fc=BLUE_L, ec=BLUE, lw=2, r=0.2)
rbox(0.35, 13.75, 4.0, 0.32, fc=BLUE, ec=BLUE, r=0.1)
txt(2.35, 13.91, 'FIELD LAYER - RFID  (TYPE A & B)', fs=8.5, fw='bold', color=WHITE)

# Pepper C1 #1
rbox(0.45, 12.75, 3.9, 0.82, fc=WHITE, ec=BLUE, lw=1.5, r=0.12)
rbox(0.55, 12.87, 0.8, 0.55, fc=BLUE_L, ec=BLUE, lw=1.5, r=0.08)
txt(0.95, 13.14, 'RFID', fs=8, fw='bold', color=BLUE)
txt(2.7, 13.25, 'Pepper C1  -  SMK Exit', fs=8.5, fw='bold', color=BLUE, ha='left')
txt(2.7, 13.03, 'Badge START + END  |  Phase 1', fs=7.5, color=GRAY, ha='left')

# Pepper C1 #2
rbox(0.45, 11.78, 3.9, 0.82, fc=WHITE, ec=BLUE, lw=1.5, r=0.12)
rbox(0.55, 11.90, 0.8, 0.55, fc=BLUE_L, ec=BLUE, lw=1.5, r=0.08)
txt(0.95, 12.17, 'RFID', fs=8, fw='bold', color=BLUE)
txt(2.7, 12.28, 'Pepper C1  -  Zone Attente', fs=8.5, fw='bold', color=BLUE, ha='left')
txt(2.7, 12.06, 'Vers postes assemblage  |  Phase 2', fs=7.5, color=GRAY, ha='left')

# Phase badges
txt(1.0, 11.42, 'Phase 1', fs=7, fw='bold', color=BLUE,
    bbox=dict(boxstyle='round,pad=0.2', facecolor=BLUE_L, edgecolor=BLUE, lw=1))
txt(2.25, 11.42, '+', fs=8, color=GRAY)
txt(3.1, 11.42, 'Phase 2', fs=7, fw='bold', color=PURPLE,
    bbox=dict(boxstyle='round,pad=0.2', facecolor=PURPLE_L, edgecolor=PURPLE, lw=1))

# ============================================================
# FIELD LAYER DROIT - QR Code Type C + D
# ============================================================
rbox(5.5, 11.15, 4.3, 3.0, fc=GREEN_L, ec=GREEN, lw=2, r=0.2)
rbox(5.65, 13.75, 4.0, 0.32, fc=GREEN, ec=GREEN, r=0.1)
txt(7.65, 13.91, 'FIELD LAYER - QR CODE  (TYPE C & D)', fs=8.5, fw='bold', color=WHITE)

# Pistolet scanner
rbox(5.75, 12.45, 3.9, 1.12, fc=WHITE, ec=GREEN, lw=1.5, r=0.12)
rbox(5.85, 12.58, 0.8, 0.55, fc=GREEN_L, ec=GREEN, lw=1.5, r=0.08)
txt(6.25, 12.85, 'QR', fs=9, fw='bold', color=GREEN)
txt(7.9, 13.1, 'Pistolet Scanner  -  Phase 3', fs=8.5, fw='bold', color=GREEN, ha='left')
txt(7.9, 12.88, 'Operateur scanne au poste', fs=7.5, color=GRAY, ha='left')
txt(7.9, 12.66, 'Type C (P-70) + Type D (palettes)', fs=7.5, color=GRAY, ha='left')

txt(6.55, 11.42, 'Phase 3', fs=7, fw='bold', color=GREEN,
    bbox=dict(boxstyle='round,pad=0.2', facecolor=GREEN_L, edgecolor=GREEN, lw=1))

# Correction note QR
rbox(5.6, 11.55, 4.1, 0.52, fc=RED_L, ec=RED, lw=1.5, r=0.1)
txt(7.65, 11.81, '[CORRECTION] QR Scanner -> Flask directement', fs=8, fw='bold', color=RED)
txt(7.65, 11.62, 'PAS via MQTT Broker  (MQTT = Pepper C1 uniquement)', fs=7.5, color=RED)

# ============================================================
# MQTT BROKER - uniquement pour RFID
# ============================================================
rbox(2.2, 9.55, 2.6, 1.3, fc='#F0F4FF', ec=BLUE, lw=2, r=0.2)
rbox(2.35, 10.52, 2.3, 0.28, fc=BLUE, ec=BLUE, r=0.08)
txt(3.5, 10.66, 'MQTT Broker  (Mosquitto)', fs=8, fw='bold', color=WHITE)
rbox(2.45, 9.68, 0.72, 0.5, fc=BLUE_L, ec=BLUE, lw=1.5, r=0.08)
txt(2.81, 9.93, 'MQ', fs=8, fw='bold', color=BLUE)
txt(3.55, 10.27, 'Port 8883  MQTTS + TLS', fs=8, color=GRAY, ha='left')
txt(3.55, 10.05, 'Topics : rfid/buc/#', fs=7.5, color=GRAY, ha='left')
txt(3.55, 9.83, 'QoS 1  -  livraison garantie', fs=7.5, color=GRAY, ha='left')

# Fleche Pepper C1 -> MQTT
arrow(2.35, 11.15, 3.1, 10.83, color=BLUE, lw=2.2)
lbl(2.6, 10.97, 'MQTTS\n8883', fc=BLUE, fs=7)

# ============================================================
# STATUTS
# ============================================================
rbox(0.2, 8.52, 9.6, 0.88, fc='#FAFAFA', ec='#CBD5E0', lw=1.2, r=0.15)

# Type A/B
txt(0.55, 9.2, 'TYPE A/B :', fs=7.5, fw='bold', color=BLUE, ha='left')
items_ab = [('PREPAREE', ORANGE), ('EN_ATTENTE', BLUE), ('EN_APPROCHE', TEAL), ('RETOUR', GREEN)]
trig_ab  = ['badge START', '2e Pepper C1', 'badge END']
sx = 2.2
for i, (s, c) in enumerate(items_ab):
    rbox(sx-0.45, 9.07, 0.96, 0.27, fc=c, ec=c, r=0.06)
    txt(sx+0.03, 9.21, s, fs=6.5, fw='bold', color=WHITE)
    if i < 3:
        ax.annotate('', xy=(sx+0.63, 9.21), xytext=(sx+0.51, 9.21),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.2), zorder=4)
        txt(sx+0.57, 9.07, trig_ab[i], fs=5.5, color=GRAY)
    sx += 1.62

# Type C/D
txt(0.55, 8.8, 'TYPE C/D :', fs=7.5, fw='bold', color=GREEN, ha='left')
items_cd = [('PREPAREE', ORANGE), ('EN_APPROCHE', TEAL), ('RETOUR', GREEN)]
trig_cd  = ['scan QR', 'scan QR']
sx2 = 2.2
for i, (s, c) in enumerate(items_cd):
    rbox(sx2-0.45, 8.66, 0.96, 0.27, fc=c, ec=c, r=0.06)
    txt(sx2+0.03, 8.80, s, fs=6.5, fw='bold', color=WHITE)
    if i < 2:
        ax.annotate('', xy=(sx2+0.63, 8.80), xytext=(sx2+0.51, 8.80),
                    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.2), zorder=4)
        txt(sx2+0.57, 8.66, trig_cd[i], fs=5.5, color=GRAY)
    sx2 += 1.62
txt(6.0, 8.80, '<- Pas EN_ATTENTE', fs=7, color=RED, style='italic', ha='left')

# ============================================================
# APPLICATION LAYER
# ============================================================
rbox(0.2, 6.32, 9.6, 1.98, fc='#FFFBEB', ec=ORANGE, lw=2, r=0.2)
rbox(0.35, 7.94, 9.3, 0.3, fc=ORANGE, ec=ORANGE, r=0.1)
txt(5.0, 8.09, 'APPLICATION & DATA LAYER  (Raspberry Pi  ->  futur Serveur Linux GE)',
    fs=8.5, fw='bold', color=WHITE)

comps = [
    ('Flask App', 'API', BLUE),
    ('Business', 'Rules', PURPLE),
    ('Status', 'Manager', TEAL),
    ('Oracle', 'Interface', RED),
]
cx = 0.6
for line1, line2, c in comps:
    rbox(cx, 6.45, 2.1, 1.35, fc=WHITE, ec=c, lw=1.8, r=0.15)
    rbox(cx+0.1, 7.37, 1.9, 0.3, fc=c, ec=c, r=0.08)
    txt(cx+1.05, 7.52, line1, fs=8.5, fw='bold', color=WHITE)
    txt(cx+1.05, 7.0, line2, fs=9, fw='bold', color=c)
    txt(cx+1.05, 6.7, '--------', fs=7, color='#CBD5E0')
    cx += 2.42

# Fleche MQTT -> Flask
arrow(3.5, 9.55, 1.65, 8.3, color=BLUE, lw=2.2)
lbl(2.4, 8.9, 'MQTTS\n-> Flask', fc=BLUE, fs=7)

# CORRECTION: Fleche QR -> Flask DIRECTEMENT (bypass MQTT)
arrow(7.65, 11.15, 3.0, 8.3, color=GREEN, lw=2.8)
lbl(5.7, 9.75, '[CORRECTION] HTTPS direct -> Flask\nQR ne passe PAS par MQTT', fc=GREEN, fs=7.5)

# ============================================================
# MYSQL + ORACLE
# ============================================================
rbox(0.2, 4.15, 4.55, 1.95, fc='#F0FDF4', ec=GREEN, lw=2, r=0.18)
rbox(0.35, 5.75, 4.25, 0.3, fc=GREEN, ec=GREEN, r=0.08)
txt(2.47, 5.9, 'MySQL  -  rfid_buc', fs=8.5, fw='bold', color=WHITE)
rbox(0.45, 4.28, 0.72, 0.5, fc=GREEN_L, ec=GREEN, lw=1.5, r=0.08)
txt(0.81, 4.53, 'DB', fs=9, fw='bold', color=GREEN)
items_db = ['Chariots (A, B, C, D)', 'Missions + Jobs Oracle',
            'Status History', 'oracle_move_queue', 'Audit Logs']
for j, item in enumerate(items_db):
    txt(1.55, 5.47 - j*0.23, '- ' + item, fs=7.8, color=GRAY, ha='left')

rbox(5.3, 4.15, 4.55, 1.95, fc='#FFF5F5', ec=RED, lw=2, r=0.18)
rbox(5.45, 5.75, 4.25, 0.3, fc=RED, ec=RED, r=0.08)
txt(7.62, 5.9, 'INTEGRATION LAYER', fs=8.5, fw='bold', color=WHITE)
rbox(5.42, 4.28, 0.75, 0.5, fc=RED_L, ec=RED, lw=1.5, r=0.08)
txt(5.79, 4.53, 'ORA', fs=7.5, fw='bold', color=RED)
txt(7.4, 5.47, 'Oracle ERP  (GLPROD / GLTEST)', fs=8.5, fw='bold', color=RED, ha='left')
txt(7.4, 5.24, 'Move Transactions WIP', fs=8, color=GRAY, ha='left')
txt(7.4, 5.01, 'Telnet MWA MSCA', fs=8, color=GRAY, ha='left')
txt(7.4, 4.78, 'sync_oracle.py  (periodique)', fs=8, color=GRAY, ha='left')
txt(7.4, 4.55, '[OK] Valide : Hino GE Healthcare Japon', fs=7.5, color=GREEN, fw='bold', ha='left')

# Fleches
arrow(5.0, 7.1, 2.47, 6.1, color=GRAY, lw=1.8)
arrow(4.75, 5.12, 5.3, 5.12, color=RED, lw=2)
lbl(5.02, 5.22, 'oracle_msca\n_move.py', fc=RED, fs=6.5)

# ============================================================
# USERS & DASHBOARDS
# ============================================================
rbox(0.2, 0.3, 9.6, 3.65, fc=GRAY_L, ec=GRAY, lw=1.5, r=0.2)
rbox(0.35, 3.58, 9.3, 0.3, fc=GRAY, ec=GRAY, r=0.08)
txt(5.0, 3.73, 'USERS & DASHBOARDS', fs=9, fw='bold', color=WHITE)

dash = [
    ('Web\nDashboard', 'Operators', BLUE),
    ('Power BI\nDashboards', 'Management', PURPLE),
    ('Teams\nAlerts', 'Notifications', ORANGE),
    ('Mobile /\nTablet', 'Water Spider', TEAL),
]
dx = 0.42
for (line1, sub, c) in dash:
    rbox(dx, 0.55, 2.15, 2.88, fc=WHITE, ec=c, lw=1.8, r=0.15)
    rbox(dx+0.1, 3.05, 1.95, 0.3, fc=c, ec=c, r=0.08)
    for li, lpart in enumerate(line1.split('\n')):
        txt(dx+1.075, 3.19, lpart, fs=7.5, fw='bold', color=WHITE)
    rbox(dx+0.55, 2.25, 1.1, 0.55, fc=c, lw=0, r=0.1, zorder=2)
    txt(dx+1.075, 2.52, line1.split('\n')[0][:3].upper(), fs=9, fw='bold', color=WHITE, zorder=3)
    txt(dx+1.075, 2.0, sub, fs=8.5, fw='bold', color=c)
    txt(dx+1.075, 1.75, '(' + sub + ')', fs=7.5, color=GRAY)
    dx += 2.42

arrow(2.47, 4.15, 2.47, 3.88, color=GREEN, lw=1.8)

# ============================================================
# BARRE CORRECTIONS EN BAS
# ============================================================
rbox(0.2, 0.05, 9.6, 0.22, fc=RED_L, ec=RED, lw=1.2, r=0.06)
txt(5.0, 0.16,
    '[CORRECTIONS] MariaDB -> MySQL  |  QR Scanner -> Flask direct (PAS via MQTT Broker)',
    fs=8, fw='bold', color=RED)

plt.savefig(r'C:\Users\ADMIN\Desktop\rfid\Phase3_Architecture_Corrigee.png',
            dpi=150, bbox_inches='tight', facecolor='white')
print('[OK] Phase3_Architecture_Corrigee.png genere')
