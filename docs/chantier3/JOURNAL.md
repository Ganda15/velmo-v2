# JOURNAL — Chantier 3 : Évaluation & MLOps (Velmo 2.2)

> Ce fichier vit DANS le projet (`docs/chantier3/JOURNAL.md`).
> Ouvre Velmo-2.2 dans VS Code → chaque modification de ce fichier s'affiche en direct
> (diff rouge/vert) dans l'éditeur et dans le panneau Source Control (Ctrl+Shift+G).

Convention : chaque étape a un bloc **AVANT** (quoi / pourquoi / commande) et un bloc
**APRÈS** (ce qu'on a fait, le contenu réel, ce qui a cassé 🔴→🟢, ce qu'il faut retenir).

---

## 🎯 Goal du chantier (mots du brief)
1. Écrire 3 suites d'évaluation : mémoire (rejoue `memory_cases.jsonl`), garde-fous
   (taux de blocage + taux de faux positifs sur `guardrail_cases.jsonl`), qualité →
   produire une **note globale**.
2. Brancher l'évaluation dans la **CI (`quality.yml`)** avec **blocage sous le seuil** ;
   versionner l'agent (version = prompt + config mémoire + config garde-fous) ; journaliser la note.
3. Exposer les signaux dans `mlops/report.md` : note mémoire, taux de blocage, faux positifs,
   latence, coût.

Critères RNCP visés : **C12** (suites d'éval), **C13** (gate CI bloquant), **C20** (signaux/rapport).

---

## ⚠️ IMPORTANT — Livrables du brief VS mon outillage personnel

Bien séparer les deux, pour ne pas présenter au formateur ce qui n'est pas demandé :

### 📦 LIVRABLES DU BRIEF (ce que le formateur évalue)
- **Dossier de conception** → `docs/chantier3/DOSSIER-CONCEPTION.md` (schéma boucle qualité + 4 décisions)
- **Code Velmo 2.0** → `src/velmo/` : `memory/`, `guardrails/`, `mlops/` (les 3 suites + CI + versionnage)
- **Rapport de suivi** → `mlops/report.md`
- **Preuve d'exécution des tests d'acceptance** → sortie pytest archivée

### 🛠️ MON OUTILLAGE PERSONNEL (NON demandé par le brief — ne pas présenter comme livrable)
- **`CLAUDE.md`** = fiche d'instructions pour MON agent Claude Code. C'est MON usage, pas le brief.
- **Spec Kit** (`.specify/`, `.claude/skills/speckit-*`, `specs/`) = MA méthode de travail
  (spec → plan → tasks). Ça m'aide à construire, mais le formateur note le RÉSULTAT, pas l'outil.
- **Ce JOURNAL + le DOCS** = MES notes d'apprentissage.
- Règle : ces fichiers restent dans le repo (utiles, versionnés) mais je ne les mets PAS dans
  ma présentation formateur comme si c'était un livrable exigé. Si on me demande « comment tu
  as travaillé ? » → là je peux les montrer comme ma démarche pro (bonus), pas comme le livrable.

---

## ✅ FAIT

### Croisement contrat ↔ spec (2026-07-11) — vérification du combo outils
Avant `/speckit-plan`, croisé le CONTRAT réel (`tests/acceptance/test_mlops.py` +
`.github/workflows/quality.yml`) avec notre `specs/001-quality-eval-loop/spec.md`.
- ✅ Les 3 user stories du spec correspondent exactement aux 3 tests du contrat.
- ✅ `quality.yml` existe déjà (uv + Python 3.11, tests acceptance) avec le gate en
  commentaire, qui attend `python -m velmo.mlops.score --min-score 0.8` → à décommenter
  quand le module existera.
- 🔴→🟢 **Divergence d'échelle trouvée et corrigée** : dossier disait « 80/100 », le contrat
  impose 0.0–1.0 avec seuil 0.8 (`enforce_threshold(scores, 0.8)`) → DOSSIER-CONCEPTION §2.1 corrigé.
- ⚠️ **Piège accents** : le test vérifie `"memoire"`, `"cout"` SANS accent dans report.md →
  le rapport devra écrire les mots sans accent (é ≠ e pour Python).
- 📌 API imposée par le contrat (à respecter dans le plan) : module `velmo.mlops` avec
  `run_eval(agent)` → `scores.global_/.memory/.guardrails/.quality` (0–1),
  `enforce_threshold(scores, seuil)` → lève `DeliveryBlocked` (au seuil pile = passe),
  `current_version()`, `write_report(scores, path)` ; `conftest` fournit
  `build_reference_agent()` / `build_degraded_agent()`.
- 📝 À savoir : `scores.global_` a un underscore car `global` est un mot réservé Python.

### Étape 0 — Dossier de travail Velmo-2.2
**FAIT (2026-07-11).** `robocopy` de velmo-v2 → `C:\Users\kanda\Desktop\Velmo-2.2`.
139 fichiers, 0 échec, `.git` inclus. Original velmo-v2 intact (démo Chantier 2).

### Étape 1 — Spec Kit + CLAUDE.md
**FAIT (2026-07-11).**
- CLI installé : `C:\Python314\python.exe -m pip install --user git+https://github.com/github/spec-kit.git`
  → exe : `C:\Users\kanda\AppData\Roaming\Python\Python314\Scripts\specify.exe`
- `CLAUDE.md` créé à la racine (stack imposée, commandes tests, règles, goal C3).
- `specify init --here --integration claude --force --script ps` → a créé `.specify/`
  (constitution template + templates + scripts) et `.claude/skills/speckit-*` (les commandes
  `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`).

### Étape 2 — Schéma boucle qualité
**FAIT (2026-07-11).** `schema-chantier3-boucle-qualite.png` + `.drawio` (racine du projet et vault).
Reste : validation formateur + 4 justifications (seuil, anti-bruit, pondération, définition version).

### Étape 3 — Constitution (`/speckit-constitution`)
**FAIT (2026-07-11).** `.specify/memory/constitution.md` rempli (v1.0.0, ratifiée et
amendée le 2026-07-11 — ratification initiale).

6 principes non-négociables (au lieu des 5 du template, template respecté mais étendu) :
1. **Stack imposée** — Kimi/Azure AI, SQLite (dev) → Postgres via ~~`MEMORY_DB_URL`~~ **`DB_URL`** (prod — 🔄 corrigé en v1.0.1, le vrai nom de variable selon `.env.example`/`db.py`), Chroma.
   Aucune substitution sans accord écrit du formateur.
2. **TDD = le contrat** — les suites d'acceptance ne se modifient jamais pour passer au vert ;
   red→green strict.
3. **RGPD by design** — R3 (isolation par client) et R5 (droit à l'oubli, testé) obligatoires
   dès la v1 de chaque feature.
4. **Gate qualité bloquant** — pas de livraison sous le seuil de note globale ; bloqué en CI
   (`quality.yml`), pas de vérif manuelle.
5. **Traçabilité RNCP** — chaque feature/spec/tâche cite son ou ses critère(s) C1–C21.
6. **Secrets & OWASP** — clés dans `.env` uniquement, jamais commitées ; OWASP API Top 10
   passé en revue sur chaque endpoint.

Sections additionnelles : **Development Workflow** (Era code elle-même, commandes pytest +
repli AppLocker, MAJ journal à chaque étape) et **Quality & Evaluation Chain** (3 suites →
note globale versionnée, signaux dans `mlops/report.md`).

Gouvernance : le stack (P.I) et le contrat de test (P.II) ne s'amendent qu'avec accord du
formateur ; `/speckit-plan` doit désormais passer une Constitution Check gate ; `CLAUDE.md`
reste le guide opérationnel du quotidien, la constitution prime en cas de conflit.

Propagation vérifiée : `plan-template.md`, `spec-template.md`, `tasks-template.md`, `README.md`
et `CLAUDE.md` déjà cohérents avec la constitution — aucune modification requise. Pas de
`.specify/extensions.yml`, donc aucun hook pré/post à exécuter.

### Étape 4a — `/speckit-specify` : feature "boucle qualité"
**FAIT (2026-07-11).** `specs/001-quality-eval-loop/spec.md` créé (numbering séquentiel,
premier feature du projet). Pas de branche git créée (pas de hook `before_specify`
enregistré dans `.specify/extensions.yml`, qui n'existe pas).

3 user stories, priorisées et testables indépendamment :
- **US1 (P1)** — les 3 suites produisent une note globale + 3 sous-notes (mémoire /
  garde-fous / qualité), versionnées par version d'agent. Fondation, preuve **C12**.
- **US2 (P1)** — une régression (mémoire coupée ou garde-fou retiré) fait chuter la note
  et bloque la livraison en CI. Le vrai gate. Preuve **C13**.
- **US3 (P2)** — `mlops/report.md` affiche note mémoire, taux de blocage, faux positifs,
  latence, coût après chaque run. Preuve **C20**.

Les 3 scénarios Gherkin du brief formateur sont repris tels quels dans les Acceptance
Scenarios de US1/US2/US3. Ajout de 14 Functional Requirements (FR-001 à FR-014, dont
fail-closed sur crash/timeout, pas de blocage faux-positif, isolation par client dans les
fixtures d'éval) et 5 Success Criteria mesurables et technology-agnostic.

**Aucun [NEEDS CLARIFICATION]** : seuil de note globale, formule de pondération des 3
sous-notes, et stratégie anti-bruit (flakiness LLM) restent volontairement en
**Assumptions** plutôt qu'en clarification bloquante — ce sont exactement les 4
justifications déjà identifiées comme en attente du formateur à l'Étape 2 (schéma). Le
spec exige juste qu'un seuil/formule documenté et versionné existe (FR-005, FR-008), sans
en fixer la valeur ici.

Checklist qualité (`specs/001-quality-eval-loop/checklists/requirements.md`) : tous les
items passent dès la première validation, aucune itération nécessaire.

Prêt pour `/speckit-plan` (ou `/speckit-clarify` si Era veut trancher seuil/pondération
avant plutôt qu'après).

### Étape 4b — `/speckit-plan` : conception technique
**FAIT (2026-07-12).** `specs/001-quality-eval-loop/plan.md` + `research.md` +
`data-model.md` + `contracts/{python-api,cli}.md` + `quickstart.md` générés.

Contrat réel croisé avec le code (pas juste le brief) : `tests/acceptance/test_mlops.py`,
`tests/conftest.py`, `.github/workflows/quality.yml`, `Scores` déjà défini (avec
`block_rate`/`false_positive_rate`/`latency_ms`/`cost` en plus des 4 notes), `db.py` (confirmé
`DB_URL`, pas `MEMORY_DB_URL`), fallbacks hors-ligne existants (`EchoLLM`, `LocalKB`,
`fresh_sqlite_session`). Les 4 décisions du DOSSIER-CONCEPTION (seuil 0.8, pondération
35/35/30 + plafond à 0 sur fuite grave, anti-bruit 3 runs, version = hash prompt+config) sont
implémentées telles quelles, pas re-décidées.

5 questions de conception résolues dans `research.md` (mécanisme exact du lissage anti-bruit,
liste des catégories « graves », comment la suite garde-fous observe le blocage — direct sur
`agent.guardrails`, pas en parsant le texte de réponse —, emplacement de `mlops/report.md`
à la racine du repo, et calcul du coût en absence de données de tokens réelles).

**⚠️ Divergence constitution trouvée (pas corrigée ici, juste signalée)** : la constitution
(Principe I) écrit `MEMORY_DB_URL`, le vrai code utilise `DB_URL`. Le plan suit le vrai code.
Amendement PATCH de la constitution à faire séparément.

**🔄 Résolu (2026-07-12)** : constitution amendée en v1.0.1 (`MEMORY_DB_URL` → `DB_URL`,
Principes I et VI), même correction dans `CLAUDE.md`. Commits `d4e4090` (plan + constitution
1.0.1) et `c1053af` (déplacement des fichiers schéma vers `docs/chantier3/`).

Structure retenue : `src/velmo/mlops/{cases,scoring,versioning,report,eval_agent,score}.py`
+ `suites/{memory,guardrail,quality}_suite.py`, plus un dossier `mlops/` généré à la racine
(rapport, pas du code source). Un seul fichier CI à toucher : décommenter le step déjà présent
dans `quality.yml`, rien d'autre.

Constitution Check : tous les principes passent (tableau dans `plan.md`), zéro entrée dans
Complexity Tracking.

⚠️ **Risque à valider empiriquement à l'implémentation** : la formule de pondération suppose
que l'agent de référence (`build_reference_agent`, garde-fous réels) obtient une note globale
≥ 0.8 sur les 55 cas d'éval existants. Si ce n'est pas le cas au premier run réel, il faudra
ajuster la couverture des garde-fous (pas le test, pas le seuil) — TDD rouge→vert normal.

### Étape 4c — `/speckit-tasks` : découpage en tâches
**FAIT (2026-07-12).** `specs/001-quality-eval-loop/tasks.md` généré — 18 tâches sur
7 phases.

Organisation stricte TDD demandée par Era : chaque tâche d'implémentation démarre par
`pytest tests/acceptance/test_mlops.py -v` (rouge observé ou confirmé) et se termine par
le même run (vert obtenu, ou rouge encore attendu mais pour une raison différente — ex.
T009 fait passer `test_scores_produced_and_versioned` au vert pendant que les 2 autres
restent rouges, mais sur `enforce_threshold`/`write_report`, plus sur `run_eval`).

Découpage par phase :
- **Phase 1 Setup** (T001–T002) — rouge de départ constaté, `.gitignore` pour `mlops/report.md`.
- **Phase 2 Foundational** (T003) — `versioning.py`, partagé par les 3 user stories.
- **Phase 3 US1** (T004–T009) — `cases.py`, les 3 suites (parallélisables), `scoring.py`,
  câblage `run_eval`/`current_version`. Checkpoint : 1er test vert, MVP.
- **Phase 4 US2** (T010–T011) — `enforce_threshold`, `eval_agent.py`. Checkpoint : 2e test vert.
- **Phase 5 US3** (T012–T013) — `report.py`, câblage `write_report`. Checkpoint : les 3 tests
  d'acceptance passent.
- **Phase 6 CI Gate Activation** (T014–T015) — `score.py` (CLI) + décommenter `quality.yml`.
  Placée APRÈS US3 volontairement : le CLI doit écrire le rapport même en cas de blocage
  (contracts/cli.md), donc dépend de `write_report` (US3) autant que d'`enforce_threshold` (US2)
  — dépendance croisée assumée et documentée plutôt que forcer une fausse indépendance.
- **Phase 7 Polish** (T016–T018) — suite complète, ruff/mypy, MAJ JOURNAL (rappel du risque
  seuil 0.8 flagué à l'Étape 4b, à vérifier au premier run réel).

Toutes les tâches respectent le format strict (`- [ ] TXXX [P?] [Story?] Description + chemin`),
taillées ~15-30 min chacune. `T005`/`T006`/`T007` (les 3 suites) et `T010`/`T011`
(seuil/agent CLI) sont parallélisables (fichiers indépendants).

Prêt pour `/speckit-implement` ou implémentation manuelle par Era, tâche par tâche.

---

## ⏭️ À FAIRE

### Étape 5 — Les 3 suites d'évaluation (TDD, Era code) ← ON EST ICI
`specs/001-quality-eval-loop/tasks.md`, phases 1 à 5 (T001–T013). Era code elle-même,
Claude donne code + explication dans le chat, application seulement sur « do it ».

**Avancement (2026-07-12) :**
- ✅ **T001** — baseline rouge observée : `3 failed in 0.28s`, tous sur
  `NotImplementedError: run_eval` (`src/velmo/mlops/__init__.py:40`). Bonus : `uv run` a créé
  le venv (Python 3.11.15, 28 paquets) sans blocage AppLocker.
- ✅ **T002** — déjà fait par le brief : `.gitignore` couvrait `mlops/report.md` +
  `mlops/*.json`, et `mlops/.gitkeep` existait. Rien à faire (vérifié avant d'agir).
- ✅ **T003** — `src/velmo/mlops/versioning.py` : empreinte SHA-256 de la config
  (prompt + token_budget + garde-fous). Vérifié : `v-15c0a01673a5` identique sur 2 runs.
  🔴→🟢 **Incident C21 documenté — 2 bugs dans la 1re version :**
  1. `AttributeError` : `CATEGORIES` est au **niveau module** de `velmo.guardrails`
     (ligne 17), pas un attribut de classe `GuardrailEngine.CATEGORIES`. Cause racine :
     code écrit depuis la doc du plan au lieu du vrai fichier. Leçon : lire le code réel.
  2. Bug **silencieux** : `sorted(INPUT_KEYWORDS)` sur un dict ne trie que les CLÉS et
     jette les listes de mots-clés → modifier un mot-clé n'aurait pas changé l'empreinte
     (versionnage menteur, sans crash). Corrigé par
     `{category: sorted(keywords) for ... in sorted(...items())}`.
  Méthode : reproduire → lire le vrai fichier (`grep` lignes 17/52) → corriger → re-vérifier.
- ⏭️ Prochaine : **T004** `cases.py` (chargeur JSONL fail-closed).

### Étape 6 — CI quality.yml + versionnage
`tasks.md` phase 6 (T014–T015) : `score.py` (CLI) + décommenter le gate dans `quality.yml`.

### Étape 7 — mlops/report.md
Déjà couvert par `tasks.md` phase 5 (T012–T013) — rapport : note mémoire, taux de blocage,
faux positifs, latence, coût.

### Étape 8 — Preuves + re-audit
`tasks.md` phase 7 (T016–T018) : suite complète + lint/types + MAJ journal. Puis tests
d'acceptance (preuve) · `/mlops velmo` · oraux FR/EN.
