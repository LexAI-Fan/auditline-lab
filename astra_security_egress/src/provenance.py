\
import json, hashlib, time
from pathlib import Path
outdir = Path("out"); outdir.mkdir(exist_ok=True)

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def append_event(stream_path: Path, event: dict):
    prev = ""
    if stream_path.exists():
        lines = stream_path.read_text().splitlines()
        if lines:
            last_obj = json.loads(lines[-1])
            prev = last_obj.get("_selfhash","")
    event["_ts"] = time.time()
    event["_prev"] = prev
    payload = json.dumps(event, sort_keys=True).encode("utf-8")
    event["_selfhash"] = sha256_bytes(payload)
    with stream_path.open("a") as f:
        f.write(json.dumps(event)+"\n")
    return event["_selfhash"]

if __name__ == "__main__":
    alerts = json.loads((outdir/"alerts.json").read_text())
    stream = outdir/"provenance.jsonl"
    append_event(stream, {"type":"START", "note":"begin incident provenance"})
    for a in alerts[:200]:
        append_event(stream, {"type":"ALERT", "kind":a["kind"], "at":a["event"]["ts"], "pid":a["event"]["pid"]})
    append_event(stream, {"type":"END", "count": len(alerts)})
    print("Wrote", stream)
