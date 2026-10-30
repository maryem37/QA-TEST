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