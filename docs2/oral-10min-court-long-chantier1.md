# Chantier 1 Mémoire — Script MODULABLE (court + long par section)

> Version 2026-07-07. Chaque section a DEUX niveaux :
> **[COURT]** entre crochets = 1-2 phrases, à dire si le temps presse.
> **LONG** = le paragraphe complet, à développer si tu as le temps ou si on te pose une question.
> Tu montes/descends de niveau selon l'horloge, sans perdre le fil. Commandes et numéros de ligne vérifiés.

---

## Avant de commencer

**[COURT]** *[J'ouvre VS Code dans le vrai projet, terminal neuf. Plan B si uv.exe bloqué : `.\.venv\Scripts\Activate.ps1` puis `python -m pytest`.]*

```powershell
code -r C:\Users\kanda\velmo-v2
```

**LONG** — J'ouvre VS Code directement dans le vrai projet, avec un terminal NEUF (les anciens peuvent afficher d'anciens résultats). Si Windows bloque `uv.exe` (AppLocker), j'active le venv une fois (`.\.venv\Scripts\Activate.ps1`) et je remplace `uv run pytest` par `python -m pytest` — résultats identiques, projet installé en editable. Et je ne colle jamais la ligne de prompt, seulement ce qui suit le `>`.

Je dis : « Aujourd'hui je présente le Chantier 1 : la Mémoire. Je ne sépare pas la théorie et la démo — j'ouvre les vrais fichiers, je lance les vraies commandes, j'explique la sortie. »

---

## 1. Le problème

**[COURT]** *[Velmo = assistant SAV maillots collector. Un bon agent ne fait pas que répondre : il doit se souvenir, ne pas mélanger les clients, et oublier sur demande. D'où 4 exigences : R1 rappel 30 tours, R2 persistance, R3 isolation, R5 oubli. Méthode : agent sain → tests rouges → code → preuve.]*

**LONG** — « Velmo est un assistant de support pour une boutique de maillots collector. Il répond sur les commandes, la livraison, les retours, le stock et la FAQ. Mais pour un vrai agent de support, répondre ne suffit pas : il doit être fiable. Il doit se souvenir des faits utiles du client, ne pas mélanger les clients, et pouvoir oublier une information sur demande. Mon Chantier 1 était de construire cette mémoire durable. Elle a quatre exigences : R1 rappeler un fait après 30 tours, R2 persister entre les sessions, R3 isoler entre les clients, R5 oublier sur demande. Ma méthode : d'abord prouver l'agent existant sain, puis lancer les tests mémoire en rouge, puis implémenter, et tout prouver au terminal. »

---

## 2. Prouver l'agent métier

```powershell
uv run pytest tests/acceptance/test_business.py -v
```
→ `7 passed`

**[COURT]** *[Je commence par les tests métier : 7 verts. Si l'agent était cassé, je ne saurais pas si une panne future vient de mon code. Le socle est propre.]*

**LONG** — « Je commence par les tests métier, avant de toucher la mémoire. Parce que si l'agent d'origine est déjà cassé, je ne peux pas savoir si une panne future vient de mon code ou du squelette. Ces tests protègent le métier : une commande expédiée ne se modifie pas, un gros remboursement escalade, Marc n'accède pas à la commande de Sophie, l'agent n'invente pas de stock. Sept verts : mon point de départ est propre, je peux coder la mémoire sans casser l'agent. »

**LONG+ [si on pose la question API]** — « Une précision : ces tests tournent hors-ligne en 0,2 seconde via EchoLLM — un bouchon de trois lignes, pas un modèle local. Le produit ne parle qu'à Kimi via l'API Azure, comme la note d'expert l'impose. Je garde l'API hors des tests exprès : un test qui dépend d'un LLM est non-déterministe, et la CI doit tourner sans clé. Même interrupteur que la base : une variable d'environnement, zéro code changé. »

---

## 3. Le contrat mémoire

```powershell
code -r -g C:\Users\kanda\velmo-v2\tests\acceptance\test_memory.py:8
```

**[COURT]** *[Ce fichier est mon contrat — je ne l'ai pas touché. 4 tests = R1 rappel, R2 persistance, R3 isolation, R5 oubli. Rouges au départ : c'est le TDD, pas un échec.]*

**LONG** — « Ce fichier est mon contrat, je ne l'ai pas modifié — il dit exactement ce que la mémoire doit faire. R1 : le client donne un fait au début, 30 messages de bruit arrivent, la mémoire doit quand même le retrouver. R2 : la mémoire ne peut pas vivre en RAM — un nouveau MemoryManager doit toujours voir le fait. R3 : un client ne voit jamais la mémoire d'un autre. R5 : après une demande d'oubli, les lectures ne retournent plus le fait. Au départ ces tests étaient rouges — normal, c'est le TDD : rouge d'abord, puis le code, puis vert. »

---

## 4. Le stockage : store.py

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\store.py:20
```

**[COURT]** *[Table `memory_facts` : id, user_id, key, value, deleted. user_id = isolation, deleted = oubli. SQLite en test, Postgres en prod via MEMORY_DB_URL — 0 ligne changée grâce à SQLAlchemy. Deux bases séparées : db.py métier, store.py mémoire.]*

**LONG** — « La première question : où vivent les souvenirs ? Dans un objet Python, ils disparaissent à l'arrêt du programme — la persistance ne passerait jamais. Donc une table : `memory_facts`, un souvenir = une ligne. Cinq colonnes : id, user_id le client, key le nom du fait, value la valeur, deleted le flag d'oubli. Le user_id garantit l'isolation : Marc et Sophie peuvent avoir la même clé, mais des lignes différentes. Le deleted permet l'oubli sans supprimer physiquement : je marque, read() ignore — effacé côté client, tracé côté système. Pour les tests, SQLite : rien à installer, la table se crée toute seule. Pour la prod, Postgres via MEMORY_DB_URL — SQLAlchemy fait le pont, le code ne change pas. Et deux bases séparées : db.py le métier (re-seedé à chaque test), store.py la mémoire (qui doit survivre). »

**LONG+ [piège métadonnées]** — « Pour être précis : deleted est ma seule métadonnée aujourd'hui. created_at, version ou confidence seraient des évolutions — elles n'existent pas encore, je ne prétends pas le contraire. »

---

## 5. Le pipeline : agent.py

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:70
```

**[COURT]** *[agent.py = le chef d'orchestre, non modifié. respond() en 5 temps : garde-fou entrée → memory.read (l.77) → routage → garde-fou sortie → memory.write (l.84). Avant, ces appels tombaient dans le vide ; maintenant, vraie mémoire.]*

**LONG** — « Ce fichier n'est pas la mémoire, c'est le chef d'orchestre. Chaque message passe par cinq temps : un, le garde-fou d'entrée — et même un refus est écrit en mémoire, donc traçable. Deux, memory.read. Trois, le routage : détecter un numéro de commande, comprendre une intention, appeler les outils, le stock, la FAQ, ou le LLM en dernier recours — avec confirmation avant les actions sensibles, et escalade si la commande est expédiée ou le montant trop élevé. Quatre, le garde-fou de sortie. Cinq, memory.write. Avant mon chantier, ces appels tombaient dans des coquilles vides ; maintenant, ils touchent une vraie mémoire. »

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:138
```

**[COURT — transparence]** *[Ligne 138 : le LLM reçoit une chaîne vide au lieu du contexte. La prise existe déjà dans llm.py — il ne manque que passer context.render(). C'est ma prochaine ligne, je préfère le dire.]*

**LONG — transparence** — « J'ai trouvé une limite moi-même : ligne 138, le LLM reçoit une chaîne vide à la place du contexte. Mais la prise existe déjà de l'autre côté : dans llm.py, invoke a un paramètre context depuis le début, et le client Azure sait l'ajouter au prompt sous un bloc "Mémoire:". Le squelette a été conçu pour ma mémoire — il ne manque que la fiche : context.render() au lieu de la chaîne vide. Le contrat est complet et testé ; ce branchement est la prochaine amélioration. Je préfère vous le dire que vous le laisser trouver. »

---

## 6. La façade : __init__.py

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:20
```

**[COURT]** *[FACT_PATTERN (:20) extrait "Ma X est Y" → clé/valeur. read (:51) filtre user_id + deleted. write (:63) distille au lieu de tout stocker. remember_fact (:71) upsert. forget (:87) soft-delete par inclusion. write réutilise remember_fact = un seul chemin d'écriture.]*

**LONG** — « C'est ici que les tests sont satisfaits. FACT_PATTERN détecte les faits simples : "Ma commande prioritaire est O-2024-0101" donne clé "commande prioritaire", valeur "O-2024-0101" — je ne stocke pas toute la conversation, je distille. read retourne les faits d'un seul user, filtrés par user_id et deleted — c'est pourquoi isolation et oubli sont structurels. write reçoit l'échange mais ne stocke que les faits utiles : capital pour le budget de tokens, car 30 tours de bruit alourdiraient le contexte. remember_fact fait l'upsert : met à jour si le fait existe, insère sinon — pas de doublons. Et forget : le test dit "adresse" mais la clé est "adresse de livraison", donc je cherche par inclusion, pas égalité ; je marque deleted=True, un soft-delete ; read ne le retourne plus — et je n'ai jamais eu à modifier read, il filtre les supprimés depuis le début. »

**LONG+ [limite regex]** — « J'assume la limite : une regex ne couvre que les formes prévues. En production, l'extracteur serait le LLM — même architecture. La regex est le choix minimal qui honore le contrat sans réseau. »

*(Numéros pour approfondir : read :51 · write :63 · remember_fact :71 · forget :87)*

---

## 7. Démo live

```powershell
uv run python -c "
from velmo.memory import MemoryManager
mm = MemoryManager()
mm.write('demo', 'Ma commande prioritaire est O-2024-0101.', 'ok')
mm.write('demo', 'Question de suivi sur un maillot.', 'ok')
print('Retenu :', mm.read('demo', '?').render())
print('Oubli  :', mm.forget('demo', 'commande'), 'fait supprime')
print('Apres  :', repr(mm.read('demo', '?').render()))
"
```
→ `Retenu : fact:commande prioritaire=O-2024-0101` · `Oubli : 1` · `Apres : ''`

**[COURT]** *[Deux messages entrent, un seul fait ressort : le bruit ne stocke rien (budget tokens). Oubli renvoie 1. Après : vide. Extraction + soft-delete + RGPD en trois lignes.]*

**LONG** — « Je démontre tout le chantier en un exemple. Je crée un MemoryManager, j'écris une phrase utile puis une question bruyante, je lis, j'oublie, je relis. Première ligne : la mémoire n'a retenu que le fait utile — le bruit est ignoré, write a distillé au lieu de tout stocker. Deuxième ligne : Oubli 1, un fait trouvé et marqué supprimé. Troisième ligne : vide, la lecture ne retourne plus rien. Cette démo prouve l'extraction, le filtrage du bruit, le soft-delete et le droit à l'oubli. »

---

## 8. La preuve : tests mémoire

```powershell
uv run pytest tests/acceptance/test_memory.py -v
```
→ `4 passed`

**[COURT]** *[4 verts = R1, R2, R3, R5. Ce ne sont pas mes démos, ce sont les tests exigés. Progression : 4 rouges → 2 → 3 → 4 verts.]*

**LONG** — « Ce sont les tests officiels, pas mes démos. Quatre verts : R1 rappel, R2 persistance, R3 isolation, R5 oubli — le contrat est complet. La progression est au journal : 4 rouges à la baseline, 2 verts après le store, 3 après l'extraction, puis un échec qui m'a appris une leçon : j'ai relancé en croyant forget codé, mais le disque disait encore return 0. Le test mesure le code sur disque, pas mon intention. Une fois vraiment sauvegardé : 4 verts. »

---

## 9. Non-régression

```powershell
uv run pytest tests/acceptance/test_business.py -v
```
→ `7 passed`

**[COURT]** *[Je relance le métier : toujours 7 verts. 4 + 7 = 11 verts. La mémoire n'a rien cassé.]*

**LONG** — « Je relance les tests métier car la mémoire ne doit pas casser l'agent. Une fonctionnalité n'est pas finie quand ses propres tests passent — elle doit préserver le comportement précédent. Sept verts toujours : 4 mémoire + 7 métier = 11 verts pour la partie terminée. »

---

## 10. Global (optionnel)

```powershell
uv run pytest -q
```

**[COURT]** *[Suite complète : les rouges restants = Chantiers 2 et 3 (garde-fous, MLOps), pas commencés. Mon périmètre : 11 verts, zéro régression.]*

**LONG** — « Cette commande lance toute la suite. Les rouges restants correspondent aux chantiers futurs — garde-fous et MLOps. Pour mon périmètre : 4 mémoire verts, 7 métier verts, aucune régression. »

---

## Clôture

**[COURT]** *[Chantier 1 = contrat mémoire testé : R1, R2, R3, R5 verts. Limites : ligne 138 à brancher, inspect() à coder, budget tokens sans troncature. Chaque affirmation a sa commande.]*

**LONG** — « Mon Chantier 1 n'est pas juste du code, c'est un contrat mémoire testé. J'ai prouvé l'agent (7 verts), utilisé les 4 tests comme contrat TDD, créé la table memory_facts avec user_id pour l'isolation et deleted pour l'oubli, implémenté read, write, remember_fact et forget. J'ai démontré que la mémoire extrait les faits utiles, ignore le bruit, persiste, isole, et oublie sur demande. Mes limites honnêtes : l'injection du contexte ligne 138 (la prise existe dans llm.py), inspect() à coder après ce debrief, et le budget de tokens respecté par conception mais sans code de troncature — nécessaire quand l'historique court terme et l'épisodique arriveront. Aujourd'hui je défends exactement ce qui est fini : l'agent tourne, les tests métier et mémoire sont verts, la mémoire couvre R1, R2, R3, R5 — et chaque affirmation est prouvée par une commande, un fichier, une sortie. »

---

# 📊 TABLEAU — les points qui méritent plus d'explication (court ↔ long)

> Utilise ce tableau si le formateur creuse un point précis : la colonne COURT est ta réponse rapide, la colonne LONG est le développement.

| Point | COURT (réponse rapide) | LONG (développement si on creuse) |
|---|---|---|
| **Soft-delete** | « deleted=True au lieu d'effacer : invisible client, tracé système. » | « Je ne supprime pas la ligne physiquement, je la marque deleted=True. read() filtre deleted=False, donc côté client le fait a disparu. Mais la ligne reste en base : trace d'audit RGPD — si un client conteste, on prouve que l'oubli a eu lieu, et on peut restaurer en cas d'erreur. » |
| **Inclusion vs égalité** | « "adresse" doit trouver "adresse de livraison" — donc inclusion, pas ==. » | « Le test demande d'oublier "adresse", mais la clé stockée par write était "adresse de livraison". Une égalité exacte (key == "adresse") ne trouverait rien. Je cherche donc les faits dont la clé OU la valeur CONTIENT la cible. C'était le vrai piège de l'étape forget. » |
| **Budget de tokens** | « 31 messages ne tiennent pas dans 2000 tokens, donc je distille en faits. » | « Le LLM a une limite de contexte. Garder 31 tours bruts la dépasserait. write extrait un fait compact clé=valeur et jette le reste : une phrase utile = une ligne, 30 tours de bruit = zéro octet. Le budget est respecté par conception ; il n'y a pas encore de code de troncature, qui deviendra nécessaire pour l'historique court terme. » |
| **SQLite → Postgres** | « Une variable, MEMORY_DB_URL. SQLAlchemy parle aux deux, 0 code changé. » | « SQLAlchemy est le pont entre objets Python et tables SQL. Le code écrit MemoryFact ; SQLAlchemy traduit en SQL adapté au moteur. En dev, SQLite (rien à installer). En prod, il suffit de définir MEMORY_DB_URL vers Postgres — même code, même API, seule l'URL change. C'est le même interrupteur que pour le LLM (EchoLLM/Kimi). » |
| **Ligne 138** | « Le contexte lu n'est pas encore injecté dans le prompt — prochaine ligne. » | « L'agent appelle memory.read() ligne 77, mais le résultat n'est pas passé au LLM : ligne 138, invoke reçoit "". La prise existe pourtant dans llm.py (paramètre context, bloc "Mémoire:"). Le contrat de stockage est à 4/4 ; brancher context.render() est une seule ligne, ma prochaine étape avec inspect(). » |
| **EchoLLM vs Kimi** | « EchoLLM = bouchon hors-ligne des tests. Le produit parle à Kimi via API. » | « get_llm() est un interrupteur : si la clé Azure existe, il renvoie AzureLLM (le vrai Kimi) ; sinon EchoLLM, un stub de 3 lignes qui accuse réception. Ce n'est PAS un modèle local (la note interdit les modèles locaux). Les tests tournent sur EchoLLM : déterministe, hors-ligne, gratuit, compatible CI sans clé. » |
| **Deux bases** | « db.py = métier (re-seedé). store.py = mémoire (doit survivre). » | « Cycles de vie opposés : la base métier est recréée fraîche à chaque test pour partir d'un état connu ; la mémoire doit persister entre sessions. Les mélanger casserait la persistance (R2). En prod, la mémoire vise Postgres via MEMORY_DB_URL, indépendamment de la base métier. Séparation des responsabilités. » |
| **Upsert** | « remember_fact met à jour si le fait existe, insère sinon. » | « Si Marc change de commande prioritaire, je ne crée pas une deuxième ligne : je mets à jour la valeur de la clé existante. remember_fact cherche d'abord (user_id + key, non supprimé), met à jour si trouvé, insère sinon. Ça garde la table propre et évite les doublons contradictoires. » |
