# Mac Setup Guide — Cyber Security Suite

Complete steps to run the Cyber Security Suite on macOS.

---

## Step 1 — Open Terminal and navigate to the project

```bash
cd ~/Downloads/cyber-security-suite
```

> Adjust the path to wherever you downloaded or cloned the project.

---

## Step 2 — Check Python version

```bash
python3 --version
```

Needs to be **Python 3.10 or higher**. If not installed:

```bash
brew install python@3.12
```

> If Homebrew is not installed: https://brew.sh

---

## Step 3 — Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when the environment is active.

---

## Step 4 — Install all dependencies

```bash
pip install streamlit pandas numpy scikit-learn plotly \
  opencv-python-headless pillow pymupdf \
  anthropic groq google-generativeai reportlab openpyxl
```

---

## Step 5 — Add API keys

The `keys_config.json` files are gitignored and not included in the downloaded code.
Create them manually by running these two commands in the terminal:

**Deepfake Detector keys:**

```bash
cat > deepfake_detector/keys_config.json << 'EOF'
{
  "groq": [
    "YOUR_GROQ_KEY_1",
    "YOUR_GROQ_KEY_2"
  ],
  "claude": [
    "YOUR_CLAUDE_KEY"
  ],
  "gemini": [
    "YOUR_GEMINI_KEY_1",
    "YOUR_GEMINI_KEY_2",
    "YOUR_GEMINI_KEY_3",
    "YOUR_GEMINI_KEY_4",
    "YOUR_GEMINI_KEY_5"
  ]
}
EOF
```

> Replace the placeholder values with your actual API keys before running.
> Groq keys start with `gsk_`, Claude keys with `apikey_` or `sk-ant-`, Gemini keys with `AIza` or `AQ.`.

**AI Threat Hunter keys:**

```bash
cat > ai_threat_hunter/keys_config.json << 'EOF'
{
  "claude": [
    "YOUR_CLAUDE_KEY"
  ]
}
EOF
```

> Use the same Claude key value in both files.

---

## Step 6 — Run the app

```bash
python3 -m streamlit run Home.py
```

Open **http://localhost:8501** in your browser.

---

## Step 7 — (Optional) Run Live Feed

Open a **second terminal tab**, then:

```bash
cd ~/Downloads/cyber-security-suite
source venv/bin/activate
cd ai_threat_hunter
python3 live_log_generator.py
```

In the app: Sidebar → **Live Feed** mode → **Live Feed** tab.
New attacks appear every 20–45 seconds, panel refreshes every 5 seconds.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `command not found: python3` | `brew install python@3.12` |
| `No module named 'cv2'` | `pip install opencv-python-headless` |
| `No module named 'fitz'` | `pip install pymupdf` |
| `No module named 'sklearn'` | `pip install scikit-learn` |
| Port 8501 already in use | `python3 -m streamlit run Home.py --server.port 8502` |
| App uses wrong Python | Always use `python3 -m streamlit run`, never just `streamlit run` |
| Virtual env not active | Run `source venv/bin/activate` first |
| AI engines show no keys | Make sure Step 5 was completed — keys_config.json must exist |

---

## Every Time You Return

```bash
cd ~/Downloads/cyber-security-suite
source venv/bin/activate
python3 -m streamlit run Home.py
```

---

*Cyber Security Suite — Deepfake Detector + AI Threat Hunter — 2026*
