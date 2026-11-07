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
statut masqués par la passerelle. Les 7 tests `xfail` (DEF-001, DEF-002, DEF-003) restent inchangés
avec le bug. Résultat identique en local et en CI (GitHub Actions, ubuntu-24.04).
