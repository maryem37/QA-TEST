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

## DEF-003 : RETIRÉ (faux positif)
- Hypothèse initiale : DELETE /api/room/<id> renvoie 500 via la passerelle.
- Vérification : suppression via l'interface (DELETE /api/room/<id> -> 202, la ligne
  disparaît, l'API ne contient plus la chambre) et test API vert sans xfail.
- Conclusion : pas de défaut. Les 500 venaient de nos appels de test directs.
- Statut : fermé.
