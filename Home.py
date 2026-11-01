"""
CYBER SECURITY SUITE — Landing page / navigation hub
Run:  python -m streamlit run Home.py
"""
import streamlit as st

st.set_page_config(
    page_title="Cyber Security Suite",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
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

/* ── Hero ── */
.hero-wrap {
    text-align: center;
    padding: 2.8rem 1rem 2rem;
}
.hero-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00ff88 0%, #00d4ff 40%, #ff4444 70%, #00ff88 100%);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 5s infinite linear;
    letter-spacing: 6px;
    margin-bottom: 0.4rem;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:300%} }
.hero-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #4a7a9b;
    letter-spacing: 4px;
    text-transform: uppercase;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
    padding: 1.2rem 2rem;
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    margin: 0.5rem 0 2rem 0;
}
.stat-item { text-align: center; min-width: 80px; }
.stat-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #00d4ff;
    line-height: 1.2;
}
.stat-lbl {
    font-size: 0.62rem;
    color: #4a7a9b;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Tool cards ── */
.tool-card {
    background: linear-gradient(135deg, #0d1526, #101f3a);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.tool-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 0 0 20px 20px;
}
.card-deep::after { background: linear-gradient(90deg, #ff4444, #ff8800); }
.card-hunt::after { background: linear-gradient(90deg, #00ff88, #00d4ff); }
.tool-icon { font-size: 3.8rem; margin-bottom: 1rem; }
.tool-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 0.6rem;
}
.tool-desc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #8ab0c8;
    line-height: 1.9;
    min-height: 80px;
    margin-bottom: 1.2rem;
}
.tag-row { margin: 0.6rem 0 1.4rem 0; }
.tag {
    display: inline-block;
    background: #1e3a5f;
    color: #00d4ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.62rem;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 3px 2px;
}
.tag-red   { background: #3d0a0a; color: #ff6666; }
.tag-green { background: #0a2a1a; color: #00ff88; }

/* ── How it works ── */
.how-card {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
}
.how-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #c8d6e5;
    line-height: 1.7;
}
.step-num {
    min-width: 28px;
    height: 28px;
    background: linear-gradient(135deg, #00ff88, #00d4ff);
    color: #0a0e1a;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.8rem;
    flex-shrink: 0;
}

/* ── Tech chips ── */
.tech-chip {
    display: inline-block;
    background: #0d1526;
    border: 1px solid #1e3a5f;
    color: #8ab0c8;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.63rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 4px;
}

/* Streamlit button override */
.stButton > button {
    background: linear-gradient(135deg, #00ff88, #00d4ff) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    padding: 0.6rem 1.4rem !important;
    width: 100%;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.2rem 0 0.8rem;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:1.3rem;
                    color:#00ff88;letter-spacing:3px;">🔐 CYBER SUITE</div>
        <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;margin-top:4px;">
            AI SECURITY TOOLS 2026
        </div>
    </div>
    <hr style="border-color:#1e3a5f;margin:0.5rem 0 1rem 0;">
    """, unsafe_allow_html=True)
    st.markdown("**Navigate to a tool:**")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#8ab0c8;line-height:2.2;">
        🔍 &nbsp;<b style="color:#ff8800;">Deepfake Detector</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;→ AI media forensics<br>
        🛡️ &nbsp;<b style="color:#00d4ff;">AI Threat Hunter</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;→ Network threat detection
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#4a7a9b;line-height:1.8;">
        Use the sidebar navigation<br>above or the launch buttons<br>on the main page.
    </div>
    """, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">⬡ CYBER SECURITY SUITE ⬡</div>
    <div class="hero-sub">AI-Powered Threat Intelligence · Media Forensics · Incident Response</div>
</div>
""", unsafe_allow_html=True)

# ── Stats bar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-val">2</div>
        <div class="stat-lbl">AI Tools</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">12+</div>
        <div class="stat-lbl">Dimensions</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">MITRE</div>
        <div class="stat-lbl">ATT&amp;CK</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">3</div>
        <div class="stat-lbl">AI Providers</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">Live</div>
        <div class="stat-lbl">Detection</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">IR</div>
        <div class="stat-lbl">Playbook Gen</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tool cards ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("""
    <div class="tool-card card-deep">
        <div class="tool-icon">🔍</div>
        <div class="tool-name" style="color:#ff8800;">DEEPFAKE DETECTOR</div>
        <div class="tool-desc">
            Multi-dimensional AI forensics for images, videos &amp; PDFs.<br>
            Detects GAN artifacts, face swaps, inpainting &amp; splicing.<br>
            QR code scanning &amp; document authenticity checks.
        </div>
        <div class="tag-row">
            <span class="tag tag-red">Face Swap</span>
            <span class="tag tag-red">GAN Artifacts</span>
            <span class="tag tag-red">Inpainting</span>
            <span class="tag">QR Scanner</span>
            <span class="tag">PDF Support</span>
            <span class="tag">7-Dimension AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍  Launch Deepfake Detector", key="btn_deepfake"):
        st.switch_page("pages/1_Deepfake_Detector.py")

with col_right:
    st.markdown("""
    <div class="tool-card card-hunt">
        <div class="tool-icon">🛡️</div>
        <div class="tool-name" style="color:#00d4ff;">AI THREAT HUNTER</div>
        <div class="tool-desc">
            Real-time network anomaly detection via Isolation Forest ML.<br>
            MITRE ATT&amp;CK mapped alerts with kill chain analysis.<br>
            AI-generated incident response playbooks on demand.
        </div>
        <div class="tag-row">
            <span class="tag tag-green">MITRE ATT&amp;CK</span>
            <span class="tag tag-green">Kill Chain</span>
            <span class="tag tag-green">IR Playbook</span>
            <span class="tag">Isolation Forest</span>
            <span class="tag">Network Graph</span>
            <span class="tag">IOC Extraction</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛡️  Launch AI Threat Hunter", key="btn_threat"):
        st.switch_page("pages/2_AI_Threat_Hunter.py")

# ── How it works ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col_d, col_t = st.columns(2, gap="large")

with col_d:
    st.markdown("#### 🔍 How Deepfake Detector Works")
    st.markdown("""
    <div class="how-card">
        <div class="how-step">
            <div class="step-num">1</div>
            <div>Upload image, video, PDF, or screenshot</div>
        </div>
        <div class="how-step">
            <div class="step-num">2</div>
            <div>Heuristic pre-analysis: frequency domain, ELA, noise patterns, compression artifacts</div>
        </div>
        <div class="how-step">
            <div class="step-num">3</div>
            <div>AI Vision engine analyses 7 forensic dimensions — facial biometrics, GAN patterns, lighting consistency, etc.</div>
        </div>
        <div class="how-step">
            <div class="step-num">4</div>
            <div>Rich forensic report: manipulation type, evidence list, provenance assessment &amp; recommendation</div>
        </div>
        <div class="how-step">
            <div class="step-num">5</div>
            <div>Download full AI report as text file</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_t:
    st.markdown("#### 🛡️ How AI Threat Hunter Works")
    st.markdown("""
    <div class="how-card">
        <div class="how-step">
            <div class="step-num">1</div>
            <div>Upload CSV / JSON / syslog network logs — or use built-in sample data</div>
        </div>
        <div class="how-step">
            <div class="step-num">2</div>
            <div>Isolation Forest ML detects anomalies in traffic patterns: port scans, brute force, exfiltration, C2</div>
        </div>
        <div class="how-step">
            <div class="step-num">3</div>
            <div>AI maps each threat to MITRE ATT&amp;CK tactic + technique + sub-technique, profiles threat actor</div>
        </div>
        <div class="how-step">
            <div class="step-num">4</div>
            <div>Dashboard shows timeline, heatmap, network graph and MITRE ATT&amp;CK coverage</div>
        </div>
        <div class="how-step">
            <div class="step-num">5</div>
            <div>Generate &amp; download IR playbook — immediate actions, investigation, containment, remediation</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Tech stack ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:0.8rem 0 0.4rem;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                color:#4a7a9b;letter-spacing:3px;margin-bottom:0.8rem;">TECHNOLOGY STACK</div>
    <span class="tech-chip">Streamlit</span>
    <span class="tech-chip">Isolation Forest</span>
    <span class="tech-chip">AI Vision API</span>
    <span class="tech-chip">MITRE ATT&CK</span>
    <span class="tech-chip">OpenCV</span>
    <span class="tech-chip">Plotly</span>
    <span class="tech-chip">PyMuPDF</span>
    <span class="tech-chip">Pandas · NumPy</span>
    <span class="tech-chip">Key Rotation Pool</span>
    <span class="tech-chip">Scikit-Learn</span>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0.5rem;margin-top:1rem;
            font-family:'Share Tech Mono',monospace;font-size:0.65rem;
            color:#1e3a5f;letter-spacing:3px;border-top:1px solid #1e3a5f;">
    ⬡ CYBER SECURITY SUITE · AI VISION FORENSICS · MITRE ATT&amp;CK · EDITION 2026 ⬡
</div>
""", unsafe_allow_html=True)
