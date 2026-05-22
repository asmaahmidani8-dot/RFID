"""
Genere MCD_rfid_buc.drawio — 13 tables — fleches bien organisees
Ouvrir : app.diagrams.net > File > Open from > Device
"""

ROW_H = 26
HDR_H = 30

COLORS = {
    'static':  {'fill': '#003087', 'stroke': '#001F5B'},
    'dynamic': {'fill': '#00857C', 'stroke': '#005F58'},
    'queue':   {'fill': '#C0392B', 'stroke': '#922B21'},
    'ref':     {'fill': '#6C3483', 'stroke': '#4A235A'},
    'event':   {'fill': '#1E8449', 'stroke': '#145A32'},
    'monitor': {'fill': '#B7950B', 'stroke': '#7D6608'},
}

ROW_COLORS = {
    'PK': {'bg1': '#D6EAF8', 'fc1': '#003087', 'bg2': '#EBF5FB', 'fw': 1},
    'FK': {'bg1': '#FADBD8', 'fc1': '#C0392B', 'bg2': '#FDEDEC', 'fw': 1},
    'UQ': {'bg1': '#E8DAEF', 'fc1': '#6C3483', 'bg2': '#F3E5F5', 'fw': 1},
    '':   {'bg1': 'none',    'fc1': '#1E293B', 'bg2': 'none',    'fw': 0},
}

def make_table(tid, title, x, y, w, attrs, ctype):
    c = COLORS[ctype]
    h = HDR_H + len(attrs) * ROW_H
    out = []
    out.append(
        f'    <mxCell id="{tid}" value="{title}" '
        f'style="shape=table;startSize={HDR_H};container=1;collapsible=0;'
        f'childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;'
        f'align=center;resizeLast=1;fontSize=12;'
        f'fillColor={c["fill"]};fontColor=#FFFFFF;strokeColor={c["stroke"]};" '
        f'vertex="1" parent="1">'
    )
    out.append(f'      <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />')
    out.append(f'    </mxCell>')

    for i, attr in enumerate(attrs):
        lbl  = attr.get('lbl', '')
        name = attr['name']
        rc   = ROW_COLORS.get(lbl, ROW_COLORS[''])
        ry   = HDR_H + i * ROW_H
        rid  = f"{tid}_r{i}"
        ck   = f"{tid}_r{i}_k"
        cv   = f"{tid}_r{i}_v"
        alt  = '#F0F4FF' if (i % 2 == 0 and lbl == '') else 'none'

        out.append(
            f'    <mxCell id="{rid}" value="" '
            f'style="shape=tableRow;horizontal=0;startSize=0;'
            f'swimlaneHead=0;swimlaneBody=0;fillColor={alt};collapsible=0;dropTarget=0;'
            f'points=[[0,0.5],[1,0.5]];portConstraint=eastwest;'
            f'fontSize=11;top=0;left=0;right=0;bottom=1;" '
            f'vertex="1" parent="{tid}">'
        )
        out.append(f'      <mxGeometry y="{ry}" width="{w}" height="{ROW_H}" as="geometry" />')
        out.append(f'    </mxCell>')
        out.append(
            f'    <mxCell id="{ck}" value="{lbl}" '
            f'style="shape=partialRectangle;connectable=0;fillColor={rc["bg1"]};'
            f'top=0;left=0;bottom=0;right=0;fontStyle={rc["fw"]};fontSize=9;'
            f'overflow=hidden;fontColor={rc["fc1"]};" vertex="1" parent="{rid}">'
        )
        out.append(
            f'      <mxGeometry width="36" height="{ROW_H}" as="geometry">'
            f'<mxRectangle width="36" height="{ROW_H}" as="alternateBounds" /></mxGeometry>'
        )
        out.append(f'    </mxCell>')
        out.append(
            f'    <mxCell id="{cv}" value="{name}" '
            f'style="shape=partialRectangle;connectable=0;fillColor={rc["bg2"]};'
            f'top=0;left=0;bottom=0;right=0;overflow=hidden;fontSize=10;" '
            f'vertex="1" parent="{rid}">'
        )
        out.append(
            f'      <mxGeometry x="36" width="{w-36}" height="{ROW_H}" as="geometry">'
            f'<mxRectangle width="{w-36}" height="{ROW_H}" as="alternateBounds" /></mxGeometry>'
        )
        out.append(f'    </mxCell>')

    return '\n'.join(out)


def make_edge(eid, src, tgt, label='', dashed=False, color='#475569',
              ex=1, ey=0.5, nx=0, ny=0.5):
    """
    ex/ey = exit point (0-1) sur la cellule source
    nx/ny = entry point (0-1) sur la cellule cible
    Conventions :
      exitX=0  → sortie par la gauche
      exitX=1  → sortie par la droite
      entryX=0 → entree par la gauche
      entryX=1 → entree par la droite
    """
    dash = 'dashed=1;dashPattern=8 4;' if dashed else ''
    return (
        f'    <mxCell id="{eid}" value="{label}" '
        f'style="edgeStyle=entityRelationEdgeStyle;endArrow=ERmany;startArrow=ERone;'
        f'exitX={ex};exitY={ey};exitConstraint=0;'
        f'entryX={nx};entryY={ny};entryConstraint=0;'
        f'{dash}strokeColor={color};strokeWidth=1.8;fontSize=10;'
        f'fontColor={color};fontStyle=1;" '
        f'edge="1" source="{src}" target="{tgt}" parent="1">\n'
        f'      <mxGeometry relative="1" as="geometry" />\n'
        f'    </mxCell>'
    )


# ═══════════════════════════════════════════════════════
# TABLES — 4 colonnes
# ═══════════════════════════════════════════════════════
tables = [

    # ── COL 1 (x=20) — Statique ────────────────────────
    {
        'id': 'rfid_scanners', 'title': 'RFID_SCANNERS',
        'x': 20, 'y': 30, 'w': 230, 'color': 'static',
        'attrs': [
            {'lbl': 'PK', 'name': 'scanner_id'},
            {'lbl': '',   'name': 'nom'},
            {'lbl': '',   'name': 'localisation'},
            {'lbl': '',   'name': 'ip_address'},
            {'lbl': '',   'name': 'actif'},
        ]
    },
    {
        'id': 'gammes', 'title': 'GAMMES',
        'x': 20, 'y': 250, 'w': 230, 'color': 'static',
        'attrs': [
            {'lbl': 'PK', 'name': 'gamme_code'},
            {'lbl': '',   'name': 'gamme_label'},
        ]
    },
    {
        'id': 'chariots', 'title': 'CHARIOTS',
        'x': 20, 'y': 380, 'w': 230, 'color': 'static',
        'attrs': [
            {'lbl': 'PK', 'name': 'chariot_id'},
            {'lbl': '',   'name': 'nom'},
            {'lbl': '',   'name': 'job_type'},
            {'lbl': '',   'name': 'type_chariot'},
            {'lbl': '',   'name': 'operation_code'},
            {'lbl': '',   'name': 'poste'},
            {'lbl': '',   'name': 'feeder_num'},
            {'lbl': '',   'name': 'nb_ofs'},
            {'lbl': '',   'name': 'partie'},
            {'lbl': '',   'name': 'groupe_ref'},
            {'lbl': '',   'name': 'actif'},
        ]
    },
    {
        'id': 'rfid_cards', 'title': 'RFID_CARDS',
        'x': 20, 'y': 800, 'w': 230, 'color': 'static',
        'attrs': [
            {'lbl': 'PK', 'name': 'uid'},
            {'lbl': 'FK', 'name': 'chariot_id'},
            {'lbl': '',   'name': 'badge_type'},
            {'lbl': '',   'name': 'actif'},
        ]
    },

    # ── COL 2 (x=330) — Dynamique ──────────────────────
    {
        'id': 'cart_missions', 'title': 'CART_MISSIONS',
        'x': 330, 'y': 30, 'w': 250, 'color': 'dynamic',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'FK', 'name': 'chariot_id'},
            {'lbl': 'FK', 'name': 'groupe_id'},
            {'lbl': 'FK', 'name': 'gamme_code'},
            {'lbl': '',   'name': 'rfid_uid'},
            {'lbl': '',   'name': 'statut'},
            {'lbl': '',   'name': 'partie'},
            {'lbl': '',   'name': 'ts_preparee'},
            {'lbl': '',   'name': 'ts_en_attente'},
            {'lbl': '',   'name': 'ts_en_approche'},
            {'lbl': '',   'name': 'ts_retour'},
            {'lbl': '',   'name': 'ts_terminee'},
            {'lbl': '',   'name': 'actif'},
        ]
    },
    {
        'id': 'cart_mission_jobs', 'title': 'CART_MISSION_JOBS',
        'x': 330, 'y': 600, 'w': 250, 'color': 'dynamic',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'FK', 'name': 'mission_id'},
            {'lbl': 'FK', 'name': 'of_number + operation_code'},
            {'lbl': '',   'name': 'item_code'},
            {'lbl': '',   'name': 'item_desc'},
            {'lbl': '',   'name': 'statut'},
            {'lbl': '',   'name': 'cree_le'},
        ]
    },
    {
        'id': 'oracle_move_queue', 'title': 'ORACLE_MOVE_QUEUE',
        'x': 330, 'y': 920, 'w': 250, 'color': 'queue',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'FK', 'name': 'mission_job_id'},
            {'lbl': '',   'name': 'of_number'},
            {'lbl': '',   'name': 'operation_code'},
            {'lbl': '',   'name': 'qty'},
            {'lbl': '',   'name': 'exe_flag (N/P/D/E)'},
            {'lbl': '',   'name': 'erreur'},
            {'lbl': '',   'name': 'execute_le'},
        ]
    },

    # ── COL 3 (x=660) — Ref / Events ───────────────────
    {
        'id': 'pristina_catalogue', 'title': 'PRISTINA_CATALOGUE',
        'x': 660, 'y': 30, 'w': 270, 'color': 'ref',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'UQ', 'name': 'gamme_code + item_code'},
            {'lbl': 'FK', 'name': 'gamme_code'},
            {'lbl': '',   'name': 'item_code'},
            {'lbl': '',   'name': 'item_desc'},
            {'lbl': '',   'name': 'feeder_num'},
            {'lbl': '',   'name': 'job_type'},
        ]
    },
    {
        'id': 'cart_events', 'title': 'CART_EVENTS',
        'x': 660, 'y': 450, 'w': 260, 'color': 'event',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'FK', 'name': 'mission_id'},
            {'lbl': 'FK', 'name': 'chariot_id'},
            {'lbl': 'FK', 'name': 'scanner_id'},
            {'lbl': '',   'name': 'evenement'},
            {'lbl': '',   'name': 'rfid_uid'},
            {'lbl': '',   'name': 'ts'},
        ]
    },
    {
        'id': 'oracle_transaction_logs', 'title': 'ORACLE_TRANSACTION_LOGS',
        'x': 660, 'y': 730, 'w': 270, 'color': 'queue',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'FK', 'name': 'queue_id'},
            {'lbl': '',   'name': 'statut (SUCCESS/ERROR/RETRY)'},
            {'lbl': '',   'name': 'retry_count'},
            {'lbl': '',   'name': 'error_message'},
            {'lbl': '',   'name': 'executed_at'},
        ]
    },

    # ── COL 4 (x=1010) ─────────────────────────────────
    {
        'id': 'jobs_planning', 'title': 'JOBS_PLANNING',
        'x': 1010, 'y': 30, 'w': 270, 'color': 'ref',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'UQ', 'name': 'of_number + operation_code'},
            {'lbl': '',   'name': 'of_number'},
            {'lbl': '',   'name': 'operation_code'},
            {'lbl': '',   'name': 'item_code'},
            {'lbl': '',   'name': 'item_desc'},
            {'lbl': '',   'name': 'statut'},
            {'lbl': '',   'name': 'qty_totale'},
            {'lbl': '',   'name': 'qty_faite'},
            {'lbl': '',   'name': 'date_besoin'},
        ]
    },
    {
        'id': 'mission_groupes', 'title': 'MISSION_GROUPES',
        'x': 1010, 'y': 420, 'w': 250, 'color': 'dynamic',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': '',   'name': 'cree_le'},
        ]
    },
    {
        'id': 'system_health', 'title': 'SYSTEM_HEALTH',
        'x': 1010, 'y': 590, 'w': 260, 'color': 'monitor',
        'attrs': [
            {'lbl': 'PK', 'name': 'id'},
            {'lbl': 'UQ', 'name': 'service_name'},
            {'lbl': '',   'name': 'statut (OK/WARNING/ERROR)'},
            {'lbl': '',   'name': 'last_seen'},
            {'lbl': '',   'name': 'error_message'},
        ]
    },
]

# ═══════════════════════════════════════════════════════
# EDGES — routage precis par direction
#
# Regles :
#   col droite → col gauche  : exit gauche (ex=0), entree droite (nx=1)
#   col gauche → col droite  : exit droite (ex=1), entree gauche (nx=0)
#   meme colonne vers le bas : exit droite (ex=1), entree droite (nx=1) — boucle droite
#   meme colonne vers le haut: exit gauche (ex=0), entree gauche (nx=0) — boucle gauche
# ═══════════════════════════════════════════════════════
edges = [
    # ── rfid_cards → chariots
    # col1 meme colonne, rfid_cards EST EN DESSOUS de chariots
    # → boucle gauche : exit gauche de rfid_cards, entree gauche de chariots
    ('e1',  'rfid_cards_r1',
             'chariots_r0',
             '', False, '#003087',
             0, 0.5,   # exit gauche
             0, 0.5),  # entree gauche

    # ── pristina_catalogue → gammes
    # col3 → col1 : exit gauche, entree droite
    ('e2',  'pristina_catalogue_r2',
             'gammes_r0',
             '', False, '#6C3483',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_missions → chariots
    # col2 → col1 : exit gauche, entree droite
    ('e3',  'cart_missions_r1',
             'chariots_r0',
             '', False, '#003087',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_missions → mission_groupes
    # col2 → col4 : exit droite, entree gauche
    ('e4',  'cart_missions_r2',
             'mission_groupes_r0',
             '', False, '#00857C',
             1, 0.5,   # exit droite
             0, 0.5),  # entree gauche

    # ── cart_missions → gammes
    # col2 → col1 : exit gauche, entree droite
    ('e5',  'cart_missions_r3',
             'gammes_r0',
             '', False, '#00857C',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_mission_jobs → cart_missions
    # col2 meme colonne, cart_mission_jobs EST EN DESSOUS
    # → boucle droite : exit droite, entree droite
    ('e6',  'cart_mission_jobs_r1',
             'cart_missions_r0',
             '', False, '#00857C',
             1, 0.5,   # exit droite
             1, 0.5),  # entree droite

    # ── cart_mission_jobs → jobs_planning
    # col2 → col4 : exit droite, entree gauche
    ('e7',  'cart_mission_jobs_r2',
             'jobs_planning_r1',
             '', False, '#6C3483',
             1, 0.5,   # exit droite
             0, 0.5),  # entree gauche

    # ── oracle_move_queue → cart_mission_jobs
    # col2 meme colonne, oracle_move_queue EST EN DESSOUS
    # → boucle droite : exit droite, entree droite
    ('e8',  'oracle_move_queue_r1',
             'cart_mission_jobs_r0',
             '', False, '#C0392B',
             1, 0.5,   # exit droite
             1, 0.5),  # entree droite

    # ── oracle_transaction_logs → oracle_move_queue
    # col3 → col2 : exit gauche, entree droite
    ('e9',  'oracle_transaction_logs_r1',
             'oracle_move_queue_r0',
             '', False, '#C0392B',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_events → cart_missions
    # col3 → col2 : exit gauche, entree droite
    ('e10', 'cart_events_r1',
             'cart_missions_r0',
             '', False, '#1E8449',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_events → chariots
    # col3 → col1 : exit gauche, entree droite
    ('e11', 'cart_events_r2',
             'chariots_r0',
             '', False, '#1E8449',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── cart_events → rfid_scanners
    # col3 → col1 en haut : exit gauche, entree droite
    ('e12', 'cart_events_r3',
             'rfid_scanners_r0',
             '', False, '#1E8449',
             0, 0.5,   # exit gauche
             1, 0.5),  # entree droite

    # ── pristina_catalogue → jobs_planning  (ref logique, pointille)
    # col3 → col4 : exit droite, entree gauche
    ('e13', 'pristina_catalogue_r3',
             'jobs_planning_r4',
             'item_code', True, '#6C3483',
             1, 0.5,   # exit droite
             0, 0.5),  # entree gauche
]

# ═══════════════════════════════════════════════════════
# BUILD XML
# ═══════════════════════════════════════════════════════
xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxGraphModel dx="1800" dy="900" grid="1" gridSize="10" guides="1"
  tooltips="1" connect="1" arrows="1" fold="1" page="1"
  pageScale="1" pageWidth="1654" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
'''

for t in tables:
    xml += make_table(
        t['id'], t['title'], t['x'], t['y'], t['w'], t['attrs'], t['color']
    ) + '\n'

for e in edges:
    xml += make_edge(*e) + '\n'

xml += '  </root>\n</mxGraphModel>\n'

out = r'C:\Users\ADMIN\Desktop\rfid\MCD_rfid_buc.drawio'
with open(out, 'w', encoding='utf-8') as f:
    f.write(xml)

print(f'[OK] {out}')
print('     app.diagrams.net > File > Open from > Device')
