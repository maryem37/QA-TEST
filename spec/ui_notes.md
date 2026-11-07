# Notes sur l'interface (relevées avec Playwright codegen, application locale)

Base URL : http://localhost:8080

## Connexion : /admin
- Champs : `get_by_role("textbox", name="Username")`, `get_by_role("textbox", name="Password")`
- Bouton : `get_by_role("button", name="Login")`
- Identifiants : admin / password
- Après connexion : redirection vers /admin/rooms

## Barre de navigation (admin)
- Rooms, Report, Branding, Messages (avec compteur), Front Page, Logout

## Page /admin/rooms
- Tableau des chambres : colonnes Room #, Type, Accessible, Price, Room details
- Chambres initiales : 101 Single true 100 ; 102 Double true 150 ; 103 Suite true 225
- Formulaire de création :
  - numéro : `get_by_test_id("roomName")`
  - type : liste déroulante (valeur par défaut Single)
  - accessibilité : `#accessible` (valeurs "true" / "false")
  - prix : `#roomPrice`
  - équipements : cases à cocher `get_by_role("checkbox", name="WiFi")`, TV, Refreshments, Safe, et d'autres (Radio, Views) à confirmer
  - bouton : `get_by_role("button", name="Create")`

## Messages observés
- Numéro vide et prix non numérique : « Failed to create room »; aucune chambre n'est créée.
- Numéro vide avec un prix valide : « Room name must be set ».
- Numéro rempli et prix non numérique : « Failed to create room »; aucune chambre n'est créée.
- Création valide : message ou ligne de confirmation à relever après observation.

## Règles pour les tests
- Ne jamais inventer un message : utiliser uniquement ceux de ce fichier.
- Vérifier l'effet côté API (GET /api/room) en plus de l'écran.
- Les chambres créées portent un nom unique (uuid) et sont supprimées via l'API dans un bloc finally.

## Valeurs possibles
- Types : Single, Twin, Double, Family, Suite
- Équipements : WiFi, TV, Radio, Refreshments, Safe, Views
- Accessible : "false" (défaut) ou "true"
