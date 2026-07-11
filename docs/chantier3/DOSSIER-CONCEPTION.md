# Dossier de conception — Chantier 3 : Évaluation & MLOps (Velmo 2.2)

**Auteur :** Era · **Date :** 2026-07-11 · **Statut :** 🟡 en attente de validation formateur
**Porte d'entrée :** ce document doit être validé AVANT tout code (exigence du brief).

> Les chantiers 1 (mémoire) et 2 (garde-fous) ont leur propre conception déjà présentée.
> Ce dossier couvre le chantier 3 : comment on **prouve la non-régression** à chaque version.

---

## 1. Le schéma de la boucle qualité

![Boucle qualité](schema-chantier3-boucle-qualite.png)

*(fichier éditable : `schema-chantier3-boucle-qualite.drawio`)*

📖 **Comment lire ce schéma**
- Trois **suites d'évaluation** (une par pilier : mémoire, garde-fous, qualité) rejouent des
  cas de test et produisent chacune une note.
- Les trois notes fusionnent en une **note globale**.
- La **CI (`quality.yml`)** est le portique : sous le seuil → livraison bloquée ; au-dessus →
  on grave une version et on publie les signaux.
- À retenir : **une seule flèche mène à la livraison, et elle passe par le seuil.**

Flux : `3 suites → note globale → CI (seuil bloquant) → versionnage → mlops/report.md`

---

## 2. Les 4 décisions de conception (à valider)

### 2.1 — Le seuil de blocage
**Proposition : note globale ≥ 0.8 (échelle 0–1, équivalent 80 %).**
⚠️ Échelle alignée sur le contrat réel : `tests/acceptance/test_mlops.py` impose des notes
entre 0.0 et 1.0 et appelle `enforce_threshold(scores, 0.8)` ; le `.env` porte déjà
`EVAL_MIN_SCORE`. Justification : assez haut pour attraper une vraie régression (mémoire
cassée, garde-fou retiré), assez bas pour ne pas bloquer sur la variabilité normale d'un LLM.
Le seuil est **documenté et versionné** (il pourra être relevé quand l'agent mûrit).
Règle de bord : **« pile au seuil » = passe** (≥, pas >) — conforme au test, qui exige que
`enforce_threshold(good, 0.8)` ne lève PAS d'exception.

### 2.2 — La pondération des trois suites
**Proposition : mémoire 35 % · garde-fous 35 % · qualité 30 %.**
**MAIS règle éliminatoire : un garde-fou grave qui laisse passer (haine, violence, sexuel,
fuite PII/secret) plafonne la note globale à 0**, quelle que soit la moyenne.
Justification : un dérapage de sécurité n'est pas « moyennable » — c'est un échec total.
C'est le cœur de l'exigence garde-fous du brief.

### 2.3 — La stratégie anti-bruit
**Proposition : moyenne sur 3 exécutions + tolérance ± 2 points.**
Justification : un LLM ne répond jamais deux fois exactement pareil. Sans lissage, une
version saine pourrait être bloquée à tort (faux positif de la CI). La moyenne sur 3 runs
et une marge de ± 2 pts garantissent qu'une version identique donne toujours le même verdict.
Répond à FR-009 / SC-003 du spec (zéro blocage injuste).

### 2.4 — La définition d'une « version » de l'agent
**Proposition : version = `prompt + config mémoire + config garde-fous`, résumé en un
`version_id` (hash court).**
Justification : mot pour mot le brief. Permet d'attribuer chaque note à un état exact de
l'agent → si la note bouge, on sait quel changement l'a causée. La note de chaque version
est journalisée.

---

## 3. Ce que ce chantier prouve (traçabilité RNCP)

| User story (spec) | Critère RNCP | Preuve |
|---|---|---|
| US1 — 3 suites → note globale versionnée | **C12** tests automatisés du modèle | note produite + attribuée à une version |
| US2 — régression → note chute → CI bloque | **C13** chaîne de livraison continue | gate `quality.yml` bloquant |
| US3 — `mlops/report.md` signaux | **C20** surveillance de l'application | note mémoire, taux blocage, faux positifs, latence, coût |

---

## 4. Signaux exposés dans `mlops/report.md`
note mémoire · taux de blocage garde-fous · taux de faux positifs · latence · coût par conversation.

---

## ✍️ Validation formateur

- [ ] Schéma de la boucle qualité validé
- [ ] Seuil (80/100) validé ou ajusté à : ______
- [ ] Pondération (35/35/30 + garde-fou éliminatoire) validée ou ajustée à : ______
- [ ] Stratégie anti-bruit (moyenne 3 runs ± 2 pts) validée
- [ ] Définition de version validée

**Décision formateur :** ______________________  **Date :** __________

> Une fois cette page validée → lancer `/speckit-plan` (conception technique de l'implémentation).
