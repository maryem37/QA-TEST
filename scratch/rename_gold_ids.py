from pathlib import Path

RENAMES = {
    "tests/gold/test_api_auth.py": {"TC-001-03": "TC-901-01"},
    "tests/gold/test_api_create_room.py": {
        "TC-002-02": "TC-901-02",
        "TC-002-03": "TC-901-03",
        "TC-003-01": "TC-901-04",
    },
}

for path, mapping in RENAMES.items():
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    for old, new in mapping.items():
        assert f'"{old}"' in text, f"{old} introuvable dans {path}"
        text = text.replace(f'"{old}"', f'"{new}"')
    p.write_text(text, encoding="utf-8")
    print("OK", path)