# 🔐 Cyber Security Suite

> **AI-powered security toolkit for the 2026 Cyber Security Competition**
> Two production-ready tools — Deepfake Detector and AI Threat Hunter — unified in a single Streamlit app.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the combined suite
python -m streamlit run Home.py
```

Open **http://localhost:8501** — choose your tool from the landing page.

---

## 🛠️ Tools Included

| Tool | Purpose | Key Tech |
|---|---|---|
| [🔍 Deepfake Detector](./deepfake_detector/) | Detect AI-generated / manipulated media | AI Vision API, OpenCV, PyMuPDF |
| [🛡️ AI Threat Hunter](./ai_threat_hunter/) | Network anomaly detection & IR playbooks | Isolation Forest, MITRE ATT&CK |

---

## 📁 Project Structure

```
Cyber Security Suite/
├── Home.py                          # Landing page — tool selector
├── requirements.txt                 # All dependencies
├── pages/
│   ├── 1_Deepfake_Detector.py       # Multi-page nav entry
│   └── 2_AI_Threat_Hunter.py        # Multi-page nav entry
├── deepfake_detector/               # Deepfake detection engine
│   ├── app.py
│   ├── requirements.txt
│   └── core/
│       ├── gemini_analyzer.py       # Gemini vision AI
│       ├── groq_analyzer.py         # Groq Llama vision
│       ├── claude_analyzer.py       # Claude vision AI
│       ├── key_rotator.py           # Auto key rotation pool
│       ├── detector.py              # Heuristic pre-analysis
│       ├── audio_processor.py       # Audio/video handling
│       └── video_processor.py
└── ai_threat_hunter/                # Threat detection engine
    ├── app.py
    ├── requirements.txt
    └── core/
        ├── detector.py              # Isolation Forest ML
        ├── explainer.py             # AI forensic explainer
        ├── key_rotator.py           # Claude key rotation
        ├── log_parser.py            # CSV/JSON/syslog parser
        └── sample_logs.py           # Demo data generator
```

---

## ⚙️ Configuration

### Adding API Keys

Both tools use a built-in key rotation pool. To add your own keys:

1. Use the **Backup AI Key** input in the app sidebar — working keys are auto-saved
2. Or edit the `_GROQ_KEYS` / `_CLAUDE_KEYS` / `_GEMINI_KEYS` lists in `core/key_rotator.py`

**Supported providers:**
- Groq (`gsk_...`) — Llama vision models
- Claude (`sk-ant-...` or `apikey_...`) — Anthropic vision
- Gemini (`AIza...` or `AQ....`) — Google vision models

> `keys_config.json` is gitignored — your keys never leave your machine.

---

## 📦 Requirements

```
streamlit>=1.39.0    plotly          scikit-learn
pandas               opencv-python   anthropic
numpy                Pillow          google-genai
PyMuPDF              groq            matplotlib
```

---

## 🏆 Competition Notes

- All AI analysis uses **key rotation** — if one key hits quota, the next is tried automatically
- No API key is required to start — both tools have rule-based fallbacks
- Sample data is built-in for instant demo (no file upload needed)
- All brand names removed from UI — generic "AI Engine" labelling throughout
