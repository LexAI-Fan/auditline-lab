import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
import statsmodels.api as sm
import statsmodels.formula.api as smf

Path("out").mkdir(exist_ok=True)
df = pd.read_csv("out/synthetic_trials.csv")

# --- Risk–coverage (AURC) utility ---
def risk_coverage_auc(unc, y):
    taus = np.linspace(0,1,101)
    cover, risk = [], []
    for t in taus:
        mask = unc >= t
        if mask.sum() == 0:
            cov = 0.0; r = 0.0
        else:
            cov = mask.mean()
            r = y[mask].mean()
        cover.append(cov); risk.append(r)
    auc = np.trapz(risk, cover)
    return auc, taus, np.array(cover), np.array(risk)

# Participant-level AURC on seeded-error trials
se = df[df['seeded_error']==1].copy()
aurcs = []
for pid, g in se.groupby("participant"):
    auc, taus, cov, risk = risk_coverage_auc(g["uncertainty"].values, g["over_trust"].values)
    aurcs.append(dict(participant=pid, AURC=auc))
aurc_df = pd.DataFrame(aurcs)
aurc_df.to_csv("out/aurc_by_participant.csv", index=False)

plt.figure()
plt.hist(aurc_df["AURC"], bins=20)
plt.title("AURC distribution (participant-level)")
plt.xlabel("AURC"); plt.ylabel("Count")
plt.tight_layout(); plt.savefig("out/aurc_hist.png")

# --- Logistic regression (cluster-robust by participant) ---
se["technique"] = se["technique"].astype("category")
se["modality"]  = se["modality"].astype("category")
logit = smf.logit("over_trust ~ C(technique) + C(modality)", data=se).fit(disp=False)
rob   = logit.get_robustcov_results(cov_type="cluster", groups=se["participant"])
with open("out/overtrust_logit.txt","w") as f:
    f.write(str(rob.summary()))

# --- Recovery time: log-RT with participant FE (stand-in for mixed) ---
se["log_rt"] = np.log(se["recovery_time"])
fe = smf.ols("log_rt ~ C(technique) + C(modality) + C(participant)", data=se).fit()
with open("out/recovery_lm.txt","w") as f:
    f.write(str(fe.summary()))

print("Wrote AURC CSV + hist, overtrust_logit.txt, recovery_lm.txt to out/")
