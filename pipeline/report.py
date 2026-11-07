import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from pipeline.push_results import JUNIT, collect

load_dotenv()

OUT = Path("reports/report.md")
PROMPT_VERSION = "v1"


def facts() -> dict:
    results = collect()
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    cases = []
    for f in sorted(Path("cases").glob("REQ-*.json")):
        cases += json.loads(f.read_text(encoding="utf-8"))["cases"]

    def has_test(c: dict) -> bool:
        folder = "tests/api" if c["layer"] == "API" else "tests/ui_playwright"
        return (Path(folder) / f"test_{c['id'].lower().replace('-', '_')}.py").exists()

    with_test = [c for c in cases if has_test(c)]
    covered = {c["requirement_id"] for c in with_test}
    uncovered = sorted({c["requirement_id"] for c in cases} - covered)

    defects: dict[str, dict] = {}
    for r in results:
        if r["status"] == "KNOWN_DEFECT" and r["defect"]:
            e = defects.setdefault(
                r["defect"],
                {"description": r["reason"].split(" : ", 1)[-1], "tests": []},
            )
            e["tests"].append(r["tc_id"] or r["test"].split("::")[-1])

    return {
        "total": len(results),
        "counts": counts,
        "duration_s": round(sum(r["duration_s"] for r in results), 1),
        "cases_total": len(cases),
        "cases_api": sum(c["layer"] == "API" for c in cases),
        "cases_ui": sum(c["layer"] == "UI" for c in cases),
        "cases_with_test": len(with_test),
        "requirements_without_test": uncovered,
        "defects": defects,
        "failures": [
            {"test": r["test"].split("::")[-1], "tc": r["tc_id"]}
            for r in results
            if r["status"] == "FAILED"
        ],
    }


def commentary(f: dict) -> str:
    from pipeline.llm_client import MODEL, complete  # import tardif : exige GROQ_API_KEY

    system = Path(f"prompts/{PROMPT_VERSION}/report.md").read_text(encoding="utf-8")
    text = complete(
        system, json.dumps(f, ensure_ascii=False, indent=2), PROMPT_VERSION, json_mode=False
    )
    return f"{text.strip()}\n\n*Commentaire généré par le modèle `{MODEL}` (prompt {PROMPT_VERSION}).*"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()
    if not JUNIT.exists():
        raise SystemExit("reports/junit.xml introuvable")

    f = facts()
    c = f["counts"]
    lines = [
        "# Rapport de synthèse QA",
        "",
        "## Chiffres (calculés par le code)",
        "",
        "| Indicateur | Valeur |",
        "|---|---|",
        f"| Tests exécutés | {f['total']} |",
        f"| Réussis | {c.get('PASSED', 0)} |",
        f"| Échoués | {c.get('FAILED', 0)} |",
        f"| Tests en défaut connu (xfail) | {c.get('KNOWN_DEFECT', 0)} |",
        f"| Défauts distincts | {len(f['defects'])} |",
        f"| Durée cumulée | {f['duration_s']} s |",
        f"| Cas de test | {f['cases_total']} (API : {f['cases_api']}, UI : {f['cases_ui']}) |",
        f"| Cas avec test automatisé | {f['cases_with_test']} / {f['cases_total']} |",
        f"| Exigences sans test automatisé | {', '.join(f['requirements_without_test']) or 'aucune'} |",
        "",
        "## Défauts connus",
        "",
        "| Défaut | Description | Tests |",
        "|---|---|---|",
    ]
    for d, e in sorted(f["defects"].items()):
        lines.append(f"| {d} | {e['description']} | {', '.join(e['tests'])} |")

    lines += ["", "## Tests échoués", ""]
    if f["failures"]:
        lines += ["| Test | Cas |", "|---|---|"]
        for x in f["failures"]:
            lines.append(f"| {x['test']} | {x['tc'] or '-'} |")
    else:
        lines.append("Aucun.")

    lines += ["", "## Commentaire (généré par IA)", ""]
    if args.no_llm or not os.getenv("GROQ_API_KEY"):
        lines.append("*Commentaire non généré (pas de clé API ou option --no-llm).*")
    else:
        lines.append(commentary(f))

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Rapport écrit : {OUT}")


if __name__ == "__main__":
    main()
