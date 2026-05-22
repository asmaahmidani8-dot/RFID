import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

LINE_H = 0.30
HDR_H  = 0.52

def eh(n):
    return HDR_H + n * LINE_H + 0.10

def ent(ax, x, y, w, title, attrs, hc, lc='#EFF6FF'):
    h = eh(len(attrs))
    # Shadow
    ax.add_patch(mpatches.Rectangle(
        (x+0.08, y-0.08), w, h, fc='#94A3B8', ec='none', zorder=1, alpha=0.45))
    # Body
    ax.add_patch(mpatches.Rectangle(
        (x, y), w, h, fc='#FFFFFF', ec=hc, lw=2.2, zorder=2))
    # Header
    ax.add_patch(mpatches.Rectangle(
        (x, y+h-HDR_H), w, HDR_H, fc=hc, ec='none', zorder=3))
    ax.text(x+w/2, y+h-HDR_H/2, title,
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='#FFFFFF', zorder=4)
    # Separator
    ax.plot([x, x+w], [y+h-HDR_H]*2, color=hc, lw=0.8, zorder=3)
    # Attributes
    for i, a in enumerate(attrs):
        ay = y + h - HDR_H - (i+1)*LINE_H
        if i % 2 == 0:
            ax.add_patch(mpatches.Rectangle(
                (x+0.02, ay+0.02), w-0.04, LINE_H-0.03,
                fc=lc, ec='none', zorder=2))
        if a.startswith('[PK]'):
            fc = '#003087'; fw = 'bold'
        elif a.startswith('[FK]'):
            fc = '#C0392B'; fw = 'bold'
        elif a.startswith('[UQ]'):
            fc = '#6C3483'; fw = 'bold'
        else:
            fc = '#1E293B'; fw = 'normal'
        ax.text(x+0.12, ay+LINE_H/2, a,
                ha='left', va='center', fontsize=7,
                color=fc, fontweight=fw, zorder=4, fontfamily='monospace')
    cx, cy = x+w/2, y+h/2
    return dict(x=x, y=y, w=w, h=h, cx=cx, cy=cy,
                L=(x,    cy),
                R=(x+w,  cy),
                T=(cx,   y+h),
                B=(cx,   y))

def rel(ax, p1, p2, c1, c2, color='#475569', rad=0.0, dashed=False):
    ls = (0, (5, 3)) if dashed else 'solid'
    ax.annotate('', xy=p2, xytext=p1,
        arrowprops=dict(
            arrowstyle='-', color=color, lw=1.6,
            linestyle=ls,
            connectionstyle=f'arc3,rad={rad}'),
        zorder=5)
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    d  = (dx**2+dy**2)**0.5 or 1
    off = 0.55
    for (px, py, card) in [
        (p1[0]+dx/d*off, p1[1]+dy/d*off, c1),
        (p2[0]-dx/d*off, p2[1]-dy/d*off, c2),
    ]:
        ax.text(px, py, card,
                ha='center', va='center', fontsize=8.5,
                color=color, fontweight='bold',
                bbox=dict(fc='white', ec='none', boxstyle='round,pad=0.18'),
                zorder=6)

# ── Canvas ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(26, 17))
ax.set_xlim(0, 26)
ax.set_ylim(0, 17)
ax.axis('off')
fig.patch.set_facecolor('#F1F5F9')

CS = '#003087'   # GE Blue   — tables statiques
CD = '#00857C'   # GE Teal   — tables dynamiques
CQ = '#C0392B'   # Red       — Oracle move queue
CR = '#6C3483'   # Purple    — referentiels / Oracle
CE = '#1E8449'   # Green     — evenements

E = {}

# ─── COL 1 — Statique ──────────────────────────────────────────
E['rfid_scanners'] = ent(ax, 0.3, 12.5, 4.2, 'RFID_SCANNERS',
    ['[PK] scanner_id', 'nom', 'localisation', 'ip_address', 'actif'],
    CS)

E['chariots'] = ent(ax, 0.3, 7.3, 4.2, 'CHARIOTS',
    ['[PK] chariot_id', 'nom', 'job_type', 'type_chariot',
     'operation_code', 'poste', 'feeder_num', 'nb_ofs',
     'partie', 'groupe_ref', 'actif'],
    CS)

E['rfid_cards'] = ent(ax, 0.3, 4.8, 4.2, 'RFID_CARDS',
    ['[PK] uid', '[FK] chariot_id', 'badge_type', 'actif'],
    CS)

# ─── COL 2 — Dynamique ─────────────────────────────────────────
E['cart_missions'] = ent(ax, 5.7, 8.3, 6.0, 'CART_MISSIONS',
    ['[PK] id', '[FK] chariot_id', '[FK] groupe_id',
     'rfid_uid', 'gamme_code', 'statut', 'partie',
     'ts_preparee', 'ts_en_attente', 'ts_en_approche',
     'ts_retour', 'ts_terminee', 'actif'],
    CD, '#E8F8F5')

E['cart_mission_jobs'] = ent(ax, 5.7, 4.8, 6.0, 'CART_MISSION_JOBS',
    ['[PK] id', '[FK] mission_id', 'of_number',
     'operation_code', 'item_code', 'item_desc', 'statut'],
    CD, '#E8F8F5')

E['oracle_move_queue'] = ent(ax, 5.7, 0.9, 6.0, 'ORACLE_MOVE_QUEUE',
    ['[PK] id', '[FK] mission_job_id', 'of_number',
     'operation_code', 'qty', 'exe_flag', 'erreur', 'execute_le'],
    CQ, '#FDEDEC')

# ─── COL 3 — Ref / Events ──────────────────────────────────────
E['pristina_catalogue'] = ent(ax, 13.0, 9.5, 5.8, 'PRISTINA_CATALOGUE',
    ['[PK] id', '[UQ] gamme_code + item_code',
     'gamme_code', 'gamme_label', 'item_code',
     'item_desc', 'feeder_num', 'job_type'],
    CR, '#F3E5F5')

E['cart_events'] = ent(ax, 13.0, 5.0, 5.8, 'CART_EVENTS',
    ['[PK] id', '[FK] mission_id', '[FK] chariot_id',
     '[FK] scanner_id', 'evenement', 'rfid_uid', 'ts'],
    CE, '#EAFAF1')

# ─── COL 4 ─────────────────────────────────────────────────────
E['jobs_planning'] = ent(ax, 20.0, 9.5, 5.7, 'JOBS_PLANNING',
    ['[PK] id', '[UQ] of_number + op_code',
     'of_number', 'operation_code', 'item_code',
     'item_desc', 'statut', 'qty_totale', 'qty_faite', 'date_besoin'],
    CR, '#F3E5F5')

E['mission_groupes'] = ent(ax, 20.0, 7.2, 5.5, 'MISSION_GROUPES',
    ['[PK] id', 'cree_le'],
    CD, '#E8F8F5')

# ─── RELATIONS FK (solid) ──────────────────────────────────────
rel(ax, E['chariots']['B'],
        E['rfid_cards']['T'],
        '1', 'N', CS)

rel(ax, E['chariots']['R'],
        E['cart_missions']['L'],
        '1', 'N', CD)

rel(ax, E['cart_missions']['B'],
        E['cart_mission_jobs']['T'],
        '1', 'N', CD)

rel(ax, E['cart_mission_jobs']['B'],
        E['oracle_move_queue']['T'],
        '1', 'N', CQ)

rel(ax, E['cart_missions']['R'],
        E['cart_events']['L'],
        '1', 'N', CE, rad=0.18)

# chariots → cart_events (direct FK dans cart_events)
rel(ax,
    (E['chariots']['x']+E['chariots']['w'], E['chariots']['y'] + E['chariots']['h']*0.18),
    (E['cart_events']['x'], E['cart_events']['cy']),
    '1', 'N', CE, rad=-0.18)

# rfid_scanners → cart_events
rel(ax, E['rfid_scanners']['R'],
        E['cart_events']['T'],
        '1', 'N', CE, rad=0.28)

# mission_groupes → cart_missions (right side, upper portion)
rel(ax,
    E['mission_groupes']['L'],
    (E['cart_missions']['x']+E['cart_missions']['w'],
     E['cart_missions']['y'] + E['cart_missions']['h'] - HDR_H*0.6),
    '1', 'N', CD, rad=0.12)

# ─── REFERENCES LOGIQUES (dashed) ──────────────────────────────
rel(ax,
    E['cart_missions']['R'],
    E['pristina_catalogue']['L'],
    'ref', 'gamme_code', CR, rad=0.0, dashed=True)

rel(ax,
    (E['cart_mission_jobs']['x']+E['cart_mission_jobs']['w'],
     E['cart_mission_jobs']['cy']),
    E['jobs_planning']['L'],
    'ref', 'of_number', CR, rad=0.22, dashed=True)

# ─── LEGENDE TYPE ──────────────────────────────────────────────
ax.add_patch(mpatches.Rectangle(
    (0.2, 0.1), 25.5, 0.65, fc='#E2E8F0', ec='none', zorder=0, alpha=0.7))

legend_items = [
    (CS, 'Statique  (referentiel)'),
    (CD, 'Dynamique  (runtime)'),
    (CQ, 'Oracle Move Queue'),
    (CR, 'Oracle / Catalogue'),
    (CE, 'Evenements historique'),
]
for i, (c, l) in enumerate(legend_items):
    lx = 0.5 + i*5.1
    ax.add_patch(mpatches.Rectangle((lx, 0.22), 0.38, 0.22, fc=c, ec='none'))
    ax.text(lx+0.48, 0.33, l, va='center', fontsize=8.5, color='#1E293B')

# Legende attributs
ax.text(12.0, 0.33, ' [PK] = Cle primaire', va='center', fontsize=7.5,
        color=CS, fontweight='bold', fontfamily='monospace')
ax.text(15.0, 0.33, '[FK] = Cle etrangere', va='center', fontsize=7.5,
        color=CQ, fontweight='bold', fontfamily='monospace')
ax.text(18.2, 0.33, '[UQ] = Unique', va='center', fontsize=7.5,
        color=CR, fontweight='bold', fontfamily='monospace')
ax.text(20.8, 0.33, '--- = Ref logique', va='center', fontsize=7.5,
        color=CR, fontfamily='monospace')

# ─── TITRE ─────────────────────────────────────────────────────
ax.text(13, 16.5, 'MCD — Base de donnees rfid_buc',
        ha='center', va='center', fontsize=17,
        fontweight='bold', color='#1E2761')
ax.text(13, 16.0, 'Projet RFID  |  GE Healthcare Buc  |  Ligne Pristina  |  9 tables',
        ha='center', va='center', fontsize=10, color='#64748B')

# Zone separatrice colonnes (subtle)
for xv in [4.7, 12.8, 19.8]:
    ax.plot([xv]*2, [0.85, 15.5], color='#CBD5E0', lw=0.8, ls='--', zorder=0, alpha=0.6)

# Labels colonnes
for (xv, lbl) in [(2.4, 'STATIQUE'), (8.7, 'DYNAMIQUE'), (15.9, 'REF / EVENTS'), (22.8, 'GROUPES / ORACLE')]:
    ax.text(xv, 15.6, lbl, ha='center', va='center', fontsize=8,
            color='#94A3B8', fontweight='bold')

plt.tight_layout(pad=0.3)
plt.savefig(r'C:\Users\ADMIN\Desktop\rfid\MCD_rfid_buc.png', dpi=150,
            bbox_inches='tight', facecolor='#F1F5F9')
print('[OK] MCD genere : C:\\Users\\ADMIN\\Desktop\\rfid\\MCD_rfid_buc.png')
