# Velmo 2.2 — Agent SAV boutique collector (chantiers 1+2+3)

## Stack imposée (brief formateur — ne pas changer)
- LLM : Kimi via Azure AI (clé dans .env, jamais commitée)
- Mémoire long terme : SQLite en dev, Postgres via MEMORY_DB_URL en prod
- Vectoriel : Chroma

## Commandes
- Tests métier : python -m pytest tests/acceptance/test_agent.py -v
- Tests mémoire : python -m pytest tests/acceptance/test_memory.py -v
- Toujours lancer avec le venv activé
- Repli AppLocker si venv bloqué : C:\Python314\python.exe -m pytest

## Règles de travail
- TDD : les tests d'acceptance sont le contrat, ne jamais les modifier pour les faire passer
- Era écrit le code lui-même : donner code + explication dans le chat, ne pas appliquer sans "do it"
- Mettre à jour le JOURNAL Obsidian à chaque étape (Projets/Velmo/JOURNAL-chantier3-evaluation-mlops.md)

## Chantier 3 en cours (Évaluation & MLOps)
- Goal : 3 suites d'éval (mémoire / garde-fous / qualité) → note globale versionnée ;
  CI quality.yml avec seuil BLOQUANT ; signaux dans mlops/report.md
- Conception : schéma boucle qualité validé par le formateur AVANT tout code
- Critères RNCP visés : C12 (suites), C13 (gate CI), C20 (signaux)
