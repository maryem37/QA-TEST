# Journal de validation humaine

Ce journal consigne les corrections et décisions de revue manuelles. Les cas
générés dans `cases/` sont validés séparément par `pipeline.check_cases`.

| Date | Fichier(s) | Modification | Motif |
|---|---|---|---|
| 2026-11-07 | `cases/REQ-001.json` à `cases/REQ-012.json` | Corrections manuelles apportées aux cas générés, conservées dans le dépôt. | Clarifier les scénarios et garder une base de tests relisible sans dépendance au cache LLM. |
| 2026-11-07 | `tests/gold/test_api_auth.py` | Ajout d'un test de référence pour le comportement de login attendu. | Couvrir manuellement le contrat d'authentification. |
| 2026-11-07 | `tests/gold/test_api_create_room.py` | Ajout des scénarios de création, refus sans authentification et suppression; nettoyage via la passerelle. | Tests de référence et vérification de la configuration Docker utilisée par le dépôt. |
| 2026-11-07 | `spec/defects.md`, `tests/gold/test_api_create_room.py`, `tests/conftest.py` | DEF-003 reclassé comme problème de configuration amont; suppression du contournement direct et du xfail dans le compose racine. | Le Dockerfile assets du dépôt configure `ROOM_API=http://rbp-room:3001`; le compose amont seul garde le fallback localhost. |
| 2026-11-07 | `pipeline/gen_cases.py` | Ajout de la conservation des fichiers existants, avec `--force` et filtre de REQ. | Éviter d'écraser les corrections humaines lors d'une génération normale. |
| 2026-11-07 | `pipeline/llm_client.py`, `.env.example`, `.gitignore`, `pyproject.toml` | Journal cache/appels enrichi, variables d'environnement documentées, cache DeepEval ignoré, dépendance Anthropic retirée. | Reproductibilité, sécurité du dépôt et alignement des dépendances sur le fournisseur utilisé. |
