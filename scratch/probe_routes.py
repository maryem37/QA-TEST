import requests

B = "http://localhost:8080"
s = requests.Session()
tok = s.post(f"{B}/api/auth/login",
             json={"username": "admin", "password": "password"}).json()["token"]
s.headers.update({"Cookie": f"token={tok}"})

ids = [r["roomid"] for r in s.get(f"{B}/api/room").json()["rooms"]]
print("ids présents:", ids)
rid = ids[-1]

# 1. Lecture d'une chambre par id, via la passerelle
r = s.get(f"{B}/api/room/{rid}")
print("GET  passerelle /api/room/%s ->" % rid, r.status_code, r.text[:80])

# 2. Suppression via la passerelle (le cas qui échoue)
r = s.delete(f"{B}/api/room/{rid}")
print("DEL  passerelle /api/room/%s ->" % rid, r.status_code, r.text[:80])

# 3. Même suppression en direct sur le service des chambres (port 3001)
r = s.delete(f"http://localhost:3001/room/{rid}")
print("DEL  direct     :3001/room/%s ->" % rid, r.status_code, r.text[:80])

print("restant:", [x["roomid"] for x in s.get(f"{B}/api/room").json()["rooms"]])