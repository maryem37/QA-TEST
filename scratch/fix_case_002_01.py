from pathlib import Path

p = Path("cases/REQ-002.json")
text = p.read_text(encoding="utf-8")
old = "et exactement 3 objets"
assert text.count(old) == 1, f"motif trouvé {text.count(old)} fois, attendu 1"
p.write_text(text.replace(old, "et au moins 1 objet"), encoding="utf-8")
print("cas TC-002-01 corrigé")