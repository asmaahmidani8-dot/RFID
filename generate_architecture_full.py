import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(30, 20))
ax.set_xlim(0, 30); ax.set_ylim(0, 20); ax.axis('off')
fig.patch.set_facecolor('#F7F9FC')
ax.set_facecolor('#F7F9FC')

# ── COULEURS ──────────────────────────────────────────────
C_GE_BLUE   = '#003087'
C_TEAL      = '#00857C'
C_ORANGE    = '#E86D1E'
C_RED       = '#C0392B'
C_GREEN     = '#1E8449'
C_PURPLE    = '#6C3483'
C_GRAY      = '#5D6D7E'
C_DARK      = '#1C2833'
C_WHITE     = '#FFFFFF'
C_YELLOW    = '#B7950B'
C_CLOUD     = '#1565C0'

PH1  = '#D6EAF8'   # bleu clair  phase 1
PH2  = '#D5F5E3'   # vert clair  phase 2
PH3  = '#FDEBD0'   # orange clair phase 3
PHF  = '#E8DAEF'   # violet clair phase finale

# ── HELPERS ───────────────────────────────────────────────
def box(x, y, w, h, fc='#EEF2F7', ec='#BDC3C7', lw=1.8, r=0.2, z=2):
    ax.add_patch(FancyBboxPatch((x,y), w, h,
        boxstyle=f'round,pad={r}', facecolor=fc, edgecolor=ec,
        linewidth=lw, zorder=z))

def dbox(x, y, w, h, fc='#FAFAFA', ec=C_GRAY, lw=1.5, z=1):
    ax.add_patch(FancyBboxPatch((x,y), w, h,
        boxstyle='round,pad=0.2', facecolor=fc, edgecolor=ec,
        linewidth=lw, linestyle='--', zorder=z))

def t(x, y, s, sz=9, c=C_DARK, bold=False, ha='center', va='center', z=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=sz,
            fontweight='bold' if bold else 'normal', color=c, zorder=z,
            fontfamily='DejaVu Sans')

def arr(x1,y1,x2,y2, c=C_GRAY, lw=2, ls='-', lab='', lbx=None, lby=None):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
        arrowprops=dict(arrowstyle='->', color=c, lw=lw,
                        linestyle=ls, connectionstyle='arc3,rad=0.0'), zorder=6)
    if lab:
        mx = lbx if lbx else (x1+x2)/2
        my = lby if lby else (y1+y2)/2 + 0.2
        ax.text(mx, my, lab, ha='center', va='center', fontsize=7.5,
                fontweight='bold', color=c, zorder=7,
                bbox=dict(boxstyle='round,pad=0.18', facecolor='white',
                          edgecolor=c, linewidth=1, alpha=0.95))

def phase_tag(x, y, label, color):
    ax.add_patch(FancyBboxPatch((x,y), 1.5, 0.38,
        boxstyle='round,pad=0.05', facecolor=color, edgecolor=color,
        linewidth=1, zorder=8))
    t(x+0.75, y+0.19, label, sz=7.5, c=C_WHITE, bold=True, z=9)

# ════════════════════════════════════════════════════════════
# TITRE
# ════════════════════════════════════════════════════════════
box(0.3, 18.8, 29.4, 1.0, fc=C_GE_BLUE, ec=C_GE_BLUE, r=0.15)
t(15, 19.42, 'SYSTEME RFID — SUIVI CHARIOTS — GE HEALTHCARE BUC — LIGNE PRISTINA',
  sz=17, c=C_WHITE, bold=True)
t(15, 19.05, 'Architecture Complete  |  Phase 1 → Phase 2 → Phase 3 → Production (Serveur Linux + Cloud)',
  sz=10, c='#AED6F1')

# ════════════════════════════════════════════════════════════
# LEGENDE PHASES (haut droit)
# ════════════════════════════════════════════════════════════
box(23.5, 16.9, 6.2, 1.65, fc='#FDFEFE', ec=C_GRAY, lw=1.2, r=0.15)
t(26.6, 18.27, 'Legende phases', sz=8.5, c=C_GRAY, bold=True)
legends = [(23.65,17.82,PH1,C_GE_BLUE,'Phase 1'),
           (25.3, 17.82,PH2,C_GREEN,  'Phase 2'),
           (26.95,17.82,PH3,C_ORANGE, 'Phase 3'),
           (28.6, 17.82,PHF,C_PURPLE, 'Finale')]
for lx,ly,fc,ec,lab in legends:
    box(lx,ly,1.3,0.42,fc=fc,ec=ec,lw=1.5,r=0.1)
    t(lx+0.65,ly+0.21,lab,sz=7.5,c=ec,bold=True)
ax.plot([23.65,29.65],[17.7,17.7],color=C_GRAY,lw=0.6,alpha=0.4)
t(26.6,17.35,'Ajouts incrementaux par phase',sz=7.5,c=C_GRAY)

# ════════════════════════════════════════════════════════════
# ORACLE + BRILLIANT FACTORY (barre haute)
# ════════════════════════════════════════════════════════════
box(0.3, 16.9, 11.8, 1.65, fc='#F5EEF8', ec=C_PURPLE, lw=2, r=0.15)
t(6.2, 18.32, 'Oracle GLTEST / GLPROD', sz=11, c=C_PURPLE, bold=True)
t(6.2, 17.92, 'WIP_DISCRETE_JOBS  |  WIP_OPERATIONS  |  MTL_SYSTEM_ITEMS_B', sz=8.5, c=C_DARK)
t(6.2, 17.55, 'OFs RELEASED  →  sync_oracle.py  →  MySQL', sz=8, c=C_GRAY)
ax.plot([0.5,12.0],[17.72,17.72],color=C_PURPLE,lw=0.8,alpha=0.3)

box(12.3, 16.9, 10.9, 1.65, fc='#EBF5FB', ec=C_GE_BLUE, lw=2, r=0.15)
t(17.75, 18.32, 'Brilliant Factory BUC', sz=11, c=C_GE_BLUE, bold=True)
t(17.75, 17.92, 'pristina_catalogue  |  120 articles  |  11 gammes Pristina', sz=8.5, c=C_DARK)
t(17.75, 17.55, 'feeder_num  →  item_code  →  jobs_planning', sz=8, c=C_GRAY)

# ════════════════════════════════════════════════════════════
# ZONE SUPERMARCHE
# ════════════════════════════════════════════════════════════
dbox(0.3, 3.8, 7.2, 12.8, fc='#F0FBFA', ec=C_TEAL, lw=2.2)
t(3.9, 16.85, 'SUPERMARCHE  (SMK)', sz=12, c=C_TEAL, bold=True)

# -- Tablette WS --
box(0.55, 13.5, 6.7, 3.0, fc='#D6EAF8', ec=C_GE_BLUE, lw=2, r=0.15)
phase_tag(0.65, 16.1, 'Phase 1', C_GE_BLUE)
t(3.9, 16.08, '', sz=9, c=C_GE_BLUE)
t(3.9, 15.98, 'Tablette WS  —  Dashboard Web', sz=12, c=C_GE_BLUE, bold=True)
t(3.9, 15.55, 'http://serveur:5000  |  Bootstrap 5  |  JavaScript', sz=8.5, c=C_DARK)
ax.plot([0.65,7.15],[15.22,15.22],color=C_GE_BLUE,lw=0.8,alpha=0.4)
t(3.9, 14.88, '1. Choisit le chariot disponible', sz=8, c=C_DARK)
t(3.9, 14.55, '2. Associe le job (OF Released)', sz=8, c=C_DARK)
t(3.9, 14.22, '3. Cree la mission  →  PREPAREE', sz=8, c=C_GREEN, bold=True)
t(3.9, 13.82, 'SEULE VALIDATION HUMAINE REQUISE', sz=8, c=C_RED, bold=True)

# -- Pepper C1 #1 --
box(0.55, 10.0, 6.7, 3.2, fc='#FDEDEC', ec=C_RED, lw=2, r=0.15)
phase_tag(0.65, 12.8, 'Phase 1', C_GE_BLUE)
t(3.9, 12.72, 'Pepper C1  #1  —  RFID HF Reader', sz=12, c=C_RED, bold=True)
t(3.9, 12.3,  'Frontiere SMK / Ligne  |  Portique automatique', sz=8.5, c=C_DARK)
ax.plot([0.65,7.15],[11.98,11.98],color=C_RED,lw=0.8,alpha=0.4)
t(3.9, 11.65, 'Badge START (cote droit)  →  EN_ATTENTE', sz=8, c=C_DARK)
t(3.9, 11.32, '                         →  Move Oracle (auto)', sz=8, c=C_GREEN, bold=True)
ax.plot([0.65,7.15],[11.02,11.02],color=C_RED,lw=0.5,alpha=0.3)
t(3.9, 10.72, 'Badge END   (cote gauche) →  RETOUR', sz=8, c=C_DARK)
t(3.9, 10.35, 'Types A + B  (98 badges RFID HF)', sz=8, c=C_RED, bold=True)

# -- Pistolets QR (Phase 2+) --
box(0.55, 7.2, 6.7, 2.55, fc='#FEF9E7', ec=C_ORANGE, lw=2, r=0.15)
phase_tag(0.65, 9.38, 'Phase 2', C_GREEN)
t(3.9, 9.3,  'Pistolets QR Code', sz=12, c=C_ORANGE, bold=True)
t(3.9, 8.88, 'Zebra / Honeywell  |  WiFi  |  HTTP POST', sz=8.5, c=C_DARK)
ax.plot([0.65,7.15],[8.58,8.58],color=C_ORANGE,lw=0.8,alpha=0.4)
t(3.9, 8.28, 'Type C (P-70 lourds)  →  scan QR au poste', sz=8, c=C_DARK)
t(3.9, 7.95, 'Type D (Palettes)     →  scan QR au poste', sz=8, c=C_DARK)
t(3.9, 7.55, 'PREPAREE  →  EN_APPROCHE  →  RETOUR', sz=8, c=C_ORANGE, bold=True)

# -- Chariots (Phase 1) --
box(0.55, 3.95, 6.7, 3.0, fc='#EAFAF1', ec=C_GREEN, lw=2, r=0.15)
phase_tag(0.65, 6.55, 'Phase 1', C_GE_BLUE)
t(3.9, 6.47, '49 Chariots  —  98 Badges RFID HF', sz=11, c=C_GREEN, bold=True)
t(3.9, 6.08, 'Type A : 25 ch groupes  (OP10, OP20, OP25)', sz=8, c=C_DARK)
t(3.9, 5.75, 'Type B : 24 ch simples  (OP80→OP130)', sz=8, c=C_DARK)
ax.plot([0.65,7.15],[5.45,5.45],color=C_GREEN,lw=0.6,alpha=0.4)
phase_tag(0.65, 5.0, 'Phase 2', C_GREEN)
t(3.9, 4.92, 'Type C : 2 ch lourds P-70  (QR code)', sz=8, c=C_DARK)
ax.plot([0.65,7.15],[4.65,4.65],color=C_GREEN,lw=0.6,alpha=0.4)
phase_tag(0.65, 4.2, 'Phase 3', C_ORANGE)
t(3.9, 4.12, 'Type D : Palettes  OP140/150/160/170  (QR)', sz=8, c=C_DARK)

# ════════════════════════════════════════════════════════════
# ZONE ATTENTE + PEPPER C1 #2 (Phase 2)
# ════════════════════════════════════════════════════════════
dbox(7.85, 9.5, 3.5, 7.1, fc='#F0FFF4', ec=C_GREEN, lw=2)
t(9.6, 16.85, 'ZONE ATTENTE', sz=10, c=C_GREEN, bold=True)
box(8.05, 12.5, 3.1, 3.85, fc='#D5F5E3', ec=C_GREEN, lw=2, r=0.15)
phase_tag(8.15, 16.0, 'Phase 2', C_GREEN)
t(9.6, 15.92, 'Pepper C1  #2', sz=11, c=C_GREEN, bold=True)
t(9.6, 15.52, 'RFID HF Reader', sz=8.5, c=C_DARK)
t(9.6, 15.18, 'Entre zone attente', sz=8, c=C_DARK)
t(9.6, 14.88, 'et postes', sz=8, c=C_DARK)
ax.plot([8.15,11.05],[14.58,14.58],color=C_GREEN,lw=0.8,alpha=0.4)
t(9.6, 14.28, 'Badge detecTE', sz=8, c=C_DARK)
t(9.6, 13.95, '→ EN_APPROCHE', sz=8, c=C_GREEN, bold=True)
t(9.6, 13.62, '→ Move Oracle', sz=8, c=C_GREEN, bold=True)
t(9.6, 13.22, '  (auto)', sz=8, c=C_GRAY)

box(8.05, 9.65, 3.1, 2.62, fc='#EBF5FB', ec=C_GE_BLUE, lw=1.5, r=0.15)
t(9.6, 11.98, 'Chariots', sz=9, c=C_GE_BLUE, bold=True)
t(9.6, 11.62, 'attendent ici', sz=8.5, c=C_DARK)
t(9.6, 11.28, 'en file', sz=8, c=C_GRAY)
t(9.6, 10.92, 'avant livraison', sz=8, c=C_GRAY)
t(9.6, 10.52, 'au poste', sz=8, c=C_GRAY)
t(9.6, 10.1, 'statut:', sz=8, c=C_GRAY)
t(9.6, 9.82, 'EN_ATTENTE', sz=8, c=C_GE_BLUE, bold=True)

# ════════════════════════════════════════════════════════════
# ZONE SERVEUR
# ════════════════════════════════════════════════════════════
dbox(11.65, 3.8, 8.5, 12.8, fc='#F8F9FA', ec=C_GE_BLUE, lw=2.2)
t(15.9, 16.85, 'SERVEUR', sz=12, c=C_GE_BLUE, bold=True)

# -- Raspberry Pi label --
box(11.85, 15.85, 8.1, 0.72, fc=PH1, ec=C_GE_BLUE, lw=1.5, r=0.1)
phase_tag(11.95, 15.88, 'Phase 1-2-3', C_GE_BLUE)
t(16.9, 16.21, 'Raspberry Pi  (prototype)  |  Python  |  MQTT  |  HTTP', sz=9, c=C_GE_BLUE, bold=True)

# -- Mosquitto --
box(11.85, 13.1, 3.8, 2.52, fc='#FDEDEC', ec=C_RED, lw=2, r=0.15)
t(13.75, 15.32, 'Mosquitto', sz=12, c=C_RED, bold=True)
t(13.75, 14.92, 'Broker MQTT', sz=8.5, c=C_DARK)
ax.plot([11.95,15.55],[14.62,14.62],color=C_RED,lw=0.8,alpha=0.4)
t(13.75, 14.32, 'Port 1883', sz=8, c=C_DARK)
t(13.75, 14.0,  '(proto)', sz=8, c=C_GRAY)
t(13.75, 13.6,  'Port 8883 MQTTS', sz=8, c=C_RED, bold=True)
t(13.75, 13.28, '(prod + TLS)', sz=8, c=C_GRAY)

# -- rfid_mqtt.py --
box(15.9, 13.1, 4.1, 2.52, fc='#FDEDEC', ec=C_RED, lw=1.5, r=0.15)
t(17.95, 15.32, 'rfid_mqtt.py', sz=11, c=C_RED, bold=True)
t(17.95, 14.92, 'Ecoute MQTT', sz=8.5, c=C_DARK)
ax.plot([16.0,19.9],[14.62,14.62],color=C_RED,lw=0.8,alpha=0.4)
t(17.95, 14.28, 'START → EN_ATTENTE', sz=8, c=C_DARK)
t(17.95, 13.95, 'START → oracle_queue', sz=8, c=C_GREEN, bold=True)
t(17.95, 13.6,  'END   → RETOUR', sz=8, c=C_DARK)
t(17.95, 13.28, 'Couche 1 + Couche 2', sz=7.5, c=C_GRAY)

# -- MySQL --
box(11.85, 10.5, 3.8, 2.35, fc='#E8F8F5', ec=C_TEAL, lw=2, r=0.15)
t(13.75, 12.55, 'MySQL', sz=12, c=C_TEAL, bold=True)
t(13.75, 12.15, 'Base : rfid_buc', sz=8.5, c=C_DARK)
ax.plot([11.95,15.55],[11.85,11.85],color=C_TEAL,lw=0.8,alpha=0.4)
t(13.75, 11.52, 'chariots', sz=7.5, c=C_DARK)
t(13.75, 11.22, 'cart_missions', sz=7.5, c=C_DARK)
t(13.75, 10.92, 'cart_mission_jobs', sz=7.5, c=C_DARK)
t(13.75, 10.65, 'jobs_planning', sz=7.5, c=C_DARK)
t(13.75, 10.35, 'rfid_cards  |  rfid_scanners', sz=7.5, c=C_DARK)

# -- Flask --
box(15.9, 10.5, 4.1, 2.35, fc='#EAFAF1', ec=C_GREEN, lw=2, r=0.15)
t(17.95, 12.55, 'Flask', sz=12, c=C_GREEN, bold=True)
t(17.95, 12.15, 'Serveur Web Python', sz=8.5, c=C_DARK)
ax.plot([16.0,19.9],[11.85,11.85],color=C_GREEN,lw=0.8,alpha=0.4)
t(17.95, 11.52, 'dashboard_ws.py', sz=8, c=C_DARK)
t(17.95, 11.22, 'GET / → chariots dispo', sz=7.5, c=C_GRAY)
t(17.95, 10.92, 'GET /chariot → jobs', sz=7.5, c=C_GRAY)
t(17.95, 10.62, 'POST /mission → creer', sz=7.5, c=C_GRAY)
t(17.95, 10.32, 'Port 5000 (5000→443 Nginx)', sz=7.5, c=C_GREEN)

# -- sync_oracle.py --
box(11.85, 8.6, 3.8, 1.65, fc='#F5EEF8', ec=C_PURPLE, lw=1.8, r=0.15)
t(13.75, 10.02, 'sync_oracle.py', sz=10, c=C_PURPLE, bold=True)
t(13.75, 9.62, 'Oracle → MySQL periodique', sz=8, c=C_DARK)
t(13.75, 9.25, 'OFs Released copiEs', sz=7.5, c=C_GRAY)

# -- oracle_msca_move.py --
box(15.9, 8.6, 4.1, 1.65, fc='#F5EEF8', ec=C_PURPLE, lw=1.8, r=0.15)
t(17.95, 10.02, 'oracle_msca_move.py', sz=9.5, c=C_PURPLE, bold=True)
t(17.95, 9.62, 'Move Transaction Oracle', sz=8, c=C_DARK)
t(17.95, 9.25, 'Telnet MWA MSCA (auto)', sz=7.5, c=C_GRAY)

# -- Linux Server (Phase finale) --
box(11.85, 6.6, 8.1, 1.75, fc=PHF, ec=C_PURPLE, lw=2, r=0.15)
phase_tag(11.95, 8.02, 'Phase Finale', C_PURPLE)
t(16.85, 7.95, 'Serveur Linux GE  (Ubuntu Server 22.04 LTS)  —  Production', sz=10, c=C_PURPLE, bold=True)
t(16.85, 7.52, 'Mosquitto port 8883 (MQTTS+TLS)  |  Flask + Nginx port 443 (HTTPS)  |  MySQL  |  IP fixe reseau GE', sz=8, c=C_DARK)
t(16.85, 7.15, 'Meme code que Raspberry Pi  —  juste changer la configuration serveur', sz=8, c=C_GRAY)

# -- Cloud (Phase finale) --
box(11.85, 4.55, 8.1, 1.82, fc='#DBEAFE', ec=C_CLOUD, lw=2, r=0.15)
phase_tag(11.95, 6.0, 'Phase Finale', C_PURPLE)
t(16.85, 5.95, 'Cloud GE  (Azure / GE Cloud)', sz=10, c=C_CLOUD, bold=True)
t(16.85, 5.55, 'Dashboard accessible hors usine  |  Sauvegarde MySQL  |  Monitoring + Alertes', sz=8, c=C_DARK)
t(16.85, 5.18, 'Multi-sites  |  Reporting direction  |  Optionnel — decision IT + management', sz=8, c=C_GRAY)

# -- oracle_move_queue --
box(11.85, 3.85, 8.1, 0.52, fc='#FEF9E7', ec=C_YELLOW, lw=1.5, r=0.1)
t(16.85, 4.11, 'oracle_move_queue  (MySQL)  —  File attente Move Transactions  —  exe_flag=1 → telnet MSCA Oracle', sz=8, c=C_YELLOW, bold=True)

# ════════════════════════════════════════════════════════════
# ZONE POSTES ASSEMBLAGE
# ════════════════════════════════════════════════════════════
dbox(20.5, 3.8, 9.2, 12.8, fc='#FFF9F0', ec=C_ORANGE, lw=2.2)
t(25.1, 16.85, 'POSTES ASSEMBLAGE', sz=12, c=C_ORANGE, bold=True)

# -- Tablettes operateurs (Phase 2) --
box(20.7, 13.5, 8.8, 3.0, fc='#FDEBD0', ec=C_ORANGE, lw=2, r=0.15)
phase_tag(20.8, 16.1, 'Phase 2', C_GREEN)
t(25.1, 16.02, 'Tablettes Operateurs  —  1 par poste', sz=12, c=C_ORANGE, bold=True)
t(25.1, 15.6,  'https://serveur/poste/X  |  Auto-refresh 10s', sz=8.5, c=C_DARK)
ax.plot([20.8,29.4],[15.28,15.28],color=C_ORANGE,lw=0.8,alpha=0.4)
t(25.1, 14.95, 'Voir chariots EN_APPROCHE pour ce poste', sz=8, c=C_DARK)
t(25.1, 14.62, '[CHARIOT VIDE]  →  operateur confirme', sz=8, c=C_RED, bold=True)
t(25.1, 14.25, 'OP10 OP20 OP25 OP80 OP90 OP100 OP110 OP130', sz=8, c=C_GRAY)

# -- Postes Phase 1 --
box(20.7, 10.0, 8.8, 3.25, fc='#D6EAF8', ec=C_GE_BLUE, lw=2, r=0.15)
phase_tag(20.8, 12.85, 'Phase 1', C_GE_BLUE)
t(25.1, 12.78, 'Postes Assemblage — Phase 1', sz=12, c=C_GE_BLUE, bold=True)
t(25.1, 12.35, 'FEEDER-1  FEEDER-2  FEEDER-3', sz=8.5, c=C_DARK)
t(25.1, 12.02, 'FEEDER-4  FEEDER-5', sz=8.5, c=C_DARK)
ax.plot([20.8,29.4],[11.72,11.72],color=C_GE_BLUE,lw=0.8,alpha=0.4)
t(25.1, 11.4,  'POSTE-1  POSTE-2  POSTE-3', sz=8.5, c=C_DARK)
t(25.1, 11.05, 'POSTE-6', sz=8.5, c=C_DARK)
t(25.1, 10.62, 'Chariot arrive  →  statut EN_ATTENTE (Phase1)', sz=8, c=C_GRAY)
t(25.1, 10.28, '                →  statut EN_APPROCHE (Phase2)', sz=8, c=C_GREEN)

# -- Statuts par type --
box(20.7, 7.2, 8.8, 2.58, fc='#F8F9FA', ec=C_GRAY, lw=1.5, r=0.15)
t(25.1, 9.52, 'Statuts par type de chariot', sz=10, c=C_GRAY, bold=True)
ax.plot([20.8,29.4],[9.22,9.22],color=C_GRAY,lw=0.8,alpha=0.4)
rows = [
    ('Type A + B', 'PREPAREE → EN_ATTENTE → EN_APPROCHE → RETOUR', C_GE_BLUE, C_GREEN),
    ('Type C      ', 'PREPAREE → EN_APPROCHE → RETOUR', C_RED, C_GREEN),
    ('Type D      ', 'PREPAREE → EN_APPROCHE → RETOUR', C_ORANGE, C_GREEN),
]
for i,(tp,sts,c1,c2) in enumerate(rows):
    y = 8.88 - i*0.58
    t(21.8, y, tp, sz=8, c=c1, bold=True, ha='center')
    t(25.9, y, sts, sz=7.5, c=C_DARK, ha='center')

# -- Oracle Move trigger --
box(20.7, 4.55, 8.8, 2.42, fc='#F5EEF8', ec=C_PURPLE, lw=1.8, r=0.15)
t(25.1, 6.68, 'Declenchement Move Oracle', sz=10, c=C_PURPLE, bold=True)
ax.plot([20.8,29.4],[6.38,6.38],color=C_PURPLE,lw=0.8,alpha=0.4)
t(25.1, 6.05, 'Phase 1  →  badge START  (EN_ATTENTE)', sz=8.5, c=C_DARK)
t(25.1, 5.7,  'Phase 2  →  badge APPROCHE  (EN_APPROCHE)', sz=8.5, c=C_DARK)
t(25.1, 5.35, 'Type C/D →  scan QR  (EN_APPROCHE)', sz=8.5, c=C_DARK)
t(25.1, 4.95, '100% automatique apres association job+chariot', sz=8, c=C_GREEN, bold=True)

# -- Chariots types icons --
box(20.7, 3.88, 8.8, 0.5, fc='#E8F4FD', ec=C_GE_BLUE, lw=1.2, r=0.1)
t(25.1, 4.12, 'Type A (groupes) | Type B (simples) | Type C (lourds P-70) | Type D (palettes)', sz=8, c=C_GE_BLUE, bold=True)

# ════════════════════════════════════════════════════════════
# FLECHES PRINCIPALES
# ════════════════════════════════════════════════════════════

# Tablette WS → Flask (HTTPS)
arr(7.25, 14.5, 11.65, 12.0, C_GE_BLUE, lw=2.5,
    lab='HTTPS', lbx=9.6, lby=13.55)

# Pepper C1 #1 → Mosquitto (MQTT)
arr(7.25, 11.5, 11.65, 14.2, C_RED, lw=2.8,
    lab='MQTT/MQTTS', lbx=9.2, lby=12.62)

# Pepper C1 #2 (Phase 2) → Mosquitto
arr(11.35, 14.5, 11.65, 14.5, C_GREEN, lw=2.2,
    lab='MQTT', lbx=11.5, lby=14.78)

# Pistolets QR → Flask (HTTP)
arr(7.25, 8.2, 11.65, 11.2, C_ORANGE, lw=2,
    lab='HTTP', lbx=9.2, lby=9.5)

# Mosquitto → rfid_mqtt
arr(15.65, 14.0, 15.9, 14.0, C_RED, lw=2)
t(15.77, 14.22, 'on_msg', sz=7, c=C_RED)

# rfid_mqtt → MySQL
arr(17.95, 13.1, 15.75, 12.72, C_RED, lw=1.8)

# Flask ↔ MySQL
arr(15.65, 11.5, 15.9, 11.5, C_GREEN, lw=2)
arr(15.9,  11.2, 15.65,11.2, C_TEAL,  lw=1.8)

# MySQL → oracle_move_queue
arr(13.75, 10.5, 13.75, 10.15, C_TEAL, lw=1.8)

# oracle_move_queue → oracle_msca_move
arr(16.85, 8.6, 17.5, 8.6, C_YELLOW, lw=1.8,
    lab='poll 10s', lbx=17.2, lby=8.85)

# oracle_msca_move → Oracle (Telnet)
arr(17.95, 8.6, 7.1, 17.28, C_PURPLE, lw=2,
    lab='Telnet MWA MSCA', lbx=12.0, lby=13.8)

# Flask → Tablette operateur (HTTPS)
arr(20.0, 11.5, 20.5, 14.5, C_GREEN, lw=2.5,
    lab='HTTPS', lbx=20.05, lby=12.88)

# sync_oracle ↔ Oracle
arr(13.75, 10.25, 13.75, 8.6, C_PURPLE, lw=1.5, ls='--')
arr(6.2, 16.9, 13.5, 10.25, C_PURPLE, lw=1.5, ls='--',
    lab='sync periodique', lbx=10.2, lby=13.85)

# Linux Server (Phase finale) - evolution arrow
arr(15.9, 7.35, 15.9, 8.25, C_PURPLE, lw=2.5, ls='--',
    lab='Migration', lbx=16.8, lby=7.8)

# Cloud arrow
arr(15.9, 6.6, 15.9, 6.37, C_CLOUD, lw=2, ls='--')

# ════════════════════════════════════════════════════════════
# CYCLE STATUTS (bas)
# ════════════════════════════════════════════════════════════
box(0.3, 0.25, 29.4, 3.35, fc='#FDFEFE', ec=C_GRAY, lw=1.2, r=0.15)
t(15, 3.35, "Cycle de vie d'une mission  —  Statuts MySQL  cart_missions", sz=11, c=C_GRAY, bold=True)
ax.plot([0.5,29.6],[3.05,3.05],color=C_GRAY,lw=0.8,alpha=0.4)

statuts = [
    ('PREPAREE',    '#7F8C8D', 'WS tablette\nassocie job'),
    ('EN_ATTENTE',  '#2980B9', 'Badge START\nPepper C1 #1\n(Phase 1)'),
    ('EN_APPROCHE', '#E67E22', 'Badge APPROCHE\nPepper C1 #2\n(Phase 2)'),
    ('RETOUR',      '#27AE60', 'Badge END\nPepper C1 #1'),
]
sx = [1.0, 7.5, 14.2, 21.0]
sw = 5.8
for i,(s,c,sub) in enumerate(statuts):
    bx = sx[i]
    box(bx, 1.55, sw, 1.25, fc=c, ec=c, r=0.12, lw=1)
    t(bx+sw/2, 2.2,  s,   sz=11, c=C_WHITE, bold=True)
    t(bx+sw/2, 0.88, sub, sz=7.5, c=C_GRAY)
    if i < 3:
        arr(bx+sw, 2.18, sx[i+1], 2.18, c=C_GRAY, lw=2.5,
            lab='auto', lbx=sx[i]+sw+0.5, lby=2.45)

# Legende Oracle trigger
t(7.5, 1.22, 'Move Oracle', sz=7.5, c=C_PURPLE, bold=True)
t(7.5, 0.88, '(Phase 1)', sz=7, c=C_GRAY)
t(14.2, 1.22, 'Move Oracle', sz=7.5, c=C_PURPLE, bold=True)
t(14.2, 0.88, '(Phase 2)', sz=7, c=C_GRAY)

# ════════════════════════════════════════════════════════════
plt.tight_layout(pad=0.1)
out = r'C:\Users\ADMIN\Desktop\rfid\Architecture_RFID_GE_FULL.png'
plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='#F7F9FC')
print(f'[OK] Schema architecture complet genere : {out}')
plt.show()
