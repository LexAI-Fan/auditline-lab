# Security — Egress Simulation & Detector Heuristics (Research Sample)

A **research-oriented** sample for studying egress anomalies and canary detections.
Generates synthetic egress, runs simple detectors, chains **decision-provenance**, and builds a signed **incident packet**.

**No operational PDF is included**. Use JSON outputs to integrate with your own evaluation.

## Quickstart
```bash
python src/simulate_egress.py
python src/detect_exfil.py
python src/provenance.py
python src/build_incident_packet.py
python src/assess_incident.py   # writes JSON status only
```

Outputs (`out/`):
- `egress.jsonl` – synthetic traffic
- `alerts.json` – detections
- `provenance.jsonl` – append-only hash chain
- `incident_packet.json` – HMAC-signed packet
- `incident_status.json` – severity & reasons (JSON)

Research angles: detection precision/recall, canary tripwire performance, exfil-like host heuristics.
