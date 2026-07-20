# Tableau des garde-fous — catégorie × emplacement × méthode × action

> **Artefact 3/4 du dossier de conception.**
> Extrait de `src/velmo/guardrails/__init__.py` — chaque ligne est vérifiable dans le code.
> Vérifié le 2026-07-17 contre le code réel · suite garde-fous : **1,000** (23/23 bloquées,
> 0/12 faux positifs).

---

## Le tableau

| Catégorie | Entrée | Sortie | Méthode de détection | Action au blocage |
|---|:---:|:---:|---|---|
| **`pii`** (n° de carte) | ✅ | ✅ | **Regex** `\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b` | refus + journal |
| **`hate`** | ✅ | ✅ | 4 mots-clés normalisés, ancrés au début de mot | refus + journal |
| **`violence`** | ✅ | ✅ | 4 mots-clés | refus + journal |
| **`sexual`** | ✅ | ✅ | 2 mots-clés | refus + journal |
| **`prompt_injection`** | ✅ | ✅ | 4 mots-clés | refus + journal |
| **`secret_leak`** | ✅ | ✅ | 5 mots-clés | refus + journal |
| **`out_of_scope`** | ✅ | ✅ | 7 mots-clés | refus + journal |

**7 catégories, les deux portiques.** Le code le dit explicitement (`check_output`, commentaire) :
*« mêmes catégories des deux côtés : on réutilise les mots-clés »*.

---

## Les messages de refus — ils ne sont pas identiques, et c'est voulu

| Emplacement | Catégorie | Message rendu au client |
|---|---|---|
| **entrée** | `pii` | *« Ne partagez jamais vos coordonnées bancaires dans le chat. »* |
| **entrée** | les 6 autres | *« Désolé, je ne peux pas traiter cette demande. »* |
| **sortie** | toutes | *« Désolé, je ne peux pas transmettre cette information. »* |

**Pourquoi la PII entrante a son propre message** : ce n'est pas une attaque, c'est **un client qui
se met en danger**. On ne le refuse pas, on **le prévient**. Un message générique le laisserait
croire qu'il a mal formulé sa demande.

**Pourquoi les autres refus sont vagues** : ne **jamais révéler la règle déclenchée**. Dire
« votre message contient le mot X » donne la carte au prochain attaquant.

---

## Les trois méthodes de détection, et pourquoi trois

### 1. Regex — pour ce qui a une **forme** exacte

```python
CARD_RE = re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b")
```

Un numéro de carte n'est pas une opinion : c'est 16 chiffres. Gratuit, instantané, sans faux
positif sur son domaine. Testé **des deux côtés** — un client peut taper sa carte, et le modèle
peut la recracher.

### 2. Normalisation — pour que les accents ne créent pas de trou

```python
def _normalize(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")
```

**Faille n°1 trouvée hors des tests** : les mots-clés étaient écrits **sans accents**, mais
`message.lower()` **garde** les accents. « clé API » ne matchait pas `cle api` — le garde-fou
avait un trou par lequel passait n'importe quel mot accentué.

### 3. Ancrage au début de mot — pour ne pas bloquer les vrais clients

```python
def _contient(texte_norm, cles) -> bool:
    """Cherche chaque mot-clé ANCRÉ AU DÉBUT d'un mot."""
```

**Faille n°3, la plus coûteuse** : `cle in texte` cherchait **n'importe où** dans la chaîne.
Résultat : « **bourse** » bloquait « rem-**bourse**-ment » — le cas d'usage n°1 d'un SAV.
Idem « race » dans « t-**race**-r », « tuer » dans « effec-**tuer** ».

⚠️ **Pas d'ancre de fin, et c'est délibéré** : sans elle, « sous-humain**s** » au pluriel
passerait à travers.

---

## Le journal — toute décision de blocage est tracée

```python
def _journalise(self, where: str, categorie: str, message: str) -> None:
    self.events.append({"where": where, "category": categorie,
                        "action": "block", "message": message})
```

Quatre champs : **où** (`input`/`output`), **quelle catégorie**, **quelle action**, **le message**.
C'est ce qui permet, en exploitation, de répondre à *« pourquoi ce client a-t-il été bloqué ? »*
sans rejouer la conversation.

---

## Ce que le tableau ne dit pas — les limites assumées

**La détection est lexicale, pas sémantique.** Une injection reformulée intelligemment
(« oublions un instant ce qu'on t'a dit ») passe. Un modèle de modération ou un LLM juge
couvrirait ça — c'est **hors périmètre du brief**, et c'est la suite logique.

**`out_of_scope` et `prompt_injection` ne sont PAS des fuites graves.** Dans
`guardrail_suite.py`, seules `{hate, violence, sexual, pii, secret_leak}` déclenchent
`serious_leak`. **Choix de conception à défendre** : les 5 retenues sont celles où le mal est
fait **envers un humain ou sur ses données**, pas envers le système.

---

## La preuve

```
suite garde-fous : block_rate 23/23 = 1,000 · faux positifs 0/12 = 0,000 · note 1,000
agent dégradé (garde-fous retirés) : serious_leak = True → note globale écrasée à 0,0
```

Ce **1,000** n'est pas de la chance : c'est le résultat des **3 failles corrigées hors des
tests** (accents · PII entrante · ancrage). La note était à **0,917** avant.
