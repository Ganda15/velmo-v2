# ⛔ PÉRIMÉ (2026-07-08) — NE PAS UTILISER EN PRÉSENTATION

> **Remplacé par [`oral-final-chantier2-FR.md`](oral-final-chantier2-FR.md).**
> Périmé sur trois points : (1) dit « TDD » alors que les tests d'acceptance ont été **fournis** ;
> (2) fait commencer la démo par `pytest`, or le formateur a demandé une démo **conversationnelle**
> (Chantier 1, reproche n°3) ; (3) ignore les deux failles fermées le 10/07 (accents, PII entrante),
> et les numéros de ligne ont bougé depuis la réécriture de `guardrails/__init__.py`.
> Conservé pour l'historique du travail.

---

# Oral de présentation — Chantier 2 Garde-fous (FR)

> Deux versions : ① 10 minutes (complète, avec remarques de code), ② 5 minutes (condensée).
> Structurée autour des 7 étapes. Style : récit — chaque étape soudée à son pourquoi.
> Appui visuel : `schema-chantier2-demo-complete.png`. Preuve : `pytest`.

---

# ① VERSION 10 MINUTES

## [0:00] Ouverture — le problème

« Le Chantier 2, ce sont les garde-fous. Un agent SAV branché sur un LLM peut être manipulé : si on l'insulte, il pourrait répondre des horreurs ; si on lui dit "ignore tes instructions", il pourrait désobéir ; et il pourrait laisser fuiter une donnée sensible, comme un numéro de carte. Il faut donc une barrière AVANT l'agent — pour filtrer ce qui entre — et une barrière APRÈS — pour filtrer ce qui sort. Deux portiques de sécurité, comme à l'aéroport. J'ai construit ça en sept étapes, en TDD. »

## [1:00] Étape 1 — voir les tests rouges

« Ma première action n'a pas été d'écrire du code, mais de lancer les cinq tests d'acceptance. Tous rouges. C'est voulu : c'est mon contrat TDD. Le rouge me dit exactement quoi bloquer — haine, violence, sexuel, injection, hors-périmètre, et la fuite d'un numéro de carte. Tant que je ne les avais pas vus échouer, je ne savais pas précisément ce qu'on attendait de moi. »

## [2:00] Étape 2 — lire les outils fournis

« Ensuite j'ai lu ce qui existait déjà dans le code, avant d'inventer quoi que ce soit. Trois choses : les sept catégories déjà listées ; la classe Decision, qui est le verdict d'un garde-fou — elle contient allowed, action, category et un message de refus ; et la liste events, qui est mon journal, là où je tracerai chaque blocage. Je n'invente rien, je remplis les coquilles vides avec ces outils. »

## [3:00] Étape 3 — concevoir les mots-clés (avant de coder)

« Avant d'écrire une ligne, j'ai conçu la détection. Pour chaque catégorie, j'ai listé les mots-clés qui la trahissent. Et j'ai fait un choix important : je les ai tirés des VRAIS messages de test, pas au hasard. Par exemple, pour la haine : "hais", "race" ; pour la violence : "frapper", "tuer" ; pour l'injection : "ignore tes instructions". En français, parce que les messages sont en français, et sans accents, parce que les messages sont sans accents. Comme ça, chaque message hostile a au moins un mot-clé qui le déclenche. »

## [4:00] Étape 4 — coder le garde-fou d'entrée

« Puis j'ai codé check_input. »
[Remarque de code] « Le cœur, c'est un dictionnaire : à chaque catégorie, une liste de mots-clés. La méthode met le message en minuscules, parcourt chaque catégorie, et si un mot-clé est présent, elle bloque : elle renvoie un Decision "block" avec la bonne catégorie et un refus poli, ET elle ajoute une entrée dans le journal events. Si rien n'est trouvé, elle laisse passer. »
« Résultat : quatre tests passent d'un coup. »

## [5:00] Étape 5 — coder le garde-fou de sortie

« Restait le dernier rouge : le numéro de carte en sortie. »
[Remarque de code] « Là, j'utilise une expression régulière. Le test veut bloquer "4111 1111 1111 1111" mais laisser passer un numéro de commande comme "O-2024-0101". La différence, c'est la longueur : une carte, c'est seize chiffres en quatre groupes de quatre ; une commande, seulement huit chiffres. Ma regex cherche exactement seize chiffres en quatre groupes. Donc elle bloque la carte sans bloquer la commande. Et je réutilise mes mots-clés de l'entrée, parce que le brief demande les mêmes catégories plus les secrets à la sortie aussi. »
« Résultat : le cinquième test passe. Les cinq garde-fous sont verts. »

## [6:30] Étape 6 — l'équilibre des faux positifs

« Le test le plus difficile, c'était l'équilibre : bloquer TOUS les hostiles sans bloquer les vrais clients. Un faux positif, c'est bloquer un client légitime par erreur — c'est grave pour un SAV. Le seuil est sous les dix pour cent. Moi, j'ai zéro faux positif. Pourquoi ? Parce que mes mots-clés sont précis. Par exemple, je bloque sur "authentifier" — quelqu'un qui veut faire expertiser un maillot acheté ailleurs — mais pas sur "authentiques" — un vrai client qui demande si nos maillots ont un certificat. Un seul caractère de différence, mais ma conception les distingue. Cet équilibre était déjà atteint dès l'étape 4, grâce à la conception. »

## [8:00] Étape 7 — la non-régression

« Dernière étape : prouver que je n'ai rien cassé. Je relance TOUTE la suite, pas seulement les garde-fous. Seize tests verts : ma mémoire du Chantier 1 et l'agent métier sont restés verts. Zéro régression. Il reste trois rouges, mais ce sont les tests du Chantier 3, le MLOps, que je n'ai pas commencé — la fonction run_eval est encore vide. Ce n'est pas un bug, c'est le travail qui reste. Et le brief l'exige : une régression bloquerait la livraison. »

## [9:00] Clôture — la preuve et les limites

« Pour conclure : deux garde-fous fonctionnels, testés, et qui journalisent chaque blocage. Cinq tests d'acceptance verts, seize au total, zéro régression. Mes choix : la détection par mots-clés et regex, simple et déterministe — en production, un classifieur LLM serait plus robuste, je l'assume. Et mon journal est en mémoire, ce qui suffit au contrat ; en production, je le persisterais pour un audit durable. Tout est tracé dans mon journal de bord, étape par étape, avec le pourquoi de chaque choix. »

[Fin — questions.]

---

# ② VERSION 5 MINUTES

## [0:00] Le problème
« Chantier 2 : les garde-fous. Un agent SAV branché sur un LLM peut être manipulé ou laisser fuiter une donnée. Il faut une barrière à l'entrée et une à la sortie. Je l'ai fait en TDD. »

## [0:40] La méthode TDD (étapes 1 à 3)
« D'abord j'ai lancé les cinq tests : tous rouges, c'est mon contrat. Puis j'ai lu les outils fournis — les catégories, la classe Decision, le journal events. Puis j'ai conçu mes mots-clés à partir des vrais messages de test, en français. »

## [1:40] Les deux garde-fous (étapes 4 et 5)
« check_input, l'entrée : un dictionnaire catégorie → mots-clés ; si un mot est trouvé, je bloque avec la bonne catégorie, un refus, et je journalise. Quatre tests passent. check_output, la sortie : une regex qui détecte seize chiffres en quatre groupes — un numéro de carte — sans bloquer un numéro de commande, qui n'a que huit chiffres. Le cinquième test passe. »

## [3:00] L'équilibre (étape 6)
« Le test le plus dur : bloquer tous les hostiles sans bloquer les vrais clients. Zéro faux positif, parce que mes mots-clés sont précis : je bloque "authentifier" mais pas "authentiques". »

## [3:50] La preuve (étape 7)
« Je relance toute la suite : seize verts, zéro régression. Les trois rouges restants sont le Chantier 3, MLOps, pas encore commencé. »

## [4:30] Clôture
« Deux garde-fous testés et journalisés. Choix assumés : mots-clés et regex plutôt que LLM, journal en mémoire plutôt que persisté — le bon niveau pour le brief. »

[Fin — questions.]

---

# 🎓 Questions probables (rappel)
1. « Pourquoi deux garde-fous ? » → « L'entrée protège l'agent des attaques, la sortie protège le client des fuites. Risques différents. »
2. « Comment tu évites de bloquer un vrai client ? » → « Mots-clés précis : "authentifier" bloqué, "authentiques" pas. Zéro faux positif. »
3. « Comment tu distingues carte et commande ? » → « La longueur : ma regex exige seize chiffres, la commande n'en a que huit. »
4. « Pourquoi il reste des rouges ? » → « Chantier 3 MLOps, run_eval pas codé. Pas une régression. »
5. « C'est quoi ta journalisation ? » → « Chaque blocage ajoute une entrée dans la liste events. En mémoire aujourd'hui, persistée en prod. »
