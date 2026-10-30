# Défauts observés

Les défauts décrivent un écart entre le comportement observé du site et le
comportement attendu défini par les exigences (requirements/REQ-xxx.md).

## DEF-001 : JSON invalide sur le login renvoie 500 au lieu de 400
- Endpoint : POST /api/auth/login
- Reproduction : envoyer le corps `{bad` avec `Content-Type: application/json`
  (reproduit le 30/10/2026 via requests, hors PowerShell)
- Attendu : 400 (erreur du client)
- Observé : 500, `{"error":"An unexpected error occurred"}`
- Gravité : mineure
- Exigence liée : REQ-001
- Test automatisé : test_login_invalid_json_returns_400 (xfail strict)
- Statut : ouvert

## DEF-002 : GET /api/message accessible sans jeton valide
- Endpoint : GET /api/message
- Reproduction : appeler l'endpoint sans cookie, ou avec le cookie `token=invalid_token`
- Attendu : 401 ou 403 (REQ-012)
- Observé : 200, avec la liste des messages (id, nom, sujet, état lu/non lu)
- Contraste : POST /api/room sans jeton renvoie bien 401 `{"errors":["Authentication required"]}`
- Gravité : moyenne à haute (exposition de données de visiteurs, en lecture seule)
- Exigences liées : REQ-010, REQ-012
- Tests automatisés (rouges volontairement) :
  - TC-010-02 : lecture des messages sans jeton
  - TC-010-03 : lecture des messages avec jeton invalide
  - TC-012-02 : lecture des messages sans jeton
  - TC-012-03 : lecture des messages avec jeton invalide
- Statut : ouvert
- Réserve : il peut s'agir d'un choix de conception des auteurs de l'application.
  Le défaut est établi par rapport à notre exigence REQ-012, pas par rapport à leur intention.

## DEF-003 : GET et DELETE /api/room/{id} renvoient 500 via la passerelle (:8080)
- Endpoints : GET /api/room/{id}, DELETE /api/room/{id}
- Reproduction : login, POST /api/room, GET /api/room (relever l'id),
  puis DELETE /api/room/{id} avec `Cookie: token=<jeton>`
- Attendu : 200 ou 202 (suppression), 200 (lecture)
- Observé : 500 en texte brut, la chambre reste dans la liste
- Contraste : DELETE http://localhost:3001/room/{id} en direct renvoie 202
  et la chambre disparaît
- Preuve : interface admin (DELETE /api/room/6 -> 500) et script
  scratch/probe_routes.py ; logs rbp-assets :
  "Failed to proxy http://localhost:3001/room/7 ... ECONNREFUSED 127.0.0.1:3001"
- Conséquence : impossible de supprimer une chambre depuis l'interface admin
- Gravité : majeure
- Exigence liée : (à renseigner : celle de la gestion des chambres)
- Test automatisé : test_delete_room_succeeds (xfail strict)
- Statut : ouvert
- Réserve : la cause probable est une adresse 127.0.0.1 dans la configuration
  de la passerelle, donc un défaut d'environnement ou de configuration plutôt
  que de logique applicative. Non confirmé tant que le docker-compose.yml
  n'a pas été examiné.