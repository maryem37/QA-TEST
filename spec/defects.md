# Défauts observés

Les défauts décrivent un écart entre le comportement observé du site et le
comportement attendu défini par les exigences (`requirements/REQ-xxx.md`).

## DEF-001 : JSON invalide sur le login renvoie 500 au lieu de 400
- Endpoint : POST /api/auth/login
- Reproduction : envoyer `{bad` avec `Content-Type: application/json`.
- Attendu : 400 (erreur du client).
- Observé : 500, `{"error":"An unexpected error occurred"}`.
- Gravité : mineure.
- Exigence liée : REQ-001.
- Test automatisé : `test_login_invalid_json_returns_400` (xfail strict).
- Statut : ouvert.

## DEF-002 : GET /api/message accessible sans jeton valide
- Endpoint : GET /api/message.
- Reproduction : appeler l'endpoint sans cookie ou avec `token=invalid_token`.
- Attendu : 401 ou 403 selon REQ-012.
- Observé : 200 avec la liste des messages (id, nom, sujet, état lu/non lu).
- Contraste : POST /api/room sans jeton renvoie 401.
- Gravité : moyenne à haute (exposition de données de visiteurs en lecture seule).
- Exigences liées : REQ-010, REQ-012.
- Tests automatisés (xfail strict, défaut connu) : TC-010-02, TC-010-03,
  TC-012-02, TC-012-03.
- Statut : ouvert.
- Réserve : le défaut est établi par rapport à REQ-012, pas à l'intention des auteurs.

## Configuration amont : passerelle assets vers le service room

Le `docker-compose.yml` amont ne définit pas `ROOM_API`. L'asset utilise donc
son URL par défaut `http://localhost:3001`; dans un conteneur, localhost désigne
le conteneur assets lui-même. Cela explique `ECONNREFUSED 127.0.0.1:3001` et
les erreurs observées lors de l'utilisation du compose amont.

Le compose racine de ce dépôt construit `assets/Dockerfile`, qui définit
`ROOM_API=http://rbp-room:3001` sur le réseau Compose. Cette configuration
corrige le problème pour l'environnement de test de ce dépôt. La suppression
passe désormais par la passerelle dans `tests/gold/test_api_create_room.py`;
ce problème n'est donc suivi ici comme défaut applicatif ni marqué xfail.
