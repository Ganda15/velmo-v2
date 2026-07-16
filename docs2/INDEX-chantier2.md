# Chantier 2 — Garde-fous : par où commencer

> État au 2026-07-10 : **5 tests garde-fous verts, 16 verts au total**, plus **trois** failles trouvées
> hors tests (accents, PII entrante — corrigées ; « remboursement » = limite documentée). Code figé.

---

## ⭐ LE PAQUET DÉFINITIF — v2

| Fichier | Contenu |
|---|---|
| [`PRESENTATION-chantier2-v2-FR.md`](PRESENTATION-chantier2-v2-FR.md) | **Tout, en un seul fichier** : déroulé, oral mot à mot, 3 failles, démo commande→résultat→pourquoi, preuve, carte d'archi, 9 questions |
| [`PRESENTATION-chantier2-v2-EN.md`](PRESENTATION-chantier2-v2-EN.md) | La même chose en anglais |

**Pour répéter et présenter, ouvre uniquement ceux-là.** Le reste ci-dessous = matière d'appui.

### Historique des versions
- **v2 (10/07, après-midi)** — 3 failles (ajoute « remboursement »/sous-chaîne) + carte d'archi. Code figé.
- **v1 (10/07, matin)** — 2 failles (accents, PII). Fichiers `oral-final-chantier2-FR.md` / `-EN.md`, conservés.

---

## Les fichiers d'appui (à jour)

| Fichier | À quoi il sert |
|---|---|
| [`schema-chantier2-EXPLICATION.md`](schema-chantier2-EXPLICATION.md) | Ce que chaque boîte du schéma veut dire + le vocabulaire à éviter |
| [`DEMO-TEST-chantier2-guardrails.md`](DEMO-TEST-chantier2-guardrails.md) | Les commandes exactes et comment lire chaque résultat |
| [`JOURNAL-chantier2-guardrails.md`](JOURNAL-chantier2-guardrails.md) | Journal de bord, étapes 1 à 9, code ligne par ligne (FR) |
| [`JOURNAL-chantier2-guardrails-EN.md`](JOURNAL-chantier2-guardrails-EN.md) | Le même journal en anglais |
| [`oral-final-chantier2-FR.md`](oral-final-chantier2-FR.md) / [`-EN`](oral-final-chantier2-EN.md) | **v1** (2 failles) — historique |

Code : [`demo_guardrails.py`](demo_guardrails.py) · chat manuel : [`chat_guardrails.py`](chat_guardrails.py) · chat Azure : [`chat_azure.py`](chat_azure.py).

---

## Les 3 commandes, dans l'ordre de la présentation

```powershell
.\.venv\Scripts\python.exe docs2\demo_guardrails.py                           # 1. l'AGENT parle
.\.venv\Scripts\python.exe -m pytest tests/acceptance/test_guardrails.py -v   # 2. 5 passed
.\.venv\Scripts\python.exe -m pytest -q                                        # 3. 16 passed, 3 failed
```

⚠️ **`python` tout court échoue** (`ModuleNotFoundError: No module named 'velmo'`) : le
`pythonpath = ["src","tests"]` de `pyproject.toml` est sous `[tool.pytest.ini_options]`, donc il ne
vaut que pour pytest. Toujours `.\.venv\Scripts\python.exe`.

**Règle de présentation : l'agent parle avant que pytest ne parle.** C'est le reproche n°3 du
Chantier 1 — « les tests qui passent ne suffisent pas à montrer le fonctionnement ».

---

## Les trois failles à raconter

| Faille | Trouvée en | Le symptôme | État |
|---|---|---|---|
| **Accents** | relisant mon code | « clé API » passait | ✅ corrigé (`_normalize`) |
| **PII entrante** | relisant le brief (`reco_expert.md:17`) | un client tapant sa carte passait, écrite en mémoire | ✅ corrigé (`CARD_RE` en entrée, refus dédié) |
| **Sous-chaîne** (« remboursement » → « bourse ») | **parlant à l'agent** | un client demandant un remboursement est refusé (`out_of_scope`) | 📝 limite documentée, correctif `\b` connu, non déployé |

**La phrase à retenir :** les cinq tests étaient **déjà verts** avant ces découvertes. Un test vert ne
veut pas dire qu'on est protégé — il veut dire qu'on est protégé contre ce qu'on a pensé à tester.

---

## Les fichiers périmés (conservés, à ne pas ouvrir)

Ils datent du 08/07, disent « TDD » (or les tests étaient **fournis**), font commencer la démo par
`pytest`, et citent des numéros de ligne qui ont bougé quand `guardrails/__init__.py` a été réécrit :

- `oral-presentation-chantier2-FR.md` / `-EN.md`
- `oral-schemas-chantier2.md` / `-EN.md`
- `oral-demo-schema-chantier2.md` / `-EN.md`

Chacun porte un bandeau ⛔ en tête qui renvoie vers son remplaçant.

---

## Les deux images à projeter

| Fichier | Quand |
|---|---|
| [`schema-A-gauche.png`](schema-A-gauche.png) | de 0:00 à 4:30 |
| [`schema-AB-complet.png`](schema-AB-complet.png) | à partir de 4:30 |

Sources retouchables : `schema-A-gauche.html`, `schema-AB-complet.html`, `schema-chantier2.drawio`.

---

## Ce qui reste

- **Répéter à voix haute**, chrono en main. 5 min de parole, pas 8.
- *(optionnel)* Lancer une fois contre le vrai Kimi : `uv sync --extra llm`, remplir `.env`, vérifier
  que `get_llm()` renvoie `AzureLLM`. Le brief impose Azure (`reco_expert.md:9` : « aucun modèle local »).
- **Chantier 3** : `run_eval` est vide (`mlops/__init__.py:40`). Le journal `self.events` du Chantier 2
  en est la matière première.
