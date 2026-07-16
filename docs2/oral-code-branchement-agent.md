# Oral — le code du branchement mémoire ↔ agent (correction feedback)

> Créé 2026-07-07 après le debrief. Documente les DEUX vrais changements de code faits dans l'agent pour corriger le feedback formateur.
> Numéros de ligne vérifiés contre le code réel. C'est du VRAI code produit (`src/velmo/agent.py`), pas un script de démo.

## Ce que le formateur reprochait
« Je pensais que tu avais branché la mémoire à l'agent. Les tests passent, mais ce n'est pas assez pour montrer le fonctionnement. »
→ Réponse : j'ai fait deux branchements réels dans `agent.py`.

---

## CHANGEMENT 1 — L'agent DONNE la mémoire au LLM (ligne 152)

**Le problème** : l'agent lisait la mémoire (ligne 77) mais ne la passait PAS au LLM — ligne 152, le LLM recevait une chaîne vide `""`.

**Comment ouvrir** :
```
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:152
```

**AVANT :**
```python
        return self.llm.invoke(SYSTEM_PROMPT, "", message)
```
**APRÈS :**
```python
        return self.llm.invoke(SYSTEM_PROMPT, context.render(), message)
```

**Le chemin complet du contexte** (à montrer) :
- ligne 77 : `context = self.memory.read(user_id, message)` — on CAPTURE le contexte (avant, il était jeté)
- ligne 89 : `def _handle(..., context: MemoryContext)` — on le PASSE à la fonction de routage
- ligne 152 : `context.render()` — on l'INJECTE dans le prompt du LLM

**Phrase orale** : « L'agent lisait déjà la mémoire ligne 77, mais la jetait. Maintenant je la capture, je la passe à `_handle`, et je l'injecte dans le LLM ligne 152 avec `context.render()`. C'est pour ça que l'agent répond maintenant "vous faites du L". »

---

## CHANGEMENT 2 — L'agent COMPREND « oublie X » (lignes 96-107)

**Le problème** : « oublie ma pointure » partait au LLM et ne supprimait RIEN. L'agent ne routait pas l'intention d'oubli vers `memory.forget()`.

**Comment ouvrir** :
```
code -r -g C:\Users\kanda\velmo-v2\src\velmo\agent.py:96
```

**Le code ajouté dans `_handle`** :
```python
        # Intention « droit à l'oubli » : on route vers la mémoire (R5).
        if order_id is None and any(w in low for w in ("oublie", "oublier", "efface", "supprime")):
            words = (
                low.replace("oublier", " ").replace("oublie", " ")
                .replace("efface", " ").replace("supprime", " ").split()
            )
            stop = {"ma", "mon", "mes", "la", "le", "les", "de", "du", "stp", "svp",
                    "s'il", "te", "plait", "plaît", "information", "informations"}
            target = " ".join(w for w in words if w not in stop).strip(" .!?")
            removed = self.memory.forget(user_id, target)
            if removed:
                return f"C'est noté, j'ai oublié ce qui concerne « {target} » ({removed} information supprimée)."
            return f"Je n'ai rien concernant « {target} » en mémoire."
```

**Ligne par ligne** :
- `if order_id is None and any(w in low ...)` : si le message contient « oublie/efface/supprime » ET pas de numéro de commande → c'est une demande d'oubli
- `words = low.replace(...)` : on enlève les verbes (« oublie », « efface »…) du message
- `stop = {...}` : liste de mots vides (ma, mon, le…) à ignorer
- `target = ...` : ce qui reste = la cible (ex : « oublie ma pointure » → `pointure`)
- `removed = self.memory.forget(user_id, target)` : on appelle VRAIMENT `forget()` de la mémoire
- les deux `return` : message de confirmation (ou « rien trouvé »)

**Phrase orale** : « J'ai ajouté une détection d'intention : si le client dit "oublie ma pointure", l'agent extrait le mot "pointure" et appelle `memory.forget()`. Avant, ça partait au LLM sans rien supprimer. Maintenant l'agent oublie vraiment — c'est le "l'agent oublie à tel moment" que vous vouliez voir. »

---

## Comment le montrer en démo (relie code + comportement)

1. Ouvre `agent.py:152` → « voici où la mémoire entre dans le LLM »
2. Ouvre `agent.py:96` → « voici où j'attrape l'intention d'oubli »
3. Lance `python docs2/demo_chat.py` → tape « Ma pointure est L » puis « Oublie ma pointure » → montre la ligne `🧠 Mémoire` qui passe de `pointure = L` à `(vide)`

Le code (agent.py) + le comportement (démo) racontent la même histoire : la mémoire est branchée.

---

## Preuve — non-régression
```
python -m pytest tests/acceptance/test_memory.py tests/acceptance/test_business.py -q
```
→ `11 passed` (4 mémoire + 7 métier) — les deux changements n'ont rien cassé.

## Honnêteté (si on demande)
- `demo_chat.py` (dans docs2) = un script de démo QUE J'AI FAIT pour montrer, ce n'est PAS l'agent. Le vrai code est dans `agent.py`.
- Le forget-intent utilise un découpage de mots simple (regex/stopwords) ; en production, l'intention serait détectée par le LLM. Choix minimal pour la démo.
