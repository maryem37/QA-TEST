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
statut masqués par la passerelle. Les 7 tests `xfail` (DEF-001 et DEF-002) restent inchangés
avec le bug. Résultat identique en local et en CI (GitHub Actions, ubuntu-24.04).
## Reproductibilité

| Vérification | Résultat |
|---|---|
| Deux exports locaux successifs (`make sync`), dossier supprimé entre les deux | 34 fichiers, empreintes identiques |
| Export local (Windows) contre export CI (ubuntu-24.04) | `MOCK-1.json` identique : 89AB77B1…668D |
| Deux runs CI consécutifs sur `main` (statuts des 23 tests, `scripts/compare_runs.py`) | 0 différence |
| Run CI contre exécution locale | à compléter après l'étape 1 |

Limite : le commentaire du LLM n'est pas reproductible (pas de cache en CI), alors que les chiffres du
rapport, l'export et les statuts le sont. Les durées varient d'un run à l'autre et sont exclues de la comparaison.