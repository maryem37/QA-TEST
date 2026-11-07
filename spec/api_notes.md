Base URL : http://localhost:8080

## GET /api/room
- Auth : aucune
- Succès : 200, JSON `{"rooms": [ ... ]}`
- Champs d'une chambre : roomid (int), roomName (str), type (Single|Double|Suite),
  roomPrice (int), accessible (bool), description (str), features (list[str]), image (str)
- Données initiales : 3 chambres (101 Single 100, 102 Double 150, 103 Suite 225)

## GET /api/branding
- Auth : aucune
- Succès : 200, JSON (infos de l'hôtel, forme à compléter)

## POST /api/auth/login
- Auth : aucune
- Corps : {"username": "admin", "password": "password"}
- Succès : 200, JSON {"token": "<chaîne>"} (pas de Set-Cookie)
- Échec (mauvais mot de passe) : <code observé>
- Le jeton est ensuite envoyé en cookie `token` (à confirmer)
## POST /api/auth/login
- Auth : aucune
- Corps : {"username": "admin", "password": "password"}
- Succès : 200, JSON {"token": "<chaîne>"} (pas de Set-Cookie)
- Mauvais mot de passe : 401, {"error": "Invalid credentials"}
- JSON invalide : 500 (voir DEF-001)

## GET /api/message
- Auth : cookie `token=<jeton>`
- Succès : 200, {"messages": [{"id": int, "name": str, "read": bool, "subject": str}]}
- Donnée initiale : 1 message (James Dean, "Booking enquiry", non lu)

## POST /api/auth/login
- Succès : 200, {"token": "..."}. Le jeton est dans le corps JSON, PAS dans un cookie Set-Cookie.
- Champs vides ou mauvais identifiants : 401, {"error": "Invalid credentials"}
- JSON invalide : 500 (voir DEF-001)

## GET /api/room
- roomid (int, 1 à 3) est DIFFÉRENT de roomName (str, "101" à "103").
- Chambres initiales : roomid 1 / roomName "101" / Single / 100 ; roomid 2 / "102" / Double / 150 ; roomid 3 / "103" / Suite / 225
## POST /api/auth/login
- Succès : 200, {"token": "..."}. Le jeton est dans le corps JSON, PAS dans un cookie Set-Cookie.
- Champs vides ou mauvais identifiants : 401, {"error": "Invalid credentials"}
- JSON invalide : 500 (voir DEF-001)

## GET /api/room
- roomid (int, 1 à 3) est DIFFÉRENT de roomName (str, "101" à "103").
- Chambres initiales : roomid 1 / roomName "101" / Single / 100 ; roomid 2 / "102" / Double / 150 ; roomid 3 / "103" / Suite / 225
## GET /api/message
- Auth : aucune exigée en pratique (200 sans jeton, et avec jeton invalide) : voir DEF-002

## POST /api/room
- Auth : cookie `token` obligatoire
- Sans jeton : 401, {"errors": ["Authentication required"]}
- Corps : {"roomName": str, "type": str, "accessible": bool, "description": str,
  "image": str, "roomPrice": int, "features": [str]}
- Succès avec jeton : code et forme de réponse à relever
## POST /api/room
- Avec jeton : 200, {"success": true} (pas d'id renvoyé : retrouver la chambre via GET /api/room par roomName)

## PUT /api/room/<roomid>
- Auth : cookie token.
- Observé via l'interface : 202.

## DELETE /api/room/<roomid>
- Auth : cookie token. Observé : 202, la chambre disparaît.

## GET /api/message
- Comportement ATTENDU (REQ-012) : 401 ou 403 sans jeton valide.
- Comportement OBSERVÉ : 200 (DEF-002). Les tests vérifient l'ATTENDU, jamais l'observé.
