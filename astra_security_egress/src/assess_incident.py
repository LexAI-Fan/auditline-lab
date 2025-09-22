import json, re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
outdir = ROOT / "out"

events = [json.loads(l) for l in (outdir/"egress.jsonl").read_text(encoding="utf-8").splitlines()]
alerts = json.loads((outdir/"alerts.json").read_text(encoding="utf-8"))

by_kind = Counter(a["kind"] for a in alerts)
by_host = Counter(e["host"] for e in events)

cfg_text = (ROOT/"src"/"config.yaml").read_text(encoding="utf-8")
m = re.search(r'canary_domains:\s*\[(.*?)\]', cfg_text, re.M)
canaries = [x.strip() for x in m.group(1).split(',')] if m else []

status = {
    "severity": "CRITICAL" if by_kind.get("CANARY_HIT", 0) > 0 else ("ELEVATED" if sum(by_kind.values())>0 else "NORMAL"),
    "reasons": (["Active CANARY_HIT detected."] if by_kind.get("CANARY_HIT",0)>0 else
                (["Anomalies detected without canary hits."] if sum(by_kind.values())>0 else ["No anomalies detected."])),
    "counts": {
        "alerts_total": sum(by_kind.values()),
        "by_kind": dict(by_kind),
        "top_canary_hits": {c: by_host.get(c, 0) for c in canaries},
    }
}

(outdir/"incident_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
print("Wrote", outdir/"incident_status.json")
