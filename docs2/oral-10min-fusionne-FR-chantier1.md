# Chantier 1 Mémoire — Script oral fusionné 10 minutes (corrigé & complet)

> Version corrigée, 2026-07-07. Tous les numéros de ligne vérifiés contre le vrai code.
> Version récit complète : `docs2/oral-humanise-complet-chantier1.md` (Partie A).

## Avant de commencer

J'ouvre VS Code directement dans le vrai projet, avec un terminal NEUF (ferme les anciens — un vieux terminal peut afficher d'anciens résultats) :

```powershell
code -r C:\Users\kanda\velmo-v2
```

⚠️ Plan B si Windows bloque `uv.exe` (message AppLocker « stratégie de contrôle d'application ») : active le venv une fois, puis remplace `uv run pytest` par `python -m pytest` et `uv run python` par `python` — résultats identiques, car le projet est installé en mode editable :

```powershell
.\.venv\Scripts\Activate.ps1
```

⚠️ Ne colle jamais la ligne de prompt (`(velmo-v2) PS C:\...>`) — seulement ce qui vient après le `>`.

Je dis : « Aujourd'hui je présente le Chantier 1 : la Mémoire. Je ne sépare pas la théorie et la démo. J'explique chaque étape, j'ouvre les vrais fichiers, je lance les vraies commandes, et j'explique la sortie directement. »

## 1. Commencer par le problème

« Velmo est un assistant de support pour une boutique de maillots de foot collector. L'agent doit répondre aux questions client sur les commandes, la livraison, les retours, les remboursements, le stock et la FAQ. Mais pour un vrai agent de support, répondre ne suffit pas. L'agent doit aussi être fiable. Il doit se souvenir des faits utiles du client, il ne doit pas mélanger les clients, et il doit pouvoir oublier une information quand le client le demande. Donc mon objectif du Chantier 1 était de construire une mémoire durable pour l'agent. Cette mémoire a quatre exigences : R1 : rappeler un fait utile après 30 tours. R2 : persister la mémoire entre les sessions. R3 : isoler la mémoire entre les clients. R5 : oublier un fait sur demande. Ma méthode était simple : d'abord prouver que l'agent existant est sain, ensuite lancer les tests mémoire en rouge, puis implémenter la mémoire manquante, et enfin tout prouver avec des commandes terminal. »

## 2. Prouver que l'agent métier d'origine est sain

Je lance :

```powershell
uv run pytest tests/acceptance/test_business.py -v
```

Je dis pendant que ça tourne : « Je commence par les tests métier, avant de toucher la mémoire. Pourquoi ? Parce que si l'agent d'origine est déjà cassé, je ne peux pas savoir si une panne future vient de mon code ou du squelette initial. Ces tests protègent le comportement métier de Velmo : commandes, remboursements, stock, escalade et isolation des clients. »

Sortie attendue :

```text
7 passed
```

J'explique la sortie : « Ici, sept tests métier passent. Ça veut dire que l'agent fonctionne déjà pour les règles métier existantes. Par exemple, une commande expédiée ne peut pas être modifiée, un remboursement au-dessus de la limite est escaladé, Marc ne peut pas accéder à la commande de Sophie, et l'agent n'invente pas de stock quand le produit est indisponible. Donc mon point de départ est propre. Je peux maintenant travailler sur la mémoire sans casser l'agent métier. »

[AJOUT — la question de l'API, avant qu'on la pose] J'ajoute : « Une précision : ces tests tournent hors-ligne en 0,2 seconde, via EchoLLM — un bouchon déterministe de trois lignes, pas un modèle local. Le produit lui-même ne parle qu'à Kimi via l'API Azure, comme la note d'expert l'impose : `get_llm()` construit le client Azure dès que la clé est configurée, et j'ai validé cette chaîne séparément — le vrai Kimi a répondu. Je garde l'API hors des tests exprès : un test qui dépend d'une réponse de LLM est non-déterministe, et la CI dans GitHub Actions doit tourner sans ma clé API. Même philosophie d'interrupteur que la base de données : une variable d'environnement, zéro ligne de code changée. J'ai aussi vérifié `git status` au départ : le repo du formateur était intact — je n'ai jamais touché aux tests ni aux contrats. »

## 3. Ouvrir le contrat mémoire

J'ouvre les tests d'acceptance :

```powershell
code -r -g C:\Users\kanda\velmo-v2\tests\acceptance\test_memory.py:8
```

Je dis : « Maintenant j'ouvre les tests d'acceptance mémoire. Ce fichier est mon contrat. Je ne l'ai pas modifié. Il me dit exactement ce que la mémoire doit faire. »

J'explique les quatre tests : « Le premier test est le rappel sur 30 tours. Le client donne un fait important au début, puis il y a 30 messages de bruit, et la mémoire doit quand même retourner le fait utile. Le deuxième test est la persistance entre sessions. Ça veut dire que la mémoire ne peut pas vivre uniquement dans la RAM Python. Si je crée un nouveau MemoryManager, le fait doit toujours exister. Le troisième test est l'isolation des clients. Un client ne doit jamais voir la mémoire d'un autre client. Le quatrième test est le droit à l'oubli. Si le client demande d'oublier quelque chose, les lectures futures ne doivent plus retourner ce fait. »

J'ajoute : « Au début, ces tests étaient rouges. C'était normal parce que la mémoire n'était pas encore implémentée. C'est le TDD : rouge d'abord, puis le code, puis vert. »

## 4. Ouvrir la couche de stockage : où vivent les souvenirs

J'ouvre le store mémoire :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\store.py:20
```

Je dis : « La première question technique était : où vivent les souvenirs ? Si je stocke la mémoire seulement dans un objet Python, elle disparaît quand le programme s'arrête. Donc le test de persistance ne peut jamais passer. C'est pour ça que j'ai créé une couche de stockage en base de données. »

J'explique la table : « Ici j'ai une table appelée `memory_facts`. Un souvenir est une ligne durable. Les colonnes importantes sont : `id`, l'identifiant technique. `user_id`, l'identifiant du client. `key`, le nom du fait, par exemple commande prioritaire ou adresse de livraison. `value`, la valeur stockée. `deleted`, un booléen pour l'oubli. »

Puis j'explique pourquoi chaque colonne compte : « Le `user_id` est essentiel pour l'isolation. Chaque souvenir appartient à un client. Donc Marc et Sophie peuvent avoir la même clé, mais ils auront quand même des lignes de mémoire différentes. Le flag `deleted` est essentiel pour le droit à l'oubli. Je ne supprime pas physiquement la ligne. Je la marque comme supprimée. Ensuite `read()` ignore les faits supprimés. Du point de vue du client, le fait a disparu. Du point de vue du système, on garde une trace d'audit. [AJOUT — piège des métadonnées] Et pour être précis : `deleted` est ma seule métadonnée implémentée aujourd'hui. Des colonnes comme created_at, version ou confidence seraient des évolutions possibles — elles n'existent pas encore, et je ne prétendrai pas le contraire. »

J'explique SQLite et Postgres : « Pour les tests et le développement, j'utilise SQLite. C'est rapide, local, et ça ne nécessite ni Docker ni réseau — c'est livré avec Python, et SQLAlchemy crée la table automatiquement au chargement. Pour la production, le même code peut utiliser Postgres en définissant `MEMORY_DB_URL` — et Postgres lui-même se lance avec un seul `docker run postgres`. La raison pour laquelle ça marche, c'est SQLAlchemy. SQLAlchemy est le pont entre les objets Python et les tables SQL. Donc le code mémoire n'a pas besoin de changer quand je passe de SQLite à Postgres. »

J'ajoute la distinction importante : « Il y a deux bases de données dans le projet. `db.py` est la base métier du formateur : commandes, produits, clients. `store.py` est ma base mémoire : les faits durables sur les utilisateurs. Je les garde séparées parce que la base métier est re-seedée pendant les tests, mais la mémoire doit survivre entre les sessions. Si je les mélangeais, je pourrais créer une mémoire amnésique. »

## 5. Ouvrir le pipeline de l'agent : où la mémoire est appelée

J'ouvre l'agent :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:70
```

Je dis : « Maintenant j'ouvre le pipeline de l'agent. Ce fichier n'est pas la mémoire elle-même. C'est le chef d'orchestre. Il reçoit le message client et décide quoi faire. »

J'explique le flux : « Chaque message accepté passe par cinq étapes. Premièrement, le garde-fou d'entrée vérifie le message utilisateur — [AJOUT] et remarquez un détail : même un message refusé est écrit en mémoire, donc les refus restent traçables. Deuxièmement, l'agent appelle `memory.read()`. Troisièmement, l'agent route le message. Il peut détecter un numéro de commande, comprendre une intention comme un remboursement ou un changement d'adresse, appeler les outils métier, vérifier le stock, vérifier la FAQ, ou utiliser le LLM en dernier recours — et pour les actions sensibles il exige d'abord une confirmation explicite, et les outils escaladent quand la commande est expédiée ou que le montant dépasse le plafond. Quatrièmement, le garde-fou de sortie vérifie la réponse. Cinquièmement, l'agent appelle `memory.write()` pour extraire et stocker les faits utiles. »

Je dis : « Avant mon chantier, le pipeline avait déjà les appels à la mémoire, mais les méthodes mémoire étaient des coquilles vides. Après mon travail, les mêmes appels se connectent maintenant à une vraie mémoire. »

Puis j'ouvre la limite honnête :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:138
```

Je dis : « J'ai aussi trouvé moi-même une limite importante. L'agent appelle `memory.read()`, mais à la ligne 138 le LLM reçoit encore une chaîne de contexte vide. [AJOUT — l'argument de la prise] Ce qui est intéressant, c'est que la prise existe déjà de l'autre côté : dans `llm.py`, la méthode `invoke` a un paramètre `context` depuis le premier jour, et le client Azure sait déjà l'ajouter au prompt sous un bloc « Mémoire: ». Le squelette a été conçu pour recevoir ma mémoire — il ne manque que la fiche. Donc le contrat de stockage mémoire est complet, mais la prochaine étape est d'injecter `context.render()` dans le prompt du LLM. Je préfère le dire clairement : la mémoire est implémentée et testée, mais l'injection du contexte dans le LLM est la prochaine amélioration. »

## 6. Ouvrir la façade mémoire : les méthodes que j'ai implémentées

J'ouvre la façade mémoire :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:20
```

Je dis : « Maintenant je montre la façade mémoire principale. C'est ici que les tests d'acceptance sont satisfaits. »

J'explique le motif : « Ici, `FACT_PATTERN` détecte des faits utiles simples en langage naturel. Par exemple, si le client dit : ‘Ma commande prioritaire est O-2024-0101’, la mémoire peut extraire : clé : commande prioritaire, valeur : O-2024-0101. C'est important parce que je ne stocke pas toute la conversation. Je distille le fait utile. [AJOUT — limite regex, assumée] J'assume aussi la limite : une regex ne couvre que les formes prévues. En production, cet extracteur serait le LLM — même architecture, extracteur différent. La regex est le choix minimal qui honore le contrat de test sans accès réseau. »

Puis j'ouvre `read()` :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:51
```

Je dis : « `read()` retourne les faits d'un seul utilisateur. Il filtre par `user_id`. Il filtre aussi les faits supprimés. C'est pour ça que l'isolation des clients et l'oubli fonctionnent structurellement. »

Puis j'ouvre `write()` :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:63
```

Je dis : « `write()` reçoit le message client et la réponse de l'agent. Mais il ne stocke pas chaque message. Il extrait seulement les faits utiles. C'est important pour le budget de tokens. Si on stocke 30 tours de bruit, le contexte devient trop lourd. À la place, on garde des faits compacts. »

Puis j'ouvre `remember_fact()` :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:71
```

Je dis : « `remember_fact()` stocke un fait. Il fonctionne comme un upsert : si le fait existe déjà, il le met à jour. S'il n'existe pas, il l'insère. Donc le même client peut mettre à jour un fait sans créer de doublons inutiles. [AJOUT — argument de réutilisation] Et `write()` appelle `remember_fact()` au lieu d'écrire son propre SQL : un seul chemin d'écriture vers la base, un seul endroit à déboguer. »

Puis j'ouvre `forget()` :

```powershell
code -r -g C:\Users\kanda\velmo-v2\src\velmo\memory\__init__.py:87
```

Je dis : « `forget()` implémente le droit à l'oubli. Le test peut demander d'oublier ‘adresse’, mais la clé stockée peut être ‘adresse de livraison’. Donc l'égalité exacte est trop stricte. J'utilise la logique d'inclusion. Ensuite je marque le fait comme `deleted=True`. Je ne supprime pas la ligne physiquement. C'est le soft-delete. Après ça, `read()` ne le retourne plus — [AJOUT] et l'élégant, c'est que je n'ai jamais eu à modifier `read()` pour ça : il filtre les faits supprimés depuis le premier jour. Une décision prise deux étapes plus tôt a payé ici. »

## 7. Démo live : extraction, bruit ignoré, oubli

Je lance la commande live :

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

Je dis avant d'appuyer sur Entrée : « Maintenant je démontre tout le chantier mémoire dans un petit exemple live. D'abord, je crée un MemoryManager. Puis j'écris une phrase utile : ‘Ma commande prioritaire est O-2024-0101.’ Puis j'écris une question de suivi bruyante. Après ça, je lis la mémoire. Puis j'oublie le fait commande. Enfin, je relis. »

Sortie attendue :

```text
Retenu : fact:commande prioritaire=O-2024-0101
Oubli  : 1 fait supprime
Apres  : ''
```

J'explique la sortie : « La première ligne montre que la mémoire n'a retenu que le fait utile : `fact:commande prioritaire=O-2024-0101`. Le message bruyant a été ignoré. Donc `write()` a distillé la conversation au lieu de tout stocker. La deuxième ligne dit : `Oubli : 1 fait supprime`. Ça veut dire qu'un fait correspondant a été trouvé et marqué comme supprimé. La troisième ligne dit : `Apres : ''`. Ça veut dire qu'après l'oubli, la lecture mémoire retourne vide. Donc cette démo live prouve l'extraction, le filtrage du bruit, le soft-delete, et le droit à l'oubli. »

## 8. Lancer les tests d'acceptance mémoire

Je lance :

```powershell
uv run pytest tests/acceptance/test_memory.py -v
```

Je dis : « Maintenant je lance les tests d'acceptance mémoire officiels. C'est la vraie preuve, parce que ce ne sont pas mes commandes de démo. Ce sont les tests exigés. »

Sortie attendue :

```text
4 passed
```

J'explique : « Quatre tests passent. Ça veut dire que la mémoire satisfait les quatre exigences : R1 : rappel après 30 tours. R2 : persistance entre sessions. R3 : isolation entre clients. R5 : oubli sur demande. Donc le contrat mémoire est complet. [AJOUT — la progression et la leçon du disque] La progression est dans mon journal de bord : 4 rouges à la baseline, 2 verts après le store, 3 verts après l'extraction, puis un échec de plus qui m'a appris une leçon — j'ai relancé les tests en croyant que `forget` était codé, mais le fichier sur le disque disait encore `return 0`. Un test ne mesure pas mon intention : il mesure le code sur le disque. Une fois le code vraiment sauvegardé : 4 verts. »

## 9. Relancer les tests métier pour la non-régression

Je relance :

```powershell
uv run pytest tests/acceptance/test_business.py -v
```

Je dis : « Je relance les tests métier parce que la mémoire ne doit pas casser l'agent existant. Une fonctionnalité n'est pas finie seulement quand ses propres tests passent. Elle doit aussi préserver le comportement précédent. »

Sortie attendue :

```text
7 passed
```

J'explique : « Les sept tests métier sont toujours verts. Donc j'ai 4 tests mémoire passés et 7 tests métier passés. Ensemble, ça donne 11 tests verts pour la partie terminée. »

## 10. Commande globale optionnelle

Je peux lancer :

```powershell
uv run pytest -q
```

Je dis : « Cette commande lance la suite de tests plus large. S'il reste des tests rouges, ils correspondent aux chantiers futurs, surtout les garde-fous et le MLOps. Pour mon périmètre actuel, le résultat important est : 4 tests mémoire verts. 7 tests métier verts. Aucune régression sur l'agent existant. »

## Clôture finale

« Pour conclure, mon Chantier 1 n'est pas juste du code. C'est un contrat mémoire testé. J'ai commencé par prouver l'agent existant avec 7 tests métier. Puis j'ai utilisé les 4 tests mémoire comme mon contrat TDD. J'ai créé une table `memory_facts` durable avec `user_id` pour l'isolation et `deleted` pour l'oubli. J'ai implémenté `read`, `write`, `remember_fact` et `forget`. J'ai démontré que la mémoire extrait les faits utiles, ignore le bruit, persiste entre les sessions, isole les clients, et oublie les faits sur demande. [AJOUT — limites honnêtes complètes] Les limites honnêtes restantes sont trois : l'injection du contexte LLM à la ligne 138 — la mémoire est lue, mais `context.render()` doit encore être passé dans le prompt, et la prise pour ça existe déjà dans `llm.py` ; la méthode `inspect()` — du confort d'observabilité, sans test d'acceptance, que je coderai juste après ce debrief ; et le budget de tokens de 2000 — respecté par conception parce que je ne stocke que des faits compacts, mais sans code de troncature pour l'instant, qui deviendra nécessaire quand l'historique court terme et la mémoire épisodique arriveront. Donc aujourd'hui je peux défendre exactement ce qui est terminé : l'agent fonctionne toujours. Les tests métier sont verts. Les tests mémoire sont verts. La mémoire couvre R1, R2, R3 et R5. Et chaque affirmation que j'ai faite est prouvée par une commande, un fichier et une sortie. »
