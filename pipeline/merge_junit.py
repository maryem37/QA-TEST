"""Fusionne reports/junit-ui.xml dans reports/junit.xml (le second est optionnel)."""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

API = Path("reports/junit.xml")
UI = Path("reports/junit-ui.xml")


def suites(path: Path) -> list[ET.Element]:
    root = ET.parse(path).getroot()
    return [root] if root.tag == "testsuite" else list(root.iter("testsuite"))


def main() -> None:
    sources = [p for p in (API, UI) if p.exists()]
    if not sources:
        raise SystemExit("aucun fichier JUnit trouvé dans reports/")
    merged = ET.Element("testsuites")
    for p in sources:
        for s in suites(p):
            merged.append(s)
    API.parent.mkdir(exist_ok=True)
    ET.ElementTree(merged).write(API, encoding="utf-8", xml_declaration=True)
    print(f"JUnit fusionnés : {', '.join(p.name for p in sources)} -> {API}")


if __name__ == "__main__":
    sys.exit(main())