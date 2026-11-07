import requests

B = "http://localhost:8080"
D = "http://localhost:3001"

tok = requests.post(
    f"{B}/api/auth/login",
    json={"username": "admin", "password": "password"},
    timeout=10,
).json()["token"]
h = {"Cookie": f"token={tok}"}

for room in requests.get(f"{B}/api/room", timeout=10).json()["rooms"]:
    if room["roomid"] > 3:
        r = requests.delete(f"{D}/room/{room['roomid']}", headers=h, timeout=10)
        print("delete", room["roomid"], room["roomName"], r.status_code)

rooms = requests.get(f"{B}/api/room", timeout=10).json()["rooms"]
print("restant:", [r["roomid"] for r in rooms])