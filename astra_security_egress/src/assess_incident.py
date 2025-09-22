\
import json, re
from pathlib import Path
from collections import Counter

outdir = Path("out")
events = [json.loads(l) for l in (outdir/"egress.jsonl").read_text().splitlines()]
alerts = json.loads((outdir/"alerts.json").read_text())

by_kind = Counter(a["kind"] for a in alerts)
by_host = Counter(e["host"] for e in events)

cfg_text = Path("src/config.yaml").read_text()
m = re.search(r'canary_domains:\s*\[(.*?)\]', cfg_text, re.M)
canaries = [x.strip() for x in m.group(1).split(',')] if m else []

canary_hits = {c:0 for c in canaries}
for a in alerts:
    if a["kind"]=="CANARY_HIT":
        h = a["event"]["host"]
        for c in canaries:
            if h==c or h.endswith(c):
                canary_hits[c] = canary_hits.get(c,0)+1

def looks_random_label(host):
    label = host.split(".")[0]
    if len(label) < 10: return False
    uniq_ratio = len(set(label))/len(label)
    digit_ratio = sum(ch.isdigit() for ch in label)/len(label)
    return uniq_ratio > 0.6 and digit_ratio > 0.2

exfil_like = [h for h in by_host if looks_random_label(h) and (h.endswith(".zip") or h.endswith(".mov") or ".dl." in h or h.endswith(".dl.zip"))]
large_model_egress = sum(1 for a in alerts if a["kind"] in ("DATA_SPIKE","MODEL_INITIATED_EGRESS") and a["event"].get("model_initiated", False) and a["event"].get("size_kb",0) >= 512)

severity = "LOW"; reasons=[]
if sum(canary_hits.values()) > 0:
    severity = "CRITICAL"; reasons.append("Active CANARY_HIT detected.")
elif len(exfil_like) >= 3 and large_model_egress >= 3:
    severity = "CRITICAL"; reasons.append("Multiple exfil-like hosts and model-initiated large egress.")
elif len(exfil_like) >= 2 or large_model_egress >= 2:
    severity = "HIGH"; reasons.append("Exfil-like patterns or model-initiated large egress.")
elif any(h.endswith(t) for h in by_host for t in [".zip",".mov",".xyz",".top"]):
    severity = "MEDIUM"; reasons.append("Suspicious TLDs present.")

status = {
    "severity": severity,
    "reasons": reasons,
    "counts": {
        "alerts_total": sum(by_kind.values()),
        "by_kind": dict(by_kind),
        "top_canary_hits": canary_hits,
        "exfil_like_hosts": exfil_like[:10],
        "large_model_egress_events": large_model_egress
    }
}
(outdir/"incident_status.json").write_text(json.dumps(status, indent=2))
print("Wrote", outdir/"incident_status.json")
