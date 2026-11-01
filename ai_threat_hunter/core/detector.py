import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder


class ThreatDetector:
    def __init__(self, sensitivity: float = 0.1):
        # contamination = fraction of outliers; sensitivity slider 1-10 maps here
        self.contamination = max(0.01, min(0.5, sensitivity))
        self._protocol_enc = LabelEncoder()
        self._action_enc = LabelEncoder()
        self._model = IsolationForest(
            contamination=self.contamination,
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )

    # ── Public ──────────────────────────────────────────────────────────────────

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        features = self._engineer_features(df)
        raw_scores = self._model.fit_predict(features)
        anomaly_scores = self._model.decision_function(features)

        df["is_anomaly"] = raw_scores == -1
        df["risk_score"] = self._normalise_scores(anomaly_scores)
        df["anomaly_label"] = self._classify_anomaly(df)
        return df

    def get_threat_stats(self, df: pd.DataFrame) -> dict:
        threats = df[df["is_anomaly"]]
        return {
            "total_events": len(df),
            "threats_detected": int(df["is_anomaly"].sum()),
            "detection_rate": round(df["is_anomaly"].mean() * 100, 2),
            "max_risk_score": int(df["risk_score"].max()),
            "avg_risk_score": round(df["risk_score"].mean(), 1),
            "threat_types": threats["anomaly_label"].value_counts().to_dict(),
            "top_source_ips": (
                threats.groupby("source_ip").size().sort_values(ascending=False).head(5).to_dict()
            ),
        }

    # ── Private ─────────────────────────────────────────────────────────────────

    def _engineer_features(self, df: pd.DataFrame) -> np.ndarray:
        protocols = df["protocol"].fillna("UNKNOWN")
        actions   = df["action"].fillna("ALLOW")

        self._protocol_enc.fit(protocols)
        self._action_enc.fit(actions)

        # Connection rate and unique dest ports per source IP
        conn_rate    = df.groupby("source_ip")["source_ip"].transform("count")
        unique_ports = df.groupby("source_ip")["dest_port"].transform("nunique")

        bytes_sent = np.log1p(df["bytes_sent"].clip(0))
        bytes_recv = np.log1p(df["bytes_recv"].clip(0))
        ratio      = np.log1p(df["bytes_sent"] / (df["bytes_recv"] + 1))

        # Optional columns — fill with 0 if not present in the log file
        duration    = np.log1p(df["duration"].clip(0))    if "duration"    in df.columns else np.zeros(len(df))
        source_port = df["source_port"].fillna(0)          if "source_port" in df.columns else np.zeros(len(df))
        dest_port   = df["dest_port"].fillna(0)

        X = np.column_stack([
            bytes_sent,
            bytes_recv,
            duration,
            dest_port,
            source_port,
            self._protocol_enc.transform(protocols),
            self._action_enc.transform(actions),
            ratio,
            conn_rate,
            unique_ports,
        ])
        return X

    @staticmethod
    def _normalise_scores(raw: np.ndarray) -> np.ndarray:
        # IsolationForest decision_function: negative = more anomalous
        # Flip so higher = more anomalous, then scale to 0-100
        flipped = -raw
        mn, mx = flipped.min(), flipped.max()
        if mx == mn:
            return np.zeros(len(raw), dtype=int)
        normalised = (flipped - mn) / (mx - mn) * 100
        return normalised.astype(int)

    @staticmethod
    def _classify_anomaly(df: pd.DataFrame) -> pd.Series:
        labels = pd.Series(["normal"] * len(df), index=df.index)

        # Port scan: same source, many unique dest ports, tiny bytes, DENY
        port_counts = df.groupby("source_ip")["dest_port"].transform("nunique")
        port_scan_mask = (
            df["is_anomaly"]
            & (port_counts > 5)
            & (df["bytes_sent"] < 500)
        )
        labels[port_scan_mask] = "Port Scan"

        # Brute force: dest_port 22/3389, DENY, auth event
        brute_mask = (
            df["is_anomaly"]
            & df["dest_port"].isin([22, 3389, 23, 21])
            & (df["action"] == "DENY")
        )
        labels[brute_mask] = "Brute Force"

        # Data exfiltration: massive bytes_sent
        exfil_mask = (
            df["is_anomaly"]
            & (df["bytes_sent"] > 1_000_000)
        )
        labels[exfil_mask] = "Data Exfiltration"

        # C2: anomaly not already classified, small symmetric traffic, unusual ports
        suspicious_ports = ~df["dest_port"].isin([80, 443, 53, 22, 3389, 445, 3306, 25, 8080])
        c2_mask = (
            df["is_anomaly"]
            & (labels == "normal")
            & suspicious_ports
        )
        labels[c2_mask] = "C2 / Suspicious"

        # Anything else that's anomalous
        other_mask = df["is_anomaly"] & (labels == "normal")
        labels[other_mask] = "Anomalous Traffic"

        return labels
