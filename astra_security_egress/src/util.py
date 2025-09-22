from pathlib import Path
import re

def read_yaml_min(path):
    txt = Path(path).read_text(encoding="utf-8")
    def get_int(k, d):
        m = re.search(rf'^{k}:\s*([0-9]+)\s*$', txt, re.M)
        return int(m.group(1)) if m else d
    def get_float(k, d):
        m = re.search(rf'^{k}:\s*([0-9.]+)\s*$', txt, re.M)
        return float(m.group(1)) if m else d
    def get_list(k, d):
        m = re.search(rf'^{k}:\s*\[(.*?)\]\s*$', txt, re.M)
        if not m: return d
        return [x.strip() for x in m.group(1).split(',') if x.strip()]
    return {
        "seed": get_int("seed", 0),
        "participants": get_int("participants", 4),
        "duration_minutes": get_int("duration_minutes", 10),
        "events_per_minute_mean": get_int("events_per_minute_mean", 20),
        "canary_domains": get_list("canary_domains", []),
        "suspicious_tlds": get_list("suspicious_tlds", []),
        "entropy_threshold": get_float("entropy_threshold", 3.3),
        "rare_domain_threshold": get_float("rare_domain_threshold", 0.01),
        "data_spike_threshold_kb": get_int("data_spike_threshold_kb", 512),
        "model_initiated_rate": get_float("model_initiated_rate", 0.1),
        "exfil_burst_probability": get_float("exfil_burst_probability", 0.05),
        "exfil_burst_size_mean": get_int("exfil_burst_size_mean", 30),
        "time_jitter_ms": get_int("time_jitter_ms", 100),
    }

