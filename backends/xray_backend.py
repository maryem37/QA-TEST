"""Backend Jira + Xray Cloud : Stories (exigences), Tests (cas) et résultats d'exécution."""

import os
import re
import time
from datetime import UTC, datetime

import requests
from dotenv import load_dotenv

from backends.base import TestManagementBackend

load_dotenv()

XRAY = "https://xray.cloud.getxray.app/api/v2"
LINK_TYPE = "Test"  # un Test « tests » une Story (sens vérifié avec scratch/probe_xray_write.py)

CREATE_TEST = """
mutation($steps: [CreateStepInput], $jira: JSON!) {
  createTest(testType: {name: "Manual"}, steps: $steps, jira: $jira) {
    test { issueId jira(fields: ["key"]) }
    warnings
  }
}"""

IMPORTABLE = {"PASSED": "PASSED", "FAILED": "FAILED", "KNOWN_DEFECT": "FAILED"}
RANK = {"PASSED": 0, "FAILED": 1}


def normalize_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if "://" not in url:
        url = "https://" + url.lstrip("/")
    return url


def adf(lines: list[str]) -> dict:
    content = [
        {"type": "paragraph", "content": [{"type": "text", "text": ln}]}
        for ln in lines
        if ln.strip()
    ]
    if not content:
        content = [{"type": "paragraph", "content": [{"type": "text", "text": "-"}]}]
    return {"type": "doc", "version": 1, "content": content}


def _inline(text: str) -> list[dict]:
    nodes = []
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if not part:
            continue
        node = {"type": "text", "text": part}
        if i % 2 == 1:
            node["marks"] = [{"type": "strong"}]
        nodes.append(node)
    return nodes or [{"type": "text", "text": "-"}]


def md_to_adf(md: str) -> dict:
    """Convertit un Markdown simple (titres, listes, gras) au format de description Jira."""
    content: list[dict] = []
    current: dict | None = None
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            current = None
            continue
        head = re.match(r"^(#{1,6})\s+(.*)", line)
        bullet = re.match(r"^\s*[-*]\s+(.*)", line)
        number = re.match(r"^\s*\d+[.)]\s+(.*)", line)
        if head:
            current = None
            level = min(len(head.group(1)), 6)
            content.append(
                {"type": "heading", "attrs": {"level": level}, "content": _inline(head.group(2))}
            )
        elif bullet or number:
            kind = "bulletList" if bullet else "orderedList"
            if current is None or current["type"] != kind:
                current = {"type": kind, "content": []}
                content.append(current)
            text = (bullet or number).group(1)
            item = {"type": "paragraph", "content": _inline(text)}
            current["content"].append({"type": "listItem", "content": [item]})
        else:
            current = None
            content.append({"type": "paragraph", "content": _inline(line)})
    return {"type": "doc", "version": 1, "content": content or adf(["-"])["content"]}


class XrayBackend(TestManagementBackend):
    def __init__(self) -> None:
        self.base = normalize_url(os.environ["JIRA_URL"])
        self.project = os.environ["JIRA_PROJECT_KEY"]
        self._auth = (os.environ["JIRA_USER"], os.environ["JIRA_API_TOKEN"])
        self._client = (os.environ["XRAY_CLIENT_ID"], os.environ["XRAY_CLIENT_SECRET"])
        self._token: tuple[str, float] | None = None

    # ---------- HTTP ----------
    def _send(self, method: str, url: str, **kw) -> requests.Response:
        r = None
        for attempt in range(4):
            r = requests.request(method, url, timeout=60, **kw)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2**attempt)
                continue
            break
        return r

    def _jira(self, method: str, path: str, **kw) -> requests.Response:
        r = self._send(
            method,
            f"{self.base}/rest/api/3{path}",
            auth=self._auth,
            headers={"Accept": "application/json"},
            **kw,
        )
        if not r.ok:
            raise RuntimeError(f"Jira {method} {path} -> {r.status_code} {r.text[:300]}")
        return r

    def _xray_headers(self) -> dict:
        if not self._token or time.time() > self._token[1]:
            r = self._send(
                "POST",
                f"{XRAY}/authenticate",
                json={"client_id": self._client[0], "client_secret": self._client[1]},
            )
            if not r.ok:
                raise RuntimeError(f"Xray authenticate -> {r.status_code}")
            self._token = (r.json(), time.time() + 23 * 3600)
        return {"Authorization": f"Bearer {self._token[0]}"}

    def _graphql(self, query: str, variables: dict) -> dict:
        r = self._send(
            "POST",
            f"{XRAY}/graphql",
            json={"query": query, "variables": variables},
            headers=self._xray_headers(),
        )
        data = r.json()
        if not r.ok or data.get("errors"):
            raise RuntimeError(f"Xray GraphQL -> {r.status_code} {str(data)[:300]}")
        return data["data"]

    # ---------- recherche par label (ID externe) ----------
    def _find(self, issue_type: str, label: str) -> str | None:
        jql = f'project = "{self.project}" AND issuetype = "{issue_type}" AND labels = "{label}"'
        r = self._jira(
            "POST", "/search/jql", json={"jql": jql, "fields": ["key"], "maxResults": 5}
        )
        keys = [i["key"] for i in r.json().get("issues", [])]
        if len(keys) > 1:
            raise RuntimeError(f"doublon détecté pour {label} : {keys}")
        return keys[0] if keys else None

    # ---------- exigences (Stories) ----------
    def ensure_requirement(
        self, req_id: str, title: str, text: str, known_key: str | None = None
    ) -> str | None:
        key = known_key or self._find("Story", req_id)
        if key:
            self._jira("PUT", f"/issue/{key}", json={"fields": {"description": md_to_adf(text)}})
            return key
        if title.upper().startswith(req_id.upper()):
            title = title[len(req_id) :].lstrip(" :-–—") or req_id
        r = self._jira(
            "POST",
            "/issue",
            json={
                "fields": {
                    "project": {"key": self.project},
                    "issuetype": {"name": "Story"},
                    "summary": f"{req_id} : {title}"[:250],
                    "description": md_to_adf(text),
                    "labels": [req_id],
                }
            },
        )
        return r.json()["key"]

    def link_to_requirement(self, test_key: str, requirement_key: str) -> None:
        r = self._jira("GET", f"/issue/{test_key}", params={"fields": "issuelinks"})
        for lk in r.json()["fields"].get("issuelinks", []):
            if (
                lk["type"]["name"] == LINK_TYPE
                and lk.get("outwardIssue", {}).get("key") == requirement_key
            ):
                return
        self._jira(
            "POST",
            "/issueLink",
            json={
                "type": {"name": LINK_TYPE},
                "inwardIssue": {"key": test_key},
                "outwardIssue": {"key": requirement_key},
            },
        )

    # ---------- tests ----------
    @staticmethod
    def _summary(case: dict) -> str:
        return f"{case['id']} : {case['title']}"[:250]

    @staticmethod
    def _description(case: dict) -> dict:
        meta = (
            f"Type : {case.get('type', '-')} | Couche : {case.get('layer', '-')} "
            f"| Priorité : {case.get('priority', '-')}"
        )
        lines = [f"Exigence : {case['requirement_id']}", meta]
        pre = case.get("preconditions") or []
        if pre:
            lines.append("Préconditions :")
            lines += [f"- {p}" for p in pre]
        return adf(lines)

    def _set_fields(self, key: str, case: dict) -> None:
        self._jira(
            "PUT",
            f"/issue/{key}",
            json={
                "fields": {
                    "summary": self._summary(case),
                    "description": self._description(case),
                }
            },
        )

    def find_by_external_id(self, external_id: str) -> str | None:
        return self._find("Test", external_id)

    def create_test(self, case: dict) -> str:
        steps = [
            {"action": s["action"], "result": s.get("expected") or "-"} for s in case["steps"]
        ]
        data = self._graphql(
            CREATE_TEST,
            {
                "steps": steps,
                "jira": {
                    "fields": {
                        "summary": self._summary(case),
                        "project": {"key": self.project},
                        "labels": [case["id"], case["requirement_id"]],
                    }
                },
            },
        )
        key = data["createTest"]["test"]["jira"]["key"]
        self._set_fields(key, case)
        return key

    def update_test(self, key: str, case: dict) -> None:
        """Met à jour le titre et la description (pas les étapes)."""
        try:
            self._set_fields(key, case)
        except RuntimeError as e:
            raise RuntimeError(
                f"{e} (ticket supprimé ? retirez sa ligne de mapping.xray.json)"
            ) from e

    # ---------- résultats ----------
    def import_results(self, results: list[dict]) -> str:
        by_key: dict[str, dict] = {}
        for r in results:
            key, status = r.get("test_key"), r.get("status")
            if not key or status not in IMPORTABLE:
                continue
            entry = {"testKey": key, "status": IMPORTABLE[status]}
            if status == "KNOWN_DEFECT":
                entry["comment"] = r.get("reason") or r.get("defect") or "défaut connu"
            old = by_key.get(key)
            if old is None or RANK[entry["status"]] > RANK[old["status"]]:
                by_key[key] = entry
        if not by_key:
            raise RuntimeError(
                "aucun résultat rattachable à un test Xray "
                "(lancez d'abord make sync BACKEND=xray pour remplir mapping.xray.json)"
            )
        stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
        r = self._send(
            "POST",
            f"{XRAY}/import/execution",
            json={
                "info": {"summary": f"Exécution automatisée {stamp}", "project": self.project},
                "tests": list(by_key.values()),
            },
            headers=self._xray_headers(),
        )
        if not r.ok:
            raise RuntimeError(f"Xray import execution -> {r.status_code} {r.text[:300]}")
        body = r.json()
        return body.get("key") or str(body)[:100]

