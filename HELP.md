# HELP — Cyber Security Suite

Complete reference for the **Deepfake Detector** and **AI Threat Hunter** combined suite.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Running the App](#2-running-the-app)
3. [Deepfake Detector — Full Guide](#3-deepfake-detector--full-guide)
4. [AI Threat Hunter — Full Guide](#4-ai-threat-hunter--full-guide)
5. [Live Feed Setup](#5-live-feed-setup)
6. [API Key Setup](#6-api-key-setup)
7. [Troubleshooting](#7-troubleshooting)
8. [Project Structure](#8-project-structure)
9. [Competition Demo Scripts](#9-competition-demo-scripts)
10. [FAQ](#10-faq)

---

## 1. Installation

### Requirements

- Python 3.10 or later
- pip

### Install all dependencies

```bash
pip install streamlit pandas numpy scikit-learn plotly opencv-python-headless \
            pillow pymupdf anthropic groq google-generativeai reportlab openpyxl
```

Or from the root requirements file:

```bash
pip install -r requirements.txt
```

### Windows note

Always use `python -m streamlit run` — not just `streamlit run` — to ensure the same Python
environment that has your packages installed is used.

---

## 2. Running the App

### Combined suite (recommended)

```bash
python -m streamlit run Home.py
```

Open **http://localhost:8501** — the landing page lets you choose either tool.

### Run tools individually

```bash
# Deepfake Detector only
cd deepfake_detector
python -m streamlit run app.py

# AI Threat Hunter only
cd ai_threat_hunter
python -m streamlit run app.py
```

### Generate PDF documentation

```bash
python generate_pdf.py
# Output: Cyber_Security_Suite_Project.pdf
```

---

## 3. Deepfake Detector — Full Guide

### What it does

Analyses **images, videos, PDFs and screenshots** for signs of:

| Threat | Description |
|---|---|
| Deepfake face swap | AI-replaced face using GAN / diffusion model |
| GAN-generated image | Fully synthetic image, no real photo source |
| Image splicing | Region copied/pasted from another photo |
| Inpainting | Object removed or background filled with AI |
| Screenshot fakery | Manipulated document or chat screenshot |
| Metadata mismatch | Camera or creation metadata inconsistencies |
| QR code threat | Malicious URL embedded in a QR code |

### Supported file types

| Format | Extensions |
|---|---|
| Images | JPG, PNG, WEBP, BMP, TIFF |
| Videos | MP4, AVI, MOV, MKV (key frames extracted) |
| PDFs | Any PDF — first 5 pages rasterised and scanned |

### How to use

1. Open the app → click **🔍 Launch Deepfake Detector** (or run directly)
2. **Sidebar:** Upload a file, or click **Analyze Demo** for an instant synthetic example
3. Wait for the spinner — AI queries run in order: Groq → Claude → Gemini
4. Read the **verdict banner**: FAKE / REAL / UNCERTAIN + confidence %
5. Expand the **AI Forensic Report** section for full analysis
6. Click **Download Report** to save the findings as a `.txt` file

### 7-Dimension analysis

The AI examines every upload across these dimensions:

| # | Dimension | What is checked |
|---|---|---|
| 1 | Facial Forensics | Skin texture, eye asymmetry, hair boundaries, geometry |
| 2 | GAN Artifacts | Checkerboard patterns, spectral anomalies, upsampling |
| 3 | Noise & Compression | JPEG block artefacts, sensor noise, double-compression |
| 4 | Lighting & Shadows | Specular highlights, shadow direction, reflection match |
| 5 | Background & Depth | Semantic coherence, depth-of-field, object boundaries |
| 6 | Colour & Chromatic | HSV distribution, colour temperature, saturation |
| 7 | Document / Text | Font consistency, QR codes, metadata timestamps |

### Sidebar controls

| Control | Purpose |
|---|---|
| File uploader | Upload image, video, or PDF |
| Analyze Demo | Runs on a built-in synthetic fake — no file needed |
| Backup API Key | Paste any provider key if the built-in pool is exhausted |

### AI key rotation

The tool has a built-in pool of AI provider keys tried in this order:

```
Groq (Llama Vision)  →  Claude (claude-3.5-sonnet)  →  Gemini (gemini-1.5-pro)
```

If all keys are exhausted it falls back to heuristic-only analysis (FFT + ELA + noise).

---

## 4. AI Threat Hunter — Full Guide

### What it does

Detects network intrusions from log files or a live stream using
**Isolation Forest** (unsupervised ML) — no labelled training data required.
Every alert is mapped to **MITRE ATT&CK** and explained by AI.

### Detected threat types

| Threat | Trigger Pattern | MITRE ID | Tactic |
|---|---|---|---|
| Port Scan | One IP → 50+ ports, tiny bytes | T1046 | Reconnaissance |
| Brute Force | SSH/RDP port 22/3389, high DENY rate | T1110.001 | Credential Access |
| Data Exfiltration | Outbound bytes > 1 MB per event | T1048.003 | Exfiltration |
| C2 / Suspicious | Beaconing to unusual ports (4444, 1337) | T1071.001 | Command & Control |
| Anomalous Traffic | Statistical outlier, unclassified | T1040 | Discovery |

### Supported log formats

| Format | Example |
|---|---|
| CSV | timestamp, source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action |
| JSON | Same fields as CSV, array of objects |
| Syslog | Auto-parsed via regex — common firewall formats |

**Minimum required columns:** `source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action`

Optional columns (used if present): `timestamp, source_port, duration`

### How to use

1. Launch the app → click **🛡️ Launch AI Threat Hunter**
2. **Sidebar — Upload / Sample mode:**
   - Click **⚡ Use Sample Data** for an instant 500-event demo
   - Or upload your own CSV / JSON log file
3. Adjust the **Sensitivity** slider (1 = very few alerts, 10 = very sensitive)
4. Click **Analyze** to run the Isolation Forest model
5. Browse the 6 tabs:

| Tab | What you see |
|---|---|
| Overview | Timeline scatter, threat distribution, top attacker IPs, heatmap |
| Threat Log | All detected threats, sortable table, CSV export |
| AI Analysis | Select a threat → full AI forensic report + MITRE mapping |
| Incident Response | Select a threat → AI-generated IR playbook, downloadable |
| Network Graph | Force-directed graph — red nodes = attackers |
| Live Feed | Real-time panel updating every 5 seconds |

### AI forensic report sections

When you select a threat in the **AI Analysis** tab, the AI generates:

1. Severity + Confidence
2. Threat Title
3. MITRE ATT&CK tactic + technique + sub-technique
4. Cyber Kill Chain phase
5. Executive summary
6. Evidence analysis
7. Impact assessment
8. Threat actor profile (type, sophistication, motivation)
9. Indicators of Compromise (IOCs)
10. False positive assessment
11. Related threat types
12. Analyst notes

### Incident Response playbook

Available in the **Incident Response** tab:

| Phase | Timeframe | Content |
|---|---|---|
| Immediate Actions | 0 – 15 min | Block IP, isolate endpoint, preserve logs |
| Investigation | 15 – 60 min | SIEM queries, EDR check, lateral movement hunt |
| Containment & Eradication | 1 – 4 hrs | Revoke creds, patch service, clean malware |
| Long-term Remediation | Days | Detection rule, policy update, lessons learned |

Download the playbook as a `.txt` file — hand it directly to a SOC analyst.

---

## 5. Live Feed Setup

Run two terminals simultaneously.

**Terminal 1 — Start the app:**
```bash
python -m streamlit run Home.py
```

**Terminal 2 — Start the log generator:**
```bash
cd ai_threat_hunter
python live_log_generator.py
```

The generator writes realistic network events to `ai_threat_hunter/live_feed.csv` continuously:

- **Normal traffic:** 3–8 events every 0.5–1.5 seconds
- **Attacks injected:** one every 20–45 seconds (Port Scan / Brute Force / Exfil / C2 beacon)

In the app sidebar, switch to **📡 Live Feed** mode. The Live Feed tab refreshes every 5 seconds
**without reloading the full page** (uses Streamlit `@st.fragment`).

### Live Feed tab auto-navigation

If the page reloads (e.g., after a Streamlit update), it automatically returns to the Live Feed tab
via JavaScript that reads `session_state._live_feed_on`.

---

## 6. API Key Setup

### Built-in key pool

Both tools have embedded key pools for competition use. Keys are tried in rotation:
Groq → Claude → Gemini. If one is exhausted, the next is tried automatically.

### Adding your own key (sidebar)

1. Open the app → expand **Backup API Key** in the sidebar
2. Paste any provider key — it is auto-detected by its prefix:
   - `gsk_...` → Groq
   - `sk-ant-...` → Claude / Anthropic
   - `AIza...` → Google Gemini
3. The key is tested; if valid, it is saved for the session.

### Key prefix reference

| Provider | Key prefix | Model used |
|---|---|---|
| Groq | `gsk_` | llama-3.2-90b-vision-preview |
| Anthropic | `sk-ant-` | claude-3-5-sonnet-20241022 |
| Google Gemini | `AIza` | gemini-1.5-pro |

### Security note

Keys embedded in this project are for competition demonstration only.
**Revoke any key after the competition.** Never commit real production keys to git.

---

## 7. Troubleshooting

### `ModuleNotFoundError: No module named 'sklearn'`

**Cause:** Using `streamlit run` with a different Python than the one where packages are installed.

**Fix:**
```bash
# Always use:
python -m streamlit run Home.py
# NOT:
streamlit run Home.py
```

### `ImportError: cannot import name 'ThreatDetector' from 'core.detector'`

**Cause:** Python cached the deepfake_detector's `core` package when the AI Threat Hunter's
`core` package is loaded.

**Fix:** Already handled in the page wrappers — they flush `sys.modules['core*']` before
each tool loads. If you see this, restart the Streamlit server.

### `KeyError: 'duration'` or `KeyError: 'source_port'`

**Cause:** Uploaded CSV does not have `duration` or `source_port` columns.

**Fix:** These columns are optional. The detector fills them with zeros if missing. If you
still see the error, check your CSV has at minimum:
`source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action`

### `background_gradient requires matplotlib`

**Cause:** Old version of the app used `df.style.background_gradient()`.

**Fix:** Already removed. Upgrade to the latest code; run `pip install matplotlib` if needed.

### Live Feed panel not updating

1. Make sure `live_log_generator.py` is running in a separate terminal
2. Check that `ai_threat_hunter/live_feed.csv` exists and is growing
3. Ensure the sidebar is set to **📡 Live Feed** mode
4. The fragment refreshes every 5 seconds — wait a moment

### AI analysis returns generic response

All AI provider keys may be exhausted. The tool falls back to a rule-based response.
Add a fresh key via the **Backup API Key** sidebar input.

### PDF generation fails on Windows

If you see `UnicodeEncodeError: 'charmap'`, set the console encoding:
```bash
set PYTHONIOENCODING=utf-8
python generate_pdf.py
```

---

## 8. Project Structure

```
Cyber Security/
│
├── Home.py                          # Landing page — tool selector
├── HELP.md                          # This file
├── README.md                        # Suite overview
├── requirements.txt                 # All dependencies
├── generate_pdf.py                  # PDF documentation generator
├── Cyber_Security_Suite_Project.pdf # Generated PDF (after running generate_pdf.py)
│
├── pages/
│   ├── 1_Deepfake_Detector.py       # Streamlit page wrapper for deepfake tool
│   └── 2_AI_Threat_Hunter.py        # Streamlit page wrapper for threat hunter
│
├── deepfake_detector/
│   ├── app.py                       # Main Streamlit app
│   ├── README.md                    # Tool-specific README
│   └── core/
│       ├── analyzer.py              # AI vision API + heuristic analysis
│       ├── key_manager.py           # Multi-provider key rotation
│       └── media_utils.py           # Image/video/PDF preprocessing
│
└── ai_threat_hunter/
    ├── app.py                       # Main Streamlit app (6 tabs + live feed)
    ├── README.md                    # Tool-specific README
    ├── live_log_generator.py        # Generates synthetic live attack stream
    ├── live_feed.csv                # Runtime output of live_log_generator.py
    └── core/
        ├── detector.py              # Isolation Forest ML detector
        ├── ai_analyzer.py           # Claude AI forensic report generator
        └── sample_data.py           # 500-event synthetic log generator
```

---

## 9. Competition Demo Scripts

### 2-minute Deepfake Detector demo

```
1. Open app → click "Launch Deepfake Detector"
2. Sidebar → click "Analyze Demo"
3. Point to verdict banner: FAKE / confidence %
4. Scroll to AI Forensic Report → manipulation type + primary indicators
5. Expand a dimension card → suspicion bar + per-dimension evidence
6. Upload a real photo → show it scores AUTHENTIC
7. Upload a PDF → show multi-page scan + QR code detection
```

### 2-minute AI Threat Hunter demo

```
1. Navigate Home → click "Launch AI Threat Hunter"
2. Click "Use Sample Data" → dashboard fills instantly
3. Overview tab → timeline scatter: red dots = attacks
4. Heatmap → "attacks cluster at 2-4 AM, classic attacker pattern"
5. AI Analysis tab → select highest risk alert (Data Exfiltration 90+/100)
6. Show MITRE: TA0010 → T1048.003, Kill Chain: Exfiltration
7. Threat Actor Profile → financially-motivated, medium sophistication
8. Incident Response tab → show IR playbook → download as .txt
9. Sidebar → Live Feed mode → Terminal 2: python live_log_generator.py
10. Live Feed tab → new attacks appear every 20-45s, panel refreshes every 5s
```

### Key talking points

| Point | What to say |
|---|---|
| No labelled data | "Isolation Forest needs zero labelled attack data — works on any network day 1" |
| No vendor lock-in | "3 AI providers with automatic fallback — system stays up even if one API goes down" |
| MITRE ATT&CK | "Every alert maps to the global standard used by real SOC teams worldwide" |
| End-to-end | "From raw logs to a downloadable IR playbook in under 10 seconds" |
| Live demo | "Watch a port scan appear in real time — this is live data, not static" |
| Production-ready | "Key rotation, error handling, rule-based fallback, exportable reports" |

---

## 10. FAQ

**Q: Can I use my own network logs?**

Yes. Upload any CSV with `source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action`.
JSON and syslog formats also supported. Extra columns are ignored.

**Q: What if I have no API keys?**

The Deepfake Detector falls back to heuristic-only analysis (FFT + ELA + noise distribution).
The AI Threat Hunter falls back to rule-based forensic reports. Both tools remain functional
without any AI keys.

**Q: How do I run only one tool without the combined Home.py?**

```bash
cd deepfake_detector && python -m streamlit run app.py
# or
cd ai_threat_hunter && python -m streamlit run app.py
```

**Q: Can I add more AI providers?**

Yes. Edit `deepfake_detector/core/key_manager.py` — add entries to the key pool list and
implement a `query_<provider>()` function following the existing pattern.

**Q: The Isolation Forest flags too many / too few events.**

Adjust the **Sensitivity** slider in the sidebar:
- Low sensitivity (1–3): only very strong anomalies flagged
- High sensitivity (7–10): more events flagged, may include false positives
- Default (5): typically 5–15% of traffic flagged as anomalous

**Q: How do I stop the live feed?**

Press `Ctrl+C` in the terminal running `live_log_generator.py`.
The CSV file remains on disk. Delete it with `del ai_threat_hunter\live_feed.csv` if needed.

**Q: Can the PDF be regenerated after changes?**

Yes:
```bash
python generate_pdf.py
```
Output is always `Cyber_Security_Suite_Project.pdf` in the project root.

**Q: How do I push the project to GitHub?**

Ensure your GitHub fine-grained PAT has **Contents: Read and Write** permission:
1. Go to github.com → Settings → Developer settings → Fine-grained tokens
2. Edit your token → Repository permissions → Contents → Read and write → Save
3. Then run:

```bash
git push origin main
```

---

*Cyber Security Suite — AI Threat Hunter + Deepfake Detector — Edition 2026*
