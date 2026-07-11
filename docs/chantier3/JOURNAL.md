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

## ✅ FAIT

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
1. **Stack imposée** — Kimi/Azure AI, SQLite (dev) → Postgres via `MEMORY_DB_URL` (prod), Chroma.
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

---

## ⏭️ À FAIRE

### Étape 4 — Spec → Plan → Tasks ← ON EST ICI
`/speckit-specify` (les Gherkin du brief) → `/speckit-plan` → `/speckit-tasks`.
Era lit et corrige chaque fichier. Preuves C14–C16.

### Étape 5 — Les 3 suites d'évaluation (TDD, Era code)
`mlops/` : suite mémoire, suite garde-fous (blocage + faux positifs), suite qualité + note globale.

### Étape 6 — CI quality.yml + versionnage
GitHub Actions : exécute les suites → seuil → bloque si la note chute. Versionne + journalise la note.

### Étape 7 — mlops/report.md
Rapport : note mémoire, taux de blocage, faux positifs, latence, coût.

### Étape 8 — Preuves + re-audit
Tests d'acceptance (preuve) · `/mlops velmo` · oraux FR/EN · MAJ de ce journal.
