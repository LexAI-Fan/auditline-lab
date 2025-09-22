\
import os, json, hmac, hashlib, time
from pathlib import Path
outdir = Path("out"); outdir.mkdir(exist_ok=True)

alerts = json.loads((outdir/"alerts.json").read_text())
prov_lines = (outdir/"provenance.jsonl").read_text().splitlines()

meta = {
    "schema": "incident_packet.v0",
    "generated_at": time.time(),
    "components": {
        "simulator": "src/simulate_egress.py",
        "detector": "src/detect_exfil.py",
        "provenance": "src/provenance.py"
    },
    "counts": {"alerts": len(alerts), "provenance_events": len(prov_lines)}
}

packet = {
    "meta": meta,
    "alerts_sample": alerts[:50],
    "provenance_tail": prov_lines[-20:],
    "evidence": {
        "egress_log": "out/egress.jsonl",
        "alerts": "out/alerts.json",
        "provenance": "out/provenance.jsonl"
    }
}

key_path = Path("secret.key")
if not key_path.exists():
    key_path.write_text("dev-secret-key-change-me")
key = key_path.read_text().encode("utf-8")
sig = hmac.new(key, json.dumps(packet, sort_keys=True).encode("utf-8"), hashlib.sha256).hexdigest()
packet["signature"] = {"alg":"HMAC-SHA256", "sig": sig}

(outdir/"incident_packet.json").write_text(json.dumps(packet, indent=2))
print("Wrote", outdir/"incident_packet.json")
