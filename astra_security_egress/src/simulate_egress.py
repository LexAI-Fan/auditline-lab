\
import json, random, string
from pathlib import Path
from datetime import datetime, timedelta
from util import read_yaml_min

cfg = read_yaml_min("src/config.yaml")
random.seed(cfg["seed"])

outdir = Path("out"); outdir.mkdir(exist_ok=True)
egress_path = outdir / "egress.jsonl"

BASE = datetime(2025, 9, 20, 12, 0, 0)
T = cfg["duration_minutes"] * 60
rate = cfg["events_per_minute_mean"] / 60.0
participants = [f"p{i}" for i in range(cfg["participants"])]

popular_domains = [
    "docs.example.com","storage.example.net","updates.corp.example",
    "news.example.org","api.service.example","assets.cdn.example"
]

def rand_domain():
    import math
    from collections import Counter
    if random.random() < 0.15:
        token = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(random.randint(10,20)))
        base = random.choice(["data","cdn","cdn2","files"])
        tld = random.choice([".com",".net",".org",".zip",".mov",".top",".xyz"])
        host = f"{token}.{base}{tld}"
        c = Counter(token)
        ent = -sum((v/len(token))*math.log2(v/len(token)) for v in c.values())
        return host, round(ent,3)
    else:
        return random.choice(popular_domains), 1.5

def rand_event(t0, pid):
    dt = random.expovariate(rate)
    t = t0 + timedelta(seconds=dt) + timedelta(milliseconds=random.randint(0, cfg["time_jitter_ms"]))
    method = random.choice(["DNS","HTTPS"])
    host, ent = rand_domain()
    size_kb = max(1, int(random.gauss(32, 24)))
    model_initiated = random.random() < cfg["model_initiated_rate"]
    return t, dict(ts=t.isoformat(), pid=pid, method=method, host=host, size_kb=size_kb, ent=ent,
                   model_initiated=model_initiated)

evs=[]
cur = BASE
for pid in participants:
    t = cur
    while (t - cur).total_seconds() < T:
        t, ev = rand_event(t, pid)
        if random.random() < 0.01 and cfg["canary_domains"]:
            ev["host"] = random.choice(cfg["canary_domains"])
            ev["ent"] = 1.2
        evs.append(ev)

for _ in range(max(1, cfg["participants"]//3)):
    if random.random() < cfg["exfil_burst_probability"]:
        pid = random.choice(participants)
        t = BASE + timedelta(seconds=random.randint(0, T-60))
        n = max(5, int(random.gauss(cfg["exfil_burst_size_mean"], 8)))
        for i in range(n):
            t += timedelta(seconds=random.uniform(0.5, 2.0))
            host = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(16)) + ".dl.zip"
            ev = dict(ts=t.isoformat(), pid=pid, method="HTTPS", host=host,
                      size_kb=int(abs(random.gauss(900, 150))), ent=3.8, model_initiated=True)
            evs.append(ev)

evs.sort(key=lambda e: e["ts"])
with egress_path.open("w") as f:
    for ev in evs:
        f.write(json.dumps(ev)+"\n")
print("Wrote", egress_path)
