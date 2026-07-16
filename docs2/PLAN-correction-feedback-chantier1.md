# Plan de correction — feedback formateur Chantier 1 (1h30 demain)

> Feedback du 2026-07-07. Demain : 1h30 pour retravailler AVANT le Chantier 2.
> 3 corrections + 1 point fort à garder. Priorité dans l'ordre d'impact.

## Le feedback en clair

| # | Ce que le formateur a dit | Traduction concrète | Statut |
|---|---|---|---|
| 1 | « Je m'attendais à un schéma… comment tu joues avec les mémoires, où se trouve quel élément » | Montrer un schéma de conception EN OUVERTURE | ✅ schémas PNG déjà créés — juste à MONTRER |
| 2 | « Je pensais que tu avais branché à l'agent… les tests passent mais ce n'est pas assez » | **Brancher la mémoire à l'agent (ligne 138)** | 🔴 À CODER — priorité n°1 |
| 3 | « Les tests dans le terminal ne donnent pas une info claire… dis-moi telle info est supprimée de telle mémoire » | Démo qui montre l'info ENTRER/SORTIR de la mémoire en clair | 🟡 démo à rendre parlante |
| ✅ | « Tu arrives à entrer dans le code, identifier des fonctions spécifiques, c'est bien » | Tu connais ton code | À GARDER |

**Cause racine** : présentation dure à suivre car (a) pas de schéma d'ouverture, (b) pas de démo agent conversationnelle montrant la mémoire vivante. Les 3 points se règlent avec UNE nouvelle structure : **schéma → agent qui retient/oublie en direct → code**.

---

## PRIORITÉ 1 — Brancher la mémoire à l'agent (ligne 138) [~30 min]

C'est LE point qui change tout : le formateur veut voir l'agent UTILISER la mémoire, pas juste des tests verts.

**Le problème** : `agent.py` appelle `read()` (l.77) mais jette le résultat ; ligne 138 le LLM reçoit `""`.

**La correction** (stratégie flux de données, pas événementiel) :
```python
# respond() : capturer le contexte au lieu de le jeter
context = self.memory.read(user_id, message)
answer = self._handle(user_id, message, context)   # le passer

# _handle(self, user_id, message, context) : le recevoir
# ligne 138 : l'injecter
return self.llm.invoke(SYSTEM_PROMPT, context.render(), message)
```
⚠️ Attention : plusieurs `return` dans `_handle` passent par le LLM ? Non — seul le dernier `return` (l.138) va au LLM. Les autres retours sont des réponses métier (outils, FAQ) qui n'ont pas besoin du contexte. Donc **une seule ligne à changer** pour l'injection + le passage du paramètre.

**Preuve après** : relancer `uv run pytest -q` → toujours `11 passed` (ne rien casser).

## PRIORITÉ 2 — Démo agent conversationnelle qui MONTRE la mémoire [~30 min]

Le formateur veut voir : « l'agent oublie à tel moment / envoie l'info dans telle mémoire ». Donc une conversation où on VOIT la mémoire vivre.

**Scénario de démo** (à faire tourner dans le CLI, une fois la ligne 138 branchée) :
1. `Ma pointure est L` → l'agent accuse réception ET la mémoire stocke `pointure=L`
2. `Tu te souviens de ma pointure ?` → l'agent répond en UTILISANT la mémoire (grâce au branchement)
3. `Oublie ma pointure` → `forget()` supprime
4. `Tu te souviens de ma pointure ?` → l'agent ne l'a plus

**Le point clé** : après chaque étape, ouvrir `inspect()` ou une lecture directe pour montrer l'état de la mémoire — « regardez, avant : pointure=L présent ; après oubli : vide ». C'est ça « telle info supprimée de telle mémoire ».

→ Coder `inspect()` (R6 traçabilité) sert exactement à ça : afficher l'état mémoire lisiblement.

## PRIORITÉ 3 — Rendre l'output lisible [~15 min]

Au lieu de `4 passed` (pas parlant), une démo qui narre :
```
AVANT : mémoire de marc = {pointure: L, clubs: OM}
Action : forget('pointure')
APRÈS : mémoire de marc = {clubs: OM}
        → 'pointure' a été supprimée ✅
```
C'est ce que le formateur demande : montrer l'info bouger dans la mémoire, pas un compteur de tests.

## PRIORITÉ 4 — Ouvrir avec le schéma [0 min, déjà prêt]

`schema1-presentation.png` en premier écran. Il répond directement à « où se trouve quel élément ».

---

## Nouvelle structure de présentation (celle qui règle les 3 points)

1. **Schéma** de conception (point 1 réglé) — où vit quoi
2. **Démo agent conversationnelle** (points 2 + 3 réglés) — l'agent retient, utilise, oublie EN DIRECT, avec l'état mémoire affiché à chaque étape
3. **Code** — les fonctions (ton point fort ✅) : montrer read/write/forget qui réalisent ce qu'on vient de voir
4. **Tests** en preuve finale — mais après avoir déjà montré le fonctionnement vivant

## Checklist demain (1h30)
- [ ] Brancher ligne 138 (`context.render()`) + passer le paramètre à `_handle`
- [ ] `uv run pytest -q` → 11 passed (non-régression)
- [ ] Coder `inspect()` → afficher l'état mémoire lisiblement
- [ ] Préparer `velmo-demo.db` (base seedée) pour le CLI
- [ ] Répéter le scénario conversationnel : retient → utilise → oublie
- [ ] Vérifier que le schéma s'ouvre en premier
