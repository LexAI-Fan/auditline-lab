# auditline-lab

A small collection of audit utilities and lineage/logging helpers for ML accountability.

Python: 3.11
Policy: no secrets committed, no private data included

## What this repository is for

This repo focuses on two things:
1) run targeted audits (privacy leakage / memorization signals / egress-style checks)
2) record what ran (config, environment, hashes, outputs) so results are traceable

The goal is practical: one command produces one artifact bundle that is easy to review.

## Included modules (high level)

- audits
  - egress simulation and detection helpers
  - memorization and privacy-leakage checks
  - optional: a small graph fairness mini-study scaffold

- lineage and logging
  - capture run metadata (time, seed, package versions, git commit)
  - compute hashes for inputs and outputs
  - optional: sign logs if a signing key is provided locally

- governance artifacts
  - lightweight templates for model card, risk notes, DPIA checklist
  - these are scaffolds for review packages, not legal advice

## Quick start

### 1) Install
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

### 2) Run an example
Replace the command below with the actual entrypoint you provide.

python -m auditline.examples.run_egress_demo --config configs/egress_demo.yaml

### 3) Outputs

Each run writes to a timestamped directory under:
artefacts/

Typical contents:
- report.json
- run_meta.json
- run_log.txt
- hashes.json
- optional: signature.txt

## Repository layout

auditline/
  audits/
  lineage/
  templates/
examples/
configs/
artefacts/   (gitignored)
docs/

## Threat model notes (short)

- These tools provide diagnostic signals, not security guarantees.
- Results depend on model access (black-box vs white-box), dataset, and evaluation design.
- Each run report should state the assumed access level and data scope.

## Security and privacy notes

- Do not run audits on sensitive data without authorization.
- Do not commit secrets. Use environment variables or local config that is excluded by .gitignore.

## License

Choose one: MIT or Apache-2.0

