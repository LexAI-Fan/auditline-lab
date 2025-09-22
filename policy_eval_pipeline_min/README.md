# policy_eval_pipeline_min (fixed)

Minimal, reproducible scaffold for uncertainty-adaptive interface evaluation.

## What this shows
- Synthetic dataset with seeded-error trials and uncertainty signals.
- Risk–coverage analysis (AURC).
- Prereg-style analysis skeleton with clustered (by participant) SEs.
- Deterministic runs via seeds; artefact manifest.

## Quickstart
```bash
python simulate_data.py
python analysis_glmm.py
```
Outputs go to `out/`.
