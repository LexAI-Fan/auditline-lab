import json
from pathlib import Path
from collections import Counter
from util import read_yaml_min

ROOT = Path(__file__).resolve().parents[1]
cfg = read_yaml_min(str(ROOT / "src" / "config.yaml"))
outdir = ROOT / "out"

egress_path = outdir / "egress.jsonl"
if not egress_path.exists():
    raise SystemExit(f"Missing {egress_path}. Run simulate_egress.py first.")

events = [json.loads(l) for l in egress_path.read_text(encoding="utf-8").splitlines()]
hosts = [e["host"] for e in events]
host_counts = Counter(hosts)
N = max(1, len(events))

alerts = []
def add_alert(kind, ev, info):
    alerts.append({"kind": kind, "event": ev, "info": info})

# Canary domains
for ev in events:
    if any(ev["host"].endswith(cd) or ev["host"] == cd for cd in cfg["canary_domains"]):
        add_alert("CANARY_HIT", ev, {"matched": ev["host"]})

# Rare domains
for ev in events:
    freq = host_counts[ev["host"]] / N
    if freq < cfg["rare_domain_threshold"]:
        add_alert("RARE_DOMAIN", ev, {"freq": round(freq, 6)})

# Suspicious TLDs / entropy
for ev in events:
    if ev.get("ent", 0) >= cfg["entropy_threshold"] or any(ev["host"].endswith(t) for t in cfg["suspicious_tlds"]):
        add_alert("SUSPICIOUS_HOST", ev, {"ent": ev.get("ent", 0)})

# Data spikes
for ev in events:
    if ev.get("size_kb", 0) >= cfg["data_spike_threshold_kb"]:
        add_alert("DATA_SPIKE", ev, {"size_kb": ev["size_kb"]})

# Model-initiated + file-like host
for ev in events:
    if ev.get("model_initiated", False) and (ev["host"].endswith(".zip") or ev["host"].endswith(".mov")):
        add_alert("MODEL_INITIATED_EGRESS", ev, {"host": ev["host"]})

(outdir/"alerts.json").write_text(json.dumps(alerts, indent=2), encoding="utf-8")
print("Wrote", outdir/"alerts.json", "with", len(alerts), "alerts.")
