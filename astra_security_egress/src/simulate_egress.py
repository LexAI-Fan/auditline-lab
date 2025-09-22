
import json, random, string, argparse
from pathlib import Path
from datetime import datetime, timedelta
from util import read_yaml_min

ROOT = Path(__file__).resolve().parents[1]
cfg = read_yaml_min(str(ROOT / "src" / "config.yaml"))

parser = argparse.ArgumentParser()
parser.add_argument("--scale", type=float, default=1.0, help="Multiply total events by this factor")
parser.add_argument("--duration", type=int, default=cfg["duration_minutes"], help="Override duration_minutes")
parser.add_argument("--rate", type=float, default=cfg["events_per_minute_mean"], help="Override events_per_minute_mean")
parser.add_argument("--participants", type=int, default=cfg["participants"], help="Override participants")
parser.add_argument("--seed", type=int, default=cfg["seed"], help="Override seed")
args = parser.parse_args()

random.seed(args.seed)
outdir = ROOT / "out"; outdir.mkdir(exist_ok=True)
egress_path = outdir / "egress.jsonl"

BASE = datetime(2025, 9, 20, 12, 0, 0)
T = args.duration * 60
rate = (args.rate / 60.0) * max(0.1, args.scale)
participants = [f"p{i}" for i in range(max(1, args.participants))]

evs = []
for pid in participants:
    n = max(1, int(T * rate))
    for _ in range(n):
        t = BASE + timedelta(seconds=int(random.uniform(0, T)))
        host = f"api-{random.randint(10,99)}.example.com"
        size_kb = max(1, int(abs(random.gauss(60, 20))))
        ent = round(abs(random.gauss(2.5, 0.6)), 2)
        model_initiated = random.random() < cfg["model_initiated_rate"]
        evs.append(dict(ts=t.isoformat(), pid=pid, method="HTTPS", host=host,
                        size_kb=size_kb, ent=ent, model_initiated=model_initiated))
    # occasional exfil burst
    if random.random() < cfg["exfil_burst_probability"]:
        t = BASE + timedelta(seconds=random.randint(0, max(1, T-60)))
        n = max(5, int(random.gauss(cfg["exfil_burst_size_mean"] * args.scale, 8)))
        for _ in range(n):
            t += timedelta(seconds=random.uniform(0.5, 2.0))
            host = ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(16)) + random.choice([".dl.zip",".cdn2.mov",".files.zip"])
            evs.append(dict(ts=t.isoformat(), pid=pid, method="HTTPS", host=host,
                            size_kb=int(abs(random.gauss(900, 150))), ent=3.8, model_initiated=True))

evs.sort(key=lambda e: e["ts"])
with egress_path.open("w", encoding="utf-8") as f:
    for ev in evs:
        f.write(json.dumps(ev)+"\n")
print("Wrote", egress_path, "events:", len(evs))
