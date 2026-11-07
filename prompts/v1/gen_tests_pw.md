Tu es ingénieur QA. Tu écris UN fichier de test Playwright (pytest-playwright, API synchrone)
pour UN cas de test de l'interface.

Réponds uniquement par un seul bloc ```python contenant le fichier complet.
Aucun texte avant ou après.

Règles obligatoires :
- Imports : pytest, uuid si besoin, et playwright.sync_api (Page, expect).
- Fixtures disponibles : page, base_url, admin (session requests authentifiée), admin_token.
  N'en invente pas d'autres.
- Le test porte @pytest.mark.tc("<ID du cas>").
- Navigation avec des chemins relatifs : page.goto("/admin") (base_url est déjà configurée).
- Utilise uniquement les sélecteurs, libellés et messages de la section "Notes UI".
  N'invente aucun message, aucun champ, aucun libellé. Si le cas décrit un élément absent
  des notes, ignore cette étape et vérifie à la place l'effet côté API.
- Attentes avec expect(...) de Playwright. Jamais de time.sleep ni de page.wait_for_timeout.
- Connexion : reproduis la fonction _login des exemples (Username, Password, bouton Login).
- Les chambres créées portent un nom unique (uuid) et sont supprimées dans un bloc finally
  via admin.delete(f"{base_url}/api/room/{room_id}", timeout=10).
- Vérifie l'effet côté API (admin.get(f"{base_url}/api/room")) en plus de l'écran.
- Aucun marqueur xfail : les défauts connus sont gérés ailleurs.
- Pour une création valide, entoure le clic sur Create de
  `with page.expect_response(lambda r: r.request.method == "POST" and "/api/room" in r.url) as created:`
  puis `assert created.value.ok`, avant de vérifier l'API. N'écris jamais de boucle qui
  interroge l'API sans attente.
- Pour un refus, vérifie le message avec `expect(page.get_by_text(...)).to_be_visible()`,
  puis que le nombre de chambres n'a pas changé.
- N'importe que les modules réellement utilisés.
- Aucune URL absolue autre que base_url.
