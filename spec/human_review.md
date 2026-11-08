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
| 2026-11-07 | cases/REQ-003.json | Correction manuelle : champs et messages inexistants retirés; message d’erreur aligné sur l’interface réelle. | Validation humaine fondée sur les observations UI; aucun message de succès n’a été inventé. |
| 2026-11-07 | `spec/defects.md` | DEF-003 reclassé comme faux positif retiré. | Vérification par le parcours UI et test API vert sans xfail. |
| 2026-11-07 | `spec/api_notes.md` | Ajout des résultats observés pour PUT et DELETE /api/room/<id>. | Tracer les réponses 202 et la suppression confirmées via l'interface. |
| 2026-11-07 | `cases/REQ-004.json` | Cas de modification corrigés; l'invalidation non observée reste explicitement à vérifier via l'API. | Retirer les champs UI et messages non vérifiés. |
| 2026-11-07 | `cases/REQ-005.json` | Suppression UI décrite avec les sélecteurs observés; suppression d'id inexistant classée API. | Le champ de recherche inventé n'existe pas dans l'interface. |
| 2026-11-07 | `tests/gold/test_ui_pw_room_edit_delete.py` | Ajout d'un test UI de suppression avec création API et nettoyage garanti. | Vérifier le parcours réel et éviter de modifier les chambres initiales. |
| 2026-11-07 | `README.md` | Ajout de DEF-003 comme exemple de faux positif retiré après vérification UI. | Documenter une limite de classification des défauts. |
| 2026-11-07 | tests/gold/test_ui_pw_room_edit_delete.py | Ajout du test Playwright de modification du prix (TC-904-02). | Vérifier l'enregistrement du prix via l'interface et l'API, avec nettoyage de la chambre de test. |
| 2026-11-07 | prompts/v1/gen_tests_api.md, spec/api_notes.md | Fixtures, URLs, image et nettoyage harmonisés; observations PUT/DELETE précisées. | Empêcher la génération de tests avec des fixtures inexistantes et refléter le comportement constaté via la passerelle. |
| 2026-11-07 | spec/api_notes.md | PUT avec un prix non numérique documenté comme 400 sans modification. | Résultat vérifié par observation; ce comportement n'est pas un défaut serveur. |
| 2026-11-07 | tests/api/test_tc_004_02.py | TC-004-02 régénéré après détection d'une fixture inventée, d'une URL externe et de except: pass. | Compléter les règles du prompt API pour contraindre les fixtures, les URLs et la gestion des erreurs. |
| 2026-11-08 | `cases/REQ-002.json`, `tests/api/test_tc_002_03.py`, `tests/api/test_tc_002_01.py` | TC-002-03 hors sujet (test de login) détecté en relisant Jira, remplacé par un cas sur l'accès à la liste des chambres. TC-002-01 régénéré par `--force` : diff relu, vérifications équivalentes, version conservée. | Un seul cas devait changer ; contrôle du diff ajouté à la procédure. |
