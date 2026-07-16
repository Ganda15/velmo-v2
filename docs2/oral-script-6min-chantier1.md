# Script oral 6 minutes — Velmo 2.0, du zéro au Chantier 1 terminé

> Préparé le 2026-07-07 pour le debrief formateur. ~850 mots ≈ 6 min à débit calme.
> Les indications entre [crochets] ne se disent PAS — ce sont des repères pour toi.
> Règle d'or : tu RACONTES ce que tu as vécu, tu ne récites pas un plan.

---

## Le script

[0:00 — pose-toi, respire une fois, regarde le formateur]

« Je vais vous raconter où en est Velmo, depuis le début jusqu'à cet après-midi.

Velmo, c'est un agent de support client pour une boutique de maillots de foot collector. Le squelette que vous nous avez fourni contient déjà un agent qui tourne : il reçoit un message client, interroge la base des commandes, applique les règles métier — remboursements, escalades — et répond via le LLM. Ce qui manque, c'est tout ce qui fait qu'un agent est utilisable en vrai : une mémoire, des garde-fous, et l'évaluation. Trois chantiers. Le brief impose aussi la stack : Postgres comme source de vérité, Chroma pour l'épisodique, et Kimi via Azure.

[0:45]

Vous m'aviez donné un conseil : l'agent d'abord, la mémoire ensuite. Je l'ai appliqué à la lettre. Avant de toucher quoi que ce soit, j'ai installé les dépendances avec uv, lancé les sept tests métier — tous verts — et vérifié avec git status que le repo restait intact : je ne voulais pas risquer de modifier un contrat de test sans m'en rendre compte. J'ai aussi validé la clé Azure : Kimi m'a répondu pour de vrai. Donc au moment d'attaquer la mémoire, je savais que je construisais sur du solide.

[1:30]

Ensuite, le Chantier 1. Ma première action n'a pas été d'écrire du code — ça a été de lancer les quatre tests d'acceptance mémoire. Tout rouge. Et c'est exactement ce que je voulais voir : c'est du TDD. Ces quatre tests, c'est mon contrat — rappel sur trente tours, persistance entre sessions, isolation entre clients, droit à l'oubli. Tant que je ne les avais pas vus échouer, je ne savais pas précisément ce qu'on me demandait. Cette photo de départ, elle est dans mon journal de bord.

[2:15]

Le premier vrai problème, c'était : où vivent les souvenirs ? Si je les garde dans l'objet Python, ils meurent avec la session — la persistance ne passera jamais. Donc j'ai créé une table, memory_facts, avec SQLAlchemy, dans un fichier store.py. En développement c'est du SQLite, en production ce sera Postgres via une variable d'environnement — même code, seule l'URL change, parce que votre note d'expert impose Postgres mais que mes tests doivent tourner hors-ligne. Et j'ai pris deux décisions dans le schéma qui allaient payer plus tard : chaque fait est rangé sous le user_id du client — c'est ça qui garantit que Marc ne verra jamais les commandes de Sophie — et chaque ligne porte un flag deleted, parce que je savais que le droit à l'oubli arrivait.

Là-dessus j'ai codé remember_fact, qui enregistre ou met à jour un fait durable, et read, qui relit les faits non supprimés du client. Deux tests sont passés au vert : la persistance et l'isolation.

[3:30]

Le morceau suivant, c'était le rappel sur trente tours — le plus intéressant. Le test envoie une phrase libre : "Ma commande prioritaire est O-2024-0101", puis trente tours de bruit, et exige que l'information ressorte à la fin. Ma première idée aurait pu être de garder tout l'historique — mais trente-et-un échanges dans un budget de deux mille tokens, ça ne tient pas. Donc write ne stocke pas la conversation : il la distille. Une expression régulière reconnaît le motif "Ma ou Mon quelque-chose est valeur", extrait la clé et la valeur, et les range en base en réutilisant remember_fact — le chemin d'écriture déjà testé. Le bruit ne matche pas le motif, donc il ne coûte rien : une phrase utile devient une ligne en base, trente tours de bruit deviennent zéro octet. Troisième test vert. Et j'assume la limite : une regex ne couvre que les formes prévues. En production, c'est le LLM qui ferait l'extraction — l'architecture ne change pas, seul l'extracteur change.

[4:30]

Restait le droit à l'oubli. Le test dit "oublie mon adresse" — mais la clé stockée s'appelle "adresse de livraison". Une comparaison exacte ne trouverait rien : je cherche donc les faits dont la clé ou la valeur contient le mot. Et je ne fais pas un DELETE : je marque deleted à vrai — un soft-delete. Côté client, c'est effacé, parce que read filtre les faits supprimés depuis le premier jour — je n'ai même pas eu à le modifier. Côté base, on garde la preuve que l'oubli a eu lieu : si un client conteste, on peut auditer. C'est l'esprit du RGPD. Quatrième test vert.

[5:15]

Après chaque étape, j'ai relancé toute la suite pour vérifier que rien d'autre ne bougeait. Aujourd'hui : les quatre tests mémoire passent, les sept tests métier passent toujours, et les seuls rouges restants sont les chantiers pas encore commencés — les garde-fous et le MLOps, qui sont justement la suite. Il me reste une méthode de confort, inspect, qui n'a pas de test d'acceptance — je la code juste après ce debrief.

Tout ce que je viens de vous raconter est tracé dans mon journal de bord, dans un dossier séparé de votre code : chaque étape, la commande exacte, le résultat, et le pourquoi de chaque choix. Si vous voulez, je vous montre les quatre tests passer en direct. »

[6:00 — fin. Silence, sourire, laisse venir les questions.]

---

## Les 5 questions probables (réponses en une phrase)

1. **Pourquoi soft-delete et pas DELETE ?** → « La lecture fait comme si c'était effacé ; la base garde la preuve que l'oubli a eu lieu — auditable si un client conteste. »
2. **Pourquoi une regex et pas le LLM ?** → « Choix minimal qui honore le contrat de test sans réseau ; en prod l'extracteur devient le LLM, l'architecture ne bouge pas. »
3. **Et si deux clients ont la même clé ?** → « Chaque fait est sous le user_id : même clé, lignes différentes — c'est le test d'isolation qui le prouve. »
4. **Comment tu respectes le budget de 2000 tokens ?** → « Je ne stocke jamais la conversation brute : j'extrais des faits compacts, le bruit ne stocke rien. »
5. **C'est quoi ta prochaine étape ?** → « inspect() pour l'observabilité de la mémoire, puis le Chantier 2 : les cinq tests de garde-fous qui sont rouges et qui m'attendent. »

---

## Conseils de livraison (pour le stress)

- **Tu ne récites pas, tu racontes ta semaine.** Si tu perds le fil, la boussole c'est la chronologie : agent → rouge → table → extraction → oubli → preuve.
- Les chiffres à avoir en tête : **7** tests métier, **4** tests mémoire, **2000** tokens, **4/4 vert**.
- Aux repères [x:xx], si tu es en avance : ralentis, respire. En retard : coupe les détails de la regex, jamais les pourquoi.
- La démo live (`uv run pytest tests/acceptance/test_memory.py -v`) est ton filet de sécurité : si une question te bloque, propose de montrer le code.
