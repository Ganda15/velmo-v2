# Les 6 exigences mémoire R1→R6 — tableau à montrer au formateur

> Source : `docs/reco_expert.md` (cahier des charges, note d'expert). Les mots exacts du brief sont repris.
> À afficher quand tu parles d'une exigence : chaque ligne dit CE QUE C'EST, COMMENT le code y répond, OÙ, et la PREUVE.
> ⚠️ Les tests d'acceptance couvrent R1, R2, R3, R5 (4 tests). R4 est adressé par conception (distillation), R6 est amorcé (trace d'audit) et complété par `inspect()`.

## Le tableau complet

| # | Exigence (mots du brief) | Ce que ça veut dire concrètement | Comment le code y répond | Où (fichier / fonction) | Preuve / État |
|---|---|---|---|---|---|
| **R1** | tenue d'une longue conversation | Une info donnée au début doit ressortir après le fait initial + 30 tours de bruit (31 messages) | `write()` distille chaque message via `FACT_PATTERN` au lieu de garder la conversation brute | `memory/__init__.py` : `FACT_PATTERN` (l.20), `write` (l.63) | `test_recall_over_30_turns` 🟢 |
| **R2** | persistance multi-session | Une nouvelle session (nouveau `MemoryManager`) doit retrouver les faits écrits avant | Les faits vivent dans une table SQL, pas dans l'objet Python | `memory/store.py` : table `memory_facts` ; `read` + `remember_fact` | `test_cross_session_persistence` 🟢 |
| **R3** | isolation par utilisateur | Marc ne voit jamais les souvenirs de Sophie | Chaque fait porte un `user_id` ; chaque lecture filtre `WHERE user_id = ...` | `store.py` (colonne `user_id`) + `read` (l.51) | `test_isolation_between_customers` 🟢 |
| **R4** | tenue de la fenêtre de contexte | Ne pas dépasser le budget de tokens du LLM (ici 2000) | On ne stocke pas les 31 messages : on distille en faits compacts `clé=valeur`. Le paramètre `token_budget=2000` cadre la limite | `memory/__init__.py` : `write` (distillation) + `token_budget` (l.48) | Adressé par conception 🟡 (pas de test dédié ; pas encore de code de troncature) |
| **R5** | droit à l'oubli | « Oublie mon adresse » supprime effectivement l'info des lectures futures | `forget()` cherche par inclusion, marque `deleted=True` (soft-delete) ; `read` filtre les supprimés | `memory/__init__.py` : `forget` (l.87) ; `read` (l.51) | `test_right_to_be_forgotten` 🟢 |
| **R6** | traçabilité | Pouvoir inspecter/auditer l'état de la mémoire, garder trace des suppressions | Le soft-delete garde la ligne en base (trace d'audit) ; `inspect()` exposera l'état complet | `store.py` (flag `deleted` = trace) ; `inspect` (l.103, à compléter) | Amorcé 🟡 (trace d'audit OK ; `inspect()` à coder après le debrief) |

## Résumé d'état (à dire d'une phrase)

« Sur les six exigences : quatre sont prouvées par un test d'acceptance vert — R1 rappel, R2 persistance, R3 isolation, R5 oubli. R4, la tenue du contexte, est assurée par conception : je distille au lieu de tout garder. R6, la traçabilité, est amorcée par la trace d'audit du soft-delete, et sera complétée par `inspect()`. »

## Phrase par exigence (quand tu montres la ligne)

- **R1** — « Une info du premier tour ressort après 30 tours de bruit, parce que `write` distille au lieu de tout garder. »
- **R2** — « Deux sessions différentes voient les mêmes faits : la mémoire vit en base, pas en RAM. »
- **R3** — « Chaque lecture filtre par `user_id` : Sophie ne voit jamais les données de Marc. »
- **R4** — « 31 messages ne tiennent pas dans 2000 tokens ; je distille en faits compacts, le bruit ne coûte rien. »
- **R5** — « Après `forget`, l'adresse ne ressort plus : soft-delete, invisible client, tracé système. »
- **R6** — « La ligne supprimée reste en base comme trace d'audit ; `inspect()` exposera l'état complet — c'est ma suite. »

## Note d'honnêteté (si le formateur demande « et R4, R6 ? »)

« Le cahier des charges liste six exigences, mais la suite d'acceptance n'en teste directement que quatre — R1, R2, R3, R5. R4 et R6 sont des propriétés de conception que je peux montrer dans le code, pas des tests séparés : R4 c'est la distillation qui tient le budget, R6 c'est la trace d'audit plus `inspect()` à finir. Je préfère être précis là-dessus que prétendre six tests verts. »
