# ⛔ PÉRIMÉ (2026-07-08) — NE PAS UTILISER EN PRÉSENTATION

> **Remplacé par [`schema-chantier2-EXPLICATION.md`](schema-chantier2-EXPLICATION.md).**
> ⚠️ Ce fichier annonce « numéros de ligne vérifiés contre le vrai code » : **ils ne le sont plus.**
> `guardrails/__init__.py` a été réécrit le 10/07 (ajout de `_normalize`, de la PII entrante et de
> `_journalise`), toutes les lignes ont bougé. Il dit aussi « cycle TDD » alors que les tests
> d'acceptance ont été **fournis** par le formateur.
> Conservé pour l'historique du travail.

---

# Oral — expliquer le schéma DÉMO Chantier 2, boîte par boîte + fichier/ligne

> Schéma : `schema-chantier2-demo-complete.png`. Créé 2026-07-08.
> Pour chaque boîte / flèche : ce que tu DIS + [entre crochets : le fichier et la ligne à ouvrir, et pourquoi].
> Numéros de ligne vérifiés contre le vrai code. À droite = le cycle TDD ; à gauche = l'architecture.

**Phrase d'ouverture** :
« Voici tout mon Chantier 2 en une image. À gauche, ce que le code fait : deux portiques de sécurité autour de l'agent. À droite, comment je le construis et le prouve : le cycle TDD. La flèche du milieu relie les deux : le code que j'écris à droite devient les portiques de gauche. »

---

# PANNEAU GAUCHE — L'ARCHITECTURE

## Boîte : MESSAGE CLIENT (gris)
« Tout part d'un message du client. On ne lui fait pas confiance par défaut — il peut être normal ou hostile. »
[Rien à ouvrir — c'est l'entrée du système.]

**→ flèche vers le bas** : « Le message entre d'abord dans le premier portique. »
[C'est `agent.py:71` — `gate_in = self.guardrails.check_input(message)` : l'agent appelle le garde-fou d'entrée AVANT tout le reste.]

## Boîte ① : check_input — garde-fou d'ENTRÉE (orange)
« Premier portique. Il inspecte le message et cherche six choses : haine, violence, sexuel, injection de prompt, hors-périmètre, demande de secret. »
[Fichier à ouvrir : `src/velmo/guardrails/__init__.py:40` — la méthode `check_input`. C'est ici que je code la détection. Pourquoi cette ligne : c'est la coquille vide qui renvoie "allow" aujourd'hui, je dois la remplir.]

**→ flèche latérale "hostile" → BLOQUÉ (rouge)** : « Si le message est hostile, il est bloqué ici : l'agent renvoie un refus poli et journalise l'événement. Le message n'atteint jamais le LLM. »
[La décision de blocage = `Decision(allowed=False, action="block", category=..., refusal=...)`, défini `guardrails/__init__.py:24`. La journalisation = la liste `events`, ligne 38. Côté agent, le refus est renvoyé à `agent.py:72-73` (`if not gate_in.allowed: return refusal`).]

**→ flèche "autorisé" vers le bas** : « Si le message est propre, il est autorisé et passe à l'agent. »
[`agent.py:72` — quand `gate_in.allowed` est vrai, le code continue vers l'agent.]

## Boîte : AGENT (bleu)
« L'agent fait son travail : il utilise ma mémoire du Chantier 1 et le LLM Kimi pour produire une réponse. »
[`agent.py:77` (memory.read) et `agent.py:78` (_handle qui produit la réponse). C'est le Chantier 1 déjà fait.]

**→ flèche vers le bas** : « Mais avant que la réponse parte au client, elle repasse un deuxième contrôle. »
[`agent.py:80` — `gate_out = self.guardrails.check_output(answer)` : le garde-fou de sortie sur la réponse.]

## Boîte ② : check_output — garde-fou de SORTIE (orange)
« Deuxième portique. Selon le brief, il contrôle les mêmes catégories que l'entrée + la fuite de PII (n° de carte bancaire), les secrets et le hors-périmètre. Il laisse passer une réponse métier normale, mais bloque ce qui ne doit pas sortir. »
[Fichier à ouvrir : `src/velmo/guardrails/__init__.py:44` — la méthode `check_output`. Pourquoi : c'est l'autre coquille vide à remplir, avec une regex pour le n° de carte.]

**→ flèche latérale "fuite" → BLOQUÉ (rouge)** : « Si la réponse contient une fuite, elle est bloquée et remplacée par un refus. Le client ne voit jamais la donnée sensible. »
[Côté agent : `agent.py:81-82` (`if not gate_out.allowed: answer = refusal`).]

**→ flèche "autorisé" vers le bas** : « Sinon, la réponse est propre et part au client. »

## Boîte : RÉPONSE CLIENT (vert)
« Le client reçoit une réponse sûre — contrôlée à l'entrée ET à la sortie. »

---

# PANNEAU DROIT — LE CYCLE TDD

## Boîte A : LANCER LE TEST (rouge) — terminal `5 failed`
« Je commence par lancer les 5 tests d'acceptance AVANT de coder. Ils sont rouges : c'est mon contrat, il me dit quoi bloquer. »
[Commande : `python -m pytest tests/acceptance/test_guardrails.py -v`. Fichier des tests : `tests/acceptance/test_guardrails.py` — je ne le modifie jamais, c'est lui qui me juge.]

**→ flèche "je code"** : « Donc je sais quoi produire, j'écris le code. »

## Boîte B : ÉCRIRE / MODIFIER LE CODE (violet)
« J'écris dans `guardrails/__init__.py` : `check_input` détecte les mots-clés et renvoie un blocage + journalise ; `check_output` utilise une regex pour le n° de carte et les secrets. »
[Fichier : `src/velmo/guardrails/__init__.py`. Les deux méthodes lignes 40 et 44. J'utilise `Decision` (ligne 24) et `CATEGORIES` (ligne 12) déjà fournis.]

**→ flèche "je relance"** : « Une fois le code écrit, je relance le test. »

## Boîte C : RELANCER LE TEST (vert) — terminal `5 passed`
« Je relance la même commande. Les 5 tests passent au vert : le contrat est rempli. »
[Même commande qu'en A : `python -m pytest tests/acceptance/test_guardrails.py -v`. Le test mesure le code sur le disque — donc je sauvegarde avant.]

**→ flèche rouge (boucle) "test encore ROUGE ? je retourne coder (B)"** : « Si un test est encore rouge, je ne panique pas : je retourne au code, je corrige, je relance. C'est la boucle du TDD — rouge, corriger, vert. »

**→ flèche vers le bas** : « Quand tout est vert, je vérifie que je n'ai rien cassé. »

## Boîte D : NON-RÉGRESSION (gris)
« Je lance toute la suite. 16 verts au total : 5 garde-fous + 4 mémoire + 7 métier. La sécurité est ajoutée sans rien casser. »
[Commande : `python -m pytest -q`. Attendu : 16 passed.]

---

# LA NOTE JOURNAL (en bas à gauche)

« Sous le flux, la note : chaque BLOCAGE est journalisé dans `self.events`. C'est la journalisation exigée par le brief — à chaque fois qu'un portique bloque, j'ajoute une entrée. C'est une liste en mémoire (suffit au test) ; en prod, je la persisterais. »
[Fichier : `guardrails/__init__.py:38` — la liste `events`. C'est là que `check_input` et `check_output` écriront `self.events.append({...})` à chaque blocage.]

---

# LA FLÈCHE DU MILIEU (violette) — la liaison

« Cette flèche relie les deux panneaux : le code que j'écris dans la boîte B **devient** exactement les deux portiques ① et ② de gauche. Ce n'est pas deux choses séparées — c'est la même chose vue sous deux angles : à gauche le comportement, à droite comment je l'ai construit. »
[Concrètement : `guardrails/__init__.py:40` (check_input) = portique ① ; `guardrails/__init__.py:44` (check_output) = portique ②. L'agent les appelle en `agent.py:71` et `agent.py:80`.]

---

# 🎓 Questions probables du formateur (avec fichier/ligne)

1. « Où est appelé ton garde-fou dans l'agent ? » → « À l'entrée, `agent.py:71` ; à la sortie, `agent.py:80`. Je n'ai pas modifié l'agent, il appelait déjà ces deux points. »
2. « Comment tu journalises un blocage ? » → « J'ajoute une entrée dans la liste `events` de `GuardrailEngine` (`guardrails/__init__.py:38`). Le test vérifie `len(engine.events) >= 3`. »
3. « Pourquoi la sortie ne bloque pas tout ? » → « `check_output` doit laisser passer "commande O-2024-0101 prepared" mais bloquer un n° de carte. C'est une détection ciblée, pas un blocage aveugle. »
4. « C'est quoi `Decision` ? » → « C'est le verdict d'un garde-fou (`guardrails/__init__.py:24`) : `allowed`, `action`, `category`, `refusal`. C'est ce que mes deux méthodes renvoient. »
