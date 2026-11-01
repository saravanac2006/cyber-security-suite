import io
import json
import re
from datetime import datetime

import pandas as pd
import numpy as np


REQUIRED_COLS = [
    "timestamp", "source_ip", "dest_ip", "source_port", "dest_port",
    "protocol", "bytes_sent", "bytes_recv", "duration", "action",
    "user", "event_type", "anomaly_type",
]

_COL_ALIASES = {
    "src_ip": "source_ip", "src": "source_ip", "srcip": "source_ip",
    "dst_ip": "dest_ip", "dst": "dest_ip", "dstip": "dest_ip", "destination_ip": "dest_ip",
    "sport": "source_port", "src_port": "source_port",
    "dport": "dest_port", "dst_port": "dest_port", "destination_port": "dest_port",
    "proto": "protocol",
    "sent": "bytes_sent", "out_bytes": "bytes_sent",
    "recv": "bytes_recv", "received": "bytes_recv", "in_bytes": "bytes_recv",
    "time": "timestamp", "date": "timestamp", "datetime": "timestamp",
    "username": "user", "uid": "user",
    "type": "event_type",
}


class LogParser:
    def parse_csv(self, file_obj) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_obj)
        except Exception:
            file_obj.seek(0)
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            df = pd.read_csv(io.StringIO(content))
        return self.normalize(df)

    def parse_json(self, file_obj) -> pd.DataFrame:
        try:
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            data = json.loads(content)
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try common wrappers
                for key in ("logs", "events", "records", "data"):
                    if key in data:
                        df = pd.DataFrame(data[key])
                        break
                else:
                    df = pd.DataFrame([data])
        except Exception as exc:
            raise ValueError(f"Could not parse JSON: {exc}")
        return self.normalize(df)

    def parse_text(self, file_obj) -> pd.DataFrame:
        """Parse common syslog/firewall text formats."""
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")

        records = []
        syslog_re = re.compile(
            r"(?P<timestamp>\w{3}\s+\d+\s+[\d:]+)\s+(?P<source_ip>[\d.]+).*?"
            r"(?:port\s+(?P<dest_port>\d+)|DPT=(?P<dest_port2>\d+))",
            re.IGNORECASE,
        )
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            m = syslog_re.search(line)
            rec = {
                "timestamp": datetime.now(),
                "source_ip": "0.0.0.0",
                "dest_ip": "0.0.0.0",
                "source_port": 0,
                "dest_port": 0,
                "protocol": "TCP",
                "bytes_sent": 0,
                "bytes_recv": 0,
                "duration": 0.0,
                "action": "ALLOW",
                "user": "unknown",
                "event_type": "syslog",
                "anomaly_type": "normal",
                "_raw": line,
            }
            if m:
                rec["source_ip"] = m.group("source_ip") or "0.0.0.0"
                port = m.group("dest_port") or m.group("dest_port2")
                rec["dest_port"] = int(port) if port else 0
                try:
                    rec["timestamp"] = pd.to_datetime(m.group("timestamp"))
                except Exception:
                    pass
            records.append(rec)

        if not records:
            raise ValueError("No parseable lines found in text log.")
        df = pd.DataFrame(records)
        df.pop("_raw", None)
        return self.normalize(df)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        df.rename(columns=_COL_ALIASES, inplace=True)

        # Ensure required columns exist with defaults
        defaults = {
            "timestamp": datetime.now(),
            "source_ip": "0.0.0.0",
            "dest_ip": "0.0.0.0",
            "source_port": 0,
            "dest_port": 0,
            "protocol": "TCP",
            "bytes_sent": 0,
            "bytes_recv": 0,
            "duration": 0.0,
            "action": "ALLOW",
            "user": "unknown",
            "event_type": "network",
            "anomaly_type": "normal",
        }
        for col, default in defaults.items():
            if col not in df.columns:
                df[col] = default

        # Type coercions
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").fillna(pd.Timestamp.now())
        for col in ("source_port", "dest_port"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        for col in ("bytes_sent", "bytes_recv"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0.0)
        df["protocol"] = df["protocol"].astype(str).str.upper()
        df["action"] = df["action"].astype(str).str.upper()

        return df[REQUIRED_COLS]
