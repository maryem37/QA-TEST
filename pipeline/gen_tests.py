"""Génération des tests API à partir des cas (cases/REQ-*.json)."""

import ast
import json
import re
import sys
import time
from pathlib import Path

from groq import RateLimitError
from pydantic import ValidationError

from pipeline.llm_client import complete
from schemas.models import CaseList, GeneratedTest

PROMPT_VERSION = "v1"
SYSTEM = Path(f"prompts/{PROMPT_VERSION}/gen_tests_api.md").read_text(encoding="utf-8")
NOTES = Path("spec/api_notes.md").read_text(encoding="utf-8")
GOLD = "\n\n".join(
    p.read_text(encoding="utf-8") for p in sorted(Path("tests/gold").glob("test_api_*.py"))
)
OUT = Path("tests/api")


def extract_code(raw: str) -> str:
    """Extrait le code Python d'un bloc markdown, et déplie les \\n littéraux."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", raw, re.DOTALL)
    code = (m.group(1) if m else raw).strip()
    # Réponse « échappée » sur une seule ligne
    if "\n" not in code and "\\n" in code:
        code = code.replace("\\n", "\n").replace("\\t", "\t")
    return code + "\n"


def generate(case_json: str) -> str:
    user = f"## Cas de test\n{case_json}\n\n## Notes API\n{NOTES}\n\n## Exemples\n{GOLD}"
    error = ""
    for _ in range(3):
        prompt = (
            user
            if not error
            else (
                f"{user}\n\nRéponse précédente invalide : {error}\n"
                "Renvoie uniquement le code Python complet dans un seul bloc ```python."
            )
        )
        raw = complete(SYSTEM, prompt, PROMPT_VERSION, max_tokens=8000, json_mode=False)
        code = extract_code(raw)
        try:
            ast.parse(code)
            return GeneratedTest.model_validate({"code": code}).code
        except SyntaxError as e:
            error = f"code Python invalide : {e.msg} (ligne {e.lineno})"
        except ValidationError as e:
            error = str(e)[:400]
    raise RuntimeError(f"échec après 3 essais ({error})")


def main(args: list[str]) -> None:
    force = "--force" in args
    only = [a for a in args if not a.startswith("--")]
    OUT.mkdir(parents=True, exist_ok=True)

    files = [
        f for f in sorted(Path("cases").glob("REQ-*.json")) if not only or f.stem in only
    ]
    if not files:
        print(f"Aucun fichier cases/ ne correspond à : {', '.join(only) or '(aucun)'}")
        return

    generated = 0
    for f in files:
        cases = CaseList.model_validate(json.loads(f.read_text(encoding="utf-8")))
        api_cases = [c for c in cases.cases if c.layer == "API"]
        if not api_cases:
            layers = sorted({c.layer for c in cases.cases})
            print(f"{f.stem} : aucun cas API (couches : {', '.join(layers)}), ignoré")
            continue
        for c in api_cases:
            target = OUT / f"test_{c.id.lower().replace('-', '_')}.py"
            if target.exists() and not force:
                print(f"{c.id} : {target.name} existe déjà, ignoré (--force pour régénérer)")
                continue
            try:
                code = generate(c.model_dump_json(indent=2))
            except RateLimitError as e:
                print(f"Quota LLM atteint, arrêt propre : {str(e)[:200]}")
                print(f"{generated} test(s) généré(s). Relancez plus tard.")
                sys.exit(1)
            target.write_text(code, encoding="utf-8")
            print(f"{c.id} -> {target}")
            generated += 1
            time.sleep(3)
    print(f"{generated} test(s) généré(s)")


if __name__ == "__main__":
    main(sys.argv[1:])
