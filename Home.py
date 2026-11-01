"""
CYBER SECURITY SUITE — Main landing page
Run with:  streamlit run Home.py
"""
import streamlit as st

st.set_page_config(
    page_title="Cyber Security Suite",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    background-color: #0d1526 !important;
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * { color: #c8d6e5 !important; }
#MainMenu, footer, header { visibility: hidden; }

.hero {
    text-align: center;
    padding: 3rem 2rem 2.5rem;
}
.hero-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 3.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00ff88, #00d4ff, #ff4444, #00ff88);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 5s infinite linear;
    letter-spacing: 6px;
    margin-bottom: 0.5rem;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:300%} }
.hero-sub {
    font-size: 1rem;
    color: #4a7a9b;
    letter-spacing: 4px;
    text-transform: uppercase;
}
.tool-card {
    background: linear-gradient(135deg, #0d1526, #101f3a);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 2.2rem 2rem 1.8rem;
    margin: 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.tool-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 20px 20px 0 0;
}
.card-deepfake::before { background: linear-gradient(90deg, #ff4444, #ff8800); }
.card-threat::before   { background: linear-gradient(90deg, #00ff88, #00d4ff); }
.tool-card:hover {
    transform: translateY(-6px);
    border-color: #00d4ff;
    box-shadow: 0 12px 40px rgba(0,212,255,0.2);
}
.tool-icon { font-size: 4rem; margin-bottom: 1.2rem; }
.tool-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 0.6rem;
    letter-spacing: 2px;
}
.tool-desc {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.76rem;
    color: #8ab0c8;
    line-height: 1.8;
    margin-bottom: 1.2rem;
}
.tag {
    display: inline-block;
    background: #1e3a5f;
    color: #00d4ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 3px;
}
.tag-red   { background: #3d0000; color: #ff4444; }
.tag-green { background: #003020; color: #00ff88; }
.launch-btn {
    display: inline-block;
    margin-top: 1.2rem;
    background: linear-gradient(135deg, #00ff88, #00d4ff);
    color: #0a0e1a !important;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 2px;
    padding: 0.5rem 1.6rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    text-decoration: none;
}
.stats-bar {
    display: flex;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
    padding: 1.5rem 2rem;
    background: #0d1526;
    border-radius: 16px;
    border: 1px solid #1e3a5f;
    margin: 1.5rem 0;
}
.stat-item { text-align: center; }
.stat-val {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #00d4ff;
}
.stat-lbl {
    font-size: 0.65rem;
    color: #4a7a9b;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.tech-chip {
    display: inline-block;
    background: #0d1526;
    border: 1px solid #1e3a5f;
    color: #8ab0c8;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">⬡ CYBER SECURITY SUITE ⬡</div>
    <div class="hero-sub">AI-Powered Threat Intelligence · Forensics · Incident Response</div>
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
        <div class="stat-lbl">Analysis Dimensions</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">MITRE</div>
        <div class="stat-lbl">ATT&amp;CK Mapped</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">Real-Time</div>
        <div class="stat-lbl">Detection</div>
    </div>
    <div class="stat-item">
        <div class="stat-val">AI</div>
        <div class="stat-lbl">Key Rotation</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tool cards ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="tool-card card-deepfake">
        <div class="tool-icon">🔍</div>
        <div class="tool-name" style="color:#ff8800;">DEEPFAKE DETECTOR</div>
        <div class="tool-desc">
            Multi-dimensional AI forensic analysis of images and videos.<br>
            Detects AI-generated faces, GAN artifacts, splicing, and manipulation.<br>
            Supports images, PDFs, and QR code scanning.
        </div>
        <div>
            <span class="tag tag-red">Facial Forensics</span>
            <span class="tag tag-red">GAN Detection</span>
            <span class="tag tag-red">QR Scanner</span>
            <span class="tag">PDF Analysis</span>
            <span class="tag">7-Dimension AI Report</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍  Launch Deepfake Detector", use_container_width=True, key="launch_deepfake"):
        st.switch_page("pages/1_Deepfake_Detector.py")

with col2:
    st.markdown("""
    <div class="tool-card card-threat">
        <div class="tool-icon">🛡️</div>
        <div class="tool-name" style="color:#00d4ff;">AI THREAT HUNTER</div>
        <div class="tool-desc">
            Real-time network log analysis using Isolation Forest anomaly detection.<br>
            MITRE ATT&amp;CK mapped alerts with AI-generated incident response playbooks.<br>
            Kill chain analysis, IOC extraction, and threat actor profiling.
        </div>
        <div>
            <span class="tag tag-green">MITRE ATT&amp;CK</span>
            <span class="tag tag-green">Kill Chain</span>
            <span class="tag tag-green">IR Playbook</span>
            <span class="tag">Isolation Forest</span>
            <span class="tag">Network Graph</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛡️  Launch AI Threat Hunter", use_container_width=True, key="launch_threat"):
        st.switch_page("pages/2_AI_Threat_Hunter.py")

# ── Tech stack ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;padding:1rem 0 0.5rem;">
    <div style="font-size:0.75rem;color:#4a7a9b;letter-spacing:3px;margin-bottom:0.8rem;">TECHNOLOGY STACK</div>
    <span class="tech-chip">Streamlit</span>
    <span class="tech-chip">Isolation Forest</span>
    <span class="tech-chip">AI Vision API</span>
    <span class="tech-chip">MITRE ATT&CK</span>
    <span class="tech-chip">OpenCV</span>
    <span class="tech-chip">Plotly</span>
    <span class="tech-chip">PyMuPDF</span>
    <span class="tech-chip">Pandas</span>
    <span class="tech-chip">NumPy</span>
    <span class="tech-chip">Key Rotation Pool</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:1.5rem;color:#1e3a5f;font-size:0.72rem;letter-spacing:2px;margin-top:1rem;">
    ⬡ CYBER SECURITY SUITE · AI VISION FORENSICS · MITRE ATT&CK · EDITION 2026 ⬡
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:1.2rem;color:#00ff88;
                letter-spacing:3px;text-align:center;padding:1rem 0 0.5rem;">
        🔐 CYBER SUITE
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Select a tool from the main page or use the navigation above.**")
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#4a7a9b;line-height:2;">
        🔍 Deepfake Detector<br>
        🛡️ AI Threat Hunter<br>
    </div>
    """, unsafe_allow_html=True)
