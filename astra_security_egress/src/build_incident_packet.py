
import os, json, hmac, hashlib, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
outdir = ROOT / "out"; outdir.mkdir(exist_ok=True)

alerts_path = outdir / "alerts.json"
prov_path   = outdir / "provenance.jsonl"
if not alerts_path.exists():
    raise SystemExit(f"Missing {alerts_path}\nRun: python {ROOT/'src'/'detect_exfil.py'}")
if not prov_path.exists():
    raise SystemExit(f"Missing {prov_path}\nRun: python {ROOT/'src'/'provenance.py'}")

alerts = json.loads(alerts_path.read_text(encoding="utf-8"))
prov_lines = prov_path.read_text(encoding="utf-8").splitlines()

meta = {
    "schema": "incident_packet.v0",
    "generated_at": time.time(),
    "components": {
        "simulator": "src/simulate_egress.py",
        "detector":  "src/detect_exfil.py",
        "provenance":"src/provenance.py"
    },
    "counts": {"alerts": len(alerts), "provenance_events": len(prov_lines)},
    "paths": {"egress":"out/egress.jsonl","alerts":"out/alerts.json","provenance":"out/provenance.jsonl"},
}

packet = {
    "meta": meta,
    "alerts_sample": alerts[:50],
    "provenance_tail": prov_lines[-20:],
    "evidence": meta["paths"]
}

key = os.environ.get("INCIDENT_HMAC_KEY")
if key is None:
    key_path = ROOT / "secret.key"
    if not key_path.exists():
        key_path.write_text("dev-secret-key-change-me", encoding="utf-8")
    key = key_path.read_text(encoding="utf-8")
key_bytes = key.encode("utf-8")
sig = hmac.new(key_bytes, json.dumps(packet, sort_keys=True).encode("utf-8"), hashlib.sha256).hexdigest()
packet["signature"] = {"alg":"HMAC-SHA256", "sig": sig}

(outdir/"incident_packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")
print("Wrote", outdir/"incident_packet.json")
