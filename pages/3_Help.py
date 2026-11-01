"""
Cyber Security Suite — In-app Help & README page
"""
import streamlit as st
import os

st.set_page_config(
    page_title="Help — Cyber Security Suite",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (matches dark theme from Home.py) ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    background-color: #0a0e1a !important;
    color: #c8d6e5 !important;
    font-family: 'Rajdhani', sans-serif;
}
.stApp { background-color: #0a0e1a; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #0a0e1a 100%) !important;
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Help page specific ── */
.help-banner {
    background: linear-gradient(135deg, #0d1526, #101f3a);
    border: 1px solid #1e3a5f;
    border-left: 4px solid #00d4ff;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.4rem;
}
.help-banner h2 {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.2rem;
    color: #00d4ff;
    margin: 0 0 0.4rem 0;
    letter-spacing: 3px;
}
.help-banner p {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #8ab0c8;
    margin: 0;
    line-height: 1.7;
}

.section-bar {
    background: linear-gradient(90deg, #0d1526, #101f3a);
    border-left: 4px solid #00ff88;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 1.2rem 0 0.6rem 0;
}
.section-bar span {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #00ff88;
    letter-spacing: 2px;
    font-weight: 700;
}

.section-bar-orange { border-left-color: #ff8800; }
.section-bar-orange span { color: #ff8800; }
.section-bar-blue { border-left-color: #00d4ff; }
.section-bar-blue span { color: #00d4ff; }
.section-bar-red { border-left-color: #ff4444; }
.section-bar-red span { color: #ff4444; }
.section-bar-purple { border-left-color: #aa44ff; }
.section-bar-purple span { color: #aa44ff; }

.info-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
.info-table th {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    padding: 7px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #00d4ff;
    letter-spacing: 1px;
    text-align: left;
}
.info-table td {
    border: 1px solid #1e3a5f;
    padding: 7px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #c8d6e5;
    vertical-align: top;
    line-height: 1.6;
}
.info-table tr:nth-child(even) td { background: #0d1526; }
.info-table tr:nth-child(odd)  td { background: #101f3a; }

code {
    background: #101f3a !important;
    color: #00ff88 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 4px;
    padding: 2px 7px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.82rem;
}
pre {
    background: #101f3a !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px;
    padding: 1rem 1.2rem !important;
    overflow-x: auto;
}
pre code { border: none !important; background: transparent !important; }

.chip {
    display: inline-block;
    background: #1e3a5f;
    color: #00d4ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 3px 2px;
}

.stButton > button {
    background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 2px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.6rem;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:1.1rem;
                    color:#00ff88;letter-spacing:3px;">📖 HELP</div>
        <div style="font-size:0.62rem;color:#4a7a9b;letter-spacing:2px;margin-top:4px;">
            DOCUMENTATION
        </div>
    </div>
    <hr style="border-color:#1e3a5f;margin:0.4rem 0 1rem 0;">
    """, unsafe_allow_html=True)
    if st.button("🏠  Back to Home", key="back_home"):
        st.switch_page("Home.py")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍  Deepfake Detector", key="go_deep"):
        st.switch_page("pages/1_Deepfake_Detector.py")
    if st.button("🛡️  AI Threat Hunter", key="go_hunt"):
        st.switch_page("pages/2_AI_Threat_Hunter.py")

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#4a7a9b;line-height:2;">
        📄 Table of Contents<br>
        1. Installation<br>
        2. Running the App<br>
        3. Deepfake Detector<br>
        4. AI Threat Hunter<br>
        5. Live Feed Setup<br>
        6. API Key Setup<br>
        7. Troubleshooting<br>
        8. Project Structure<br>
        9. Demo Scripts<br>
        10. MITRE ATT&amp;CK Framework<br>
        11. FAQ
    </div>
    """, unsafe_allow_html=True)

    # PDF download
    st.markdown("---")
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "Cyber_Security_Suite_Project.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download PDF Docs",
                data=f.read(),
                file_name="Cyber_Security_Suite_Project.pdf",
                mime="application/pdf",
            )

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="help-banner">
    <h2>📖 HELP &amp; DOCUMENTATION</h2>
    <p>Complete reference for the Cyber Security Suite — Deepfake Detector &amp; AI Threat Hunter.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — INSTALLATION
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar"><span>01 — INSTALLATION</span></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("**Requirements:** Python 3.10+  &nbsp;•&nbsp;  pip")
    st.code("""pip install streamlit pandas numpy scikit-learn plotly \\
        opencv-python-headless pillow pymupdf \\
        anthropic groq google-generativeai reportlab openpyxl""", language="bash")

with col2:
    st.markdown("**Or install from requirements file:**")
    st.code("pip install -r requirements.txt", language="bash")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#ffaa00;line-height:1.8;">
    ⚠️ Windows: Always use<br>
    <code>python -m streamlit run</code><br>
    NOT just <code>streamlit run</code>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 2 — RUNNING THE APP
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-blue"><span>02 — RUNNING THE APP</span></div>',
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Combined Suite (recommended)**")
    st.code("python -m streamlit run Home.py", language="bash")
    st.markdown("<span class='chip'>http://localhost:8501</span>", unsafe_allow_html=True)

with col2:
    st.markdown("**Deepfake Detector only**")
    st.code("""cd deepfake_detector
python -m streamlit run app.py""", language="bash")

with col3:
    st.markdown("**Generate PDF docs**")
    st.code("python generate_pdf.py", language="bash")
    st.markdown("<span class='chip'>Cyber_Security_Suite_Project.pdf</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 3 — DEEPFAKE DETECTOR
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-red"><span>03 — DEEPFAKE DETECTOR</span></div>',
            unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 1])
with col1:
    st.markdown("**What It Detects**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Manipulation Type</th><th>Description</th></tr>
    <tr><td>Deepfake Face Swap</td><td>AI-replaced face using GAN / diffusion model</td></tr>
    <tr><td>GAN-Generated Image</td><td>Fully synthetic — no real photo source</td></tr>
    <tr><td>Image Splicing</td><td>Region copied / pasted from another photo</td></tr>
    <tr><td>Inpainting</td><td>Object removed or background filled with AI</td></tr>
    <tr><td>Screenshot Fakery</td><td>Manipulated document or chat screenshot</td></tr>
    <tr><td>Metadata Mismatch</td><td>Camera or creation metadata inconsistencies</td></tr>
    <tr><td>QR Code Threat</td><td>Malicious URL embedded in a QR code</td></tr>
    </table>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**7-Dimension Analysis**")
    st.markdown("""
    <table class="info-table">
    <tr><th>#</th><th>Dimension</th></tr>
    <tr><td>1</td><td>Facial Forensics — skin, eyes, hair</td></tr>
    <tr><td>2</td><td>GAN Artifacts — spectral anomalies</td></tr>
    <tr><td>3</td><td>Noise &amp; Compression — JPEG blocks</td></tr>
    <tr><td>4</td><td>Lighting &amp; Shadows — highlight match</td></tr>
    <tr><td>5</td><td>Background &amp; Depth — coherence</td></tr>
    <tr><td>6</td><td>Colour &amp; Chromatic — HSV, temperature</td></tr>
    <tr><td>7</td><td>Document / Text — fonts, QR, metadata</td></tr>
    </table>
    """, unsafe_allow_html=True)

st.markdown("**How to use:**")
st.markdown("""
<table class="info-table">
<tr><th>Step</th><th>Action</th></tr>
<tr><td>1</td><td>Open app → click <b>Launch Deepfake Detector</b></td></tr>
<tr><td>2</td><td>Sidebar: upload a file OR click <b>Analyze Demo</b> for an instant synthetic example</td></tr>
<tr><td>3</td><td>Wait for spinner — AI queries run: Groq → Claude → Gemini</td></tr>
<tr><td>4</td><td>Read the verdict banner: FAKE / REAL / UNCERTAIN + confidence %</td></tr>
<tr><td>5</td><td>Expand AI Forensic Report — manipulation type, indicators, 7-dimension breakdown</td></tr>
<tr><td>6</td><td>Click <b>Download Report</b> to save findings as .txt file</td></tr>
</table>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 4 — AI THREAT HUNTER
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-blue"><span>04 — AI THREAT HUNTER</span></div>',
            unsafe_allow_html=True)

st.markdown("**Detected Threat Types**")
st.markdown("""
<table class="info-table">
<tr><th>Threat</th><th>Detection Pattern</th><th>MITRE ID</th><th>Tactic</th></tr>
<tr><td>Port Scan</td><td>One IP hitting 50+ ports, tiny bytes, DENY responses</td><td>T1046</td><td>Reconnaissance</td></tr>
<tr><td>Brute Force</td><td>High-freq connections to port 22/3389, mostly DENY</td><td>T1110.001</td><td>Credential Access</td></tr>
<tr><td>Data Exfiltration</td><td>Outbound transfer > 1 MB per event to external IP</td><td>T1048.003</td><td>Exfiltration</td></tr>
<tr><td>C2 / Suspicious</td><td>Beaconing to unusual ports (4444, 1337, 9001)</td><td>T1071.001</td><td>Command & Control</td></tr>
<tr><td>Anomalous Traffic</td><td>Statistical outlier, unclassified</td><td>T1040</td><td>Discovery</td></tr>
</table>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Dashboard Tabs**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Tab</th><th>Content</th></tr>
    <tr><td>Overview</td><td>Timeline, pie chart, heatmap, top IPs</td></tr>
    <tr><td>Threat Log</td><td>Sortable table, CSV export</td></tr>
    <tr><td>AI Analysis</td><td>Full AI forensic report + MITRE map</td></tr>
    <tr><td>Incident Response</td><td>AI IR playbook, download as .txt</td></tr>
    <tr><td>Network Graph</td><td>Force-directed attacker/host graph</td></tr>
    <tr><td>Live Feed</td><td>5s auto-refresh, real-time attacks</td></tr>
    </table>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**IR Playbook Phases**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Phase</th><th>Timeframe</th></tr>
    <tr><td>Immediate Actions</td><td>0 – 15 min — block IP, isolate endpoint</td></tr>
    <tr><td>Investigation</td><td>15 – 60 min — SIEM, EDR, lateral movement</td></tr>
    <tr><td>Containment &amp; Eradication</td><td>1 – 4 hrs — revoke, patch, clean</td></tr>
    <tr><td>Long-term Remediation</td><td>Days — rule, policy, lessons learned</td></tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("**CSV Log Format**")
    st.code("""timestamp,source_ip,dest_ip,dest_port,
protocol,bytes_sent,bytes_recv,action""", language="text")
    st.markdown("<span class='chip'>Optional: source_port · duration</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 5 — LIVE FEED
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-orange"><span>05 — LIVE FEED SETUP</span></div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Terminal 1 — Start the app**")
    st.code("python -m streamlit run Home.py", language="bash")
    st.markdown("**Terminal 2 — Start log generator**")
    st.code("""cd ai_threat_hunter
python live_log_generator.py""", language="bash")

with col2:
    st.markdown("**What the generator produces:**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Event Type</th><th>Frequency</th></tr>
    <tr><td>Normal traffic</td><td>3–8 events per 0.5–1.5 seconds</td></tr>
    <tr><td>Port Scan (T1046)</td><td>Every 20–45 seconds</td></tr>
    <tr><td>Brute Force (T1110.001)</td><td>Every 20–45 seconds</td></tr>
    <tr><td>Data Exfil (T1048.003)</td><td>Every 20–45 seconds</td></tr>
    <tr><td>C2 Beacon (T1071.001)</td><td>Every 20–45 seconds</td></tr>
    </table>
    <br>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#8ab0c8;line-height:1.8;">
    Panel refreshes every <b style="color:#00ff88;">5 seconds</b> using<br>
    <code>@st.fragment(run_every='5s')</code><br>
    — full page does NOT reload.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 6 — API KEY SETUP
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar"><span>06 — API KEY SETUP</span></div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Built-in key rotation order**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Provider</th><th>Key Prefix</th><th>Model</th></tr>
    <tr><td>Groq</td><td>gsk_...</td><td>llama-3.2-90b-vision-preview</td></tr>
    <tr><td>Anthropic</td><td>sk-ant-...</td><td>claude-3-5-sonnet-20241022</td></tr>
    <tr><td>Google Gemini</td><td>AIza...</td><td>gemini-1.5-pro</td></tr>
    </table>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**Adding your own key**")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#c8d6e5;line-height:2.0;">
    1. Open sidebar → <b>Backup API Key</b> input<br>
    2. Paste any provider key<br>
    3. Auto-detected by prefix<br>
    4. Saved for the session if valid<br>
    <br>
    <span style="color:#ff4444;">⚠️ Revoke competition keys after the event.</span><br>
    <span style="color:#ffaa00;">Never commit real production keys to git.</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 7 — TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-red"><span>07 — TROUBLESHOOTING</span></div>',
            unsafe_allow_html=True)

issues = [
    ("ModuleNotFoundError: No module named 'sklearn'",
     "Using streamlit run with a different Python environment.",
     "python -m streamlit run Home.py  (always use python -m)"),
    ("ImportError: cannot import name 'ThreatDetector' from 'core.detector'",
     "Python cached deepfake's core package first.",
     "Handled by page wrappers (sys.modules flush). Restart Streamlit if it persists."),
    ("KeyError: 'duration' or KeyError: 'source_port'",
     "Uploaded CSV is missing optional columns.",
     "These columns are optional — filled with zeros. Minimum required: source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action"),
    ("Live Feed panel not updating",
     "live_log_generator.py is not running.",
     "Start Terminal 2: python live_log_generator.py — check live_feed.csv is growing."),
    ("AI analysis returns generic response",
     "All built-in provider keys exhausted.",
     "Add a fresh key via the Backup API Key sidebar input."),
    ("GitHub push 403 error",
     "Fine-grained PAT lacks Contents: Write permission.",
     "Settings → Developer Settings → Tokens → Edit → Contents → Read and Write → Save."),
]

for title, cause, fix in issues:
    with st.expander(f"⚠️  {title}"):
        st.markdown(f"**Cause:** {cause}")
        st.markdown(f"**Fix:** `{fix}`" if "python" in fix.lower() or "git" in fix.lower()
                    else f"**Fix:** {fix}")

# ══════════════════════════════════════════════════════════════
# SECTION 8 — PROJECT STRUCTURE
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-purple"><span>08 — PROJECT STRUCTURE</span></div>',
            unsafe_allow_html=True)

st.code("""Cyber Security/
│
├── Home.py                          # Landing page — tool selector
├── HELP.md                          # Text help file
├── README.md                        # Suite overview
├── requirements.txt                 # All dependencies
├── generate_pdf.py                  # PDF documentation generator
├── Cyber_Security_Suite_Project.pdf # Generated PDF
│
├── pages/
│   ├── 1_Deepfake_Detector.py       # Streamlit page wrapper
│   ├── 2_AI_Threat_Hunter.py        # Streamlit page wrapper
│   └── 3_Help.py                    # This help page
│
├── deepfake_detector/
│   ├── app.py                       # Main Streamlit app
│   ├── README.md
│   └── core/
│       ├── analyzer.py              # AI vision API + heuristic
│       ├── key_manager.py           # Multi-provider key rotation
│       └── media_utils.py           # Image/video/PDF preprocessing
│
└── ai_threat_hunter/
    ├── app.py                       # Main Streamlit app (6 tabs)
    ├── README.md
    ├── live_log_generator.py        # Synthetic live attack stream
    ├── live_feed.csv                # Runtime output (auto-created)
    └── core/
        ├── detector.py              # Isolation Forest ML
        ├── ai_analyzer.py           # Claude AI forensic reports
        └── sample_data.py           # 500-event synthetic logs""", language="text")

# ══════════════════════════════════════════════════════════════
# SECTION 9 — DEMO SCRIPTS
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-orange"><span>09 — COMPETITION DEMO SCRIPTS</span></div>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Deepfake Detector (2 min)**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Step</th><th>What to Show</th></tr>
    <tr><td>1</td><td>Sidebar → Analyze Demo → verdict banner + confidence %</td></tr>
    <tr><td>2</td><td>AI Forensic Report → manipulation type + indicators</td></tr>
    <tr><td>3</td><td>Dimension card → suspicion bar + evidence</td></tr>
    <tr><td>4</td><td>Upload real photo → scores AUTHENTIC</td></tr>
    <tr><td>5</td><td>Upload PDF → multi-page scan + QR detection</td></tr>
    <tr><td>6</td><td>Download Report → show .txt output</td></tr>
    </table>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("**AI Threat Hunter (2 min)**")
    st.markdown("""
    <table class="info-table">
    <tr><th>Step</th><th>What to Show</th></tr>
    <tr><td>1</td><td>Use Sample Data → dashboard fills instantly</td></tr>
    <tr><td>2</td><td>Timeline → red dots = attacks, size = data volume</td></tr>
    <tr><td>3</td><td>Heatmap → attacks cluster 2-4 AM</td></tr>
    <tr><td>4</td><td>AI Analysis → select Data Exfil, score 90+</td></tr>
    <tr><td>5</td><td>MITRE: TA0010 → T1048.003, Kill Chain: Exfiltration</td></tr>
    <tr><td>6</td><td>IR Playbook → download .txt for judges</td></tr>
    <tr><td>7</td><td>Live Feed → start generator, show real-time alerts</td></tr>
    </table>
    """, unsafe_allow_html=True)

st.markdown("**Key talking points:**")
points = [
    ("No labelled data", "Isolation Forest works on ANY network without prior training — works day 1"),
    ("No vendor lock-in", "3 AI providers with auto-fallback — stays up even if one API is down"),
    ("MITRE ATT&CK", "Every alert maps to the global standard used by real SOC teams worldwide"),
    ("End-to-end", "Raw logs to downloadable IR playbook in under 10 seconds"),
    ("Live demo", "Watch port scan appear in real time — live data, not static samples"),
]
for pt, detail in points:
    st.markdown(f"- **{pt}:** {detail}")

# ══════════════════════════════════════════════════════════════
# SECTION 10 — MITRE ATT&CK FRAMEWORK
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar section-bar-blue"><span>10 — MITRE ATT&amp;CK FRAMEWORK</span></div>',
            unsafe_allow_html=True)

st.markdown("""
<div style="background:linear-gradient(135deg,#0d1526,#101f3a);border:1px solid #1e3a5f;
            border-left:4px solid #00d4ff;border-radius:10px;padding:1.2rem 1.6rem;margin-bottom:1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#00d4ff;
                font-weight:700;letter-spacing:2px;margin-bottom:0.5rem;">
        ATT&amp;CK = Adversarial Tactics, Techniques &amp; Common Knowledge
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#c8d6e5;line-height:1.9;">
        A globally recognised <b>knowledge base of real-world cyberattack behaviour</b>, maintained by
        MITRE Corporation (a US non-profit). It is the standard language used by SOC analysts,
        threat hunters and incident responders worldwide — used in every major SIEM including
        Splunk, Microsoft Sentinel and CrowdStrike.
    </div>
</div>
""", unsafe_allow_html=True)

# Core concept
st.markdown("##### The Core Idea")
st.markdown("""
<div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:8px;
            padding:1rem 1.4rem;font-family:'Share Tech Mono',monospace;
            font-size:0.78rem;color:#c8d6e5;line-height:2.2;">
    <span style="color:#00d4ff;font-weight:700;">TACTIC</span>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;
    <b>WHY</b> the attacker did it &nbsp;(the <span style="color:#ffaa00;">goal</span>)<br>
    &nbsp;&nbsp;<span style="color:#00ff88;font-weight:700;">TECHNIQUE</span>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;
    <b>WHAT</b> they did &nbsp;(the <span style="color:#ffaa00;">method</span>)<br>
    &nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#aa44ff;font-weight:700;">SUB-TECHNIQUE</span>
    &nbsp;→&nbsp;
    <b>HOW</b> exactly &nbsp;(the <span style="color:#ffaa00;">specific variant</span>)
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 14 Tactics table
st.markdown("##### 14 Tactics — The Full Attack Lifecycle")
st.markdown("""
<table class="info-table">
<tr><th>Tactic ID</th><th>Tactic Name</th><th>What the Attacker Wants</th></tr>
<tr><td>TA0043</td><td>Reconnaissance</td><td>Gather information about the target (IPs, services, employees)</td></tr>
<tr><td>TA0042</td><td>Resource Development</td><td>Set up attack infrastructure (domains, servers, accounts)</td></tr>
<tr><td>TA0001</td><td>Initial Access</td><td>Get a foothold into the network (phishing, exploit)</td></tr>
<tr><td>TA0002</td><td>Execution</td><td>Run malicious code on the target system</td></tr>
<tr><td>TA0003</td><td>Persistence</td><td>Maintain access even after reboot or password change</td></tr>
<tr><td>TA0004</td><td>Privilege Escalation</td><td>Gain higher permissions — admin or root access</td></tr>
<tr><td>TA0005</td><td>Defence Evasion</td><td>Avoid detection by disabling security tools or hiding</td></tr>
<tr><td>TA0006</td><td>Credential Access</td><td>Steal usernames and passwords (brute force, keylogging)</td></tr>
<tr><td>TA0007</td><td>Discovery</td><td>Understand the internal network — hosts, services, shares</td></tr>
<tr><td>TA0008</td><td>Lateral Movement</td><td>Move from one machine to others inside the network</td></tr>
<tr><td>TA0009</td><td>Collection</td><td>Gather the target data to be exfiltrated</td></tr>
<tr><td>TA0011</td><td>Command &amp; Control</td><td>Communicate back to the attacker's server (C2 beacon)</td></tr>
<tr><td>TA0010</td><td>Exfiltration</td><td>Send stolen data out of the organisation</td></tr>
<tr><td>TA0040</td><td>Impact</td><td>Destroy, encrypt or disrupt systems (ransomware)</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# How our tool maps it
st.markdown("##### How AI Threat Hunter Maps to MITRE ATT&CK")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                color:#ff8800;font-weight:700;margin-bottom:0.6rem;">
        Example 1 — Port Scan Detected
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#c8d6e5;line-height:2.1;">
        <span style="color:#00d4ff;">Tactic</span>&nbsp;&nbsp;&nbsp;&nbsp;: TA0043 — Reconnaissance<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#00ff88;">Technique</span>&nbsp;: T1046 — Network Service Discovery<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#ffaa00;">Meaning</span>&nbsp;&nbsp;&nbsp;: Attacker mapping open ports<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;before the real attack<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#ff4444;">IR Action</span>&nbsp;&nbsp;: Block source IP · Check firewall<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logs for follow-up activity
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#0a1628;border:1px solid #1e3a5f;border-radius:8px;padding:1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                color:#ff4444;font-weight:700;margin-bottom:0.6rem;">
        Example 2 — Data Exfiltration Detected
    </div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#c8d6e5;line-height:2.1;">
        <span style="color:#00d4ff;">Tactic</span>&nbsp;&nbsp;&nbsp;&nbsp;: TA0010 — Exfiltration<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#00ff88;">Technique</span>&nbsp;: T1048.003 — Exfil via<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Unencrypted Protocol<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#ffaa00;">Meaning</span>&nbsp;&nbsp;&nbsp;: Data being stolen out of<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;network right now<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
        <span style="color:#ff4444;">IR Action</span>&nbsp;&nbsp;: Block destination IP ·<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Preserve forensic evidence
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Full mapping table for all 5 threat types
st.markdown("##### All 5 Threats — Full MITRE ATT&CK Mapping")
st.markdown("""
<table class="info-table">
<tr>
    <th>Threat Type</th>
    <th>Tactic ID</th>
    <th>Tactic</th>
    <th>Technique ID</th>
    <th>Technique Name</th>
    <th>Kill Chain Phase</th>
</tr>
<tr>
    <td><b style="color:#ff8800;">Port Scan</b></td>
    <td>TA0043</td>
    <td>Reconnaissance</td>
    <td>T1046</td>
    <td>Network Service Discovery</td>
    <td>Reconnaissance</td>
</tr>
<tr>
    <td><b style="color:#ff4444;">Brute Force</b></td>
    <td>TA0006</td>
    <td>Credential Access</td>
    <td>T1110.001</td>
    <td>Password Guessing</td>
    <td>Exploitation</td>
</tr>
<tr>
    <td><b style="color:#ff2277;">Data Exfiltration</b></td>
    <td>TA0010</td>
    <td>Exfiltration</td>
    <td>T1048.003</td>
    <td>Exfil via Unencrypted Protocol</td>
    <td>Exfiltration</td>
</tr>
<tr>
    <td><b style="color:#aa44ff;">C2 / Suspicious</b></td>
    <td>TA0011</td>
    <td>Command &amp; Control</td>
    <td>T1071.001</td>
    <td>Application Layer Protocol</td>
    <td>Command &amp; Control</td>
</tr>
<tr>
    <td><b style="color:#00d4ff;">Anomalous Traffic</b></td>
    <td>TA0007</td>
    <td>Discovery</td>
    <td>T1040</td>
    <td>Network Sniffing</td>
    <td>Reconnaissance</td>
</tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Cyber Kill Chain
st.markdown("##### Cyber Kill Chain — 7 Phases")
st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#8ab0c8;
            margin-bottom:0.6rem;line-height:1.6;">
    The Kill Chain maps <i>when</i> in an attack an event occurs. MITRE ATT&CK maps <i>what</i> was done.
    Together they give a complete picture of the attack.
</div>
""", unsafe_allow_html=True)

phases = [
    ("1", "Reconnaissance", "Attacker gathers info — target IPs, open ports, employee names",       "#4a7a9b"),
    ("2", "Weaponisation",  "Builds the attack tool — exploit, malware, phishing email",             "#ffaa00"),
    ("3", "Delivery",       "Sends the weapon — phishing link, USB drop, drive-by download",         "#ff8800"),
    ("4", "Exploitation",   "Weapon triggers — vulnerability exploited, code executes",              "#ff4444"),
    ("5", "Installation",   "Malware installs, persistence established, backdoor created",           "#ff2277"),
    ("6", "Command &amp; Control", "Attacker connects back to malware, issues commands remotely",    "#aa44ff"),
    ("7", "Exfiltration / Impact", "Data stolen, systems encrypted, services disrupted",            "#00d4ff"),
]

chain_html = '<table class="info-table"><tr><th>#</th><th>Phase</th><th>What Happens</th></tr>'
for num, phase, desc, col in phases:
    chain_html += f'<tr><td><b style="color:{col};">{num}</b></td><td><b style="color:{col};">{phase}</b></td><td>{desc}</td></tr>'
chain_html += '</table>'
st.markdown(chain_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Why it matters
st.markdown("##### Why MITRE ATT&CK Matters")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="background:#0d1526;border:1px solid #1e3a5f;border-left:3px solid #00ff88;
                border-radius:8px;padding:0.8rem 1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                color:#00ff88;font-weight:700;margin-bottom:0.4rem;">Common Language</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#c8d6e5;line-height:1.8;">
        A SOC analyst in India and one in the US mean exactly the same thing when they say
        <b style="color:#00d4ff;">T1110.001</b>. No ambiguity, no translation needed.
    </div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div style="background:#0d1526;border:1px solid #1e3a5f;border-left:3px solid #00d4ff;
                border-radius:8px;padding:0.8rem 1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                color:#00d4ff;font-weight:700;margin-bottom:0.4rem;">Actionable</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#c8d6e5;line-height:1.8;">
        Every technique has documented <b>detection methods</b> and <b>mitigations</b> —
        the analyst knows exactly what to do next.
    </div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div style="background:#0d1526;border:1px solid #1e3a5f;border-left:3px solid #ffaa00;
                border-radius:8px;padding:0.8rem 1rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                color:#ffaa00;font-weight:700;margin-bottom:0.4rem;">Industry Standard</div>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#c8d6e5;line-height:1.8;">
        Used by <b>Splunk, Microsoft Sentinel, CrowdStrike</b> and every major SIEM.
        400+ techniques from real-world attacks, updated continuously.
    </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 11 — FAQ
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-bar"><span>11 — FAQ</span></div>', unsafe_allow_html=True)

faqs = [
    ("Can I use my own network logs?",
     "Yes. Upload any CSV with source_ip, dest_ip, dest_port, protocol, bytes_sent, bytes_recv, action. JSON and syslog also supported. Extra columns are ignored."),
    ("What if I have no API keys?",
     "Deepfake Detector falls back to heuristic-only analysis (FFT + ELA + noise). AI Threat Hunter falls back to rule-based forensic reports. Both tools remain functional."),
    ("How do I adjust detection sensitivity?",
     "Use the Sensitivity slider in the AI Threat Hunter sidebar. Low (1-3) = only extreme outliers. Medium (4-6) = balanced. High (7-10) = catches subtle attacks with more false positives."),
    ("How do I stop the live feed?",
     "Press Ctrl+C in the terminal running live_log_generator.py. The CSV file stays on disk."),
    ("Can the PDF be regenerated after changes?",
     "Yes: python generate_pdf.py — output is always Cyber_Security_Suite_Project.pdf in the project root."),
    ("The Isolation Forest finds too many / too few threats.",
     "Adjust the Sensitivity slider. Low = few alerts, High = many alerts. Default (5) typically flags 5-15% of traffic."),
]
for q, a in faqs:
    with st.expander(f"❓  {q}"):
        st.markdown(a)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;margin-top:1rem;
            font-family:'Share Tech Mono',monospace;font-size:0.65rem;
            color:#1e3a5f;letter-spacing:3px;border-top:1px solid #1e3a5f;">
    ⬡ CYBER SECURITY SUITE &nbsp;·&nbsp; AI THREAT HUNTER &nbsp;·&nbsp; DEEPFAKE DETECTOR &nbsp;·&nbsp; 2026 ⬡
</div>
""", unsafe_allow_html=True)
