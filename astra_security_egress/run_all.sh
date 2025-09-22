#!/usr/bin/env bash
set -euo pipefail
mkdir -p out
python src/simulate_egress.py
python src/detect_exfil.py
python src/provenance.py
python src/build_incident_packet.py
python src/assess_incident.py
echo "Done. See ./out"
