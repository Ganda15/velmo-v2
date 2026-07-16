# T004 — `cases.py` : les décisions de conception AVANT le code

> **Règle de travail** : je ne code pas avant de savoir répondre à ces questions. Chacune décide
> d'une ligne du fichier. Si je ne sais pas y répondre, je ne sais pas ce que j'écris.
>
> **Statut** : conception validée par le formateur (2026-07-16) → T004 peut être codé.
> **Fichiers à produire** : `src/velmo/mlops/suites/__init__.py` (vide) + `src/velmo/mlops/cases.py`.
> **Preuve de réussite** : la commande de contrôle affiche exactement `12 35 8`.

---

## Question 1 — Pourquoi UN SEUL chargeur pour trois suites ?

**Réponse courte** : pour n'avoir qu'**un seul endroit où la règle de sécurité est écrite**.

**Le raisonnement long.** Les trois suites ont besoin de la même chose : ouvrir un `.jsonl`, lire
ligne par ligne, transformer chaque ligne en objet Python. Si chaque suite écrit sa propre
lecture, j'obtiens **trois** implémentations de la même idée. Et trois implémentations, ça veut
dire trois occasions de rater la même erreur — par exemple, deux suites qui lèvent bien sur un
fichier vide, et la troisième qui renvoie tranquillement une liste vide.

C'est le principe **DRY** (*Don't Repeat Yourself*), mais avec un enjeu de sécurité, pas de
confort : ici, la duplication ne coûte pas juste des lignes en trop, elle **fragmente la
garantie**. Une règle appliquée à trois endroits n'est plus une règle, c'est une intention.

**Ce que ça implique concrètement dans le code** :
- une seule fonction privée `_load_jsonl(path)` qui porte TOUTE la logique de sécurité ;
- trois fonctions publiques minces (`load_memory_cases`, `load_guardrail_cases`,
  `load_quality_cases`) qui ne font que dire **quel fichier** lire ;
- une seule exception, `EvalDataError`, définie une seule fois.

**Bénéfice mesurable** : le jour où j'ajoute une 4ᵉ suite, elle hérite de la sécurité
gratuitement. Et le jour où je durcis la règle, je la durcis **une fois**.

**En une phrase à l'oral** : *« Trois lecteurs, ce serait trois façons de rater la même erreur.
Un seul lecteur, c'est une seule règle — et elle s'applique partout par construction. »*

---

## Question 2 — Pourquoi FAIL-CLOSED, et pas tolérer un fichier vide ?

**Réponse courte** : parce que **zéro cas donnerait une note de 100 %**, et la CI livrerait un
agent sans garde-fous.

**Le raisonnement long — c'est le cœur de T004.** Déroule le scénario tolérant (*fail-open*) :

```
eval/guardrail_cases.jsonl est vide (mauvais merge, mauvais chemin, fichier corrompu)
   ↓ le chargeur renvoie []  (pas d'erreur, « rien à lire, c'est pas grave »)
   ↓ run_guardrail_suite() : 0 cas à tester, 0 échec
   ↓ note garde-fous = 0 échec / 0 cas → 100 % (ou pire : division par zéro masquée)
   ↓ note globale = 0,35×mémoire + 0,35×1,00 + 0,30×qualité  → confortablement > 0,8
   ↓ CI : « note ≥ seuil, tout va bien »  → LIVRAISON
   ↓ en production : un agent dont les garde-fous n'ont JAMAIS été testés
```

**Le point qui fait mal** : le système n'a pas menti, il a fait exactement ce qu'on lui a demandé.
L'absence de test a été interprétée comme **absence de problème**. C'est l'inversion la plus
dangereuse en qualité logicielle : *« je n'ai rien trouvé »* devient *« il n'y a rien »*.

**La règle que j'applique** : un fichier de test cassé doit faire **hurler** le système, jamais
le rendre **optimiste**. En sécurité, le doute **ne profite pas** à l'accusé.

**Les trois situations qui lèvent `EvalDataError`** :

| Situation | Pourquoi c'est fatal et pas tolérable |
|---|---|
| **Fichier manquant** | Mauvais chemin ou fichier supprimé. Tolérer = évaluer sur du vide. |
| **Fichier vide** | Le scénario ci-dessus. 0 cas → 100 % → livraison aveugle. |
| **Ligne JSON invalide** | Une virgule en trop. Sauter la ligne = **perdre un cas silencieusement** — mes 35 attaques deviennent 34 et personne ne le sait. |

Le 3ᵉ cas est le plus vicieux : sauter une ligne cassée paraît « robuste », mais ça **dégrade la
couverture sans le dire**. Le fichier a l'air complet, la note a l'air bonne, et il manque une
attaque. Fail-closed transforme ce risque silencieux en crash bruyant.

**Cohérence avec le reste du chantier** : c'est **exactement** la même philosophie que le
`serious_leak` éliminatoire (`scoring.py`). Dans les deux cas je refuse qu'un manque
d'information se transforme en bonne note.

**Où ça s'arrête** : `EvalDataError` doit **remonter sans être attrapée**, jusqu'à faire sortir
le CLI en code non-zéro → la CI échoue. Une exception rattrapée quelque part et loggée en
warning, ça rétablit le fail-open par la porte de derrière.

**En une phrase à l'oral** : *« Si mon fichier de garde-fous est vide, la suite tourne sur zéro
cas et rend cent pour cent. La CI voit "tout va bien" et livre un agent sans garde-fous. Un
fichier de test cassé doit faire hurler le système, jamais le rendre optimiste. »*

---

## Question 3 — Que doit contenir le message d'`EvalDataError` ?

**Réponse courte** : **quel fichier** et **quelle ligne** — sinon je débugge à l'aveugle sur
55 lignes de JSON.

**Le raisonnement long.** Une exception a **deux** métiers, et on n'en voit qu'un :
1. **arrêter** le programme (le fail-closed de la Q2) ;
2. **dire à l'humain quoi réparer**.

Un message pauvre remplit le premier et rate le second :

```
EvalDataError: invalid JSON        ← inutile : lequel ? où ? j'ouvre 3 fichiers à la main
```

Un message utile :

```
EvalDataError: eval/guardrail_cases.jsonl:17 — JSON invalide : Expecting ',' delimiter (line 1 column 84)
EvalDataError: eval/memory_cases.jsonl — fichier vide (aucun cas d'evaluation)
EvalDataError: eval/quality_cases.jsonl — fichier introuvable
```

**Les trois ingrédients, et pourquoi chacun** :

| Ingrédient | Pourquoi |
|---|---|
| **Le chemin du fichier** | Trois fichiers passent par le même chargeur. Sans le nom, je ne sais même pas où chercher. |
| **Le numéro de ligne** (`enumerate(..., start=1)`) | Le vrai gain. 55 lignes au total, mais une ligne de JSON fait 200 caractères — sans le numéro, je relis tout. **Numérotation à partir de 1**, pas 0 : c'est ce que mon éditeur affiche. |
| **La cause d'origine** | Le message de `json.JSONDecodeError` dit *quoi* est cassé (virgule, guillemet). Le reproduire, c'est offrir le diagnostic avec l'adresse. |

**Le détail technique qui compte** : lever avec `raise EvalDataError(...) from exc`. Le `from`
garde le **chaînage** — la trace montre l'erreur JSON d'origine sous la mienne. Sans lui, Python
affiche *« During handling of the above exception, another exception occurred »*, ce qui brouille
la lecture au lieu de l'éclairer.

**Le principe général** : une erreur, c'est un **message à un humain pressé** — moi, dans trois
semaines, sur un run de CI qui a échoué à 23 h. Le message doit répondre à *« qu'est-ce que je
répare, et où ? »* sans que j'aie à ouvrir un fichier.

**En une phrase à l'oral** : *« Une exception doit faire deux choses : arrêter le programme, et
dire à l'humain quoi réparer. Fichier plus ligne, sinon je relis 55 lignes de JSON à la main. »*

---

## Le piège trouvé en lisant le code réel (avant d'écrire une ligne)

Le repo a **déjà** un endroit qui localise un dossier de données — `src/velmo/kb_store.py:14` :

```python
KB_DOCS_DIR = Path(__file__).resolve().parents[2] / "kb" / "docs"
```

La tentation : copier ce `parents[2]` dans `cases.py`. **Ça pointerait à côté**, parce que
`kb_store.py` vit à `src/velmo/` alors que `cases.py` vivra à `src/velmo/mlops/` — **un niveau
plus profond**.

Mesuré, pas supposé :

```
kb_store.py  parents[2] = Velmo-2.2  -> kb/docs existe ? True
cases.py     parents[2] = src        -> eval/ existe ? False   ← le piège
cases.py     parents[3] = Velmo-2.2  -> eval/ existe ? True    ← le bon
```

**Même famille que l'incident T003** : reprendre un motif depuis un autre fichier **sans vérifier
son contexte**. Différence : ici ça crasherait tout de suite, alors que le `sorted(dict)` de T003
mentait en silence. Un bug bruyant est un cadeau ; un bug silencieux est une dette.

**La leçon, formulée pour l'oral** : *« Le repo avait déjà un motif pour trouver un dossier de
données. Je ne l'ai pas copié — je l'ai vérifié, et il ne s'appliquait pas : mon fichier est un
niveau plus profond. C'est exactement l'erreur qui m'avait coûté deux bugs en T003. »*

---

## Récapitulatif — de la question à la ligne de code

| Question | Décision de code |
|---|---|
| Un seul chargeur ? | 1 privée `_load_jsonl()` + 3 publiques minces + 1 exception |
| Fail-closed ? | 3 `raise EvalDataError` : manquant · vide · ligne invalide — jamais rattrapée |
| Message d'erreur ? | `chemin:ligne — cause`, `enumerate(start=1)`, `raise ... from exc` |
| Chemin du dossier ? | `Path(__file__).resolve().parents[3] / "eval"` — **3**, pas 2 |

**Vérification finale attendue** :
```
python -c "from velmo.mlops.cases import load_memory_cases, load_guardrail_cases, load_quality_cases as q; print(len(load_memory_cases()), len(load_guardrail_cases()), len(q()))"
→ 12 35 8
```
Et les 3 tests d'acceptance **restent rouges**, pour la même raison (`NotImplementedError:
run_eval`) — T004 ne les fait pas passer, et c'est normal.
