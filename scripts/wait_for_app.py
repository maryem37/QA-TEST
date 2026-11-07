import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()
BASE = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")

CHECKS = [
    ("GET", "/api/room", None),
    ("GET", "/api/branding", None),
    ("GET", "/api/message", None),
    ("POST", "/api/auth/login", {"username": "admin", "password": "password"}),
]


def failing() -> list[str]:
    bad = []
    for method, path, body in CHECKS:
        try:
            r = requests.request(method, BASE + path, json=body, timeout=10)
            if r.status_code != 200:
                bad.append(f"{method} {path} -> {r.status_code}")
        except requests.RequestException as e:
            bad.append(f"{method} {path} -> {type(e).__name__}")
    return bad


for i in range(1, 61):
    bad = failing()
    if not bad:
        print(f"App prête : {BASE} (tous les services répondent)")
        sys.exit(0)
    print(f"Attente ({i}/60) : {'; '.join(bad)}")
    time.sleep(5)

print("L'application n'est pas prête", file=sys.stderr)
sys.exit(1)