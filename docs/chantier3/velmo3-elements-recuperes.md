# Éléments récupérés de Velmo-3 (lecture seule) — 2026-07-16

> **Règle** : `C:\Users\kanda\Desktop\Velmo-3` est un projet SÉPARÉ, en **lecture seule**. Rien
> n'y a été écrit, sa stack Docker n'a pas été arrêtée. Ce document ne rapatrie que des **idées**.
>
> **Règle n°2 — le contrat de Velmo-2.2 ne bouge pas.** `tests/acceptance/test_mlops.py` et la
> conception validée par le formateur font loi. Tout ce qui suit est « à intégrer » ou « à
> mentionner », **jamais** « à copier ».

---

## ⛔ D'abord : ce qu'il ne faut SURTOUT PAS copier

Velmo-3 est un projet autonome avec **son propre contrat**. Ses chiffres sont incompatibles avec
les nôtres — les recopier casserait nos tests et contredirait la validation formateur.

| | **Velmo-2.2 (nous)** | **Velmo-3** |
|---|---|---|
| Seuil global | **0,80** | 0,90 |
| Pondération | **0,35 / 0,35 / 0,30** | 0,35 / 0,45 / 0,20 |
| Note garde-fous | **`block_rate × (1 − fp_rate)`** | `0,70×block + 0,30×(1−fp)` |
| Dataset garde-fous | **35 cas** | 37 cas (25 block + 12 allow) |
| Schéma des cas | `id` · `turns` · `evaluation` | `case_id` · `suite` · `input` · `expected` |
| Langue du rapport | **français sans accents** (test ASCII) | anglais |

Les schémas de données étant différents, **`cases.py` de Velmo-3 ne peut pas être réutilisé** —
il valide des champs que nos JSONL n'ont pas.

---

## ✅ Les 5 idées qui valent, et pourquoi

### 1. 🥇 Le code de sortie `INVALID` (2) — le meilleur apport

Velmo-3 distingue **trois** issues, là où nous en avons deux :

```
exit 0 = PASS     run complet, note au-dessus du seuil
exit 1 = BLOCK    run complet, note en dessous  → régression
exit 2 = INVALID  le run n'a pas pu se faire    → données ou exécution cassées
```

**Pourquoi c'est important pour nous.** C'est **l'aboutissement direct du raisonnement de T004**.
Notre `EvalDataError` fait bien son travail (fail-closed, on refuse d'évaluer sur du vide), mais
sans distinction elle remonte en plantage → la CI voit un échec → **le même signal qu'une
régression**. Or ce sont deux mondes :

- *« ton agent a régressé »* → tu regardes ton code ;
- *« je n'ai pas pu mesurer »* → tu regardes tes données.

Confondre les deux, c'est envoyer le développeur chercher un bug qui n'existe pas. §9 de leur
design le dit bien : *« une erreur de dataset ne produit jamais une note partielle présentée
comme valide »*.

**À intégrer chez nous — T014.** Notre `score.py` peut attraper `EvalDataError` et sortir en `2`
au lieu de laisser filer la trace. Ça n'ajoute **aucune** dépendance et ne touche **pas** le
contrat : `test_mlops.py` ne teste pas la CLI.

### 2. Refuser les identifiants dupliqués

Leur `cases.py` (ligne 117) :

```python
if case.case_id in seen:
    raise CaseDataError(f"duplicate case_id: {case.case_id}")
```

**Pourquoi ça vaut.** Nos trois JSONL ont tous un champ `id` (`R1-marc-3commandes`, `hate-1`,
`q-order-status`). Deux cas avec le même `id`, et on a un **doublon silencieux** : la même
attaque comptée deux fois, une note faussée, et aucun message d'erreur. C'est exactement la
famille de bug qu'on traque depuis T003 — **faux sans crasher**.

**À intégrer chez nous — T004.** Trois lignes dans `_load_jsonl()`. Notre fiche
`T004-conception-cases.md` ne l'avait pas prévu : c'est une **quatrième** raison de lever
`EvalDataError`, à côté de manquant / vide / JSON invalide.

### 3. `N/A` avec une raison, jamais un zéro inventé

Leur `report.md` réel :

```
- Latency: N/A (not measured)
- Estimated cost: N/A (provider usage not supplied)
```

Et §6 du design : *« Les métriques de coût ou latence indisponibles valent `null` avec une raison
explicite, jamais un zéro inventé. »*

**Pourquoi ça vaut.** Notre rapport doit afficher `latence` et `cout`. En EchoLLM hors-ligne, le
coût réel est **inconnu** — écrire `0,00 €` serait un **mensonge** qui a l'air d'une bonne
nouvelle. Même philosophie que le fail-closed de T004 : *ne jamais transformer « je ne sais pas »
en chiffre favorable.*

**À intégrer chez nous — T012/T013.** Attention au contrat : le test cherche les mots `latence`
et `cout` **sans accents**. On écrit donc `latence : N/A (non mesuree hors-ligne)` — le mot-clé
reste présent, la valeur est honnête.

### 4. Les mutations comme preuve exécutable

```powershell
uv run velmo-eval --mutation memory-disabled
uv run velmo-eval --mutation guardrail-disabled
```

**Pourquoi ça vaut.** C'est la **démo** que le formateur veut voir : on casse volontairement
l'agent, la note chute, la CI bloque — en direct, devant lui. Notre `test_regression_blocks_
delivery` (T010) fait la même chose, mais **enfermé dans un test**. Un drapeau CLI, ça se montre.

**À mentionner, pas à livrer.** Hors périmètre du brief. À garder pour après le Chantier 3, et à
citer à l'oral comme « la suite logique ».

### 5. L'adaptateur qui ne lit pas la réponse attendue

§4.3 : *« Il n'utilise pas `expected_action` comme oracle d'exécution ; ce champ sert uniquement
à comparer l'observation obtenue. »*

**Pourquoi ça vaut.** Le piège le plus profond de l'évaluation : si l'agent sous test **lit la
réponse attendue** pour produire sa réponse, le test ne prouve **rien** — il prouve que le code
sait recopier. Chez nous le risque est faible (on teste le **vrai** agent, qui ne connaît pas les
`.jsonl`), mais c'est une **excellente réponse d'oral** si le formateur demande *« comment tu sais
que ton éval mesure vraiment quelque chose ? »*

Aussi §6 : leur historique *« n'enregistre pas les conversations personnelles complètes ni les
contenus dangereux bruts »*. À vérifier chez nous — si `report.md` recrache le texte des attaques
haineuses et qu'on le commite, on a un problème RGPD dans le dépôt.

---

## 🐛 Un bug trouvé dans leur `cases.py` — à ne PAS reproduire

```python
lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
if not lines:
    raise CaseDataError(f"case file empty: {path}")
for line_number, line in enumerate(lines, start=1):
    ...
    raise CaseDataError(f"invalid case at {path}:{line_number}: {exc}") from exc
```

Les lignes vides sont **filtrées AVANT** `enumerate`. Donc `line_number` est le rang dans la
**liste filtrée**, pas la vraie ligne du fichier. Une seule ligne blanche au milieu du `.jsonl`,
et tous les numéros d'erreur suivants sont **décalés**.

**L'ironie** : le message promet `fichier:ligne`, c'est-à-dire exactement le but de notre
**Question 3** — et il livre une ligne fausse. Un message d'erreur qui ment est **pire** qu'un
message vague : le vague fait chercher, le faux envoie au mauvais endroit.

**Correctif chez nous** : énumérer le fichier **brut**, et sauter les lignes vides **dans** la
boucle — le compteur reste aligné sur le fichier réel.

```python
for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
        continue          # on saute, mais line_number reste la VRAIE ligne
```

---

## Récapitulatif — quoi faire de tout ça

| Idée | Décision | Où |
|---|---|---|
| Exit code `INVALID` (2) | ✅ **à intégrer** | T014 `score.py` |
| Refus des `id` dupliqués | ✅ **à intégrer** | **T004** `cases.py` |
| `N/A` + raison, jamais 0 | ✅ **à intégrer** | T012/T013 `report.md` |
| Énumérer le fichier brut (leur bug) | ✅ **à intégrer** | **T004** `cases.py` |
| Mutations `--mutation` en CLI | 💬 à mentionner | après le Chantier 3 |
| Adaptateur aveugle à l'attendu | 💬 argument d'oral | — |
| Seuils, pondération, schémas | ⛔ **ne pas toucher** | contrat + validation formateur |

**Deux idées changent T004 dès maintenant** : le refus des doublons et l'énumération du fichier
brut. Elles ne coûtent que quelques lignes et ferment deux bugs silencieux de plus.
