import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_sample_logs(n_normal: int = 500, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)

    base_time = datetime.now() - timedelta(hours=24)

    normal_src = [f"192.168.1.{i}" for i in range(1, 25)]
    normal_dst = (
        [f"10.0.0.{i}" for i in range(1, 15)]
        + ["8.8.8.8", "8.8.4.4", "1.1.1.1", "172.217.14.228", "151.101.1.140"]
    )
    common_ports = [80, 443, 53, 22, 3389, 445, 139, 3306, 8080, 25, 587]
    protocols = ["TCP", "UDP", "ICMP"]
    users = ["admin", "jsmith", "mjohnson", "alee", "system", "service_acct", "dbuser"]
    event_types = ["connection", "authentication", "file_access", "network", "dns"]

    records = []

    # ── Normal traffic ──────────────────────────────────────────────────────────
    for _ in range(n_normal):
        ts = base_time + timedelta(seconds=random.randint(0, 86400))
        records.append(
            {
                "timestamp": ts,
                "source_ip": random.choice(normal_src),
                "dest_ip": random.choice(normal_dst),
                "source_port": random.randint(1024, 65535),
                "dest_port": random.choice(common_ports),
                "protocol": random.choice(protocols),
                "bytes_sent": int(np.random.exponential(4000)) + 100,
                "bytes_recv": int(np.random.exponential(12000)) + 200,
                "duration": round(abs(np.random.normal(2.0, 1.5)), 3) + 0.01,
                "action": np.random.choice(["ALLOW", "DENY"], p=[0.95, 0.05]),
                "user": random.choice(users),
                "event_type": random.choice(event_types),
                "anomaly_type": "normal",
            }
        )

    # ── Port scan ───────────────────────────────────────────────────────────────
    scanner_ip = "192.168.1.200"
    scan_time = base_time + timedelta(hours=random.randint(2, 5))
    scanned_ports = random.sample(range(1, 65535), 20)
    for port in scanned_ports:
        records.append(
            {
                "timestamp": scan_time + timedelta(seconds=random.uniform(0, 30)),
                "source_ip": scanner_ip,
                "dest_ip": "10.0.0.5",
                "source_port": random.randint(1024, 65535),
                "dest_port": port,
                "protocol": "TCP",
                "bytes_sent": 60,
                "bytes_recv": 0,
                "duration": 0.001,
                "action": "DENY",
                "user": "unknown",
                "event_type": "connection",
                "anomaly_type": "port_scan",
            }
        )

    # ── Brute force ─────────────────────────────────────────────────────────────
    bf_ip = "203.0.113.42"
    bf_time = base_time + timedelta(hours=random.randint(6, 10))
    for _ in range(18):
        records.append(
            {
                "timestamp": bf_time + timedelta(seconds=random.uniform(0, 90)),
                "source_ip": bf_ip,
                "dest_ip": "192.168.1.10",
                "source_port": random.randint(1024, 65535),
                "dest_port": random.choice([22, 3389]),
                "protocol": "TCP",
                "bytes_sent": random.randint(200, 600),
                "bytes_recv": random.randint(100, 400),
                "duration": round(random.uniform(0.1, 0.8), 3),
                "action": "DENY",
                "user": random.choice(["root", "admin", "user", "test", "guest"]),
                "event_type": "authentication",
                "anomaly_type": "brute_force",
            }
        )

    # ── Data exfiltration ───────────────────────────────────────────────────────
    exfil_time = base_time + timedelta(hours=random.randint(14, 20))
    for _ in range(12):
        records.append(
            {
                "timestamp": exfil_time + timedelta(minutes=random.randint(0, 40)),
                "source_ip": "192.168.1.15",
                "dest_ip": "185.220.101.45",
                "source_port": random.randint(1024, 65535),
                "dest_port": random.choice([443, 8443, 4444, 9001]),
                "protocol": "TCP",
                "bytes_sent": random.randint(5_000_000, 80_000_000),
                "bytes_recv": random.randint(500, 3000),
                "duration": round(random.uniform(15, 90), 3),
                "action": "ALLOW",
                "user": "jsmith",
                "event_type": "network",
                "anomaly_type": "data_exfiltration",
            }
        )

    # ── C2 beaconing ────────────────────────────────────────────────────────────
    c2_time = base_time + timedelta(hours=random.randint(10, 14))
    for i in range(12):
        records.append(
            {
                "timestamp": c2_time + timedelta(minutes=i * 10 + random.randint(-1, 1)),
                "source_ip": "192.168.1.22",
                "dest_ip": "198.51.100.99",
                "source_port": random.randint(1024, 65535),
                "dest_port": random.choice([4444, 5555, 6666, 8888, 1337]),
                "protocol": "TCP",
                "bytes_sent": random.randint(80, 400),
                "bytes_recv": random.randint(80, 400),
                "duration": round(random.uniform(0.3, 3.0), 3),
                "action": "ALLOW",
                "user": "system",
                "event_type": "network",
                "anomaly_type": "c2_communication",
            }
        )

    df = pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
