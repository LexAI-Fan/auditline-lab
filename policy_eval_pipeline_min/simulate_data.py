import numpy as np, pandas as pd, re
from pathlib import Path

# --- Minimal YAML reader (only reads simple scalars and lists) ---
def read_yaml_min(path):
    txt = Path(path).read_text()
    def get_list(key, default):
        m = re.search(rf'^{key}:\s*\[(.*?)\]\s*$', txt, re.M)
        if not m: return default
        return [x.strip() for x in m.group(1).split(',') if x.strip()]
    def get_float(key, default):
        m = re.search(rf'^{key}:\s*([0-9.]+)\s*$', txt, re.M)
        return float(m.group(1)) if m else default
    def get_int(key, default):
        m = re.search(rf'^{key}:\s*([0-9]+)\s*$', txt, re.M)
        return int(m.group(1)) if m else default
    cfg = {
        "seed": get_int("seed", 1337),
        "conditions": get_list("conditions", ["T0","T1","T2"]),
        "modalities": get_list("modalities", ["Visual","Auditory","Haptic"]),
        "seeded_error_rate": get_float("seeded_error_rate", 0.15),
        "participants": get_int("participants", 36),
        "steps_per_participant": get_int("steps_per_participant", 48),
    }
    return cfg

cfg = read_yaml_min("protocol.yaml")
np.random.seed(cfg["seed"])

rows = []
for pid in range(cfg["participants"]):
    tech = np.random.choice(cfg["conditions"])  # between-subjects assignment
    for s in range(cfg["steps_per_participant"]):
        mod = np.random.choice(cfg["modalities"])
        seeded_error = np.random.rand() < cfg["seeded_error_rate"]
        # Uncertainty signal ~ Beta(2,5): mostly low with spikes
        unc = float(np.clip(np.random.beta(2,5), 0, 1))
        # Over-trust baseline probability on seeded-error trials
        p = 0.35 if seeded_error else 0.0
        if tech == "T1": p *= 0.80          # ACW marginal improvement
        elif tech == "T2": p *= 0.65        # ACW+PoD incremental
        if mod == "Haptic" and seeded_error: p *= 0.90
        over_trust = int(seeded_error and (np.random.rand() < p))
        # Recovery time (seconds), log-normal-ish
        mu = 2.2   # ~9s
        if tech == "T1": mu -= 0.06
        if tech == "T2": mu -= 0.18
        if mod == "Haptic": mu -= 0.04
        rt = float(np.exp(np.random.normal(mu, 0.35)))
        rows.append(dict(
            participant=pid, step=s, technique=tech, modality=mod,
            seeded_error=int(seeded_error), uncertainty=unc,
            over_trust=over_trust, recovery_time=rt
        ))

df = pd.DataFrame(rows)
Path("out").mkdir(exist_ok=True)
df.to_csv("out/synthetic_trials.csv", index=False)
print("Wrote out/synthetic_trials.csv with", len(df), "rows")
