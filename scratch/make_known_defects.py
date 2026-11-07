import json
from pathlib import Path

known = {
    "TC-010-02": {"def": "DEF-002", "title": "GET /api/message sans jeton renvoie 200"},
    "TC-010-03": {"def": "DEF-002", "title": "GET /api/message avec jeton invalide renvoie 200"},
    "TC-012-02": {"def": "DEF-002", "title": "GET /api/message sans jeton renvoie 200"},
    "TC-012-03": {"def": "DEF-002", "title": "GET /api/message avec jeton invalide renvoie 200"},
}

path = Path("spec/known_defects.json")
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(known, ensure_ascii=False, indent=2), encoding="utf-8")
print("écrit :", path.resolve())