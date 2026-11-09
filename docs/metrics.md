# Preuve de détection : injection de bugs

| Bug injecté | Détecté | Tests en échec | Remarque |
|---|---|---|---|
| bug-000 : `GET /room` renvoie 202 au lieu de 200 | non | 0 | masqué par la passerelle Next.js (direct : 202, passerelle : 200) |
| création de chambre renvoie 200 au lieu de 201 | non (analyse statique) | 0 | aucun test ne vérifie le code 201 |
| bug-001 : `GET /api/room` renvoie une liste vide | oui | 5 | workflow `bug-injection` #1 : 5 failed, 11 passed, 7 xfailed |

Tests qui détectent bug-001 :

- `test_room_list_returns_rooms` (gold)
- `test_get_room_list_contains_type_and_price` (TC-002-01)
- `test_room_101_is_single_and_available` (TC-006-03)
- `test_create_room_then_visible_in_list` (gold, effet de bord)
- `test_delete_room_succeeds` (gold, effet de bord)

Lecture : la suite détecte les défauts de contenu des réponses, mais pas les défauts de code de
statut masqués par la passerelle. Les 7 tests `xfail` correspondent à 2 défauts distincts
(DEF-001 et DEF-002), pas 3, et restent inchangés avec le bug. Résultat identique en local
et en CI (GitHub Actions, ubuntu-24.04).
## Reproductibilité

| Vérification | Résultat |
|---|---|
| Deux exports locaux successifs (`make sync`), dossier supprimé entre les deux | 34 fichiers, empreintes identiques |
| Export local (Windows) contre export CI (ubuntu-24.04) | `MOCK-1.json` identique : 89AB77B1…668D |
| Deux runs CI consécutifs sur `main` (statuts des 23 tests, `scripts/compare_runs.py`) | 0 différence |
| Run CI contre exécution locale | à compléter après l'étape 1 |

Limite : le commentaire du LLM n'est pas reproductible (pas de cache en CI), alors que les chiffres du
rapport, l'export et les statuts le sont. Les durées varient d'un run à l'autre et sont exclues de la comparaison.

## Consommation du LLM (journal local `reports/llm_log.jsonl`)

Modèle : `openai/gpt-oss-120b` (Groq, plan gratuit, coût monétaire nul).

| Jour | Appels | Tokens d'entrée | Tokens de sortie |
|---|---|---|---|
| 2026-10-30 | 108 | 164 581 | 77 326 |
| 2026-10-31 | 3 | 8 120 | 1 224 |
| 2026-11-07 | 12 | 28 349 | 10 603 |
| 2026-11-08 | 4 | 8 139 | 1 281 |
| **Total** | **127** | **209 189** | **90 434** |

Durée moyenne par appel : 6,6 s.

Lecture :
- Les chiffres incluent la mise au point (prompts durcis, régénérations avec `--force`) :
  ils mesurent l'effort de développement, pas le coût d'une génération à froid.
- Les tentatives échouées (429, erreurs de format) et les réponses servies par le cache
  ne sont pas journalisées.
- Les appels de la CI (commentaire du rapport) ne sont pas inclus : le journal est local.
- La génération des tests UI est la plus coûteuse par appel, car chaque prompt embarque
  les notes d'interface et les tests de référence.
- La contrainte réelle est le quota de tokens par jour du plan gratuit (200 000), pas le coût.

## LLM consumption (local log `reports/llm_log.jsonl`)

Model: `openai/gpt-oss-120b` (Groq free plan, no monetary cost).

| Day | Real calls | Input tokens | Output tokens |
|---|---|---|---|
| 2026-10-30 | 108 | 164,581 | 77,326 |
| 2026-10-31 | 3 | 8,120 | 1,224 |
| 2026-11-07 | 11 | 28,349 | 10,603 |
| 2026-11-08 | 3 | 8,139 | 1,281 |
| **Total** | **125** | **209,189** | **90,434** |

Plus 2 responses served from the cache (0 tokens). Average duration: 6.7 s per real call.

Reading:
- 86 % of the calls (108 of 125) happened on the first day: case generation, first API tests,
  prompt tuning and regenerations. The figures measure development effort, not the cost of a
  clean generation.
- Failed attempts (429 rate limits, format errors) are not logged, and the log is local:
  CI calls (report commentary) and other machines are not included.
- UI test generation costs the most per call, because each prompt embeds the UI notes and the
  reference tests.
- The real constraint is the free plan's daily token quota, not money.
- Not measured: the share of valid output on the first attempt, because validation retries are
  not logged.