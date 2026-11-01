"""
Live Network Log Generator — simulates a firewall/SIEM log stream.
Run in a separate terminal:  python live_log_generator.py

Writes one log entry every 0.5-2 seconds to live_feed.csv.
Injects realistic attack patterns every 30-60 seconds.
"""
import csv
import time
import random
import os
from datetime import datetime

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "live_feed.csv")

# ── Realistic IP pools ─────────────────────────────────────────────────────────
INTERNAL_IPS = [f"192.168.1.{i}" for i in range(10, 60)]
INTERNAL_SERVERS = ["10.0.0.1", "10.0.0.5", "10.0.0.10", "10.0.0.20", "172.16.0.1"]
EXTERNAL_IPS = [
    "45.33.32.156", "104.21.45.12", "185.220.101.45", "198.51.100.22",
    "203.0.113.50",  "91.108.4.1",  "162.247.72.201", "176.10.104.240",
    "51.15.43.205",  "109.70.100.2","77.247.181.162", "66.220.155.140",
]
ATTACKER_IPS = [
    "185.220.101.45",   # known Tor exit node
    "91.108.4.1",       # suspicious Eastern European range
    "176.10.104.240",   # known threat actor range
]
SERVICES = {
    80:   "TCP",  443:  "TCP",  22:   "TCP",  3389: "TCP",
    21:   "TCP",  25:   "TCP",  53:   "UDP",  8080: "TCP",
    445:  "TCP",  1433: "TCP",  3306: "TCP",  5900: "TCP",
}
ACTIONS = ["ALLOW", "ALLOW", "ALLOW", "ALLOW", "DENY"]

# ── Normal traffic templates ───────────────────────────────────────────────────
def normal_event():
    src = random.choice(INTERNAL_IPS)
    dst = random.choice(INTERNAL_SERVERS + ["8.8.8.8", "1.1.1.1"] + EXTERNAL_IPS[:4])
    port = random.choice([80, 443, 53, 8080, 22])
    proto = SERVICES.get(port, "TCP")
    return {
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip":  src,
        "dest_ip":    dst,
        "dest_port":  port,
        "protocol":   proto,
        "bytes_sent": random.randint(200, 8000),
        "bytes_recv": random.randint(500, 20000),
        "action":     random.choices(ACTIONS, weights=[9,9,9,9,2])[0],
    }

# ── Attack patterns ────────────────────────────────────────────────────────────
def port_scan_burst(attacker_ip=None):
    """One IP hitting many ports rapidly — T1046 Network Service Discovery."""
    src = attacker_ip or random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_SERVERS)
    ports = random.sample(range(1, 65535), random.randint(60, 120))
    events = []
    for port in ports:
        events.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip":  src,
            "dest_ip":    target,
            "dest_port":  port,
            "protocol":   "TCP",
            "bytes_sent": random.randint(40, 60),
            "bytes_recv": 0,
            "action":     random.choices(["DENY", "ALLOW"], weights=[7, 3])[0],
        })
    return events

def brute_force_burst(attacker_ip=None):
    """Many failed login attempts — T1110.001 Password Guessing."""
    src = attacker_ip or random.choice(ATTACKER_IPS)
    target = random.choice(INTERNAL_SERVERS)
    port = random.choice([22, 3389, 21, 5900])
    events = []
    for _ in range(random.randint(50, 100)):
        events.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip":  src,
            "dest_ip":    target,
            "dest_port":  port,
            "protocol":   "TCP",
            "bytes_sent": random.randint(300, 600),
            "bytes_recv": random.randint(100, 300),
            "action":     random.choices(["DENY", "ALLOW"], weights=[8, 2])[0],
        })
    return events

def data_exfiltration_burst(internal_ip=None):
    """Large outbound data transfer — T1048.003 Exfiltration."""
    src = internal_ip or random.choice(INTERNAL_IPS)
    dst = random.choice(EXTERNAL_IPS[4:])  # unusual external
    events = []
    for _ in range(random.randint(5, 15)):
        events.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip":  src,
            "dest_ip":    dst,
            "dest_port":  random.choice([443, 8443, 4444, 9001]),
            "protocol":   "TCP",
            "bytes_sent": random.randint(5_000_000, 20_000_000),
            "bytes_recv": random.randint(1000, 5000),
            "action":     "ALLOW",
        })
    return events

def c2_beacon(internal_ip=None):
    """Regular beaconing to C2 server — T1071.001."""
    src = internal_ip or random.choice(INTERNAL_IPS)
    dst = random.choice(ATTACKER_IPS)
    events = []
    for _ in range(random.randint(8, 20)):
        events.append({
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip":  src,
            "dest_ip":    dst,
            "dest_port":  random.choice([4444, 1337, 8080, 9001]),
            "protocol":   "TCP",
            "bytes_sent": random.randint(200, 800),
            "bytes_recv": random.randint(100, 400),
            "action":     "ALLOW",
        })
    return events

ATTACK_SCENARIOS = [
    ("🔴 PORT SCAN",         port_scan_burst),
    ("🔴 BRUTE FORCE",       brute_force_burst),
    ("🔴 DATA EXFILTRATION", data_exfiltration_burst),
    ("🔴 C2 BEACON",         c2_beacon),
]

FIELDNAMES = ["timestamp","source_ip","dest_ip","dest_port","protocol",
              "bytes_sent","bytes_recv","action"]

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*55}")
    print("  LIVE NETWORK LOG GENERATOR")
    print(f"  Writing to: {OUTPUT_FILE}")
    print(f"  Press Ctrl+C to stop")
    print(f"{'='*55}\n")

    # Write header
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

    total_events = 0
    total_attacks = 0
    next_attack_at = time.time() + random.randint(15, 30)  # first attack in 15-30s

    try:
        while True:
            now = time.time()

            # ── Inject an attack ─────────────────────────────────────────────
            if now >= next_attack_at:
                attack_name, attack_fn = random.choice(ATTACK_SCENARIOS)
                attack_events = attack_fn()
                with open(OUTPUT_FILE, "a", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    for ev in attack_events:
                        writer.writerow(ev)
                total_attacks += 1
                total_events += len(attack_events)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {attack_name} "
                      f"injected ({len(attack_events)} events) — "
                      f"Total attacks: {total_attacks}")
                next_attack_at = now + random.randint(20, 45)  # next in 20-45s

            # ── Write normal events ──────────────────────────────────────────
            n_normal = random.randint(3, 8)
            with open(OUTPUT_FILE, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                for _ in range(n_normal):
                    writer.writerow(normal_event())
            total_events += n_normal

            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"+{n_normal} normal events  |  Total: {total_events:,}",
                  end="\r")

            time.sleep(random.uniform(0.5, 1.5))

    except KeyboardInterrupt:
        print(f"\n\n✅ Generator stopped. Total events written: {total_events:,}")
        print(f"   Attacks injected: {total_attacks}")
        print(f"   File: {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
