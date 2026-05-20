import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(24, 14))
ax.set_xlim(0, 24); ax.set_ylim(0, 14); ax.axis('off')
fig.patch.set_facecolor('#FFFFFF'); ax.set_facecolor('#FFFFFF')

C_TEAL   = '#00857C'
C_BLUE   = '#003087'
C_ORANGE = '#E86D1E'
C_GRAY   = '#5D6D7E'
C_WHITE  = '#FFFFFF'
C_RED    = '#C0392B'
C_DARK   = '#2C3E50'
C_GREEN  = '#27AE60'
C_PURPLE = '#7D3C98'
C_YELLOW = '#D4AC0D'

def rbox(x, y, w, h, fc='#EEF2F7', ec='#BDC3C7', lw=1.5, ls='-', r=0.15, z=2):
    ax.add_patch(FancyBboxPatch((x,y), w, h,
        boxstyle=f'round,pad={r}', facecolor=fc, edgecolor=ec,
        linewidth=lw, linestyle=ls, zorder=z))

def t(x, y, s, sz=9, c=C_DARK, bold=False, ha='center', va='center', z=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=sz,
            fontweight='bold' if bold else 'normal', color=c, zorder=z)

def arr(x1, y1, x2, y2, c=C_GRAY, lw=2, ls='-', lab='', lx=0, ly=0):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
        arrowprops=dict(arrowstyle='->', color=c, lw=lw, linestyle=ls), zorder=4)
    if lab:
        ax.text(lx or (x1+x2)/2, ly or (y1+y2)/2+0.22,
                lab, ha='center', fontsize=8, color=c, fontweight='bold', zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                          edgecolor=c, linewidth=1, alpha=0.9))

def person(x, y, c=C_TEAL, label='', sub=''):
    ax.add_patch(plt.Circle((x, y+0.5), 0.22, color=c, zorder=4))
    ax.plot([x,x],   [y+0.28, y-0.1],  color=c, lw=3, zorder=4)
    ax.plot([x-0.28, x+0.28], [y+0.1, y+0.1], color=c, lw=3, zorder=4)
    ax.plot([x, x-0.2], [y-0.1, y-0.45], color=c, lw=3, zorder=4)
    ax.plot([x, x+0.2], [y-0.1, y-0.45], color=c, lw=3, zorder=4)
    t(x, y-0.75, label, sz=9,   c=C_DARK, bold=True)
    t(x, y-1.05, sub,   sz=7.5, c=C_GRAY)

def zone(x, y, w, h, c=C_GRAY, lab=''):
    rbox(x, y, w, h, fc='#FAFAFA', ec=c, lw=1.5, ls='--', r=0.2)
    if lab: t(x+w/2, y+h+0.18, lab, sz=10, c=c, bold=True)

# ══════════════════════════════════════════════════════
# TITRE
# ══════════════════════════════════════════════════════
t(12, 13.55, 'Systeme RFID  -  Suivi Chariots  |  GE HealthCare Buc',
  sz=16, c=C_BLUE, bold=True)
t(12, 13.08, 'Architecture Systeme  |  Ligne Pristina  |  Prototype --> Production',
  sz=10, c=C_GRAY)
rbox(0.2, 13.1, 1.7, 0.72, fc=C_BLUE, ec=C_BLUE, r=0.1)
t(1.05, 13.46, 'GE HealthCare', sz=8, c=C_WHITE, bold=True)

# ══════════════════════════════════════════════════════
# ZONES
# ══════════════════════════════════════════════════════
zone(0.2,  0.3, 5.2, 11.5, C_TEAL,   'Supermarche (SMK)')
zone(6.0,  3.3, 6.7,  8.4, C_BLUE,   'Serveur Linux')
zone(13.5, 0.3, 10.3,11.5, C_ORANGE, 'Postes Assemblage')

# Barre Oracle
rbox(0.3,  11.9, 10.4, 0.78, fc='#F4ECF7', ec=C_PURPLE, lw=1.5, r=0.1)
t(5.5, 12.29,
  'Oracle GLPROD  |  WIP_DISCRETE_JOBS  |  OFs RELEASED  -->  sync_oracle.py  -->  MariaDB',
  sz=7.8, c=C_PURPLE, bold=True)
rbox(11.1, 11.9, 12.6, 0.78, fc='#E8F4FD', ec=C_BLUE, lw=1.5, r=0.1)
t(17.4, 12.29,
  'Brilliant Factory BUC  |  material_db  |  pristina_catalogue  (120 items, 11 gammes)',
  sz=7.8, c=C_BLUE, bold=True)

# ══════════════════════════════════════════════════════
# ACTEURS
# ══════════════════════════════════════════════════════
person(2.0,  10.1, C_TEAL,   'Water Spider (WS)', 'Supermarche')
person(17.2, 10.1, C_ORANGE, 'Operateur',         'Au poste')

# ══════════════════════════════════════════════════════
# SMK — TABLETTE WS
# ══════════════════════════════════════════════════════
rbox(0.5, 6.9, 4.4, 2.65, fc='#E8F4FD', ec=C_TEAL, lw=2)
t(2.7, 9.22, 'Tablette WS', sz=11, c=C_TEAL, bold=True)
t(2.7, 8.8,  'Dashboard WS  +  Scanner QR code', sz=8.5, c=C_DARK)
t(2.7, 8.45, 'http://rpi.local:5000/ws', sz=7.5, c=C_GRAY)
ax.plot([0.6, 4.8], [8.18, 8.18], color=C_TEAL, lw=0.8, alpha=0.4)
t(2.7, 7.88, '1. Choisit operation + ligne', sz=7.5, c=C_DARK)
t(2.7, 7.55, '2. OFs associes automatiquement', sz=7.5, c=C_DARK)
t(2.7, 7.22, '3. Mission PREPAREE creee', sz=7.5, c=C_GREEN, bold=True)

# ══════════════════════════════════════════════════════
# SMK — PEPPER C1
# ══════════════════════════════════════════════════════
rbox(0.5, 4.55, 4.4, 2.05, fc='#FDEDEC', ec=C_RED, lw=2)
t(2.7, 6.32, 'Pepper C1  -  RFID HF', sz=11, c=C_RED, bold=True)
t(2.7, 5.9,  'Lecteur RFID  -  Sortie SMK', sz=8.5, c=C_DARK)
t(2.7, 5.55, 'Badge START  -->  EN_APPROCHE', sz=7.5, c=C_GRAY)
t(2.7, 5.22, 'Badge END    -->  TERMINEE', sz=7.5, c=C_GRAY)
t(2.7, 4.82, 'Types A et B  (chariots normaux/groupes)', sz=7.5, c=C_RED, bold=True)

# ══════════════════════════════════════════════════════
# SMK — QR CODE
# ══════════════════════════════════════════════════════
rbox(0.5, 1.3, 4.4, 3.0, fc='#FEF9E7', ec=C_ORANGE, lw=2)
t(2.7, 4.05, 'QR Code  -  Tablette', sz=11, c=C_ORANGE, bold=True)
t(2.7, 3.65, 'Types C et D  (lourds + palettes)', sz=8.5, c=C_DARK)
ax.plot([0.6, 4.8], [3.38, 3.38], color=C_ORANGE, lw=0.8, alpha=0.4)
t(2.7, 3.05, 'TYPE C : P-70  (chariots lourds)', sz=7.5, c=C_DARK, bold=True)
t(2.7, 2.72, '  Scan WS  -->  EN_APPROCHE', sz=7.5, c=C_GRAY)
t(2.7, 2.42, '  Re-scan  -->  TERMINEE',    sz=7.5, c=C_GRAY)
t(2.7, 2.05, 'TYPE D : Palettes POSTE-6',   sz=7.5, c=C_DARK, bold=True)
t(2.7, 1.72, '  Meme logique QR code',      sz=7.5, c=C_GRAY)
t(2.7, 1.42, '  Plusieurs voyages / jour',  sz=7.5, c=C_GRAY)

# ══════════════════════════════════════════════════════
# SERVEUR — RPi / LINUX
# ══════════════════════════════════════════════════════
rbox(6.3, 9.3, 6.3, 2.1, fc='#EBF5FB', ec=C_BLUE, lw=2.5)
t(9.45, 10.65, 'Raspberry Pi  -->  VM Linux', sz=11, c=C_BLUE, bold=True)
t(9.45, 10.2,  'Prototype  -->  Ubuntu Server 22.04 LTS', sz=8.5, c=C_GRAY)
t(9.45, 9.82,  'IP fixe  -  Reseau WiFi usine', sz=8, c=C_GRAY)

# MARIADB
rbox(6.3, 7.0, 2.85, 2.0, fc='#E8F8F5', ec=C_TEAL, lw=2)
t(7.73, 8.72, 'MariaDB', sz=10.5, c=C_TEAL, bold=True)
t(7.73, 8.3,  'Base : rfid_buc', sz=8.5, c=C_DARK)
t(7.73, 7.95, '8 tables', sz=8, c=C_GRAY)
t(7.73, 7.62, 'Toutes les donnees', sz=7.5, c=C_GRAY)
t(7.73, 7.3,  'du systeme', sz=7.5, c=C_GRAY)

# MOSQUITTO
rbox(9.75, 7.0, 2.85, 2.0, fc='#FDEDEC', ec=C_RED, lw=2)
t(11.18, 8.72, 'Mosquitto', sz=10.5, c=C_RED, bold=True)
t(11.18, 8.3,  'MQTT Broker', sz=8.5, c=C_DARK)
t(11.18, 7.95, 'Port 8883 (MQTTS)', sz=8, c=C_RED, bold=True)
t(11.18, 7.62, 'TLS / SSL', sz=8, c=C_GRAY)
t(11.18, 7.3,  'rfid/buc/#', sz=7.5, c=C_GRAY)

# FLASK
rbox(6.3, 4.6, 6.3, 2.1, fc='#EAFAF1', ec=C_GREEN, lw=2)
t(9.45, 6.45, 'Flask  -  Serveur Web', sz=11, c=C_GREEN, bold=True)
t(9.45, 6.02, 'dashboard_ws.py  |  Port 5000', sz=8.5, c=C_DARK)
t(9.45, 5.68, 'Nginx reverse proxy  -->  HTTPS port 443', sz=8, c=C_GREEN, bold=True)
t(9.45, 5.28, 'rfid_mqtt.py  -  ecoute MQTT --> MariaDB', sz=7.5, c=C_DARK)

# SYNC
rbox(6.3, 3.3, 6.3, 0.95, fc='#F4ECF7', ec=C_PURPLE, lw=1.5)
t(9.45, 3.92, 'sync_oracle.py  --  OFs RELEASED --> MariaDB', sz=8.5, c=C_PURPLE, bold=True)
t(9.45, 3.55, 'Oracle GLPROD  |  Brilliant Factory BUC', sz=7.5, c=C_GRAY)

# ══════════════════════════════════════════════════════
# POSTES — DASHBOARD OPERATEUR
# ══════════════════════════════════════════════════════
rbox(13.8, 7.2, 9.7, 4.1, fc='#FEF9E7', ec=C_ORANGE, lw=2)
t(18.65, 11.0,  'Dashboard Operateur', sz=12, c=C_ORANGE, bold=True)
t(18.65, 10.55, '1 ecran par poste  |  https://rpi.local/poste/X', sz=8.5, c=C_GRAY)
ax.plot([13.9, 23.4], [10.22, 10.22], color=C_ORANGE, lw=1, alpha=0.4)
t(18.65, 9.82, '[ Commencer ]    -->  EN_COURS', sz=10, c=C_DARK, bold=True)
t(18.65, 9.38, '[ Chariot vide ] -->  VIDE',     sz=10, c=C_DARK, bold=True)
ax.plot([13.9, 23.4], [9.05, 9.05], color=C_ORANGE, lw=1, alpha=0.4)
t(18.65, 8.72, 'Postes couverts :', sz=8.5, c=C_GRAY)
t(18.65, 8.35, 'FEEDER-1  FEEDER-2  FEEDER-3  FEEDER-4  FEEDER-5', sz=8.5, c=C_DARK)
t(18.65, 7.98, 'POSTE-1  POSTE-2  POSTE-3  POSTE-6  |  P-70  |  Palettes', sz=8.5, c=C_DARK)
t(18.65, 7.55, 'Refresh automatique toutes les 10 secondes', sz=7.5, c=C_GRAY)

# ══════════════════════════════════════════════════════
# 4 TYPES DE CHARIOTS
# ══════════════════════════════════════════════════════
t(18.65, 7.0, '4 types de chariots', sz=9, c=C_GRAY, bold=True)
types = [
    (13.8,  4.3, 2.35, 2.6, '#E8F4FD', C_BLUE,
     'TYPE A\nSIMPLES',
     ['Badge RFID', 'FEEDER-3  (2 OFs)', 'FEEDER-4  (1 OF)',
      'FEEDER-5  (7 OFs)', 'OP-80/90/100/110/130']),
    (16.4,  4.3, 2.35, 2.6, '#F4ECF7', C_PURPLE,
     'TYPE B\nGROUPES',
     ['Badge RFID x2', 'OP-10  (3+3)', 'OP-20  (3+3)',
      'OP-25  (3+10)', '2 missions liees']),
    (18.9,  4.3, 2.35, 2.6, '#FDEDEC', C_RED,
     'TYPE C\nLOURDS',
     ['QR Code', 'P-70  -  2 chariots', 'Poste : POSTE-1',
      'Scan tablette WS', 'Trop lourd -> RFID']),
    (21.45, 4.3, 2.2,  2.6, '#FEF5E7', C_ORANGE,
     'TYPE D\nPALETTES',
     ['QR Code', 'OP-130/140/150', 'P-160 / OP-170',
      'Poste : POSTE-6', 'Multi-voyages/jour']),
]
for x, y, w, h, fc, ec, title, lines in types:
    rbox(x, y, w, h, fc=fc, ec=ec, lw=2)
    t(x+w/2, y+h-0.28, title, sz=8.5, c=ec, bold=True)
    ax.plot([x+0.1, x+w-0.1], [y+h-0.56, y+h-0.56], color=ec, lw=1, alpha=0.5)
    for i, line in enumerate(lines):
        t(x+w/2, y+h-0.9-i*0.38, line, sz=6.8, c=C_DARK)

# ══════════════════════════════════════════════════════
# CYCLE STATUTS
# ══════════════════════════════════════════════════════
rbox(13.8, 1.25, 9.7, 2.75, fc='#F8F9FA', ec=C_GRAY, lw=1, r=0.1)
t(18.65, 3.68, "Cycle de vie d'une mission", sz=9.5, c=C_GRAY, bold=True)
statuts = [
    ('PREPAREE',    '#95A5A6', 'WS\ndashboard'),
    ('EN_APPROCHE', '#F39C12', 'Scan badge\nou QR'),
    ('EN_COURS',    '#E86D1E', 'Operateur\ndashboard'),
    ('VIDE',        '#E74C3C', 'Operateur\ndashboard'),
    ('TERMINEE',    '#27AE60', 'Scan badge\nou QR'),
]
for i, (s, c, sub) in enumerate(statuts):
    bx = 13.9 + i * 1.9
    rbox(bx, 2.0, 1.65, 0.9, fc=c, ec=c, r=0.1, lw=1)
    t(bx+0.82, 2.47, s,   sz=7.2, c=C_WHITE, bold=True)
    t(bx+0.82, 1.68, sub, sz=6.5, c=C_GRAY)
    if i < 4:
        arr(bx+1.65, 2.45, bx+1.9, 2.45, c=C_GRAY, lw=1.5)

# ══════════════════════════════════════════════════════
# FLECHES PRINCIPALES
# ══════════════════════════════════════════════════════

# WS --> tablette
arr(2.0, 9.15, 2.4, 9.55, C_TEAL, lw=2)

# Pepper C1 --> Mosquitto  (MQTTS)
arr(4.9, 5.55, 9.75, 8.1, C_RED, lw=2.8,
    lab='MQTTS  (port 8883)', lx=7.5, ly=7.4)

# Tablette WS --> Flask  (HTTPS)
arr(4.9, 8.1, 6.3, 6.82, C_TEAL, lw=2.5,
    lab='HTTPS  (port 443)', lx=5.8, ly=7.7)

# QR --> Flask  (HTTPS)
arr(4.9, 2.85, 6.3, 5.28, C_ORANGE, lw=2,
    lab='HTTPS  (port 443)', lx=5.35, ly=4.25)

# Mosquitto --> rfid_mqtt (interne)
arr(11.18, 7.0, 10.6, 6.7, C_RED, lw=2)

# Flask <--> MariaDB (interne)
arr(7.73, 7.0, 7.9, 6.7,  C_GREEN, lw=2)
arr(8.5,  6.7, 8.3, 7.0,  C_GREEN, lw=1.5)

# Flask --> Dashboard operateur  (HTTPS)
arr(12.6, 5.6, 13.8, 9.05, C_GREEN, lw=2.8,
    lab='HTTPS  (port 443)', lx=13.45, ly=7.6)

# Operateur --> dashboard
arr(17.2, 9.15, 17.9, 9.55, C_ORANGE, lw=2)

# sync_oracle --> MariaDB  (pointille)
arr(9.45, 3.3, 8.5, 7.0, C_PURPLE, lw=1.8, ls='dashed',
    lab='sync', lx=8.2, ly=5.3)

# ══════════════════════════════════════════════════════
# LEGENDE PROTOCOLES
# ══════════════════════════════════════════════════════
rbox(0.3, 0.3, 12.8, 0.75, fc='#F8F9FA', ec=C_GRAY, lw=1, r=0.1)
t(1.5, 0.68, 'Protocoles :', sz=8.5, c=C_GRAY, bold=True)

items = [
    (3.2,  C_RED,    'MQTTS port 8883  (Hardware --> Serveur, chiffre TLS)'),
    (10.5, C_TEAL,   'HTTPS port 443   (Web --> Serveur, chiffre SSL)'),
    (17.5, C_PURPLE, 'Sync Oracle      (interne, periodique)'),
]
for x, c, lab in items:
    ax.plot([x-0.8, x-0.3], [0.67, 0.67], color=c, lw=2.5)
    t(x+1.8, 0.67, lab, sz=7.5, c=c, bold=True)

# ══════════════════════════════════════════════════════
plt.tight_layout(pad=0.3)
out = r'C:\Users\ADMIN\Desktop\rfid\Architecture_RFID_GE.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#FFFFFF')
print(f'[OK] Schema architecture genere : {out}')
plt.show()
