# Oral — Chantier 1 (Mémoire) TERMINÉ — pour le debrief formateur

> Mis à jour le 2026-07-07 après l'Étape 13 : **4/4 tests d'acceptance verts**. Debrief demain fin d'après-midi.
> 3 versions : ① récit pour le formateur (à dire), ② longue FR (à étudier), ③ longue EN (to study).
> Style : un RÉCIT — chaque étape enchaînée avec son pourquoi, pas de sections récitées.
> Le factuel est dans `JOURNAL-developpement-velmo.md` — ici c'est uniquement l'oral.

---

## ① Le récit pour le formateur (~2 min, à dire naturellement)

« Quand j'ai récupéré le squelette, vous m'aviez dit : l'agent d'abord, la mémoire ensuite. Donc avant de toucher quoi que ce soit, j'ai voulu voir l'agent tourner pour de vrai : j'ai installé les dépendances, lancé les 7 tests métier — tout vert — et vérifié que le repo restait intact. J'ai aussi testé la clé Azure, et Kimi m'a vraiment répondu, donc la chaîne complète est branchée.

Ensuite seulement, la mémoire. Mais avant d'écrire une seule ligne, j'ai lancé les 4 tests d'acceptance — tout rouge. Et c'est voulu : ces tests, c'est mon contrat. Tant que je ne les avais pas vus échouer, je ne savais pas précisément ce qu'on me demandait.

Le premier vrai problème, c'était : où vivent les souvenirs ? Si je les garde dans l'objet Python, ils meurent à la fin de la session — le test de persistance ne passera jamais. Donc j'ai créé une vraie table, `memory_facts`, avec SQLAlchemy dans `store.py`. SQLite pour développer, Postgres en prod via la variable `MEMORY_DB_URL` — parce que votre note d'expert impose Postgres comme source de vérité, mais mes tests doivent pouvoir tourner hors-ligne. Et en créant la table, j'ai mis chaque fait sous le `user_id` du client — c'est ce qui garantit que Marc ne verra jamais les commandes de Sophie — plus un flag `deleted`, parce que je savais que le droit à l'oubli arrivait juste derrière.

Là-dessus j'ai codé `remember_fact`, qui enregistre ou met à jour un fait durable, et `read`, qui relit les faits non supprimés du client. Deux tests sont passés au vert : la persistance entre sessions et l'isolation entre clients.

Le morceau suivant, c'était le rappel sur 30 tours. Le test envoie une phrase libre — "Ma commande prioritaire est O-2024-0101" — puis 30 tours de bruit, et exige que l'info ressorte à la fin. Garder les 31 échanges dans un budget de 2000 tokens, ça ne tient pas. Donc `write()` distille : une expression régulière reconnaît le motif "Ma ou Mon quelque-chose est valeur", extrait la clé et la valeur, et les range en base via `remember_fact` — je réutilise le chemin d'écriture déjà testé au lieu d'en créer un deuxième. Le bruit ne matche pas le motif, donc on ne stocke rien pour lui. Troisième test vert. Je connais la limite : une regex ne couvre que les formes prévues — en production, c'est le LLM qui ferait l'extraction ; la regex est le choix minimal qui honore le contrat de test.

Restait le droit à l'oubli. Le test dit "oublie mon adresse" — mais la clé stockée s'appelle "adresse de livraison". Chercher l'égalité exacte ne trouverait rien : je cherche donc les faits dont la clé ou la valeur *contient* le mot. Et je ne fais pas un DELETE : je marque `deleted=True` — un soft-delete. Côté client, c'est effacé, parce que `read()` filtre les faits supprimés depuis le début ; côté base, on garde la preuve que l'oubli a eu lieu — c'est l'esprit du RGPD. La méthode renvoie le nombre de faits supprimés, comme le test l'exige. Quatrième test vert.

Au final : les 4 tests d'acceptance mémoire passent, j'ai relancé toute la suite pour vérifier que rien d'autre n'a bougé — les seuls rouges restants sont les chantiers pas encore commencés, garde-fous et MLOps. Il me reste `inspect()`, qui n'a pas de test d'acceptance — je le code après ce debrief. Tout est tracé dans mon journal de bord, étape par étape, avec le pourquoi de chaque choix. »

**Questions probables et réponses courtes** :
- « Pourquoi soft-delete et pas DELETE ? » → « La lecture fait comme si c'était effacé, la base garde la preuve que l'oubli a eu lieu. Si un client conteste, on peut auditer. »
- « Pourquoi une regex et pas le LLM ? » → « Choix minimal qui honore le contrat de test sans dépendre du réseau. En prod, l'extraction irait au LLM ; l'architecture ne change pas, seul l'extracteur change. »
- « Et si deux clients ont la même clé ? » → « Chaque fait est rangé sous le `user_id` : même clé, lignes différentes, aucune fuite — c'est le test d'isolation qui le prouve. »

---

## ② Version LONGUE — pour étudier (FR)

### Le contexte en une phrase
Velmo 2.0 est un agent SAV de boutique de maillots collector ; le squelette du formateur (`C:\Users\kanda\velmo-v2`) fournit l'agent déjà branché, et mon travail du Chantier 1 était de remplir `src/velmo/memory/` pour que l'agent se souvienne des clients. **C'est fait : 4/4 tests verts.**

### Les fichiers en jeu (chemins exacts)
| Fichier | Rôle |
|---|---|
| `C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py` | La façade : classe `MemoryManager` (`read`, `write`, `remember_fact`, `forget`, `inspect`) + dataclass `MemoryContext` + regex `FACT_PATTERN` |
| `C:\Users\kanda\velmo-v2\src\velmo\memory\store.py` | La persistance : table `memory_facts` (SQLAlchemy), SQLite partagé en dev, Postgres si `MEMORY_DB_URL` est définie |
| `C:\Users\kanda\velmo-v2\tests\acceptance\test_memory.py` | Le CONTRAT : 4 tests = 4 exigences métier (R1, R2, R3, R5) — interdiction d'y toucher |
| `C:\Users\kanda\velmo-v2\docs\reco_expert.md` | La note d'expert qui IMPOSE la stack (Postgres + Chroma + Kimi/Azure) |

### La méthode : TDD (Test-Driven Development)
1. **Rouge d'abord** : 4 tests rouges = la photo de départ. Le test est le contrat : il dit *quoi* réussir, pas *comment*.
2. **Vert ensuite** : coder le minimum qui fait passer UN test, relancer, recommencer.
3. **Non-régression** : après chaque étape, relancer TOUTE la suite — aucun vert ne doit redevenir rouge.
4. **Leçon vécue** : un test relancé sans que le code soit sauvegardé sur le DISQUE reste rouge — le test mesure le disque, pas les intentions. (C'est arrivé à l'Étape 13 : `return 0` encore en place → `assert 0 >= 1` ; une fois le code réellement appliqué → vert.)

### Ce que chaque test vérifie — TOUT EST VERT
- **R2 — persistance** (`test_cross_session_persistence`) 🟢 : deux `MemoryManager` (= deux sessions) voient les mêmes faits. Les faits vivent dans la table `memory_facts`, pas dans l'objet Python.
- **R3 — isolation** (`test_isolation_between_customers`) 🟢 : chaque requête SQL filtre `WHERE user_id = ...` — Sophie ne voit jamais les données de Marc.
- **R1 — rappel 30 tours** (`test_recall_over_30_turns`) 🟢 : `write()` matche `FACT_PATTERN` = `\b(?:ma|mon)\s+(.+?)\s+est\s+(.+?)[.!?]?$` (insensible à la casse), extrait clé + valeur, appelle `remember_fact()`. Le bruit ne matche pas → rien stocké → budget 2000 tokens respecté.
- **R5 — droit à l'oubli** (`test_right_to_be_forgotten`) 🟢 : `forget(user, "adresse")` normalise la cible, charge les faits vivants du client, garde ceux dont la clé OU la valeur **contient** la cible (`"adresse" in "adresse de livraison"` → vrai), marque `deleted=True` (soft-delete), commit, renvoie le compte. `read()` filtrant `deleted=False` depuis l'Étape 11, l'adresse ne ressort plus — sans toucher à `read()`.
- **R6 — inspection** ⬜ : pas de test d'acceptance → codé après le debrief.

### La regex `FACT_PATTERN`, morceau par morceau (question d'oral probable)
| Morceau | Type | Rôle |
|---|---|---|
| `r"..."` | chaîne brute | le `r` empêche Python d'interpréter les `\` |
| `\b` | ancre | frontière de mot — évite que le « ma » de « **ma**illot » déclenche |
| `(?:ma\|mon)` | groupe non-capturant | accepte « Ma » ou « Mon » sans le mémoriser |
| `\s+` | classe | un ou plusieurs espaces |
| `(.+?)` | groupe 1 (capturant, paresseux) | la CLÉ — s'arrête au premier « est » |
| `\s+est\s+` | littéral | le pivot du motif |
| `(.+?)` | groupe 2 (capturant, paresseux) | la VALEUR |
| `[.!?]?$` | classe + ancre | avale la ponctuation finale pour qu'elle ne colle pas à la valeur |
| `re.IGNORECASE` | drapeau | insensible à la casse |

Compilée UNE fois au niveau du module (`re.compile` a un coût) ; `write()` réutilise `remember_fact()` → un seul chemin d'écriture en base.

### `forget()` ligne par ligne (question d'oral probable)
| Ligne | Rôle | Pourquoi |
|---|---|---|
| `needle = target.strip().lower()` | normalise la cible | les clés sont stockées en minuscules — comparaison à armes égales |
| `with Session() as session:` | session base auto-fermée | même motif que `read`/`remember_fact` |
| `select(...).where(user_id, deleted.is_(False))` | charge les faits VIVANTS de CE client | l'isolation s'applique aussi à l'oubli — impossible d'effacer chez un autre client |
| `hits = [row for row in rows if needle in row.key or needle in row.value.lower()]` | recherche par INCLUSION | `"adresse"` doit trouver `"adresse de livraison"` — l'égalité exacte raterait |
| `row.deleted = True` | soft-delete | supprimé côté lecture, tracé côté base (RGPD) |
| `session.commit()` | écrit en base | sans commit, les changements sont perdus |
| `return len(hits)` | compte supprimé | c'est ce que le test vérifie (`removed >= 1`) |

### Les décisions prises (le POURQUOI)
1. **Table `memory_facts` avec `user_id` + `key` + `value` + `deleted`** : `user_id` → isolation (R3), base → persistance (R2), flag `deleted` → oubli (R5). Une table pensée dès le départ pour les 4 exigences.
2. **SQLite en dev / Postgres via `MEMORY_DB_URL` en prod** : la stack impose Postgres, les tests doivent tourner hors-ligne — même code SQLAlchemy, seule l'URL change.
3. **Extraction de faits plutôt qu'historique complet** : budget 2000 tokens → on distille ; le bruit ne stocke rien.
4. **Regex = choix minimal, LLM = choix prod** : limite assumée à l'oral.
5. **Soft-delete plutôt que DELETE** : suppression effective côté client, trace d'audit côté système.
6. **Docs séparés du repo** : le repo formateur reste propre ; journal et guides dans Obsidian `Projets/Velmo/`.

### Les commandes (preuves pour le debrief)
```
uv run pytest tests/acceptance/test_business.py -v   # 7 passed (l'agent)
uv run pytest tests/acceptance/test_memory.py -v     # 4 passed ✅ CHANTIER 1 TERMINÉ
uv run pytest -q                                      # 11 passed, 8 failed — TOUS attendus (Chantiers 2 et 3 pas commencés)
```
(Si AppLocker bloque `uv.exe` : `.\.venv\Scripts\Activate.ps1` puis `python -m pytest ...` — équivalent, installation editable.)

---

## ③ Long version — to study (EN)

### One-sentence context
Velmo 2.0 is a customer-support agent for a collector-jersey shop; the trainer's skeleton ships with a working agent, and my Chantier 1 job was to fill in `src/velmo/memory/` so the agent remembers customers. **Done: 4/4 acceptance tests green.**

### The method: TDD
Red first (4 red tests = the starting photo; the test is the contract). Green next (minimum code to turn ONE test green, re-run, repeat). Non-regression (re-run the WHOLE suite after each step). Lived lesson: a re-run test stays red if the code isn't saved on DISK — the test measures the disk, not intentions.

### What each test checks — ALL GREEN
- **R2 — cross-session persistence** 🟢: facts live in the `memory_facts` table (SQLAlchemy), not in the Python object, so a new session reads them back.
- **R3 — customer isolation** 🟢: every SQL query filters `WHERE user_id = ...`.
- **R1 — recall over 30 turns** 🟢: `write()` matches `FACT_PATTERN` (`\b(?:ma|mon)\s+(.+?)\s+est\s+(.+?)[.!?]?$`, case-insensitive), extracts key + value, calls `remember_fact()`. Noise doesn't match → nothing stored → the 2000-token budget holds.
- **R5 — right to be forgotten** 🟢: `forget(user, "adresse")` normalises the target, loads the customer's LIVING facts, keeps those whose key OR value **contains** the target (`"adresse" in "adresse de livraison"` → true), sets `deleted=True` (soft delete), commits, returns the count. Since `read()` has filtered `deleted=False` from day one, the address never resurfaces — without touching `read()`.
- **R6 — inspection** ⬜: no acceptance test → coded after the debrief.

### `forget()` explained
Normalise the needle (`strip().lower()`) → open a session (`with` auto-closes) → select the customer's living facts (isolation applies to forgetting too) → list comprehension keeps rows whose key or value contains the needle (containment, not equality — exact match would miss `adresse de livraison`) → mark `deleted=True` → commit → return `len(hits)`.

### Decisions and the WHY
1. One table designed for all four requirements: `user_id` → isolation, database → persistence, `deleted` flag → forgetting.
2. SQLite in dev / Postgres via `MEMORY_DB_URL` in prod: same SQLAlchemy code, only the URL changes.
3. Fact extraction instead of full history: distil each exchange; noise stores nothing.
4. Regex = minimal choice honouring the test contract; in production the LLM (Kimi) would extract — same architecture, different extractor.
5. Soft delete instead of DELETE: gone for the customer, auditable for the system (GDPR spirit).
6. Docs kept out of the repo: the trainer's repo stays clean; everything lives in Obsidian.

### Glossary / Glossaire (EN ↔ FR)
- Acceptance test / Test d'acceptance : test qui vérifie une exigence MÉTIER.
- Baseline / Photo de départ : l'état rouge constaté avant de coder (TDD).
- Upsert : update s'il existe, insert sinon (`remember_fact`).
- Soft delete / Suppression douce : marquer `deleted=True` au lieu d'effacer la ligne.
- Containment vs equality / Inclusion vs égalité : `"adresse" in "adresse de livraison"` (vrai) vs `==` (faux).
- Token budget / Budget de tokens : taille max du contexte réinjecté (2000 ici).
- Fact extraction / Extraction de faits : phrase libre → paire `clé=valeur`.
- Lazy quantifier / Quantificateur paresseux : `+?` prend le moins de texte possible.
- Non-regression / Non-régression : relancer toute la suite — aucun vert ne redevient rouge.
- Audit trail / Trace d'audit : la preuve en base que l'oubli a bien eu lieu.
