import argparse
import json
from pathlib import Path

from backends.base import TestManagementBackend
from backends.file_backend import FileBackend

REQUIREMENTS = Path("requirements")


def mapping_path(name: str) -> Path:
    """mapping.json pour le backend file (inchangé), mapping.<backend>.json pour les autres."""
    return Path("mapping.json") if name == "file" else Path(f"mapping.{name}.json")


def get_backend(name: str) -> TestManagementBackend:
    if name == "file":
        return FileBackend()
    if name == "xray":
        from backends.xray_backend import XrayBackend  # import tardif : exige les variables JIRA_*

        return XrayBackend()
    raise SystemExit(f"Backend inconnu : {name}")


def load_cases() -> list[dict]:
    cases = []
    for f in sorted(Path("cases").glob("REQ-*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("cases", [])
        for c in items:
            c.setdefault("requirement_id", f.stem)
            cases.append(c)
    return cases


def requirement_text(req_id: str) -> tuple[str, str]:
    """Titre (première ligne non vide) et texte complet de requirements/REQ-xxx.md."""
    f = REQUIREMENTS / f"{req_id}.md"
    if not f.exists():
        return req_id, ""
    text = f.read_text(encoding="utf-8").strip()
    title = next((ln.strip("# ").strip() for ln in text.splitlines() if ln.strip()), req_id)
    return title, text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="file")
    ap.add_argument("--limit", type=int, default=0, help="n'exporter que les n premiers cas")
    args = ap.parse_args()

    backend = get_backend(args.backend)
    path = mapping_path(args.backend)
    mapping = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    cases = load_cases()
    if args.limit:
        cases = cases[: args.limit]

    requirement_keys: dict[str, str | None] = {}
    created = updated = 0
    for case in cases:
        tc_id = case["id"]
        req_id = case["requirement_id"]
        if req_id not in requirement_keys:
            title, text = requirement_text(req_id)
            req_key = backend.ensure_requirement(req_id, title, text, mapping.get(req_id))
            requirement_keys[req_id] = req_key
            if req_key:
                mapping[req_id] = req_key

        key = mapping.get(tc_id) or backend.find_by_external_id(tc_id)
        if key:
            backend.update_test(key, case)
            updated += 1
        else:
            key = backend.create_test(case)
            created += 1
        mapping[tc_id] = key
        if requirement_keys[req_id]:
            backend.link_to_requirement(key, requirement_keys[req_id])

    path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    tests_total = sum(1 for k in mapping if k.startswith("TC-"))
    reqs = sum(1 for k in mapping if k.startswith("REQ-"))
    extra = f", {reqs} exigences" if reqs else ""
    print(
        f"Export {args.backend} : {created} créés, {updated} mis à jour, "
        f"{tests_total} au total{extra}"
    )


if __name__ == "__main__":
    main()
