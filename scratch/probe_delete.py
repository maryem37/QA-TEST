import requests

B = "http://localhost:8080"
s = requests.Session()

# Connexion : le jeton est dans le corps JSON
r = s.post(f"{B}/api/auth/login", json={"username": "admin", "password": "password"})
print("login", r.status_code, "clés:", list(r.json().keys()))
token = r.json().get("token")
print("token present:", bool(token))

# Le jeton part dans l'en-tête Cookie, comme dans le navigateur
s.headers.update({"Cookie": f"token={token}"})

# Création d'une chambre neuve
payload = {
    "roomName": "QA-9",
    "type": "Single",
    "accessible": False,
    "description": "probe",
    "features": ["WiFi"],
    "image": "https://www.mwtestconsultancy.co.uk/img/room1.jpg",
    "roomPrice": "123",
}
r = s.post(f"{B}/api/room", json=payload)
print("create", r.status_code, r.text[:200])

# Retrouver l'id de la chambre créée
rooms = s.get(f"{B}/api/room").json()["rooms"]
ids = [x["roomid"] for x in rooms if x["roomName"] == "QA-9"]
print("ids", ids)

# Suppression
for i in ids:
    d = s.delete(f"{B}/api/room/{i}")
    print("delete", i, d.status_code, d.text[:200])

print("restant", [x["roomid"] for x in s.get(f"{B}/api/room").json()["rooms"]])