import sys
import xml.etree.ElementTree as ET

def statuses(path):
    out = {}
    for t in ET.parse(path).getroot().iter("testcase"):
        s = "FAILED" if t.find("failure") is not None or t.find("error") is not None else (
            "SKIPPED" if t.find("skipped") is not None else "PASSED")
        out[f"{t.get('classname')}::{t.get('name')}"] = s
    return out

a, b = statuses(sys.argv[1]), statuses(sys.argv[2])
diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if a.get(k) != b.get(k)}
print(f"{len(a)} tests (A) / {len(b)} tests (B), différences : {len(diff)}")
for k, v in sorted(diff.items()):
    print(" ", k, v)
sys.exit(1 if diff else 0)
