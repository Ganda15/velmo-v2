# Oral — Ce que la boucle qualité révèle (à présenter au formateur)

> **Format** : conversation de 5 minutes. Tu apportes un problème **mesuré**, une cause
> **identifiée**, et deux questions à arbitrer.
>
> **Le retournement à comprendre avant de parler** : ce n'est **pas** un problème du Chantier 3.
> C'est le Chantier 3 qui fait son travail — et son premier acte est de prouver, chiffres à
> l'appui, que **le Chantier 1 n'est pas fini**. C'est exactement ce que tu lui avais dit.

---

## Le résumé en 30 secondes

« Avant de coder la suite mémoire, je l'ai simulée. Elle donne **4 sur 12**, note globale
**0,767**, sous le seuil de 0,8 : l'agent sain serait bloqué. J'ai cherché pourquoi. Ce n'est pas
la suite qui est fausse — c'est ma mémoire qui ne capte qu'**une seule tournure de phrase**, et
mon agent qui **n'appelle jamais** `forget()`. Six cas sur douze ne mémorisent **rien du tout**.
Donc ma boucle qualité, dès son premier run, me dit que mon Chantier 1 est incomplet. C'est
précisément ce qu'elle doit faire. J'ai deux questions à te poser. »

---

## 🗣️ Français

**Ce que j'ai fait, et ce que j'ai trouvé.**

« Avant d'écrire la suite mémoire, je l'ai simulée sur l'agent de référence. Elle donne quatre
sur douze. Note globale 0,767, sous le seuil de 0,8. Donc mon agent **sain** serait bloqué, et le
test de régression que tu as écrit échouerait.

Ma première réaction a été de croire que ma suite était mal conçue. J'ai vérifié avant de
corriger. Et non : la suite a raison. C'est ma mémoire qui a un trou. »

**La cause, en deux morceaux.**

« Premier morceau : mon extraction de faits repose sur un seul motif —
`Ma ou Mon quelque chose EST quelque chose`. Ça marche pour « Ma taille est L ». Ça ne marche
pour rien d'autre. Regarde ce que mes cas de test contiennent vraiment :

*« Je suis à Paris, code postal 75011 »* — rien. *« Je porte toujours la taille L »* — rien.
*« Mes clubs préférés sont l'OM et le Brésil »* — rien, parce que c'est « Mes » et « sont ».
*« J'ai acheté le maillot mu-1999-treble »* — rien. *« Contactez-moi par email »* — rien.

**Six cas sur douze ne mémorisent absolument rien.** Mémoire vide. Le client parle, l'agent
répond, et rien n'est retenu.

Deuxième morceau, et c'est ton feedback du Chantier 1 : **mon agent n'appelle jamais `forget()`**.
La méthode existe, je l'ai écrite pour R5. Mais elle n'est branchée nulle part. Je l'ai tracé :
le client dit *« Oublie mon adresse de livraison »*, et l'adresse est toujours là juste après.
Le cas de test attend même que l'assistant réponde « Adresse supprimée ». Tu m'avais dit de
brancher la mémoire à l'agent — voilà la preuve chiffrée que ce n'est pas fait. »

**Le piège que j'ai failli te présenter comme un résultat.**

« Et là je dois te dire quelque chose sur moi. Ma **première** simulation donnait six sur douze,
et j'étais content : ça passait le seuil. Sauf que j'avais oublié de remettre la mémoire à zéro
entre les cas. Cinq de mes douze cas utilisent le même client, Marc. Les faits du cas numéro un
traînaient encore dans le cas numéro quatre et le faisaient passer.

C'était un **faux positif par contamination**. Un vert qui ment. Exactement le type de bug que ma
suite est censée attraper — et je l'avais fabriqué moi-même, dans l'outil qui doit les traquer.
Corrigé, le vrai chiffre est quatre sur douze, pas six.

Ce que j'en retiens : **l'isolement n'est pas un détail de propreté, c'est ce qui rend la mesure
vraie.** C'est la même raison qui fait que ma suite garde-fous appelle le portique en direct au
lieu de passer par l'agent complet. »

**Ce que ça veut dire, et c'est le point important.**

« Donc mon Chantier 3 n'est pas cassé. Il **marche**. Son premier acte, c'est de me dire que mon
Chantier 1 est incomplet, avec des chiffres, sur des cas que je n'ai pas choisis.

Si je voulais tricher, je pourrais : je fais appeler `forget()` par ma suite elle-même, à la
place de l'agent, et je gagne un point. J'ai testé, ça donne cinq sur douze. Et ça reste sous le
seuil de toute façon. Mais surtout, ça masquerait exactement le trou que je dois boucher.

Le calcul est simple : il me faut **six sur douze** pour atteindre 0,825 et passer. J'en ai
quatre. Donc il faut que je répare ma mémoire — brancher l'oubli, et élargir l'extraction à
d'autres tournures. Ce n'est pas contourner l'évaluation, c'est faire le travail qu'elle
désigne. »

**Mes deux questions.**

« Première question. Avec `EchoLLM` codé en dur dans `conftest.py`, la question d'évaluation
tombe sur un modèle qui répète au lieu de répondre. Donc je ne peux pas vérifier la **phrase**.
Je propose de vérifier **l'état de la mémoire** — je rejoue toujours la vraie conversation par
`respond()`, seule la vérification finale change. L'argument, c'est la symétrie : pour les
garde-fous, j'appelle le portique en direct **pour isoler le coupable**. Si ma note mémoire
dépend du talent du LLM à formuler, je ne mesure plus ma mémoire, je mesure le modèle. Est-ce que
tu valides ? Je précise que ça **contredit ce que je t'ai fait valider** — mon oral disait qu'on
vérifiait la réponse.

Deuxième question, et c'est la vraie. Tu confirmes que le chemin, c'est de **réparer la mémoire
du Chantier 1** — plutôt que de baisser le seuil ou d'assouplir les cas ? Parce que je peux faire
passer le test en trichant, et je préfère te demander avant. »

---

## 🇬🇧 English

**What I did, and what I found.**

« Before writing the memory suite, I simulated it against the reference agent. It scores four out
of twelve. Global score 0.767, below the 0.8 threshold. So my **healthy** agent would be blocked,
and the regression test you wrote would fail.

My first instinct was that my suite was badly designed. I checked before fixing. And no: the
suite is right. It's my memory that has a hole. »

**The cause, in two parts.**

« First part: my fact extraction relies on a single pattern — `My something IS something`. It
works for "My size is L". It works for nothing else. Look at what my test cases actually contain:

*"I'm in Paris, postcode 75011"* — nothing. *"I always wear size L"* — nothing. *"My favourite
clubs are OM and Brazil"* — nothing, because it's "clubs" plural and "are". *"I bought the
mu-1999-treble shirt"* — nothing. *"Contact me by email"* — nothing.

**Six cases out of twelve store absolutely nothing.** Empty memory. The customer talks, the agent
answers, and nothing is kept.

Second part, and this is your Chantier 1 feedback: **my agent never calls `forget()`**. The method
exists, I wrote it for R5. But it's wired nowhere. I traced it: the customer says *"Forget my
delivery address"*, and the address is still there right after. The test case even expects the
assistant to reply "Address deleted". You told me to wire memory into the agent — here's the
measured proof it isn't done. »

**The trap I nearly presented to you as a result.**

« And here I have to tell you something about myself. My **first** simulation gave six out of
twelve, and I was pleased: it passed the threshold. Except I'd forgotten to reset memory between
cases. Five of my twelve cases use the same customer, Marc. Facts from case one were still
lying around in case four and made it pass.

It was a **false positive through contamination**. A green that lies. Exactly the kind of bug my
suite is supposed to catch — and I'd manufactured it myself, inside the very tool meant to hunt
them. Fixed, the real number is four out of twelve, not six.

What I take from it: **isolation isn't a tidiness detail, it's what makes the measurement true.**
It's the same reason my guardrail suite calls the gate directly instead of going through the full
agent. »

**What it means, and this is the point.**

« So my Chantier 3 isn't broken. It **works**. Its first act is to tell me my Chantier 1 is
incomplete, with numbers, on cases I didn't choose.

If I wanted to cheat, I could: I make my suite call `forget()` itself, instead of the agent, and
I gain a point. I tested it, that gives five out of twelve. And it stays below the threshold
anyway. But more importantly, it would hide exactly the hole I need to close.

The maths is simple: I need **six out of twelve** to reach 0.825 and pass. I have four. So I need
to repair my memory — wire the forget, and widen the extraction to other phrasings. That isn't
working around the evaluation, it's doing the work it points at. »

**My two questions.**

« First question. With `EchoLLM` hardcoded in `conftest.py`, the evaluation question falls
through to a model that echoes instead of answering. So I can't check the **sentence**. I propose
checking the **memory state** — I still replay the real conversation through `respond()`, only
the final check changes. The argument is symmetry: for guardrails, I call the gate directly **to
isolate the culprit**. If my memory score depends on the LLM's ability to phrase, I'm no longer
measuring my memory, I'm measuring the model. Do you validate that? I should say it
**contradicts what I had you validate** — my talk said we'd check the answer.

Second question, and it's the real one. Do you confirm that the path is to **repair Chantier 1's
memory** — rather than lowering the threshold or softening the cases? Because I can make the test
pass by cheating, and I'd rather ask you first. »

---

## Les chiffres exacts (à avoir sous les yeux)

| Variante | mémoire | globale | verdict |
|---|---|---|---|
| Honnête (l'agent doit oublier lui-même) | **4/12 = 0,333** | **0,767** | 🔴 bloqué |
| Si la suite appelle `forget()` à sa place | 5/12 = 0,417 | 0,796 | 🔴 bloqué quand même |
| **Cible minimale pour passer** | **6/12 = 0,500** | **0,825** | 🟢 passe |
| Si la mémoire était réparée | 8/12 = 0,667 | 0,883 | 🟢 confortable |

`globale = 0,35 × mémoire + 0,35 × 1,0 (garde-fous) + 0,30 × 1,0 (qualité)`

## Le détail des 12 cas

| Cas | Résultat | Pourquoi |
|---|---|---|
| R1-marc-3commandes | ✅ | « Ma commande O-2024-0101 **est** en préparation » → le motif matche |
| R3-isolation-a / -b | ✅ ✅ | « Mon numéro **est** O-2024-0103 » → matche |
| R5-oubli-commande | ⚠️ **faux positif** | passe parce que la mémoire est **vide** : l'interdit est absent puisque rien n'a été retenu |
| R1-adresse-debut | ❌ | « Je suis à Paris, code postal 75011 » |
| R2-pointure | ❌ | « Je porte toujours la taille L » |
| R2-clubs | ❌ | « **Mes** clubs préférés **sont**… » |
| R2-revendeur | ❌ | « Je suis revendeur » |
| R1-produit | ❌ | « J'ai acheté le maillot… » |
| R2-canal | ❌ | « Contactez-moi par email » |
| R1-deux-maillots | ❌ | « Je veux le Brazil 1970 et le France 1998 » |
| R5-oubli-adresse | ❌ | mémorisé, mais l'agent **n'appelle jamais** `forget()` |

## Mémo minute

| Point | Le fait |
|---|---|
| Le symptôme | 4/12 → globale **0,767** → l'agent sain serait bloqué |
| La cause 1 | `FACT_PATTERN` ne capte que « Ma/Mon X **est** Y » → 6 cas mémorisent **rien** |
| La cause 2 | l'agent **n'appelle jamais** `forget()` — ton feedback Chantier 1, prouvé |
| Mon erreur | 1re simulation à 6/12 = **faux positif par contamination** (5 cas partagent Marc) |
| La leçon | l'isolement rend la mesure **vraie** — même raison que le portique en direct |
| Le retournement | ce n'est pas un bug du Chantier 3 : **c'est le Chantier 3 qui fait son travail** |
| Ce qu'il faut | **6/12** minimum → réparer la mémoire, pas contourner l'éval |
| Question 1 | état mémoire plutôt que phrase du LLM ? (`EchoLLM` ne laisse pas le choix) |
| Question 2 | tu confirmes qu'on répare le Chantier 1 plutôt que baisser le seuil ? |
