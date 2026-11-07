"""Contrôles statiques des tests générés (tests/api)."""

import re
import subprocess
import sys
from pathlib import Path

TESTS = Path("tests/api")
files = sorted(TESTS.glob("test_*.py"))
errors: list[str] = []

for f in files:
    src = f.read_text(encoding="utf-8")

    try:
        compile(src, str(f), "exec")
    except SyntaxError as e:
        errors.append(f"{f.name} : compilation impossible ({e.msg}, ligne {e.lineno})")
        continue

    expected = "TC-" + "-".join(f.stem.split("_")[2:])  # test_tc_010_02 -> TC-010-02
    if not re.search(r"pytest\.mark\.tc\(\s*[\"']" + re.escape(expected), src, re.IGNORECASE):
        errors.append(f"{f.name} : marqueur @pytest.mark.tc(\"{expected}\") absent")

    if re.search(r"\btime\.sleep\s*\(", src):
        errors.append(f"{f.name} : time.sleep interdit (utiliser des attentes explicites)")

    for url in re.findall(r"https?://[^\s\"')]+", src):
        if not re.match(r"https?://(localhost|127\.0\.0\.1)", url):
            errors.append(f"{f.name} : appel externe interdit ({url})")

if files:
    r = subprocess.run([sys.executable, "-m", "ruff", "check", "tests/api"], check=False)
    if r.returncode:
        errors.append("ruff a signalé des erreurs")

print(f"{len(files)} fichiers vérifiés")
if errors:
    print("ÉCHEC")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
print("OK")
