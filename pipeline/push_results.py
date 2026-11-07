import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from pipeline.export import get_backend

JUNIT = Path("reports/junit.xml")
MAPPING = Path("mapping.json")
DEF_RE = re.compile(r"DEF-\d+")


def status(t: ET.Element) -> str:
    if t.find("failure") is not None or t.find("error") is not None:
        return "FAILED"
    s = t.find("skipped")
    if s is not None:
        return "KNOWN_DEFECT" if "xfail" in (s.get("type") or "") else "SKIPPED"
    return "PASSED"


def tc_id(classname: str) -> str | None:
    """tests.api.test_tc_010_02 -> TC-010-02 (None pour les tests gold)."""
    stem = classname.split(".")[-1]
    if stem.startswith("test_tc_"):
        return "TC-" + "-".join(stem.split("_")[2:])
    return None


def defect_of(t: ET.Element) -> tuple[str | None, str]:
    """Identifiant et raison du défaut, lus dans le message du xfail."""
    s = t.find("skipped")
    msg = (s.get("message") or "") if s is not None else ""
    m = DEF_RE.search(msg)
    return (m.group(0) if m else None), msg


def collect() -> list[dict]:
    mapping = json.loads(MAPPING.read_text(encoding="utf-8")) if MAPPING.exists() else {}
    results = []
    for t in ET.parse(JUNIT).getroot().iter("testcase"):
        classname = t.get("classname") or ""
        tc = tc_id(classname)
        defect, reason = defect_of(t)
        results.append(
            {
                "tc_id": tc,
                "test": f"{classname}::{t.get('name')}",
                "status": status(t),
                "defect": defect,
                "reason": reason,
                "test_key": mapping.get(tc) if tc else None,
                "duration_s": round(float(t.get("time") or 0), 3),
            }
        )
    return sorted(results, key=lambda r: r["test"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="file")
    args = ap.parse_args()

    if not JUNIT.exists():
        raise SystemExit("reports/junit.xml introuvable : lancez d'abord make run ou pytest")
    results = collect()
    execution_id = get_backend(args.backend).import_results(results)
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"Résultats importés dans {args.backend} ({execution_id}) : {counts}")


if __name__ == "__main__":
    main()
