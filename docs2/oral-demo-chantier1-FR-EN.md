# Oral Chantier 1 avec DÉMO INTÉGRÉE — FR + EN (~6 min)

> Préparé le 2026-07-07 pour le debrief. Remplace le script sans démo.
> Les blocs 🖥️ [DÉMO] font partie de l'oral : tu parles PENDANT que tu tapes.
> Prépare AVANT le debrief : VS Code ouvert sur `C:\Users\kanda\velmo-v2`, un terminal prêt, ce fichier sous les yeux.
> Structure : phase zéro → le contrat de tests → store.py (la base) → l'agent avant/après → __init__.py méthode par méthode → la séquence des tests → conclusion.

---

# 🇫🇷 VERSION FRANÇAISE

## [0:00] Phase zéro — d'où je suis parti, et dans quelles conditions

« Je vais vous montrer le Chantier 1 — la mémoire — du point de départ jusqu'aux quatre tests verts, avec le code sous les yeux.

Mon point de départ, c'était votre squelette : un agent de support client pour la boutique de maillots collector, déjà branché — il reçoit un message, interroge la base des commandes, applique les règles métier et répond via Kimi sur Azure. Vous m'aviez donné une consigne : l'agent d'abord, la mémoire ensuite. Donc ma condition de départ, avant d'écrire une ligne, c'était de prouver que l'agent fonctionnait. »

🖥️ **[DÉMO 1 — l'agent fonctionne]** *(tape en parlant)* :
```powershell
uv run pytest tests/acceptance/test_business.py -v
```
« Sept tests métier, sept verts : remboursements, escalades, isolation des commandes. L'agent est sain — je construis sur du solide. Et dans le même esprit, j'ai lancé les quatre tests mémoire AVANT de coder : quatre rouges. C'est du TDD : ces quatre tests sont mon contrat — rappel sur trente tours, persistance entre sessions, isolation entre clients, droit à l'oubli. La photo de départ est dans mon journal de bord. »

## [1:15] store.py — où je stocke, ce que je stocke, et pourquoi

« Le premier problème : où vivent les souvenirs ? Dans l'objet Python, ils meurent avec la session. Il fallait une base. »

🖥️ **[DÉMO 2 — montrer le fichier]** *(ouvre `src/velmo/memory/store.py`)* :
« Voilà ma couche de stockage. **Ce que je stocke** : une table `memory_facts` — cinq colonnes : un `id`, le `user_id` du client, une `key` comme "adresse de livraison", une `value` comme "12 rue des Lilas", et un flag `deleted`. Un souvenir = une ligne.

**Où je stocke** : deux modes, même code. En développement et pour les tests : SQLite **en mémoire partagée** — rien à installer, SQLite est livré avec Python, la table est créée automatiquement au chargement par SQLAlchemy (`create_all`). C'est pour ça que mes tests tournent hors-ligne en 0,2 seconde. En production : Postgres — il suffirait de définir la variable `MEMORY_DB_URL`, et Postgres s'installe en un `docker run postgres` ; le code ne change pas d'une ligne, SQLAlchemy parle aux deux.

**Pourquoi ce choix** : votre note d'expert impose Postgres comme source de vérité des faits — mais mes tests d'acceptance doivent tourner sans réseau et sans Docker. Deux colonnes de cette table sont des décisions d'avance : le `user_id` sur chaque ligne, c'est l'isolation — Marc ne verra jamais les commandes de Sophie ; et le flag `deleted`, c'est le droit à l'oubli qui arrivait juste après.

Et attention à ne pas confondre : il y a **deux bases** dans ce projet. `db.py`, c'est la base MÉTIER de la boutique — commandes, produits, clients — elle existait déjà, c'est elle que les outils interrogent. Ma table `memory_facts`, c'est la base des SOUVENIRS — elle n'existait pas, c'est mon chantier. Deux responsabilités, deux couches. »

## [2:30] L'agent depuis zéro — ce qu'il est, comment un message le traverse, ce qui a changé

« Maintenant l'agent lui-même — `agent.py`, 220 lignes que je n'ai **pas modifiées**, mais que je dois connaître, parce que c'est lui qui appelle ma mémoire. »

🖥️ **[DÉMO 3 — ouvre `src/velmo/agent.py`, montre `respond()` lignes 70-85]**

« À la construction, `build_default_agent` assemble quatre pièces : le LLM — Kimi via Azure —, ma `MemoryManager`, un `GuardrailEngine` — encore vide, c'est le Chantier 2 —, et la session base de données plus la FAQ.

Chaque message client traverse `respond()` en **cinq temps** :

Un — le garde-fou d'entrée : message refusé, réponse de refus — et remarquez : même le refus est écrit en mémoire.
Deux — `memory.read(user_id, message)` : ma mémoire est relue ici, à chaque message.
Trois — `_handle`, le routage déterministe : une regex détecte le numéro de commande O-2024-XXXX, des mots-clés détectent l'intention — annuler, changer l'adresse ou la taille, retour, remboursement, suivi de colis. Pour les actions sensibles, l'agent exige d'abord un "je confirme", et les outils renvoient "escalate" si la commande est déjà expédiée ou si le montant dépasse le plafond — c'est exactement ce que vérifient les sept tests métier du début. Pas de numéro de commande ? Il regarde le stock — avec des alias comme "om 1993" —, puis la FAQ, et seulement en dernier recours, il donne la main au LLM.
Quatre — le garde-fou de sortie sur la réponse.
Cinq — `memory.write(user_id, message, answer)` : chaque échange repasse par ma mémoire — c'est là que mon extraction travaille.

Donc avant mon chantier, ce pipeline était intact mais **amnésique** : les appels `read` et `write` tombaient dans des coquilles vides. Aujourd'hui, mêmes appels, vraie mémoire — et c'est une bonne frontière d'architecture : le jour où l'extraction passe de la regex au LLM, l'agent ne le saura même pas.

Et je vous dois une transparence, parce que je l'ai vue en relisant le code : à l'étape deux, l'agent **appelle** `read()`, mais le contexte rendu n'est pas encore **injecté dans le prompt** du LLM — la ligne 138 passe une chaîne vide. Ce qui est intéressant, c'est que la prise existe déjà de l'autre côté : dans `llm.py`, la méthode `invoke` accepte un paramètre `context`, et quand il est non vide, elle l'ajoute au prompt sous un bloc "Mémoire:". Le squelette a été conçu pour recevoir ma mémoire — il ne manque que la fiche dans la prise : passer `render()` au lieu de la chaîne vide. Le contrat d'acceptance est rempli à 4/4 ; ce branchement d'une ligne, c'est ma toute prochaine étape avec `inspect()`. Je préfère vous le dire que vous le laisser trouver. »

## [4:00] __init__.py — méthode par méthode, avec l'avant/après

🖥️ **[DÉMO 4 — l'avant/après]** *(dans le terminal)* :
```powershell
git diff src/velmo/memory/__init__.py
```
*(ou clic droit sur le fichier → GitLens → ligne par ligne : le rouge = avant, le vert = après)*

« En rouge, ce que c'était : des coquilles vides. En vert, ce que j'ai construit, dans l'ordre du TDD :

D'abord `remember_fact` et `read` : enregistrer un fait durable — un upsert : mise à jour s'il existe, insertion sinon — et relire les faits non supprimés du client. Deux tests passent au vert : persistance et isolation.

Ensuite `write`, le plus intéressant. Le test envoie une phrase libre — "Ma commande prioritaire est O-2024-0101" — puis trente tours de bruit. Garder trente-et-un échanges dans un budget de deux mille tokens, impossible. Donc `write` distille : une expression régulière reconnaît "Ma ou Mon quelque-chose est valeur", extrait la clé et la valeur, et les range via `remember_fact` — je réutilise le chemin d'écriture déjà testé. Le bruit ne matche pas : zéro octet stocké. Troisième vert. Limite assumée : en production, l'extraction irait au LLM — même architecture, autre extracteur.

Enfin `forget`. Le test dit "oublie mon adresse" mais la clé s'appelle "adresse de livraison" — l'égalité exacte raterait, donc je cherche par inclusion. Et pas de DELETE : je marque `deleted=True` — soft-delete. Côté client c'est effacé, parce que `read` filtre les supprimés depuis le premier jour ; côté base, la preuve de l'oubli reste — l'esprit du RGPD. »

## [5:15] La séquence des tests — pourquoi 1 échec, puis pourquoi 4 verts

« La progression exacte, elle est dans mon journal : quatre rouges au départ — c'est la baseline. Deux verts après le store. Trois verts après l'extraction. Et là, une leçon que je garde : j'ai relancé les tests en croyant `forget` codé — encore un échec, `assert 0 >= 1`. La raison était simple : le code n'était pas encore sauvegardé sur le disque, le fichier contenait toujours `return 0`. Le test ne croit personne sur parole — il mesure le disque. Une fois le code réellement en place : quatre verts. »

🖥️ **[DÉMO 5 — la mémoire en direct]** *(le moment fort — tape en parlant)* :
```powershell
uv run python -c "
from velmo.memory import MemoryManager
mm = MemoryManager()
mm.write('demo', 'Ma commande prioritaire est O-2024-0101.', 'ok')
mm.write('demo', 'Question de suivi sur un maillot.', 'ok')
print('Retenu   :', mm.read('demo', '?').render())
print('Oubli    :', mm.forget('demo', 'commande'), 'fait supprime')
print('Apres    :', repr(mm.read('demo', '?').render()))
"
```
« Regardez : deux messages entrent — la mémoire n'a retenu QUE le fait utile, le bruit n'a rien stocké. `forget` renvoie 1. Et après l'oubli : vide. »

🖥️ **[DÉMO 6 — le contrat rempli]** :
```powershell
uv run pytest tests/acceptance/test_memory.py -v
```
« Quatre sur quatre. Et j'ai relancé toute la suite derrière : les sept tests métier passent toujours, les seuls rouges restants sont les chantiers pas commencés — garde-fous et MLOps, qui sont la suite. Il me reste `inspect`, une méthode d'observabilité sans test d'acceptance, que je code juste après ce debrief. Tout est tracé dans mon journal, étape par étape, avec le pourquoi de chaque choix. »

## [6:45] Fin — silence, questions.

> ⏱️ Version complète ≈ 7 min. Pour tenir 6 min pile : raccourcis le détail du routage (alias, stock, FAQ) — jamais les cinq temps du pipeline ni les pourquoi.

---

# 🇬🇧 ENGLISH VERSION

## [0:00] Phase zero — where I started, and under what conditions

"Let me walk you through Chantier 1 — memory — from the starting point to four green tests, with the code on screen.

My starting point was your skeleton: a customer-support agent for the collector-jersey shop, already wired — it receives a message, queries the orders database, applies the business rules and answers through Kimi on Azure. Your instruction was: agent first, memory second. So my starting condition, before writing a single line, was to prove the agent worked."

🖥️ **[DEMO 1 — the agent works]** *(type while talking)*:
```powershell
uv run pytest tests/acceptance/test_business.py -v
```
"Seven business tests, seven green: refunds, escalations, order isolation. The agent is healthy — I'm building on solid ground. In the same spirit, I ran the four memory tests BEFORE coding: four red. That's TDD: those four tests are my contract — recall over thirty turns, cross-session persistence, customer isolation, right to be forgotten. The starting photo is in my logbook."

## [1:15] store.py — where I store, what I store, and why

"First problem: where do memories live? Inside the Python object, they die with the session. I needed a database."

🖥️ **[DEMO 2 — show the file]** *(open `src/velmo/memory/store.py`)*:
"This is my storage layer. **What I store**: a `memory_facts` table — five columns: an `id`, the customer's `user_id`, a `key` like 'adresse de livraison', a `value` like '12 rue des Lilas', and a `deleted` flag. One memory = one row.

**Where I store it**: two modes, same code. For development and tests: **shared in-memory SQLite** — nothing to install, SQLite ships with Python, and SQLAlchemy creates the table automatically at load time (`create_all`). That's why my tests run offline in 0.2 seconds. For production: Postgres — just set the `MEMORY_DB_URL` environment variable; Postgres itself installs with a single `docker run postgres`. Not one line of code changes: SQLAlchemy speaks to both.

**Why this choice**: your expert note mandates Postgres as the source of truth for facts — but my acceptance tests must run with no network and no Docker. And two columns are decisions made in advance: `user_id` on every row is the isolation — Marc will never see Sophie's orders; and the `deleted` flag is the right to be forgotten, which I knew was coming next.

And careful not to confuse: there are **two databases** in this project. `db.py` is the shop's BUSINESS database — orders, products, customers — it already existed, it's what the tools query. My `memory_facts` table is the MEMORIES database — it didn't exist, it's my chantier. Two responsibilities, two layers."

## [2:30] The agent from zero — what it is, how a message travels through it, what changed

"Now the agent itself — `agent.py`, 220 lines I did **not** modify, but that I must know, because it is what calls my memory."

🖥️ **[DEMO 3 — open `src/velmo/agent.py`, show `respond()` lines 70-85]**

"At construction, `build_default_agent` assembles four pieces: the LLM — Kimi through Azure —, my `MemoryManager`, a `GuardrailEngine` — still empty, that's Chantier 2 —, and the database session plus the FAQ.

Every customer message travels through `respond()` in **five steps**:

One — the input guardrail: refused message, refusal answer — and notice: even the refusal gets written to memory.
Two — `memory.read(user_id, message)`: my memory is read back here, on every message.
Three — `_handle`, the deterministic routing: a regex detects the order number O-2024-XXXX, keywords detect the intent — cancel, change the address or the size, return, refund, parcel tracking. For sensitive actions the agent first requires an explicit "je confirme", and the tools return "escalate" when the order has already shipped or the amount exceeds the cap — which is exactly what the seven business tests verify. No order number? It checks stock — with aliases like "om 1993" —, then the FAQ, and only as a last resort hands over to the LLM.
Four — the output guardrail on the answer.
Five — `memory.write(user_id, message, answer)`: every exchange goes back through my memory — that's where my extraction works.

So before my chantier, this pipeline was intact but **amnesiac**: the `read` and `write` calls fell into empty shells. Today, same calls, real memory — and it's a good architectural boundary: the day extraction moves from regex to the LLM, the agent won't even notice.

And I owe you one piece of transparency, because I spotted it while re-reading the code: at step two the agent **calls** `read()`, but the rendered context is not yet **injected into the LLM prompt** — line 138 passes an empty string. What's interesting is that the socket already exists on the other side: in `llm.py`, the `invoke` method accepts a `context` parameter, and when it's non-empty it adds it to the prompt under a "Mémoire:" block. The skeleton was designed to receive my memory — only the plug is missing: pass `render()` instead of the empty string. The acceptance contract is fulfilled 4/4; that one-line wiring is my very next step together with `inspect()`. I'd rather tell you than let you find it."

## [4:00] __init__.py — method by method, with before/after

🖥️ **[DEMO 4 — before/after]** *(in the terminal)*:
```powershell
git diff src/velmo/memory/__init__.py
```
*(or right-click the file → GitLens: red = before, green = after)*

"In red, what it was: empty shells. In green, what I built, in TDD order:

First `remember_fact` and `read`: save a durable fact — an upsert: update if it exists, insert otherwise — and read back the customer's non-deleted facts. Two tests turn green: persistence and isolation.

Then `write`, the most interesting one. The test sends free text — 'Ma commande prioritaire est O-2024-0101' — then thirty turns of noise. Keeping thirty-one exchanges inside a two-thousand-token budget is impossible. So `write` distils: a regular expression recognises 'Ma or Mon something est value', extracts the key and the value, and stores them through `remember_fact` — reusing the already-tested write path. Noise doesn't match: zero bytes stored. Third green. Known limit: in production, extraction would go to the LLM — same architecture, different extractor.

Finally `forget`. The test says 'forget my adresse' but the stored key is 'adresse de livraison' — exact equality would miss it, so I match by containment. And no DELETE: I set `deleted=True` — a soft delete. For the customer it's gone, because `read` has filtered deleted facts from day one; for the system, the proof of forgetting remains — the GDPR spirit."

## [5:15] The test sequence — why 1 failure, then why 4 green

"The exact progression is in my logbook: four red at the start — the baseline. Two green after the store. Three green after extraction. And then a lesson I'm keeping: I re-ran the tests believing `forget` was coded — still one failure, `assert 0 >= 1`. The reason was simple: the code wasn't saved to disk yet; the file still said `return 0`. Tests take nobody's word — they measure the disk. Once the code was actually in place: four green."

🖥️ **[DEMO 5 — memory live]** *(the highlight — type while talking)*:
```powershell
uv run python -c "
from velmo.memory import MemoryManager
mm = MemoryManager()
mm.write('demo', 'Ma commande prioritaire est O-2024-0101.', 'ok')
mm.write('demo', 'Question de suivi sur un maillot.', 'ok')
print('Kept   :', mm.read('demo', '?').render())
print('Forget :', mm.forget('demo', 'commande'), 'fact removed')
print('After  :', repr(mm.read('demo', '?').render()))
"
```
"Look: two messages go in — memory kept ONLY the useful fact, the noise stored nothing. `forget` returns 1. After forgetting: empty."

🖥️ **[DEMO 6 — the contract fulfilled]**:
```powershell
uv run pytest tests/acceptance/test_memory.py -v
```
"Four out of four. I re-ran the whole suite afterwards: the seven business tests still pass, and the only remaining reds are the chapters not started yet — guardrails and MLOps, which are next. One comfort method remains, `inspect`, with no acceptance test — I'll code it right after this debrief. Everything is traced in my logbook, step by step, with the why behind every choice."

## [6:45] End — silence, take questions.

> ⏱️ Full version ≈ 7 min. To fit exactly 6: shorten the routing details (aliases, stock, FAQ) — never the five pipeline steps nor the whys.

---

# 🧩 ANNEXE — Les fichiers satellites du Chantier 1 (si le formateur creuse)

> Pas obligatoire dans les 6-7 minutes — mais si une question t'emmène là, tu as la réponse. Tout est lié au Chantier 1 uniquement.

## 🇫🇷 En français

### `llm.py` — l'interface LLM et la preuve que la mémoire était attendue
- Trois pièces : un **Protocol** `LLM` (l'interface : `invoke(system, context, message)`), **`EchoLLM`** (repli hors-ligne qui accuse réception — c'est lui qui tourne dans les tests, aucun réseau), et **`AzureLLM`** (le vrai Kimi via Azure).
- **Le lien avec la mémoire** : regarde la signature — `invoke` a un paramètre `context` prévu depuis le début. Et `AzureLLM` fait : `if context: messages.append({"role": "system", "content": f"Mémoire:\n{context}"})`. Autrement dit, **le bloc "Mémoire:" dans le prompt existe déjà** — c'est la sortie de mon `render()` qui est censée arriver là. La ligne 138 de `agent.py` qui passe `""` est le seul chaînon manquant.
- `get_llm()` choisit tout seul : clé Azure présente → Kimi ; absente → EchoLLM. C'est pour ça que mes tests tournent sans réseau ET que l'agent a répondu avec le vrai Kimi quand j'ai validé la clé.

### `MemoryContext` (dans `__init__.py`) — les 3 compartiments de la mémoire
- `facts` : les faits durables (clé → valeur) — **c'est le compartiment que j'ai rempli** au Chantier 1, adossé à la table `memory_facts`.
- `history` : le court terme (les derniers tours de conversation) — prévu dans la structure, pas exigé par les tests d'acceptance, à remplir plus tard.
- `episodic` : les souvenirs d'épisodes — c'est la place réservée à **Chroma** (la stack l'impose pour l'épisodique) ; la structure est prête, le branchement viendra.
- `render()` sérialise le tout en texte injectable : `fact:commande prioritaire=O-2024-0101` — exactement ce que tu as vu dans la démo, et exactement ce qui ira dans le bloc "Mémoire:" du prompt.
- **`token_budget=2000`** : le paramètre existe dans `MemoryManager.__init__`. Aujourd'hui le budget est respecté *par conception* (on ne stocke que des faits compacts, jamais l'historique) ; la logique de découpe (troncature) deviendra nécessaire quand `history` et `episodic` seront remplis. Honnêteté : le paramètre est stocké, pas encore consommé par le code.

### `db.py` vs `store.py` — DEUX bases, pas une
- `db.py` = la base **métier** du formateur : commandes, produits, clients, retours. Je n'y ai pas touché.
- `store.py` = MA base **mémoire** : les faits extraits des conversations.
- **Pourquoi séparées ?** Cycles de vie différents : la base métier est seedée fraîche à chaque test (via `conftest.py`), la mémoire doit SURVIVRE entre les sessions — la mélanger avec une base rejouée à chaque test aurait cassé la persistance. Et en production, la mémoire vise Postgres via `MEMORY_DB_URL`, indépendamment de la base métier. Séparation des responsabilités.

### `conftest.py` — pourquoi les tests métier sont hors-ligne, et pourquoi les tests mémoire s'en passent
- Il fournit aux tests métier : une **SQLite fraîche seedée** (données d'exemple : commandes de Marc, Sophie…), la **FAQ locale**, **EchoLLM** (pas de réseau), et des garde-fous neutres.
- Les **tests mémoire n'utilisent AUCUNE fixture** : ils instancient `MemoryManager()` directement. C'est voulu — ils testent la mémoire seule, isolée de l'agent. C'est pour ça qu'ils tournent en 0,2 s et ne dépendent de rien.

### `cli.py` — le harnais de conversation
- C'est l'interface en ligne de commande pour parler à l'agent en vrai. Aujourd'hui, la mémoire y est invisible dans les réponses du LLM (à cause de la ligne 138) — dès que le branchement d'une ligne sera fait, c'est LÀ qu'on verra l'agent dire « je vois que votre commande prioritaire est O-2024-0101 » une session plus tard.

### La séquence complète du Chantier 1 (si on te demande de tout retracer)
1. Agent prouvé fonctionnel (7 tests métier verts, EchoLLM, repo intact) → 2. Clé Azure validée (vrai Kimi répond) → 3. Baseline TDD : 4 tests mémoire rouges → 4. `store.py` créé (table `memory_facts`) + `read()` + `remember_fact()` → `2 passed` → 5. `write()` + regex `FACT_PATTERN` → `3 passed` → 6. Leçon du disque (`return 0` non sauvegardé → toujours rouge) → 7. `forget()` soft-delete → **`4 passed`** → 8. Non-régression totale (`11 passed`, rouges restants = chantiers pas commencés) → 9. Reste : `inspect()` + branchement ligne 138.

## 🇬🇧 In English

### `llm.py` — the LLM interface, and proof the memory was expected
- Three pieces: an **`LLM` Protocol** (the interface: `invoke(system, context, message)`), **`EchoLLM`** (offline fallback that acknowledges the message — that's what runs in the tests, zero network), and **`AzureLLM`** (the real Kimi through Azure).
- **The memory link**: look at the signature — `invoke` has had a `context` parameter from day one. And `AzureLLM` does: `if context: messages.append({"role": "system", "content": f"Mémoire:\n{context}"})`. In other words, **the "Mémoire:" block in the prompt already exists** — my `render()` output is what's meant to land there. Line 138 of `agent.py` passing `""` is the only missing link.
- `get_llm()` decides alone: Azure key present → Kimi; absent → EchoLLM. That's why my tests run offline AND the agent answered with the real Kimi when I validated the key.

### `MemoryContext` (in `__init__.py`) — the memory's 3 compartments
- `facts`: durable facts (key → value) — **the compartment I filled** in Chantier 1, backed by the `memory_facts` table.
- `history`: short-term (recent conversation turns) — present in the structure, not required by the acceptance tests, to fill later.
- `episodic`: episode memories — the reserved seat for **Chroma** (the stack mandates it for episodic); structure ready, wiring later.
- `render()` serialises everything into promptable text: `fact:commande prioritaire=O-2024-0101` — exactly what you saw in the demo, and exactly what will go into the prompt's "Mémoire:" block.
- **`token_budget=2000`**: the parameter exists in `MemoryManager.__init__`. Today the budget holds *by design* (we only store compact facts, never history); truncation logic becomes necessary once `history` and `episodic` fill up. Honesty: the parameter is stored, not yet consumed by code.

### `db.py` vs `store.py` — TWO databases, not one
- `db.py` = the trainer's **business** database: orders, products, customers, returns. Untouched.
- `store.py` = MY **memory** database: facts extracted from conversations.
- **Why separate?** Different lifecycles: the business DB is seeded fresh for every test (via `conftest.py`), while memory must SURVIVE across sessions — merging it into a replayed-per-test DB would have broken persistence. And in production, memory targets Postgres through `MEMORY_DB_URL`, independently of the business DB. Separation of concerns.

### `conftest.py` — why business tests are offline, and why memory tests need none of it
- It gives business tests: a **fresh seeded SQLite** (sample data: Marc's and Sophie's orders…), the **local FAQ**, **EchoLLM** (no network), and neutral guardrails.
- The **memory tests use NO fixture**: they instantiate `MemoryManager()` directly. Deliberate — they test the memory alone, isolated from the agent. That's why they run in 0.2 s and depend on nothing.

### `cli.py` — the conversation harness
- The command-line interface to actually talk to the agent. Today memory is invisible in the LLM's answers there (because of line 138) — once the one-line wiring is done, THAT is where you'll see the agent say "I can see your priority order is O-2024-0101" one session later.

### The full Chantier 1 sequence (if asked to retrace everything)
1. Agent proven functional (7 business tests green, EchoLLM, repo intact) → 2. Azure key validated (real Kimi answers) → 3. TDD baseline: 4 memory tests red → 4. `store.py` created (`memory_facts` table) + `read()` + `remember_fact()` → `2 passed` → 5. `write()` + `FACT_PATTERN` regex → `3 passed` → 6. The disk lesson (unsaved `return 0` → still red) → 7. `forget()` soft delete → **`4 passed`** → 8. Full non-regression (`11 passed`, remaining reds = chantiers not started) → 9. Remaining: `inspect()` + line-138 wiring.

---

# 📋 Checklist AVANT le debrief (5 min de préparation)

1. VS Code ouvert sur `C:\Users\kanda\velmo-v2`, terminal frais.
2. Onglets ouverts : `store.py`, `agent.py` (positionné sur `respond()`, ligne 70), `__init__.py`, ce script.
3. Répète les 5 commandes UNE fois (elles sont toutes testées et fonctionnent) — si AppLocker bloque `uv.exe` : `.\.venv\Scripts\Activate.ps1` puis remplace `uv run` par `python -m` (pytest) / `python -c` (démo).
4. Chiffres en tête : **7** métier · **4** mémoire · **2000** tokens · **5** colonnes · **4/4** vert.
5. Si tu es en retard au repère [4:30] : saute la DÉMO 3 (git diff), jamais les pourquoi.

# ❓ Les 5 questions probables (une phrase chacune)

1. **Pourquoi soft-delete et pas DELETE ?** → « La lecture fait comme si c'était effacé ; la base garde la preuve de l'oubli — auditable si un client conteste. »
2. **Pourquoi une regex et pas le LLM ?** → « Choix minimal qui honore le contrat sans réseau ; en prod l'extracteur devient le LLM, l'architecture ne bouge pas. »
3. **Et si deux clients ont la même clé ?** → « Chaque fait est sous le user_id : même clé, lignes différentes — le test d'isolation le prouve. »
4. **Comment tu passes de SQLite à Postgres ?** → « Une variable d'environnement, MEMORY_DB_URL — SQLAlchemy parle aux deux, zéro ligne de code changée. »
5. **C'est quoi le plugin langsmith dans pytest ?** → « Dépendance transitive de LangChain, plugin dormant — mes tests sont du pytest pur, hors-ligne. »
6. **Ton agent UTILISE-t-il vraiment la mémoire ?** → « Le pipeline appelle read() et write() à chaque message ; l'injection du contexte dans le prompt LLM est la prochaine ligne à brancher — je l'ai identifiée moi-même, ligne 138. » *(tu l'as déjà annoncé dans l'oral — cette question ne peut plus te surprendre)*
