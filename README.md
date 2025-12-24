# auditline-lab


```md
# auditline-lab

Evidence-driven ML audits and lineage tooling:
- egress simulation / detection
- memorization & privacy-leakage audits
- a reproducible graph fairness mini-study
- governance-ready artefacts (model/risk cards, DPIA helpers)

**Python 3.11**. No external secrets committed.

---

## What this repository is for

This repo collects small, auditable utilities that support **model accountability**:
1) run targeted audits (privacy/memorization/egress-style checks),
2) generate artefacts that can be attached to a review package (risk notes, audit logs),
3) preserve provenance/lineage so results can be traced and reproduced.

It is intentionally modular: each audit can run independently and produce a structured output file.

---

## Key components

- **Audit utilities**
  - Egress-style simulation/detection helpers (controlled experiments)
  - Memorization / leakage checks (e.g., canary-style probing, exposure-style summaries)
  - (Optional) graph fairness mini-study scaffold (utility + fairness gaps)

- **Lineage & logging**
  - Signed/hashed run logs (to make “what ran” tamper-evident)
  - Run metadata capture (config, environment, timestamps)

- **Governance artefacts**
  - Lightweight templates for model cards / risk cards
  - DPIA helper checklist scaffolds (project-facing, not legal advice)

> Note: This repo focuses on reproducible engineering patterns. Domain-specific policy interpretation should be done with appropriate oversight.

---

## Quick start

### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt


