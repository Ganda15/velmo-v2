# Oral — Le blocage de la suite mémoire (à présenter au formateur)

> **Format** : conversation de 3 minutes, pas une présentation. Tu apportes un problème
> **mesuré**, une solution **testée**, et tu demandes un arbitrage sur un écart à la conception
> qu'il a validée.
>
> **Ce que tu ne fais PAS** : t'excuser, ou présenter ça comme un échec. Tu as trouvé un angle
> mort de la conception **avant** d'écrire le code, avec des chiffres. C'est le travail.

---

## Le résumé en 30 secondes (si tu n'as que ça)

« Avant de coder la suite mémoire, je l'ai simulée sur l'agent de référence. Elle donne **zéro**.
Pas parce que ma mémoire est cassée — elle marche, je l'ai tracée — mais parce que la question
d'évaluation tombe sur le LLM, et que l'agent de référence utilise `EchoLLM`, qui répète la
question au lieu d'y répondre. Note mémoire zéro, note globale 0,65, sous le seuil de 0,8 :
**l'agent sain serait bloqué et le test de régression échouerait**. J'ai une solution testée qui
remonte à 0,825, mais elle change ce que la note mesure — d'où ma question. »

---

## 🗣️ Français

**Le problème, et comment je l'ai trouvé.**

« Avant d'écrire la suite mémoire, j'ai fait ce qu'on s'est dit : je l'ai simulée d'abord. Et
elle donne zéro sur douze. J'ai voulu comprendre avant de corriger, alors j'ai tracé un cas
complet.

La bonne nouvelle, c'est que la mémoire marche. Je rejoue la conversation de Marc, et à la fin
la mémoire contient bien `commande o-2024-0101= en preparation`. Elle est écrite, elle est
relue. Le Chantier 1 fait son travail.

Le problème est ailleurs. La question d'évaluation, c'est *« quelle était ma toute première
commande citée ? »*. Cette question ne correspond à aucun outil — donc elle tombe sur le LLM.
Et l'agent de référence, dans `conftest.py` ligne 47, code `EchoLLM` en dur. Alors EchoLLM fait
ce qu'il sait faire : il répète. Il me renvoie *« j'ai bien reçu : quelle était ma toute première
commande citée »*. Pas de numéro de commande, donc échec.

Autrement dit : **seul un vrai LLM sait transformer un contexte mémoire en phrase.** Ma mémoire a
la bonne information, mais personne ne sait la formuler. »

**Ce que ça coûte, en chiffres.**

« Ça donne : note mémoire zéro, garde-fous à un, qualité à un. Avec la pondération qu'on a
validée : 0,35 fois zéro, plus 0,35, plus 0,30 — **0,65**. En dessous du seuil de 0,8.

Donc l'agent **sain** serait bloqué. Et le test de régression que tu as écrit demande
explicitement que `enforce_threshold` sur le bon agent **ne lève pas**. Il échouerait.

Et je ne peux rien changer autour : le test, je n'y touche pas, c'est la règle. `conftest.py`
non plus. Le seuil 0,8 est écrit en dur dans ton test. Et la pondération, c'est toi qui l'as
validée. Tout est verrouillé. »

**Ma solution, et pourquoi je pense qu'elle est meilleure.**

« Ce que je propose : que la suite mémoire vérifie **l'état de la mémoire** au lieu de la phrase
du LLM. Je rejoue toujours la vraie conversation par `respond()` — l'état construit reste réel,
ça ne change pas. C'est seulement la vérification finale qui change : au lieu de demander à
l'agent de me raconter ce qu'il sait, je regarde ce qu'il sait.

Je l'ai testé : la note passe à 6 sur 12, la globale à **0,825**, et les trois tests passent.
L'agent dégradé tombe à zéro et reste bloqué.

Mais l'argument qui me convainc n'est pas le chiffre. C'est la **symétrie avec la suite
garde-fous**. Pour les garde-fous, on est d'accord : j'appelle `check_input` en direct, jamais
`respond()`, **pour isoler le coupable** — sinon un rouge pourrait venir du garde-fou, du LLM ou
de la mémoire. C'est exactement le même raisonnement ici : si ma note mémoire dépend du talent
du LLM à formuler, un rouge ne me dit plus si la mémoire a oublié ou si le modèle a mal tourné sa
phrase. **Je ne mesurerais pas ma mémoire, je mesurerais le modèle.**

Donc : garde-fous, j'isole le portique de la chaîne. Mémoire, j'isole la mémoire du LLM. Même
principe, même raison — un rouge doit désigner **un seul** coupable. »

**Ce que je te dois en transparence.**

« Deux choses. Un : ça **contredit ce que je t'ai fait valider**. Mon oral disait « on pose la
question et on vérifie que la réponse contient l'attendu ». C'était la conception, et elle a un
angle mort que je n'ai vu qu'en la simulant. Je préfère te le dire maintenant que le découvrir
devant le jury.

Deux : le découpage de tâches que j'avais écrit est **incomplet** en plus. Il dit de vérifier
`expected_substring`, mais mes douze cas ont **trois formes**, pas une : six `recall`, quatre
`persistence`, et deux `forget` qui n'ont pas ce champ du tout — ils ont un
`forbidden_substring`, et la vérification est **inversée**, la valeur doit être **absente**.
Appliqué à la lettre, mon code plantait sur un `KeyError`. Je l'ai reproduit. »

**Le truc que je trouve le plus intéressant.**

« Un dernier point, et c'est celui qui me plaît le plus. Sur les douze cas, six échouent quand
même — et ce ne sont pas des faux négatifs. Ma mémoire n'extrait que ce qui colle à un seul
motif : *« Ma taille est L »*. La moitié des cas emploie d'autres tournures, et là elle ne
mémorise **rien**. Zéro fait.

Donc 0,50, ce n'est pas un bug de ma suite : c'est la **mesure honnête** de ce que mon Chantier 1
fait vraiment. La boucle qualité fait son travail dès le premier jour — elle mesure au lieu de
flatter. J'ai noté la dette. »

**La question.**

« Donc voilà ma question : est-ce que tu valides que la suite mémoire évalue **l'état mémoire**
plutôt que la réponse formulée ? Si oui, je code et je documente l'écart. Si tu préfères qu'on
reste sur la réponse formulée, alors il faut qu'on parle du LLM de l'évaluation — parce
qu'avec `EchoLLM` codé en dur dans `conftest`, ce n'est pas faisable. »

---

## 🇬🇧 English

**The problem, and how I found it.**

« Before writing the memory suite, I did what we agreed: I simulated it first. It scores zero out
of twelve. I wanted to understand before fixing, so I traced one case end to end.

The good news is that memory works. I replay Marc's conversation, and at the end the memory holds
`commande o-2024-0101 = en preparation`. It's written, it's read back. Chantier 1 does its job.

The problem is elsewhere. The evaluation question is *« what was the very first order I
mentioned? »*. That question matches no tool — so it falls through to the LLM. And the reference
agent, in `conftest.py` line 47, hardcodes `EchoLLM`. So EchoLLM does what it does: it echoes.
No order number, so it fails.

In other words: **only a real LLM can turn a memory context into a sentence.** My memory has the
right information, but nobody can phrase it. »

**What it costs, in numbers.**

« That gives: memory zero, guardrails one, quality one. With the weighting we validated: 0.35
times zero, plus 0.35, plus 0.30 — **0.65**. Below the 0.8 threshold.

So the **healthy** agent would be blocked. And the regression test you wrote explicitly requires
`enforce_threshold` on the good agent **not to raise**. It would fail.

And I can't change anything around it: the test, I don't touch — that's the rule. Neither
`conftest.py`. The 0.8 threshold is hardcoded in your test. And the weighting, you validated it.
Everything is locked. »

**My solution, and why I think it's better.**

« What I propose: the memory suite checks the **memory state** instead of the LLM's sentence. I
still replay the real conversation through `respond()` — the state built stays genuine, that
doesn't change. Only the final check changes: instead of asking the agent to tell me what it
knows, I look at what it knows.

I tested it: the score goes to 6 out of 12, the global to **0.825**, and all three tests pass.
The degraded agent drops to zero and stays blocked.

But the argument that convinces me isn't the number. It's the **symmetry with the guardrail
suite**. For guardrails we agree: I call `check_input` directly, never `respond()`, **to isolate
the culprit** — otherwise a red could come from the guardrail, the LLM, or memory. It's exactly
the same reasoning here: if my memory score depends on the LLM's ability to phrase, a red no
longer tells me whether memory forgot or the model worded it badly. **I wouldn't be measuring my
memory, I'd be measuring the model.**

So: guardrails, I isolate the gate from the chain. Memory, I isolate memory from the LLM. Same
principle, same reason — a red must point at **one** culprit. »

**What I owe you in transparency.**

« Two things. One: this **contradicts what I had you validate**. My talk said "we ask the
question and check the answer contains the expected value". That was the design, and it has a
blind spot I only saw by simulating it. I'd rather tell you now than discover it in front of the
jury.

Two: the task breakdown I wrote is **incomplete** as well. It says to check `expected_substring`,
but my twelve cases have **three shapes**, not one: six `recall`, four `persistence`, and two
`forget` that don't have that field at all — they have a `forbidden_substring`, and the check is
**inverted**, the value must be **absent**. Applied literally, my code crashed on a `KeyError`. I
reproduced it. »

**The bit I find most interesting.**

« One last point, and it's my favourite. Out of twelve cases, six still fail — and they're not
false negatives. My memory only extracts what matches a single pattern: *« My size is L »*. Half
the cases use other phrasings, and there it stores **nothing**. Zero facts.

So 0.50 isn't a bug in my suite: it's the **honest measure** of what my Chantier 1 actually does.
The quality loop is doing its job from day one — it measures instead of flattering. I've logged
the debt. »

**The question.**

« So here's my question: do you validate that the memory suite evaluates the **memory state**
rather than the phrased answer? If yes, I code it and document the deviation. If you'd rather we
stay on the phrased answer, then we need to talk about the evaluation's LLM — because with
`EchoLLM` hardcoded in `conftest`, it isn't feasible. »

---

## Mémo minute

| Point | Le fait | Le chiffre |
|---|---|---|
| Le symptôme | suite mémoire = 0/12 | `globale 0,65 < 0,8` → sain **bloqué** |
| La cause | EchoLLM répète, ne formule pas | `conftest.py:47`, codé en dur |
| Ce qui marche déjà | mémoire écrite ET relue | `{'commande o-2024-0101': 'en preparation'}` |
| Ma solution | vérifier l'**état**, pas la phrase | 6/12 → **0,825** → 3 tests verts |
| Le vrai argument | symétrie avec T006 | *un rouge doit nommer UN coupable* |
| L'écart assumé | contredit l'oral validé | à arbitrer par toi |
| Le bonus | 6 échecs = mesure honnête | `FACT_PATTERN` ne capte qu'une tournure |

## Si tu n'as que 3 questions à retenir pour toi

1. **Pourquoi zéro ?** Parce que la question d'éval tombe sur le LLM, et qu'EchoLLM répète.
2. **Pourquoi je ne peux pas contourner ?** Test, `conftest`, seuil et pondération : tous
   verrouillés (contrat ou validation).
3. **Pourquoi l'état plutôt que la phrase ?** Pour isoler ce qu'on mesure — exactement comme
   les garde-fous appellent le portique en direct.
