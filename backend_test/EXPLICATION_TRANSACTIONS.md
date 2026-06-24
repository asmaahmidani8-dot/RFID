# 📘 Explication complète — Système de Transactions / Move MSCA
**GE Healthcare Buc · Ligne Pristina · Projet RFID (STRAXI)**

> Ce document explique **le sujet** (pourquoi et comment) et **tout le code** du système
> de transactions Oracle (les « moves ») piloté depuis l'application web.

---

## 1. Le sujet — de quoi parle-t-on ?

### Le besoin
Sur la ligne Pristina, quand un chariot de composants est **consommé** à un poste,
il faut enregistrer dans **Oracle (EBS)** que l'opération a avancé : c'est une
**Move Transaction** (WIP Move). Aujourd'hui c'est fait à la main dans MSCA.
Le projet RFID **automatise** ce move depuis l'application web.

### Le problème à résoudre
- Le move MSCA est **lent** (~1-2 min par opération, via une session telnet).
- Si **2 personnes** lancent un move **en même temps** avec le même compte Oracle →
  les 2 sessions telnet se mélangent → **désynchronisation** → erreurs.
- Il faut respecter **l'ordre des opérations** (OP10 avant OP20 avant OP25…).
- Certains chariots (Type B) sont en **paire** (même job/op) → 1 seul move suffit.

### La solution : une FILE + un WORKER (modèle HINO)
Au lieu de faire le move directement, on **empile** la demande dans une file
(`oracle_move_queue`), et **un seul worker** (`oracle_msca.py`) traite les moves
**un par un**. Résultat :
- ✅ Jamais 2 telnet MSCA en même temps → pas de désync
- ✅ Le clic « Move » répond **instantanément** (il enregistre juste)
- ✅ Retry automatique en cas d'échec
- ✅ Traçabilité complète (qui, quand, succès/erreur)

---

## 2. L'architecture en un schéma

```
┌──────────────┐   clic Move    ┌─────────────────────┐
│  Page Web    │ ─────────────▶ │  app.py (Flask)     │
│ Transactions │                │  /api/.../move      │
└──────────────┘                │  → INSERT file (N)  │
                                │  → lance le worker  │
                                └─────────┬───────────┘
                                          │
                          ┌───────────────▼────────────────┐
                          │   oracle_move_queue (la FILE)   │
                          │   exe_flag : N → P → D / E       │
                          └───────────────┬─────────────────┘
                                          │ prend 1 par 1
                          ┌───────────────▼─────────────────┐
                          │  oracle_msca.py (le WORKER)      │
                          │  → msca_move.do_move() en telnet │
                          │  → met à jour le flag + logs     │
                          └───────────────┬─────────────────┘
                                          │ telnet
                          ┌───────────────▼─────────────────┐
                          │   MSCA / MWA (Oracle EBS)         │
                          │   "Txn Success"                   │
                          └──────────────────────────────────┘
```

**Les états (`exe_flag`) d'une demande de move :**
| Flag | Sens | Affichage page |
|------|------|----------------|
| `N`  | Not done — en attente dans la file | ⏳ En file |
| `P`  | Pending — en cours d'exécution telnet | 🔄 En cours MSCA |
| `D`  | Done — succès Oracle | ✅ Movéé |
| `E`  | Error — échec après tentatives | ❌ Erreur — Réessayer |

---

## 3. Les tables de la base (MySQL `rfid_buc`)

### `oracle_move_queue` — la FILE
| Colonne | Sens |
|---------|------|
| `id` | numéro de la demande |
| `mission_job_id` | quel job (FK → cart_mission_jobs) |
| `of_number` | le job Oracle (OF) |
| `operation_code` | l'opération à mover |
| `item_code` | l'article |
| `qty` | quantité (1) |
| `exe_flag` | **N / P / D / E** |
| `erreur` | message d'erreur si E |
| `cree_le` | heure de création (au clic Move) |
| `execute_le` | heure d'exécution par le worker |

### `oracle_transaction_logs` — les LOGS (1 ligne par tentative)
| Colonne | Sens |
|---------|------|
| `queue_id` | quelle demande de la file (FK) |
| `status` | **OK / RETRY / ERROR** |
| `retry_count` | numéro de la tentative |
| `error_message` | message Oracle si problème |
| `executed_at` | heure de la tentative |

Exemple de logs pour une move qui réussit au 2ᵉ essai :
```
queue_id=1  status=RETRY  retry=1  error="MSCA timeout"
queue_id=1  status=OK     retry=2
```

### `job_routing` — l'ORDRE des opérations (récupéré d'Oracle)
| Colonne | Sens |
|---------|------|
| `of_number` | le job |
| `operation_seq_num` | **le numéro de séquence Oracle** (= l'ordre : 10, 20, 25, 90…) |
| `count_point` | l'op est-elle un point de comptage (move requis) ? |
| `backflush` | l'op fait-elle un backflush de composants ? |

---

## 4. Le flux complet, étape par étape

### Étape A — Le clic « Move » (app.py)
Quand l'opérateur clique **Move** sur un chariot :
1. On lit tous les jobs du chariot.
2. Pour chaque job **prêt** (= l'op la plus basse non-movéé de son OF), on **empile**
   une ligne dans `oracle_move_queue` avec `exe_flag='N'`.
3. **Protection doublon Type B** : si une move N/P/D existe déjà pour ce même
   `of_number + operation_code` → on **n'empile pas** (les 2 chariots d'une paire = 1 seul move).
4. On **lance le worker** automatiquement (s'il ne tourne pas déjà).
5. Réponse **immédiate** au navigateur.

```python
# app.py — empilage d'un job (avec protection doublon)
def _enqueue_job(cur, job):
    if job["statut"] == 'MOVE_DONE':
        return False, "déjà movéé"
    # doublon Type B : move N/P/D déjà existante pour ce of+op → SKIP
    cur.execute("""
        SELECT COUNT(*) AS n FROM oracle_move_queue omq
        JOIN cart_mission_jobs cmj ON cmj.id = omq.mission_job_id
        WHERE cmj.of_number=%s AND cmj.operation_code=%s
          AND omq.exe_flag IN ('N','P','D')
    """, (job["of_number"], job["operation_code"]))
    if cur.fetchone()["n"] > 0:
        return False, "doublon ignoré"
    # empilage
    cur.execute("""INSERT INTO oracle_move_queue
        (mission_job_id, of_number, operation_code, item_code, qty, exe_flag)
        VALUES (%s,%s,%s,%s,1,'N')""",
        (job["id"], job["of_number"], job["operation_code"], job.get("item_code")))
    return True, "ajoutée à la file"
```

### Étape B — Le worker traite la file (oracle_msca.py)
Le worker tourne en boucle :
1. Prend la **plus ancienne** demande `N` → la passe en `P`.
2. Si l'op est sérialisée, récupère un n° de série (`get_sn_for_op`).
3. Exécute le move telnet (`do_move`), avec **retry** (3 tentatives).
4. Succès → `D` + `cart_mission_jobs.statut='MOVE_DONE'`. Échec → `E` + message.
5. Trace chaque tentative dans `oracle_transaction_logs`.

```python
# oracle_msca.py — le cœur du worker
def fetch_next(db):
    # prend 1 demande "N" (la plus ancienne) et la passe en "P"
    cur.execute("""SELECT ... FROM oracle_move_queue
                   WHERE exe_flag='N' ORDER BY cree_le ASC LIMIT 1""")
    ...
    cur.execute("UPDATE oracle_move_queue SET exe_flag='P' WHERE id=%s", (row["id"],))

def execute_move(db, row):
    for attempt in range(1, MAX_RETRY+1):
        res = msca_move.do_move(session, ..., of_number, to_seq, qty, sn)
        if res["success"]:
            # D + MOVE_DONE
            UPDATE oracle_move_queue SET exe_flag='D' ...
            UPDATE cart_mission_jobs  SET statut='MOVE_DONE' ...
            return
        # sinon retry, et au bout de MAX_RETRY → E
```

---

## 5. L'ordre des moves — le ROUTING (très important)

### Le principe
Un job passe par ses opérations **dans l'ordre** : `OP10 → OP20 → OP25 → … → OP90`.
On **ne peut pas** mover une op tant que la précédente **du même job** n'est pas faite.

```
Job 29434505 :
   OP10  ✅ movéé      ← fait
   OP20  🟢 PRÊT        ← son tour
   OP25  ⏳ Attente     ← bloqué (OP20 pas fait)
```

### D'où vient l'ordre ?
**D'Oracle.** Chaque produit a un **routing** défini (`WIP_OPERATIONS.OPERATION_SEQ_NUM`).
À l'assignation du chariot, on récupère ce routing et on le stocke dans `job_routing` :

```python
# sync_oracle.py — fetch_routing_for_of (appelé à l'assignation)
SELECT wen.WIP_ENTITY_NAME, wop.OPERATION_SEQ_NUM, wop.COUNT_POINT_TYPE, wop.BACKFLUSH_FLAG
FROM WIP_OPERATIONS wop, WIP_ENTITIES wen
WHERE wop.WIP_ENTITY_ID = wen.WIP_ENTITY_ID
  AND wen.WIP_ENTITY_NAME IN (...)
ORDER BY wen.WIP_ENTITY_NAME, wop.OPERATION_SEQ_NUM
```

### Comment la page décide « qui est prêt »
**Par job** (`of_number`) : l'op la plus basse non-movéé est la prochaine. Les autres attendent.

```python
# app.py — l'op prête de chaque job
min_pending = {}            # of_number -> plus petit op non-movéé
for r in rows:
    if r["job_statut"] != 'MOVE_DONE':
        of = r["of_number"]
        n  = _op_num(r["operation_code"])   # "OP20" -> 20
        if of not in min_pending or n < min_pending[of]:
            min_pending[of] = n
# un job est PRÊT si son op == l'op min non-movéé DE SON of_number
r["ready"] = (not r["moved"]) and (min_pending.get(r["of_number"]) == r["op_num"])
```

➡️ Comme les codes (OP10, OP20…) **sont** les numéros de séquence Oracle, comparer
les numéros = suivre le routing. **Chaque job a sa propre séquence, indépendante des autres.**

---

## 6. Le move MSCA — navigation INTELLIGENTE (msca_move.py)

Le move se fait via une **session telnet** vers MSCA/MWA. Le code **lit l'écran**
et **décide tout seul** — il ne tape jamais des numéros « à l'aveugle ».

### Les principes anti-erreur
1. **Anti-désync** : avant chaque saisie, on **attend** le bon écran (par un marqueur texte),
   au lieu de compter des lectures.
2. **Navigation pilotée par lecture** : on **lit le menu** et on cherche le numéro de la ligne
   « Manufacturing », « Assy & Material », « Move Assy » — peu importe l'ordre.
3. **Responsabilité adaptative** : si le compte a **une seule** responsabilité, MSCA saute
   l'écran de choix → le code le **détecte** et ne tape pas « 1 » par erreur.
4. **Série automatique** : si l'écran « Parent SN » apparaît (op sérialisée), le code saisit
   le n° de série ; sinon il fait un move normal. Il **comprend** selon l'écran.

```python
# msca_move.py — choisir une option de menu en LISANT son numéro
def _menu_number(screen, keyword):
    # ex: "3. Manufacturing" + keyword="manufacturing" -> "3"
    for line in screen.splitlines():
        m = re.match(r"\s*(\d+)\s*[\.\)\-]?\s+(.*)", line)
        if m and keyword.lower() in m.group(2).lower():
            return m.group(1)
    return None

# responsabilité : si on est DÉJÀ dans le menu (mono-responsabilité) → on ne touche à rien
if not _has(scr, MENU_MARKERS):
    num = _menu_number(scr, "mobile user") or NAV_RESP
    session.send(num)
```

### La navigation complète
```
Device List → Default
Login : user + mot de passe + Database GLTEST (pré-rempli)
[Responsabilité : choisie SEULEMENT si une liste apparaît]
Menu → Manufacturing → Assy & Material Txn → Move Assy
Org Code → BXD
Job → To Seq → To Step "To move"
→ Entrée jusqu'à <Save> → "Txn Success"
```

---

## 7. La page Transactions (transactions.html)

- **1 ligne = 1 chariot**. Le bouton **Move** empile **tous les jobs prêts** du chariot.
- **Sous-onglets de filtre** : 📋 Tous · 🟢 Prêt à mover · ⏳ Attente de l'ordre ·
  ✅ Move avec succès · ❌ Erreurs.
- **Auto-refresh** tant qu'une move est en file/en cours → la page passe
  ⏳ → 🔄 → ✅ toute seule.

---

## 8. Les fichiers du système

| Fichier | Rôle |
|---------|------|
| `app.py` | l'application web Flask (pages + API). Route `/transactions`, `/api/transactions/move`, `/api/transactions/move-chariot`, lancement auto du worker. |
| `oracle_msca.py` | **le worker** : traite la file un par un, retry, logs, flags. |
| `msca_move.py` | **le move MSCA** : navigation telnet intelligente (`do_move`). |
| `sync_oracle.py` | sync Oracle : jobs released, **routing** (`fetch_routing_for_of`), n° de série (`get_sn_for_op`). |
| `templates/transactions.html` | la page (tableau par chariot + filtres). |

---

## 9. Résumé en une phrase

> Quand on clique **Move**, l'app **empile** la demande dans une file (`oracle_move_queue`),
> et **un seul worker** (`oracle_msca.py`) fait les moves MSCA **un par un**, **dans l'ordre
> du routing** de chaque job, en **lisant l'écran** pour éviter les erreurs, avec **retry**
> et **traçabilité** — sans jamais bloquer l'opérateur ni risquer une désynchronisation.
