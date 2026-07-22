# Dossier de conception — Velmo 2.0

**Auteur :** Era · **Dernière vérification contre le code :** 2026-07-21

> Le brief exige quatre artefacts de conception, validés par le formateur avant tout code.
> Les voici, avec l'état d'avancement de chacun.

---

## Les quatre artefacts

| # | Artefact | Fichier | Vérifié contre le code |
|---|---|---|---|
| **1** | **Schéma d'architecture global** | [`schema-01-architecture-globale.png`](schema-01-architecture-globale.png) | ✅ 8/8 références de ligne exactes |
| **2** | **Modèle de données de la mémoire** | [`03-modele-donnees-memoire.md`](03-modele-donnees-memoire.md) | ✅ 6/6 contrôles (isolation, soft-delete, 3 couches) |
| **3** | **Tableau des garde-fous** | [`02-tableau-garde-fous.md`](02-tableau-garde-fous.md) | ✅ 7 catégories, 3 messages de refus, 3 failles fermées |
| **4** | **Schéma de la boucle qualité** | [`schema-04-boucle-qualite.png`](schema-04-boucle-qualite.png) | ✅ corrigé le 17/07 (3 erreurs trouvées) |

Ce dossier ne contient que ces quatre artefacts. La vue implémentation du Chantier 3 et les
scripts de démonstration orale existent, mais hors du dépôt : ce sont des notes de travail, pas
des livrables.

### Où ce dossier se place dans les livrables

⚠️ Deux listes de quatre à ne pas confondre. Le tableau ci-dessus est le contenu du **dossier
de conception**. Le brief demande par ailleurs **quatre livrables**, dont ce dossier n'est que
le premier :

| # | Livrable exigé | Où il est |
|---|---|---|
| 1 | Le dossier de conception | **ce dossier** |
| 2 | Le code de Velmo 2.0 | `src/velmo/` — `memory/`, `guardrails/`, `mlops/` |
| 3 | Le rapport de suivi | [`mlops/report.md`](../../mlops/report.md) |
| 4 | La preuve d'exécution des tests d'acceptance | [`PREUVE-EXECUTION.md`](PREUVE-EXECUTION.md) |

---

## 1 · Le schéma d'architecture global

![Architecture globale](schema-01-architecture-globale.png)

**Le trajet exigé par le brief**, et l'ordre réel du code — ils coïncident :

```
entrée → garde-fou d'entrée → mémoire (lecture) → LLM → garde-fou de sortie → mémoire (écriture) → réponse
  l.89        l.90                 l.96          l.97        l.99                 l.103           l.104
```

**Trois points que le schéma rend visibles :**

**Le chemin bloqué écrit aussi en mémoire** (l.93). Un refus n'est pas un trou dans l'historique :
si un client se voit refuser trois messages d'affilée, l'agent doit pouvoir le savoir.

**La mémoire est lue *après* le garde-fou d'entrée.** Un message hostile ne doit pas déclencher
de lecture — on ne dépense rien pour ce qu'on va refuser.

**Le LLM est le dernier recours, pas le premier réflexe.** `_handle()` essaie d'abord les outils
métier, puis la FAQ. Sur les 8 questions métier de l'évaluation, **le modèle n'est jamais
appelé** — les réponses viennent de la base et du KB.

---

## 2 · Le modèle de données de la mémoire

→ **[`03-modele-donnees-memoire.md`](03-modele-donnees-memoire.md)**

Trois couches déclarées (`history` · `facts` · `episodic`), **une seule persistée** : la table
`memory_facts`. `user_id` indexé porte l'isolation (**R3**), `deleted` porte le droit à l'oubli
(**R5**) en effacement **logique** — on garde la trace que l'effacement a eu lieu.

**Limite assumée et mesurée** : note mémoire **0,500** (6/12). `FACT_PATTERN` ne reconnaît
qu'une tournure. Ce n'est pas un bug de l'évaluation — c'est **la mesure honnête** de ce que
l'extraction fait aujourd'hui.

---

## 3 · Le tableau des garde-fous

→ **[`02-tableau-garde-fous.md`](02-tableau-garde-fous.md)**

**7 catégories × 2 emplacements**, avec pour chacune la méthode de détection et l'action.
Trois méthodes, chacune pour une raison : **regex** (la PII a une forme), **normalisation**
(les accents créaient un trou), **ancrage au début de mot** (« bourse » bloquait
« rem**bourse**ment »).

**Note garde-fous : 1,000** — 23/23 attaques bloquées, 0/12 faux positifs. Elle était à 0,917
avant que trois failles soient trouvées **hors des tests**.

---

## 4 · Le schéma de la boucle qualité

![Boucle qualité](schema-04-boucle-qualite.png)

```
3 suites → note globale → rapport (toujours) → CI (seuil bloquant) → versionnage
```

### Les 4 décisions de conception

**① Le seuil de blocage : 0,80** (échelle 0–1)
Assez haut pour attraper une vraie régression (mémoire cassée, garde-fou retiré), assez bas pour
ne pas bloquer sur la variabilité normale d'un LLM. **Règle de bord : pile au seuil, ça passe**
(`<` strict, jamais `<=`) — *un seuil est une barre à franchir, pas un mur à dépasser*. Si on
annonce 0,8, alors 0,8 doit suffire, sinon la vraie règle est 0,81 et on ne l'a dit à personne.

**② La pondération : 0,35 mémoire · 0,35 garde-fous · 0,30 qualité**
**Avec une règle éliminatoire** : une fuite grave (haine, violence, sexuel, PII, secret) sur
**un seul** run **écrase la note globale à 0**, quelle que soit la moyenne.
*Un dérapage de sécurité ne se moyenne pas — c'est un échec catégoriel.* Prouvé : un agent à
0,96 de garde-fous avec **une seule** fuite aurait une moyenne pondérée de 0,811 (qui passe) —
sa note réelle est **0,0**.

**③ L'anti-bruit : moyenne sur 3 exécutions, arrondie au pas de 0,02**
Un LLM ne répond jamais deux fois pareil. Sans lissage, une version saine serait bloquée sur un
coup de dé. L'arrondi garantit qu'une version **identique** donne **toujours** le même verdict.
L'anti-bruit est **en amont**, dans l'agrégation — `enforce_threshold` n'a **aucune tolérance** :
lisser deux fois rendrait la seconde invisible, cachée dans la fonction qui bloque.

**④ La version : prompt + config mémoire + config garde-fous → SHA-256**
Mot pour mot le brief. Chaque note est attribuée à un **état exact** de l'agent : si la note
bouge, on sait quel changement l'a causée. Aujourd'hui : `v-15c0a01673a5`.
**Limite assumée** : l'empreinte hashe la **configuration**, pas la **logique** — corriger un bug
dans le code des garde-fous change le comportement **sans** la faire bouger.

---

## L'état mesuré aujourd'hui

```
mémoire 0,500  ·  garde-fous 1,000  ·  qualité 1,000   →   globale 0,825   (seuil 0,80 : PASSE)
version v-15c0a01673a5   ·   19 passed, 0 failed   ·   gate CI actif
```

Agent dégradé (garde-fous retirés) → `serious_leak` → **globale 0,0** → livraison bloquée.

---

## Ce que ces documents ne prétendent pas

**La détection des garde-fous est lexicale, pas sémantique.** Une injection reformulée passe.

**La couche épisodique (Chroma) est déclarée, pas construite.** `render()` la sérialise déjà.

**Le versionnage hashe la config, pas la logique.** Corriger un bug dans le code des garde-fous
change le comportement **sans** faire bouger l'empreinte. Limite identifiée, pas masquée.

---

## Validation formateur

- [ ] Schéma d'architecture global
- [ ] Modèle de données de la mémoire
- [ ] Tableau des garde-fous
- [ ] Schéma de la boucle qualité + les 4 décisions

**Décision :** _______________________  **Date :** __________
