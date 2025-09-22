import json, hashlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
outdir = ROOT / "out"; outdir.mkdir(exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def append_event(stream_path: Path, event: dict):
    prev = ""
    if stream_path.exists():
        lines = stream_path.read_text(encoding="utf-8").splitlines()
        if lines:
            last_obj = json.loads(lines[-1])
            prev = last_obj.get("_selfhash","")
    event["_ts"] = time.time()
    event["_prevhash"] = prev
    payload = json.dumps(event, sort_keys=True).encode("utf-8")
    event["_selfhash"] = sha256_bytes(payload)
    with stream_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event)+"\n")
    return event["_selfhash"]

if __name__ == "__main__":
    alerts_path = outdir / "alerts.json"
    if not alerts_path.exists():
        raise SystemExit(f"Missing {alerts_path}. Run simulate_egress.py and detect_exfil.py first.")
    alerts = json.loads(alerts_path.read_text(encoding="utf-8"))
    stream = outdir/"provenance.jsonl"
    append_event(stream, {"type":"START", "note":"begin incident provenance"})
    for a in alerts[:200]:
        append_event(stream, {"type":"ALERT", "kind":a["kind"], "at":a["event"]["ts"], "pid":a["event"]["pid"]})
    append_event(stream, {"type":"END", "count": len(alerts)})
    print("Wrote", stream)

