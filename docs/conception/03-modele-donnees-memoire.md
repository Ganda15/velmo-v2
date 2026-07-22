# Modèle de données de la mémoire

> **Artefact 2/4 du dossier de conception.**
> Extrait de `src/velmo/memory/store.py` et `src/velmo/memory/__init__.py`.
> Vérifié le 2026-07-17 contre le code réel · suite mémoire : **0,500** (6/12) — voir *Limites*.

---

## Les trois couches — et pourquoi une seule est en base

`MemoryContext` (`memory/__init__.py`) prévoit **trois couches**, c'est le contrat de lecture :

| Couche | Champ | Contenu | Persistée ? |
|---|---|---|---|
| **court terme** | `history: list[Turn]` | les tours de la conversation en cours | ❌ non — meurt avec la session |
| **long terme** | `facts: dict[str, str]` | les faits durables (`taille` → `L`) | ✅ **table `memory_facts`** |
| **épisodique** | `episodic: list[str]` | souvenirs sémantiques (Chroma) | ❌ **pas encore construit** |

**Pourquoi seul le long terme est en base** : c'est ce que les exigences imposent. **R2**
(persistance inter-session) est impossible en RAM — un fait qui meurt avec le process n'est pas
un souvenir. Le court terme, lui, n'a pas besoin de survivre : il *est* la conversation.

**La couche épisodique est déclarée mais vide.** C'est une **dette assumée**, pas un oubli :
`render()` la sérialise déjà, il ne manque que le branchement Chroma.

---

## La table `memory_facts`

```python
class MemoryFact(MemoryBase):
    __tablename__ = "memory_facts"

    id:      Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str]  = mapped_column(String, index=True)     # ← isolation R3
    key:     Mapped[str]  = mapped_column(String)
    value:   Mapped[str]  = mapped_column(String)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False) # ← droit à l'oubli R5
```

| Champ | Type | Rôle | Exigence |
|---|---|---|---|
| `id` | `int` PK auto | identité de la ligne | — |
| `user_id` | `str` **indexé** | **la cloison entre clients** | **R3** |
| `key` | `str` | le nom du fait (`taille`, `adresse`) | R1 · R2 |
| `value` | `str` | sa valeur (`L`, `12 rue des Lilas`) | R1 · R2 |
| `deleted` | `bool` | **effacement logique** | **R5** |

**Un souvenir = une ligne.** Pas de JSON dans une colonne : on veut pouvoir filtrer par
`user_id` et par `deleted` **en SQL**, pas en Python après avoir tout chargé.

**`user_id` est indexé** parce que **chaque lecture** filtre dessus. Sans index, l'isolation
coûterait un scan complet à chaque tour de conversation.

---

## L'isolation par utilisateur — R3

```python
rows = session.scalars(
    select(MemoryFact).where(
        MemoryFact.user_id == user_id,      # ← la cloison
        MemoryFact.deleted.is_(False),
    )
).all()
```

**Il n'existe aucun chemin de lecture sans le filtre `user_id`.** L'isolation n'est pas une
convention qu'on pourrait oublier : c'est **la seule requête**. Marc ne peut pas voir la commande
de Sophie parce qu'aucune ligne de code ne le permet.

---

## Le droit à l'oubli — R5, et pourquoi *logique* et non *physique*

```python
deleted: Mapped[bool] = mapped_column(Boolean, default=False)
```

`forget()` **ne supprime pas la ligne** : il passe `deleted = True`, et toute lecture filtre
`deleted.is_(False)`. Le fait **disparaît de l'agent** — c'est ce que le client demande et ce que
le test exige.

**Pourquoi ne pas faire un vrai `DELETE`** : on garde la **trace qu'un effacement a eu lieu**.
Le jour où un client conteste (« vous aviez encore mon adresse »), on peut prouver la date. Un
`DELETE` sec efface aussi la preuve du respect de la demande.

⚠️ **La limite à connaître** : le RGPD peut exiger un effacement **physique**. Le soft-delete est
un choix d'exploitation, pas une conformité totale — un purge périodique des lignes `deleted`
serait la suite.

**Décision assumée dans `forget()`** : la correspondance est **mot à mot en OU**. Le client dit
« oublie mon adresse **de livraison** » quand la clé stockée est `adresse`. **Dans le doute,
sur-supprimer est le sens sûr** — rater une suppression est la faute, pas l'inverse.

---

## Où vivent les données — SQLite ou Postgres, zéro ligne à changer

```python
def _build_engine():
    url = os.getenv("MEMORY_DB_URL")
    if url:
        return create_engine(url, future=True)          # Postgres en prod
    return create_engine("sqlite://", ..., poolclass=StaticPool)   # SQLite en dev/tests
```

Une variable d'environnement, deux mondes. **Et le `StaticPool` n'est pas un détail** : il fait
qu'une seule base en mémoire est vue par **toutes** les instances de `MemoryManager` — c'est ce
qui rend **R2 (persistance inter-session)** testable sans serveur.

⚠️ **Conséquence à connaître** : la base mémoire est au **niveau module**. Créer un
`MemoryManager()` neuf ne donne **pas** une mémoire vierge dans le même process. Voulu pour R2,
mais surprenant si on l'ignore.

---

## L'écriture — un seul chemin

```
respond()  →  memory.write(user_id, message, réponse)
                    ↓
              FACT_PATTERN.search(message)      « Ma/Mon/Mes X est/sont Y »
                    ↓ si ça matche
              remember_fact(user_id, clé, valeur)   → upsert dans memory_facts
```

**Un seul point d'écriture en base.** Si demain la règle d'extraction change, elle change **à un
endroit**.

---

## Limites assumées — ce que la mesure dit

**Note mémoire : 0,500 (6/12).** Ce n'est pas un bug de l'évaluation, c'est **la mesure honnête**
de ce que l'extraction fait aujourd'hui.

`FACT_PATTERN` ne reconnaît qu'**une** tournure : « Ma/Mon/Mes *X* est/sont *Y* ». Six cas sur
douze parlent autrement — *« Je suis à Paris, code postal 75011 »*, *« Je porte toujours la
taille L »*, *« J'ai acheté le maillot mu-1999-treble »* — et **rien n'est mémorisé**.

**La suite logique** : un extracteur LLM, ou la couche épisodique Chroma. Une regex plus large
attraperait du bruit ; ajouter un motif par cas de test reviendrait à **coder le jeu de test au
lieu de la mémoire**.

**Correction apportée le 2026-07-17** : le motif a été **élargi au pluriel** (`Mes … sont`) —
*« Mes clubs préférés sont l'OM »* ne mémorisait **rien**. C'est une généralisation de la règle
existante, pas un cas particulier.

---

## Traçabilité des exigences

| Exigence | Où c'est réalisé | Preuve |
|---|---|---|
| **R1** rappel après 30+ tours | `key`/`value` en base + `FACT_PATTERN` | `test_recall_over_30_turns` ✅ |
| **R2** persistance inter-session | table + `StaticPool` / Postgres | `test_cross_session_persistence` ✅ |
| **R3** isolation par client | `user_id` indexé, filtré à **chaque** lecture | `test_isolation_between_customers` ✅ |
| **R5** droit à l'oubli | `deleted` + filtre + `forget()` | `test_right_to_be_forgotten` ✅ |
| **R6** traçabilité | `inspect()` : faits actifs + **clés** oubliées | `test_inspect_shows_what_was_remembered_and_forgotten` ✅ |
| R4 | budget de fenêtre de contexte | `token_budget` **déclaré, pas appliqué** — `read()` ne le consulte pas |

`tests/acceptance/test_memory.py` : **5 passed**.

**R6 est l'endroit où l'effacement logique paie.** `inspect()` rend les **clés** des faits
oubliés, jamais leurs valeurs : « on a supprimé quelque chose qui s'appelait *adresse* » est une
trace d'audit, « on a supprimé *12 rue des Lilas* » serait une fuite. Un `inspect()` qui
recracherait la valeur effacée détruirait le droit à l'oubli (R5) qu'il documente.

**R4 reste la seule exigence non tenue** : `token_budget` existe comme paramètre mais `read()`
ne s'en sert pas — tous les faits sont restitués, sans plafond. Limite identifiée, pas masquée.
