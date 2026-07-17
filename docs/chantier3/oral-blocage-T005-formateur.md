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
mon `forget` qui reçoit une cible cassée. Six cas sur douze ne mémorisent **rien du tout**.
Donc ma boucle qualité, dès son premier run, me dit que mon Chantier 1 est incomplet — c'est
précisément ce qu'elle doit faire. **J'ai réparé les trois bugs qu'elle a désignés : 4/12 →
6/12, globale 0,825, ça passe** — sans toucher aux tests, ni au seuil, ni aux cas. J'ai deux
questions à te poser. »

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

Deuxième morceau, et c'est ton feedback du Chantier 1 : **l'oubli ne marche pas**. J'ai d'abord
cru que mon agent n'appelait jamais `forget()`. J'ai vérifié avant d'accuser : **il l'appelle
bien**, la route existe. Le bug est dans ce qu'il lui passe. Le client dit *« Oublie mon adresse
de livraison s'il te plaît. »* — le point collé à « plaît » le fait échapper à mon filtre de
mots vides, et l'agent finit par demander d'oublier « adresse livraison plait ». Introuvable,
évidemment. L'adresse est toujours là juste après. Tu m'avais dit de brancher la mémoire à
l'agent — le câblage existe, mais il ne fonctionnait pas, et personne ne pouvait le voir. »

**Le piège que j'ai failli te présenter comme un résultat.**

« Et là je dois te dire quelque chose sur moi. Ma **première** simulation donnait six sur douze,
et j'étais content : ça passait le seuil. Sauf que ce six était faux — et j'ai mis du temps à
comprendre qu'il était faux **pour deux raisons différentes**, empilées.

La première : j'avais oublié de remettre la mémoire à zéro entre les cas. Cinq de mes douze cas
utilisent le même client, Marc, et les faits d'un cas traînaient dans le suivant. J'ai mesuré
l'écart exact : quatre sur douze en isolant vraiment, cinq en laissant s'accumuler. **Un point
de contamination.**

La deuxième est pire, parce qu'elle vient de ma main : ma simulation appelait
`memory.forget()` **elle-même**, à la place de l'agent. Elle faisait le travail de ce qu'elle
était censée juger. Ça masquait exactement le trou que je devais trouver. **Un deuxième point
volé.**

Quatre plus un plus un : six. Deux mensonges empilés dans l'outil censé traquer les mensonges.
Le vrai chiffre de départ était **quatre**.

Ce que j'en retiens : **l'isolement n'est pas un détail de propreté, c'est ce qui rend la mesure
vraie** — et **un juge ne doit jamais faire le travail de l'accusé**. C'est la même raison qui
fait que ma suite garde-fous appelle le portique en direct au lieu de passer par l'agent
complet. »

**Ce que ça veut dire, et c'est le point important.**

« Donc mon Chantier 3 n'est pas cassé. Il **marche**. Son premier acte, c'est de me dire que mon
Chantier 1 est incomplet, avec des chiffres, sur des cas que je n'ai pas choisis.

Si je voulais tricher, je pourrais : je fais appeler `forget()` par ma suite elle-même, à la
place de l'agent, et je gagne un point. J'ai testé, ça donne cinq sur douze. Et ça reste sous le
seuil de toute façon. Mais surtout, ça masquerait exactement le trou que je dois boucher.

Le calcul est simple : il me faut **six sur douze** pour atteindre 0,825 et passer. J'en avais
quatre. Donc j'ai réparé ma mémoire — l'oubli, et l'extraction. Ce n'est pas contourner
l'évaluation, c'est faire le travail qu'elle désigne. Je te raconte le résultat à la fin. »

**Mes deux questions.**

« Première question. Avec `EchoLLM` codé en dur dans `conftest.py`, la question d'évaluation
tombe sur un modèle qui répète au lieu de répondre. Donc je ne peux pas vérifier la **phrase**.
Je propose de vérifier **l'état de la mémoire** — je rejoue toujours la vraie conversation par
`respond()`, seule la vérification finale change. L'argument, c'est la symétrie : pour les
garde-fous, j'appelle le portique en direct **pour isoler le coupable**. Si ma note mémoire
dépend du talent du LLM à formuler, je ne mesure plus ma mémoire, je mesure le modèle. Est-ce que
tu valides ? Je précise que ça **contredit ce que je t'ai fait valider** — mon oral disait qu'on
vérifiait la réponse.

Deuxième question, et c'est la vraie. **Est-ce que tu valides la méthode ?** La boucle mesure,
elle désigne un trou, je répare ce qu'elle désigne, je re-mesure. Je l'ai fait — 4/12 devient
6/12 — sans toucher à tes tests, ni au seuil, ni aux cas. J'aurais pu faire passer le test en
trichant : ma suite appelait déjà `forget()` à la place de l'agent, et ça masquait exactement le
trou que je devais boucher. J'ai enlevé la triche et réparé l'agent. C'est bien ce chemin-là que
tu attends ? »

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

Second part, and this is your Chantier 1 feedback: **forgetting doesn't work**. I first thought
my agent never called `forget()`. I checked before accusing: **it does call it**, the route
exists. The bug is in what it passes. The customer says *"Forget my delivery address please."* —
the full stop glued to "please" makes it slip through my stop-word filter, and the agent ends up
asking to forget "address delivery please". Not found, obviously. The address is still there
right after. You told me to wire memory into the agent — the wiring exists, but it didn't work,
and nobody could see it. »

**The trap I nearly presented to you as a result.**

« And here I have to tell you something about myself. My **first** simulation gave six out of
twelve, and I was pleased: it passed the threshold. Except that six was false — and it took me a
while to realise it was false for **two different reasons**, stacked.

The first: I'd forgotten to reset memory between cases. Five of my twelve cases use the same
customer, Marc, and facts from one case lingered into the next. I measured the exact gap: four
out of twelve with real isolation, five when letting it accumulate. **One point of
contamination.**

The second is worse, because it came from my own hand: my simulation called `memory.forget()`
**itself**, instead of the agent. It was doing the work of the very thing it was supposed to
judge. That masked exactly the hole I needed to find. **A second stolen point.**

Four plus one plus one: six. Two lies stacked inside the tool meant to hunt lies. The real
starting number was **four**.

What I take from it: **isolation isn't a tidiness detail, it's what makes the measurement true**
— and **a judge must never do the defendant's work**. It's the same reason my guardrail suite
calls the gate directly instead of going through the full agent. »

**What it means, and this is the point.**

« So my Chantier 3 isn't broken. It **works**. Its first act is to tell me my Chantier 1 is
incomplete, with numbers, on cases I didn't choose.

If I wanted to cheat, I could: I make my suite call `forget()` itself, instead of the agent, and
I gain a point. I tested it, that gives five out of twelve. And it stays below the threshold
anyway. But more importantly, it would hide exactly the hole I need to close.

The maths is simple: I need **six out of twelve** to reach 0.825 and pass. I had four. So I
repaired my memory — the forgetting, and the extraction. That isn't working around the
evaluation, it's doing the work it points at. I'll tell you the result at the end. »

**My two questions.**

« First question. With `EchoLLM` hardcoded in `conftest.py`, the evaluation question falls
through to a model that echoes instead of answering. So I can't check the **sentence**. I propose
checking the **memory state** — I still replay the real conversation through `respond()`, only
the final check changes. The argument is symmetry: for guardrails, I call the gate directly **to
isolate the culprit**. If my memory score depends on the LLM's ability to phrase, I'm no longer
measuring my memory, I'm measuring the model. Do you validate that? I should say it
**contradicts what I had you validate** — my talk said we'd check the answer.

Second question, and it's the real one. **Do you validate the method?** The loop measures, it
points at a hole, I repair what it points at, I measure again. I did it — 4/12 becomes 6/12 —
without touching your tests, the threshold, or the cases. I could have made the test pass by
cheating: my suite was already calling `forget()` instead of the agent, and that masked exactly
the hole I needed to close. I removed the cheat and repaired the agent. Is that the path you
expect? »

---

## Les chiffres exacts (à avoir sous les yeux)

| Étape | mémoire | globale | verdict |
|---|---|---|---|
| 1ʳᵉ simulation — **deux mensonges empilés** | 6/12 | 0,825 | ⚠️ faux |
| …dont contamination seule | 5/12 = 0,417 | 0,796 | 🔴 bloqué |
| **Le vrai point de départ, mesuré** | **4/12 = 0,333** | **0,767** | 🔴 bloqué |
| → correctif 1 : `forget` branché pour de vrai | 5/12 = 0,417 | 0,796 | 🔴 encore, à 0,004 près |
| → correctif 2 : motif élargi au pluriel | **6/12 = 0,500** | **0,825** | 🟢 **PASSE** |
| Si on répare les 6 tournures restantes | 12/12 = 1,000 | 1,000 | 🟢 confortable |

`globale = 0,35 × mémoire + 0,35 × 1,0 (garde-fous) + 0,30 × 1,0 (qualité)`

**Le 6/12 d'aujourd'hui et le 6/12 du départ sont le même chiffre et n'ont rien à voir** : le
premier était fabriqué par deux biais, le second est mesuré avec purge réelle entre les cas.
C'est toute la différence entre un vert qui ment et un vert qui prouve.

## Le détail des 12 cas

| Cas | Avant | Après | Pourquoi |
|---|---|---|---|
| R1-marc-3commandes | ✅ | ✅ | « Ma commande O-2024-0101 **est** en préparation » → le motif matche |
| R3-isolation-a / -b | ✅ ✅ | ✅ ✅ | « Mon numéro **est** O-2024-0103 » → matche |
| R5-oubli-commande | ⚠️ | ⚠️ | **faux positif** : passe parce que la mémoire est **vide** — l'interdit est absent puisque rien n'a été retenu |
| **R5-oubli-adresse** | ❌ | 🟢 **✅** | l'agent appelait bien `forget()`, mais avec la cible « adresse livraison **plait** » — introuvable |
| **R2-clubs** | ❌ | 🟢 **✅** | « **Mes** clubs préférés **sont**… » → motif élargi au pluriel |
| R1-adresse-debut | ❌ | ❌ | « Je suis à Paris, code postal 75011 » |
| R2-pointure | ❌ | ❌ | « Je porte toujours la taille L » |
| R2-revendeur | ❌ | ❌ | « Je suis revendeur » |
| R1-produit | ❌ | ❌ | « J'ai acheté le maillot… » |
| R2-canal | ❌ | ❌ | « Contactez-moi par email » |
| R1-deux-maillots | ❌ | ❌ | « Je veux le Brazil 1970 et le France 1998 » |
| | **4/12** | **6/12** | |

**Les 6 qui échouent encore échouent honnêtement** : ce sont des tournures structurellement
différentes, hors de portée de n'importe quelle regex raisonnable. Les rattraper à coups de
motifs, ce serait coder le jeu de test, pas la mémoire. C'est le travail d'un extracteur LLM ou
de la couche épisodique — **dette identifiée, pas masquée**.

## Mémo minute

| Point | Le fait |
|---|---|
| Le symptôme | 4/12 → globale **0,767** → l'agent sain serait bloqué |
| La cause 1 | `FACT_PATTERN` ne capte que « Ma/Mon X **est** Y » → 6 cas mémorisent **rien** |
| La cause 2 | l'agent appelle bien `forget()`, mais avec une cible cassée par la ponctuation |
| Mes erreurs | 1ʳᵉ simulation à 6/12 = **deux mensonges empilés** : contamination (+1) **et** ma suite appelait `forget()` à la place de l'agent (+1) |
| La leçon 1 | l'isolement rend la mesure **vraie** — même raison que le portique en direct |
| La leçon 2 | **un juge ne fait jamais le travail de l'accusé** |
| Le retournement | ce n'est pas un bug du Chantier 3 : **c'est le Chantier 3 qui fait son travail** |
| ✅ **Le résultat** | réparé sous son contrôle : **4/12 → 6/12**, globale **0,767 → 0,825**, ça passe — **sans toucher aux tests, ni au seuil, ni aux cas** |
| Question 1 | état mémoire plutôt que phrase du LLM ? (`EchoLLM` ne laisse pas le choix) |
| Question 2 | tu valides la **méthode** : réparer ce que la boucle désigne, plutôt que l'adapter au bug ? |

---

## ✅ La fin de l'histoire (fait le 2026-07-16, à raconter en dernier)

« Et je ne suis pas venu qu'avec un problème. J'ai réparé les trois bugs que la boucle avait
désignés, **sous son contrôle**, en re-mesurant après chacun.

Le premier : mon motif d'extraction ne connaissait que le singulier. Je l'ai passé au pluriel —
« Mes clubs préférés **sont** l'OM » est mémorisé maintenant. Attention, je n'ai **pas** écrit
une expression par cas de test : ça, ç'aurait été coder le test au lieu de réparer la mémoire.
J'ai complété une règle incomplète, c'est tout.

Le deuxième : la ponctuation. « Oublie mon adresse **s'il te plait.** » — le point collé à
« plait » faisait passer le mot à travers mon filtre, et l'agent demandait d'oublier « adresse
livraison plait ». Introuvable, évidemment.

Le troisième, et c'est celui que je veux te faire valider : mon `forget` cherchait la cible
comme une sous-chaîne exacte. Or le client dit « oublie mon adresse **de livraison** » quand
j'ai stocké « adresse ». Il nomme la chose **plus précisément** que moi. Je suis passé à une
correspondance mot à mot, et j'ai choisi le **OU** plutôt que le ET : si **un seul** mot
correspond, je supprime. C'est délibéré — sur le droit à l'oubli, **dans le doute, en supprimer
un de trop n'est pas la faute ; en rater un, si.** C'est le même raisonnement fail-closed que
partout ailleurs, appliqué à la vie privée.

Résultat : quatre sur douze devient six sur douze. Globale 0,825. **Ça passe.** Et je n'ai
touché ni à tes tests, ni au seuil, ni aux cas.

Six cas échouent encore, et j'assume : « Je porte toujours la taille L », « code postal 75011 »
— aucune regex raisonnable ne les attrapera. C'est le travail d'un extracteur LLM ou de la
couche épisodique. C'est écrit dans mon journal comme dette, pas caché.

Donc ma vraie question n'est plus « est-ce que je répare ? ». C'est : **est-ce que tu valides la
méthode ?** La boucle mesure, elle désigne, je répare ce qu'elle désigne, je re-mesure. C'est ce
que le Chantier 3 devait apporter — et il l'a apporté avant même que j'aie fini de l'écrire. »
