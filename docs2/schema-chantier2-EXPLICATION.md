# Le schéma Chantier 2 — corrections à appliquer + explication

> Ton schéma actuel (`schema-chantier2-demo-complete.png`) est bon. Il porte deux histoires
> différentes, et c'est ça qu'il faut exploiter. Ce fichier dit **quoi corriger**, **pourquoi**,
> et **comment le montrer**.

---

## 1. Pourquoi ce schéma est déjà bien

Le feedback formateur du Chantier 1 disait, mot pour mot :

> « Le formateur attendait un schéma "comment tu joues avec les mémoires", comment le message passe, où se trouve quel élément. Il veut se projeter visuellement. »

**Ton panneau gauche répond exactement à ça.** Message → portique 1 → agent → portique 2 → réponse,
avec les deux sorties « BLOQUÉ » et le journal. En quinze secondes, on sait où vit chaque chose.

**Ton panneau droit répond à une autre question** : *comment tu as travaillé*. Rouge → code → vert →
non-régression. Ce n'est pas de l'architecture, c'est du processus.

Le pointillé vertical au milieu de ton dessin sépare déjà les deux. **Il tombe pile sur la frontière
entre tes 5 minutes de parole et tes 6 minutes de démo.**

---

## 2. Les quatre corrections

| # | Actuel | À remplacer par | Pourquoi |
|---|---|---|---|
| 1 | `② LE CYCLE TDD (démo)` | `② LE CYCLE ROUGE → VERT` | Tu n'as pas écrit les tests. Le formateur les a écrits. Dire « TDD » invite la question « tu as écrit les tests toi-même ? » et tu es coincé. |
| 2 | `AGENT — mémoire + LLM Kimi` | `AGENT — mémoire + routage outils + FAQ + LLM (fallback)` | `_handle()` (agent.py) route vers les outils et la FAQ d'abord, et n'atteint le LLM qu'à la **ligne 152**, en dernier recours. Sinon : « donc chaque message coûte un appel LLM ? » |
| 3 | `check_input` liste 6 familles | Ajouter **`PII`** dans la boîte | Depuis le correctif, `check_input` bloque aussi le n° de carte entrant. Les deux portiques portent PII, c'est ce que `reco_expert.md` exige : « dans un sens comme dans l'autre ». |
| 4 | Les flèches `BLOQUÉ` sortent dans le vide | Ajouter une flèche **BLOQUÉ → mémoire** | `agent.py` **ligne 74** : même bloqué, le message est écrit en mémoire. Personne ne l'a vu. Le pointer prouve que tu as lu ton code jusqu'au bout. |

**Bonus (correction 5)** : dans la boîte `A. LANCER LE TEST (baseline)`, écris
`contrat fourni, rouge au départ` à côté de `5 failed`. Pas « mes tests échouaient ».

---

## 3. Les deux images sont prêtes

| Fichier | Contenu | Quand le montrer |
|---|---|---|
| **[`schema-A-gauche.png`](schema-A-gauche.png)** | le panneau gauche seul | de 0:00 à 4:30 |
| **[`schema-AB-complet.png`](schema-AB-complet.png)** | les deux panneaux | à partir de 4:30 |

Les 4 corrections sont intégrées : titre `LE CYCLE ROUGE → VERT`, boîte AGENT complète avec le routage
outils, `PII` dans `check_input`, et la flèche pointillée vers `JOURNAL` + `MÉMOIRE` (`agent.py:74`).

**Pour retoucher** : les sources sont [`schema-A-gauche.html`](schema-A-gauche.html) et
[`schema-AB-complet.html`](schema-AB-complet.html). Ouvre-les dans un navigateur, modifie le texte,
puis capture d'écran. Une version `.drawio` équivalente existe aussi :
[`schema-chantier2.drawio`](schema-chantier2.drawio) (app.diagrams.net → *Open Existing Diagram*).

Tu montres `schema-A-gauche.png` de 0:00 à 4:30. Tu bascules sur `schema-AB-complet.png` au moment
où tu dis « alors justement, ces tests, parlons-en ».

**Pourquoi ne pas tout montrer d'entrée :**

1. Le formateur ne saurait pas s'il doit suivre le trajet du message ou le cycle des tests.
2. `5 failed` ne veut rien dire tant qu'on ne sait pas *quelles cinq choses* sont protégées.
3. Le panneau droit est **le sommaire de ta démo** (A, B, C, D). Si tu le brûles au début, tu le
   racontes deux fois : une fois dans le vide, une fois avec le terminal. La deuxième est morte.

Gardé pour 4:30, il devient la table des matières de ce que tu vas exécuter. Le formateur sait à
chaque instant où il en est — ce qui répond directement à son autre reproche : « présentation
difficile à suivre ».

---

## 4. Ce que chaque élément du panneau gauche veut dire

| Élément du schéma | Dans le code | Ce que tu dis |
|---|---|---|
| `MESSAGE CLIENT` | `agent.respond(user_id, message)` | « Un message arrive. » |
| `① check_input` | `guardrails/__init__.py` → `check_input` | « Avant que l'agent existe. » |
| flèche `BLOQUÉ` (haut) | `agent.py:73-75` → `return refusal` | « Il ne descend jamais. L'attaque n'atteint pas le modèle. » |
| `AGENT` | `agent.py:_handle()` | « Mémoire, puis outils, puis FAQ, puis LLM en dernier recours. » |
| `② check_output` | `guardrails/__init__.py` → `check_output` | « La réponse ne sort pas non plus directement. » |
| flèche `BLOQUÉ` (bas) | `agent.py:81-82` → `answer = gate_out.refusal` | « La réponse est remplacée, pas envoyée. » |
| `RÉPONSE CLIENT` | valeur de retour de `respond()` | « Le métier passe des deux côtés. » |
| boîte violette `self.events` | `_journalise()` | « `reco_expert.md` : toute décision de blocage est journalisée. » |
| **flèche à ajouter** `BLOQUÉ → mémoire` | `agent.py:74` → `self.memory.write(...)` | « Même bloqué, le refus fait partie de la conversation. » |

**Les deux serrures.** C'est l'idée à faire passer avec le doigt :

- à l'**entrée** on cherche une **intention** → une intention s'écrit avec des **mots** → `INPUT_KEYWORDS`
- à la **sortie** on cherche une **fuite** → un n° de carte est une **forme** → `CARD_RE` (16 chiffres)

Et l'effet de bord heureux : `O-2024-0101` fait huit chiffres, la regex en demande seize. Le numéro
de commande passe sans exception à écrire.

---

## 5. Ce que le panneau droit veut dire

| Boîte | Réalité | La phrase juste |
|---|---|---|
| `A. baseline → 5 failed` | Le formateur a écrit `test_guardrails.py`, le moteur était vide | « Le contrat fourni était rouge au départ. » |
| `B. écrire le code` | `guardrails/__init__.py` rempli | « J'ai changé l'implémentation, jamais le contrat. » |
| `C. relancer → 5 passed` | Contrat honoré | « Cinq critères du brief, verts. » |
| `D. non-régression → 16 verts` | 5 garde-fous + 4 mémoire + 7 métier | « Rien de cassé ailleurs. Les 3 rouges sont le Chantier 3. » |
| flèche rouge `encore rouge ? je retourne coder` | la boucle | « C'est la boucle que j'ai faite, pas une théorie. » |

⚠️ **Ne dis jamais** « j'ai écrit les tests », « mes tests échouaient », « j'ai créé le cycle TDD ».
**Dis** « les tests d'acceptance étaient fournis », « le contrat était rouge au départ »,
« j'ai travaillé contre les tests fournis ».

---

## 6. Vocabulaire — à dire / à ne pas dire

| À éviter | À dire à la place |
|---|---|
| « J'ai écrit les tests. » | « Les tests d'acceptance étaient fournis dans le brief. » |
| « Mes tests échouaient. » | « Le contrat fourni était rouge au départ. » |
| « J'ai créé le cycle TDD. » | « J'ai travaillé contre les tests fournis, en rouge → vert. » |
| « J'ai prouvé mes tests. » | « J'ai prouvé mon implémentation contre les tests fournis. » |
| « L'agent utilise Kimi. » | « L'agent route vers les outils d'abord ; Kimi est le dernier recours. » |

---

## 7. La phrase de clôture du schéma

> La partie gauche montre **ce que les garde-fous protègent**.
> La partie droite montre **comment j'ai prouvé l'implémentation sans modifier le contrat fourni**.

**EN :**

> The left side shows **what the guardrails protect**.
> The right side shows **how I proved the implementation without modifying the provided contract**.
