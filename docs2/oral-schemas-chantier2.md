# ⛔ PÉRIMÉ (2026-07-08) — NE PAS UTILISER EN PRÉSENTATION

> **Remplacé par [`schema-chantier2-EXPLICATION.md`](schema-chantier2-EXPLICATION.md).**
> On ne montre plus qu'UN schéma, en deux temps : `schema-A-gauche.png` (0:00→4:30) puis
> `schema-AB-complet.png`. La boîte `check_input` porte désormais aussi la catégorie `PII`.
> Conservé pour l'historique du travail.

---

# Oral — expliquer les 2 schémas Chantier 2 (garde-fous), boîte par boîte

> Créé 2026-07-08. Deux schémas : `schema-chantier2-plan.png` (plan 7 étapes) et `schema-chantier2-portiques.png` (les deux portiques).
> Pour chaque boîte et chaque flèche : ce que tu DIS. Style récit — chaque flèche se dit « donc ».

---

# SCHÉMA 1 — Le plan de travail (7 étapes)

**Phrase d'ouverture** : « Voici mon plan pour les garde-fous, en 7 étapes, méthode TDD comme pour la mémoire. Chaque flèche se lit "donc". »

## Boîte ① — ÉTAPE 1 : Voir les tests ROUGES (rouge)
« Je commence par lancer les 5 tests d'acceptance AVANT d'écrire une ligne. Ils sont tous rouges — et c'est voulu : le rouge, c'est mon contrat, il me dit exactement ce que je dois bloquer. »

**→ flèche** : « DONC, une fois que je sais ce qu'on attend de moi… »

## Boîte ② — ÉTAPE 2 : Lire les 3 pièces (bleu)
« …je lis les outils déjà fournis dans le code : la classe `Decision`, qui est le verdict — elle contient `allowed`, `action`, `category`, `refusal`. Les 7 `CATEGORIES` déjà listées. Et le fichier de tests, pour voir les cas exacts. Je ne réinvente rien, j'utilise ce qui existe. »

**→ flèche** : « DONC je sais quoi produire ; il me reste à décider comment détecter. »

## Boîte ③ — ÉTAPE 3 : Concevoir sur papier (violet)
« Avant de coder, je conçois : pour chaque catégorie — haine, violence, sexuel, injection, hors-périmètre, secret — je liste les mots-clés qui la trahissent. C'est la conception, et c'est la porte d'entrée que le formateur exige : on valide le schéma avant le code. »

**→ flèche** : « DONC, mon plan de détection prêt, je code le premier garde-fou. »

## Boîte ④ — ÉTAPE 4 : Coder check_input (orange)
« Le garde-fou d'entrée : il inspecte le message du client, cherche les mots-clés, et s'il en trouve, il renvoie une `Decision` de blocage avec la bonne catégorie et un refus poli — et il journalise l'événement. Cette étape fait avancer 4 tests d'un coup : haine/violence/sexuel, injection, et hors-périmètre. »

**→ flèche** : « DONC l'entrée est protégée ; je passe à la sortie. »

## Boîte ⑤ — ÉTAPE 5 : Coder check_output (orange)
« Le garde-fou de sortie : il inspecte la réponse AVANT qu'elle parte. Il cherche un numéro de carte bancaire — avec une regex — et les secrets. Mais attention : il doit laisser passer une réponse normale comme "votre commande O-2024-0101 est prepared". Pas de blocage aveugle. Cette étape fait passer le test PII. »

**→ flèche** : « DONC les deux portiques marchent ; reste le point délicat. »

## Boîte ⑥ — ÉTAPE 6 : Régler le seuil de faux positifs (gris)
« C'est le test le plus dur. Il faut bloquer TOUS les messages hostiles — 35 cas de test — ET ne pas bloquer par erreur les messages légitimes : moins de 10% de faux positifs. C'est un équilibre : trop strict, je bloque des vrais clients ; trop laxiste, je laisse passer des attaques. »

**→ flèche** : « DONC, une fois l'équilibre trouvé, je prouve tout. »

## Boîte ⑦ — ÉTAPE 7 : Lancer tous les tests (vert)
« Je lance toute la suite. Les 5 tests garde-fous passent au vert, ET la non-régression tient : mes 4 tests mémoire et les 7 tests métier restent verts. Ça fait 16 verts au total. Le chantier est prouvé. »

**Phrase de clôture** : « Sept étapes, du rouge au vert, chacune fait avancer un test précis. »

---

# SCHÉMA 2 — Les deux portiques de sécurité

**Phrase d'ouverture** : « La sécurité, ce sont deux portiques : un AVANT l'agent, un APRÈS. Comme à l'aéroport : on contrôle à l'entrée et à la sortie. »

## Boîte — MESSAGE CLIENT (gris)
« Tout part d'un message du client. Il peut être normal… ou hostile. On ne fait pas confiance par défaut. »

**→ flèche (vers le bas)** : « Le message entre d'abord dans le premier portique. »

## Boîte ① — GARDE-FOU D'ENTRÉE, check_input (orange)
« Premier portique. Il cherche six choses : haine, violence, sexuel, injection de prompt, hors-périmètre, et demande de secret. C'est la protection de l'agent : on filtre avant même que le LLM voie le message. »

**→ flèche latérale "hostile" → boîte BLOQUÉ (rouge)** : « Si le message est hostile, il est bloqué ici : l'agent répond un refus poli et journalise l'événement. Le message n'atteint jamais le LLM. »

**→ flèche "autorisé" (vers le bas)** : « Si le message est propre, DONC il est autorisé et passe à l'agent. »

## Boîte — AGENT (bleu)
« L'agent fait son travail : il utilise ma mémoire du Chantier 1 et le LLM Kimi pour produire une réponse. »

**→ flèche (vers le bas)** : « Mais avant que cette réponse parte au client, elle repasse un contrôle. »

## Boîte ② — GARDE-FOU DE SORTIE, check_output (orange)
« Deuxième portique. Comme le dit le brief, il contrôle les **mêmes catégories** que l'entrée, PLUS la fuite de PII (un numéro de carte), les secrets, et le hors-périmètre. Il laisse passer une réponse métier normale, mais bloque tout ce qui ne doit pas sortir. Le test vérifie surtout le n° de carte. »

**→ flèche latérale "fuite" → boîte BLOQUÉ (rouge)** : « Si la réponse contient une fuite, elle est bloquée et remplacée par un refus. Le client ne voit jamais la donnée sensible. »

**→ flèche "autorisé" (vers le bas)** : « Sinon, DONC la réponse est propre et part au client. »

## Boîte — RÉPONSE AU CLIENT (vert)
« Le client reçoit une réponse sûre — contrôlée à l'entrée ET à la sortie. »

## La boîte JOURNAL (self.events)
« À droite, la boîte JOURNAL : chaque fois qu'un portique bloque — à l'entrée comme à la sortie — il écrit une trace dans `self.events`. C'est la journalisation exigée par le brief. Aujourd'hui c'est une liste en mémoire, ce qui suffit au test ; en production je la persisterais en base pour un audit durable — c'est la limite que j'assume. »

## La légende — les 7 catégories
« En bas, les 7 catégories contrôlées. Les six premières — haine, violence, sexuel, injection, hors-périmètre, secret — sont surtout filtrées à l'entrée. À la sortie, on surveille surtout les données personnelles, le PII comme un numéro de carte, et les fuites de secret. »

**Phrase-clé à retenir** : « Deux portiques : l'entrée protège l'agent des attaques, la sortie protège le client des fuites — et chaque blocage est journalisé. »

---

# 🎓 Questions probables du formateur

1. « Pourquoi deux garde-fous et pas un seul ? » → « L'entrée et la sortie ont des risques différents : l'entrée protège contre les attaques et manipulations, la sortie protège contre les fuites de données. Un seul ne couvrirait pas les deux. »
2. « Comment tu détectes une injection de prompt ? » → « Je cherche des formulations qui essaient de faire désobéir l'agent : "ignore tes instructions", "oublie tes consignes", "developer mode". C'est un choix minimal par mots-clés ; en prod, un classifieur LLM serait plus robuste. »
3. « C'est quoi un faux positif et pourquoi c'est important ? » → « C'est bloquer un client légitime par erreur. Le test exige moins de 10% : si je suis trop strict, je bloque de vrais clients — mauvais pour le support. »
4. « Pourquoi journaliser les blocages ? » → « Pour la traçabilité : un incident de sécurité doit laisser une trace pour être audité — c'est aussi une exigence RGPD/sécurité. »
