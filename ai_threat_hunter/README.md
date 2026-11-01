# 🛡️ AI Threat Hunter

> Real-time network anomaly detection using Isolation Forest ML, with AI-generated MITRE ATT&CK-mapped forensic reports and downloadable incident response playbooks.

---

## 🎯 What It Does

1. **Ingests** network logs (CSV, JSON, syslog)
2. **Detects** anomalous traffic using unsupervised machine learning
3. **Classifies** each threat by type, severity, and MITRE ATT&CK technique
4. **Explains** the threat with a full AI forensic report
5. **Generates** a step-by-step incident response playbook

---

## 🚀 Quick Start

```bash
cd ai_threat_hunter
pip install -r requirements.txt
python -m streamlit run app.py
```

Open **http://localhost:8501** → click **⚡ Use Sample Data** for an instant demo.

---

## 🧠 Detection Engine

### Isolation Forest (Unsupervised ML)

```
Network Log Events
      ↓
Feature Engineering
├── bytes_sent / bytes_recv ratio
├── connection frequency per source IP
├── destination port entropy
├── protocol distribution
└── time-of-day patterns
      ↓
Isolation Forest
└── contamination = tunable sensitivity (sidebar slider)
      ↓
Risk Score (0–100) + Anomaly Label
```

The Isolation Forest isolates anomalies by randomly partitioning data — unusual events require fewer splits to isolate, producing a higher risk score.

### Sensitivity Slider
- **Low (1–3):** Only extreme outliers flagged — fewer false positives
- **Medium (4–6):** Balanced detection — good for demos
- **High (7–10):** Aggressive — catches subtle attacks, more false positives

---

## 🚨 Threat Types Detected

| Threat | Detection Pattern | MITRE Tactic | Technique |
|---|---|---|---|
| **Port Scan** | One IP → many ports, low bytes | Reconnaissance | T1046 |
| **Brute Force** | Many failed connections, same target | Credential Access | T1110.001 |
| **Data Exfiltration** | Large outbound transfer, unusual dest | Exfiltration | T1048.003 |
| **C2 / Suspicious** | Regular beaconing, external IPs | Command & Control | T1071.001 |
| **Anomalous Traffic** | Statistical outlier, no clear pattern | Discovery | T1040 |

---

## 📊 Dashboard Tabs

### 📊 Overview
- **Threat Timeline** — scatter plot of all anomalies over time (size = data volume)
- **Threat Distribution** — donut chart of threat type breakdown
- **Top Attacker IPs** — horizontal bar chart of most active sources
- **Activity Heatmap** — hour-of-day attack patterns per threat type
- **MITRE ATT&CK Coverage** — which tactics/techniques were observed

### 🚨 Threat Log
- Sortable table of all detected threats (up to 200 rows)
- Risk score column with colour gradient
- Export as CSV for reporting

### 🤖 AI Analysis
Select any threat → AI generates a full forensic report:

```
┌─ Severity Badge ──────────────── AI Confidence % ─────────────────┐
│  Threat Title                                    Category / Kill Chain │
│  Executive Summary (2–3 sentences)                                   │
└──────────────────────────────────────────────────────────────────────┘

MITRE ATT&CK Mapping
  TA0009 Collection → T1048 Exfiltration → T1048.003 (sub-technique)

Evidence Analysis          │  Impact Assessment
Threat Actor Profile       │  (type / sophistication / motivation)

Indicators of Compromise   False Positive Likelihood
```

### 🧭 Incident Response (IR Playbook)
AI generates a structured response plan:

| Phase | Timeframe | Example Actions |
|---|---|---|
| **Immediate Actions** | 0–15 min | Block IP at firewall, isolate endpoint |
| **Investigation Steps** | 15–60 min | Review SIEM logs, check EDR alerts |
| **Containment & Eradication** | 1–4 hrs | Revoke credentials, patch exploit |
| **Long-term Remediation** | Days | Add detection rule, update policy |

Download as a `.txt` file for offline use or handoff to SOC.

### 🕸️ Network Graph
- Force-directed graph of all source→destination connections
- Red nodes = confirmed attack sources
- Blue nodes = normal hosts
- Red edges = attack traffic paths
- Node size = number of total connections

---

## 📥 Uploading Your Own Logs

### CSV Format
```csv
timestamp,source_ip,dest_ip,dest_port,protocol,bytes_sent,bytes_recv,action
2026-01-01 10:00:00,192.168.1.100,10.0.0.1,22,TCP,1024,512,ALLOW
```

Required columns: `timestamp`, `source_ip`, `dest_ip`, `dest_port`, `protocol`, `bytes_sent`, `bytes_recv`, `action`

### JSON Format
```json
[
  {"timestamp": "2026-01-01T10:00:00", "source_ip": "192.168.1.100",
   "dest_ip": "10.0.0.1", "dest_port": 22, "protocol": "TCP",
   "bytes_sent": 1024, "bytes_recv": 512, "action": "ALLOW"}
]
```

### Syslog / Text Format
Plain syslog lines are parsed by pattern matching for common firewall/IDS formats.

---

## 🤖 AI Forensic Analysis

The explainer calls Claude AI (with key rotation fallback) using a 12-section structured prompt:

```
1. Threat Classification     7. Indicators of Compromise
2. MITRE ATT&CK Mapping      8. Immediate Actions (0–15 min)
3. Cyber Kill Chain Phase    9. Investigation Steps
4. Evidence Analysis        10. Containment & Eradication
5. Impact Assessment        11. Long-term Remediation
6. Threat Actor Profile     12. False Positive Assessment
```

If no AI key is available, a detailed **rule-based fallback** provides the same JSON structure with pre-built MITRE-mapped responses for all 5 threat types.

---

## 🗂️ File Structure

```
ai_threat_hunter/
├── app.py                      # Main Streamlit app (5 tabs)
├── requirements.txt
└── core/
    ├── detector.py             # Isolation Forest ML engine
    ├── explainer.py            # AI forensic explainer + rule fallback
    ├── key_rotator.py          # Claude key rotation pool
    ├── log_parser.py           # CSV / JSON / syslog ingestion
    └── sample_logs.py          # Synthetic log generator
```

---

## 📈 Metrics Shown on Dashboard

| Metric | Description |
|---|---|
| **Total Events** | All log entries ingested |
| **Threats Detected** | Anomalies flagged by Isolation Forest |
| **Peak Risk Score** | Highest risk score in current dataset |
| **Critical Alerts** | Threats with risk score ≥ 70 |
| **Unique Attackers** | Distinct source IPs involved in threats |

---

## 🎯 Demo Script (2 Minutes)

> *"This is AI Threat Hunter — it takes raw network logs and automatically finds cyberattacks."*

**Step 1:** Click **⚡ Use Sample Data** → 500 log entries load instantly

**Step 2:** Point to the Overview tab:
> *"The ML model found [N] threats. You can see the attack timeline — those large red dots are data exfiltration events. The heatmap shows most attacks happen between 2–4 AM."*

**Step 3:** Go to AI Analysis tab, pick the highest-risk alert:
> *"I'll analyse this Data Exfiltration alert. The AI maps it to MITRE T1048.003, identifies the kill chain phase as Exfiltration, and profiles this as a financially-motivated actor with medium sophistication."*

**Step 4:** Go to Incident Response tab:
> *"Most importantly — the AI generates a step-by-step playbook. Block the IP within 15 minutes, pull EDR logs, revoke compromised credentials. I can download this as a PDF and hand it to any analyst."*

**Step 5:** Show Network Graph:
> *"Finally, here's the network graph — red nodes are the attackers, you can see they're targeting this internal server."*

---

## ⚠️ Notes

- Sample data is randomly generated with realistic attack injection — re-run for different scenarios
- All AI analysis is heuristic — not a substitute for a real SIEM in production
- The Isolation Forest model is trained fresh on each uploaded dataset (no persistent model file)
