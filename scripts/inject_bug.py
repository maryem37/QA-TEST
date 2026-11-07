"""Injecte un bug connu dans l'application sous test (utilisé par bug-injection.yml)."""

import sys
from pathlib import Path

ROOT = Path("app/restful-booker-platform/room/src/main/java/com/automationintesting")

BUGS = {
    "bug-000": {
        "file": ROOT / "api" / "RoomController.java",
        "old": b"return ResponseEntity.status(HttpStatus.OK).body(rooms);",
        "new": b"return ResponseEntity.status(HttpStatus.ACCEPTED).body(rooms);",
        "description": "GET /room renvoie 202 au lieu de 200 (masqué par la passerelle)",
    },
    "bug-001": {
        "file": ROOT / "service" / "RoomService.java",
        "old": b"return new Rooms(roomDB.queryRooms());",
        "new": b"return new Rooms(roomDB.queryRooms().subList(0, 0));",
        "description": "GET /api/room renvoie une liste de chambres vide",
    },
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in BUGS:
        raise SystemExit("usage : inject_bug.py " + "|".join(BUGS))
    bug = BUGS[sys.argv[1]]
    path = bug["file"]
    data = path.read_bytes()
    found = data.count(bug["old"])
    if found != 1:
        raise SystemExit(f"motif trouvé {found} fois dans {path}, attendu 1")
    path.write_bytes(data.replace(bug["old"], bug["new"]))
    print(f"Bug injecté ({sys.argv[1]}) : {bug['description']}")


if __name__ == "__main__":
    main()
