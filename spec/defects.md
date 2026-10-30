# Défauts observés

Les défauts décrivent un écart entre le comportement observé du site et le
comportement attendu défini par les exigences (requirements/REQ-xxx.md).

## DEF-001 : JSON invalide sur le login renvoie 500 au lieu de 400
- Endpoint : POST /api/auth/login
- Reproduction : envoyer le corps `{bad` avec l'en-tête `Content-Type: application/json`
- Attendu : 400 (erreur du client)
- Observé : 500, `{"error":"An unexpected error occurred"}`
- Gravité : mineure
- Exigence liée : REQ-001
- Test automatisé : aucun pour l'instant (à ajouter)
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

## Observations à confirmer (pas encore des défauts)

- `GET` et `DELETE /api/room/<id>` via le port 8080 renvoient 500 en texte brut,
  alors que `GET`/`DELETE /room/<id>` sur le port 3001 fonctionnent (200 et 202).
  L'URL utilisée par l'interface n'est pas encore relevée. Si l'interface obtient
  aussi un 500, ce sera DEF-003.
- Format d'erreur incohérent : `/api/auth/login` renvoie `{"error": "..."}` (chaîne)
  alors que `/api/room` renvoie `{"errors": ["..."]}` (liste). Mineur.