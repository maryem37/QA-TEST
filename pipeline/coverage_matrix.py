"""Build the REQ -> test case -> test file -> JUnit result traceability matrix."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from schemas.models import CaseList

JUNIT = Path("reports/junit.xml")


def results() -> dict[str, str]:
    out: dict[str, str] = {}
    if not JUNIT.exists():
        return out
    for testcase in ET.parse(JUNIT).getroot().iter("testcase"):
        stem = (testcase.get("classname") or "").split(".")[-1]
        if testcase.find("failure") is not None or testcase.find("error") is not None:
            out[stem] = "FAILED"
        elif (skipped := testcase.find("skipped")) is not None:
            out[stem] = (
                "KNOWN DEFECT" if "xfail" in (skipped.get("type") or "") else "SKIPPED"
            )
        else:
            out[stem] = "PASSED"
    return out


def main() -> None:
    result_by_test = results()
    rows: list[tuple[str, ...]] = []
    missing_api = 0
    for case_file in sorted(Path("cases").glob("REQ-*.json")):
        cases = CaseList.model_validate(json.loads(case_file.read_text(encoding="utf-8")))
        for case in cases.cases:
            stem = "test_" + case.id.lower().replace("-", "_")
            folder = Path("tests/api" if case.layer == "API" else "tests/ui_playwright")
            exists = (folder / f"{stem}.py").exists()
            if case.layer == "API" and not exists:
                missing_api += 1
            rows.append(
                (
                    case.requirement_id,
                    case.id,
                    case.layer,
                    case.type,
                    f"{stem}.py" if exists else "-",
                    result_by_test.get(stem, "not run" if exists else "-"),
                )
            )

    lines = [
        "| REQ | TC | Layer | Type | Test file | Result |",
        "|---|---|---|---|---|---|",
    ]
    lines.extend(f"| {' | '.join(row)} |" for row in rows)
    Path("reports").mkdir(exist_ok=True)
    Path("reports/traceability.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} cas, {missing_api} cas API sans test")


if __name__ == "__main__":
    main()
