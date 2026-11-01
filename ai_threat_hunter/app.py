import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import io
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

from core.detector import ThreatDetector
from core.explainer import ThreatExplainer
from core.log_parser import LogParser
from core.sample_logs import generate_sample_logs
from core.key_rotator import pool_ready, next_key

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Threat Hunter",
    page_icon="🛡️",
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
    background-color: #0d1526 !important;
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * { color: #c8d6e5 !important; }

.cyber-header {
    text-align: center;
    padding: 1.5rem 0 0.8rem;
    background: linear-gradient(135deg, #0d1526 0%, #0a1628 100%);
    border-bottom: 2px solid #00ff88;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 30px rgba(0, 255, 136, 0.15);
}
.cyber-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00ff88, #00d4ff, #00ff88);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s infinite linear;
    letter-spacing: 4px;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }
.cyber-subtitle {
    font-size: 0.9rem;
    color: #5a8a7a;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: -0.2rem;
}

.metric-card {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.4);
    transition: border-color 0.3s, box-shadow 0.3s;
}
.metric-card:hover { border-color: #00d4ff; box-shadow: 0 4px 20px rgba(0,212,255,0.15); }
.metric-card.critical { border-color: #ff4444; box-shadow: 0 0 18px rgba(255,68,68,0.25); }
.metric-card.warning  { border-color: #ffaa00; box-shadow: 0 0 14px rgba(255,170,0,0.2); }
.metric-card.safe     { border-color: #00ff88; box-shadow: 0 0 14px rgba(0,255,136,0.2); }
.metric-label { font-size: 0.72rem; color: #4a7a9b; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.2rem; }
.metric-value { font-family: 'Share Tech Mono', monospace; font-size: 2rem; font-weight: 700; }
.metric-value.green  { color: #00ff88; }
.metric-value.red    { color: #ff4444; }
.metric-value.orange { color: #ffaa00; }
.metric-value.cyan   { color: #00d4ff; }

@keyframes pulse-red {
    0%   { box-shadow: 0 0 0 0 rgba(255,68,68,0.5); }
    70%  { box-shadow: 0 0 0 10px rgba(255,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(255,68,68,0); }
}
.pulse-critical { animation: pulse-red 2s infinite; }

.severity-badge {
    display: inline-block;
    padding: 0.2rem 0.8rem;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-right: 0.5rem;
}
.badge-CRITICAL { background: #3d0000; color: #ff4444; border: 1px solid #ff4444; }
.badge-HIGH     { background: #3d2a00; color: #ffaa00; border: 1px solid #ffaa00; }
.badge-MEDIUM   { background: #003040; color: #00d4ff; border: 1px solid #00d4ff; }
.badge-LOW      { background: #003020; color: #00ff88; border: 1px solid #00ff88; }

.stTabs [data-baseweb="tab-list"] { background: #0d1526; border-radius: 8px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #4a7a9b !important; border-radius: 6px; font-weight: 600; }
.stTabs [aria-selected="true"] { background: #1e3a5f !important; color: #00d4ff !important; }

[data-testid="stDataFrameResizable"] { background: #0d1526; border: 1px solid #1e3a5f; border-radius: 8px; }

.stButton>button {
    background: linear-gradient(135deg, #00ff88, #00d4ff);
    color: #0a0e1a !important;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 0.5rem 1.2rem;
    transition: opacity 0.2s;
}
.stButton>button:hover { opacity: 0.85; }

.section-hdr {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 2px;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 6px;
    margin: 1.2rem 0 0.8rem 0;
    text-transform: uppercase;
}
.info-line {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #8ab0c8;
    line-height: 1.9;
}
.bullet-item {
    background: #0d1526;
    border-left: 3px solid;
    padding: 0.4rem 1rem;
    margin-bottom: 0.35rem;
    border-radius: 0 8px 8px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #c8d6e5;
    line-height: 1.6;
}
.mitre-box {
    background: linear-gradient(135deg, #0d1526, #101f3a);
    border: 1px solid #00d4ff44;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    line-height: 2.0;
}
.sidebar-logo { font-family: 'Share Tech Mono', monospace; font-size: 1.3rem; color: #00ff88; letter-spacing: 3px; text-align: center; padding: 1rem 0 0.5rem; }
.sidebar-divider { border-top: 1px solid #1e3a5f; margin: 1rem 0; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

COLOURS = {
    "Port Scan": "#ffaa00",
    "Brute Force": "#ff4444",
    "Data Exfiltration": "#ff2277",
    "C2 / Suspicious": "#aa44ff",
    "Anomalous Traffic": "#00d4ff",
    "normal": "#1e3a5f",
}
SEVERITY_COLOR = {"CRITICAL": "#ff4444", "HIGH": "#ffaa00", "MEDIUM": "#00d4ff", "LOW": "#00ff88"}
CATEGORY_ICON = {
    "Reconnaissance": "🔭", "Initial Access": "🚪", "Execution": "⚙️",
    "Persistence": "🔒", "Privilege Escalation": "⬆️", "Defense Evasion": "🕶️",
    "Credential Access": "🔑", "Discovery": "🔍", "Lateral Movement": "➡️",
    "Collection": "📦", "Exfiltration": "📤", "Impact": "💥", "C2": "📡",
}
_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,21,38,0.6)",
    font=dict(color="#c8d6e5", family="Rajdhani"),
    margin=dict(l=10, r=10, t=40, b=10),
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _metric_card(label, value, css_class="", value_class="cyan"):
    pulse = " pulse-critical" if css_class == "critical" else ""
    return f"""<div class="metric-card {css_class}{pulse}">
        <div class="metric-label">{label}</div>
        <div class="metric-value {value_class}">{value}</div>
    </div>"""


def _bullet(text: str, color: str) -> str:
    return f'<div class="bullet-item" style="border-color:{color};">{text}</div>'


def render_threat_report(expl: dict, row: pd.Series | None = None):
    """Full rich threat analysis report — no brand names, all AI output."""
    sev = expl.get("severity", "MEDIUM")
    confidence = expl.get("confidence", 70)
    title = expl.get("title", "Unknown Threat")
    category = expl.get("threat_category", "Unknown")
    kill_chain = expl.get("kill_chain_phase", "Unknown")
    exec_summary = expl.get("executive_summary", "")
    evidence = expl.get("evidence_analysis", "")
    impact = expl.get("impact_assessment", "")
    fp_likelihood = expl.get("false_positive_likelihood", "Medium")
    fp_explanation = expl.get("false_positive_explanation", "")
    mitre = expl.get("mitre_attack", {})
    actor = expl.get("threat_actor_profile", {})
    iocs = expl.get("indicators_of_compromise", [])
    immediate = expl.get("immediate_actions", [])
    investigation = expl.get("investigation_steps", [])
    containment = expl.get("containment_eradication", [])
    remediation = expl.get("long_term_remediation", [])
    analyst_notes = expl.get("analyst_notes", "")
    related = expl.get("related_threat_types", [])

    sev_color = SEVERITY_COLOR.get(sev, "#8b949e")
    cat_icon = CATEGORY_ICON.get(category, "⚠️")
    fp_color = {"Very Low": "#00ff88", "Low": "#00ff88", "Medium": "#ffaa00", "High": "#ff4444"}.get(fp_likelihood, "#ffaa00")

    # ── Banner ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1526,#101f3a);
                border:2px solid {sev_color};border-radius:16px;
                padding:1.4rem 1.8rem;box-shadow:0 0 30px {sev_color}22;margin-bottom:1.2rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <span class="severity-badge badge-{sev}">{sev}</span>
                <span style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#8b949e;">
                    AI CONFIDENCE: {confidence}%
                </span>
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;font-weight:700;
                            color:{sev_color};margin-top:0.4rem;">{title}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;margin-bottom:2px;">CATEGORY</div>
                <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#00d4ff;">
                    {cat_icon} {category}
                </div>
                <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;margin-top:6px;margin-bottom:2px;">KILL CHAIN</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#ffaa00;">{kill_chain}</div>
            </div>
        </div>
        <hr style="border-color:#1e3a5f;margin:1rem 0;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.82rem;
                    color:#c8d6e5;line-height:1.9;border-left:4px solid {sev_color};padding-left:1.2rem;">
            {exec_summary}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Alert meta row ────────────────────────────────────────────────────────
    if row is not None:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Source IP", row.get("source_ip", "N/A"))
        c2.metric("Destination", f"{row.get('dest_ip','?')}:{row.get('dest_port','?')}")
        c3.metric("Protocol", row.get("protocol", "N/A"))
        c4.metric("Bytes Out", f"{int(row.get('bytes_sent',0)):,}")
        c5.metric("Risk Score", f"{int(row.get('risk_score',0))}/100")

    # ── MITRE ATT&CK ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">🎯 MITRE ATT&CK MAPPING</div>', unsafe_allow_html=True)
    tactic_id = mitre.get("tactic_id", "")
    tactic_name = mitre.get("tactic_name", "")
    tech_id = mitre.get("technique_id", "")
    tech_name = mitre.get("technique_name", "")
    sub_id = mitre.get("sub_technique_id") or ""
    sub_name = mitre.get("sub_technique_name") or ""
    st.markdown(f"""
    <div class="mitre-box">
        <div style="display:flex;gap:3rem;flex-wrap:wrap;">
            <div>
                <div style="color:#4a7a9b;font-size:0.65rem;letter-spacing:2px;">TACTIC</div>
                <div style="color:#00d4ff;font-size:1rem;font-weight:700;">{tactic_id}</div>
                <div style="color:#c8d6e5;">{tactic_name}</div>
            </div>
            <div style="color:#1e3a5f;font-size:2rem;">→</div>
            <div>
                <div style="color:#4a7a9b;font-size:0.65rem;letter-spacing:2px;">TECHNIQUE</div>
                <div style="color:#ffaa00;font-size:1rem;font-weight:700;">{tech_id}</div>
                <div style="color:#c8d6e5;">{tech_name}</div>
            </div>
            {'<div style="color:#1e3a5f;font-size:2rem;">→</div><div><div style="color:#4a7a9b;font-size:0.65rem;letter-spacing:2px;">SUB-TECHNIQUE</div><div style="color:#ff4444;font-size:1rem;font-weight:700;">' + sub_id + '</div><div style="color:#c8d6e5;">' + sub_name + '</div></div>' if sub_id else ''}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Evidence + Impact ─────────────────────────────────────────────────────
    col_ev, col_imp = st.columns(2)
    with col_ev:
        st.markdown('<div class="section-hdr">🔬 EVIDENCE ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line">{evidence}</div>', unsafe_allow_html=True)
    with col_imp:
        st.markdown('<div class="section-hdr">💥 IMPACT ASSESSMENT</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line">{impact}</div>', unsafe_allow_html=True)

    # ── Threat Actor ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">🕵️ THREAT ACTOR PROFILE</div>', unsafe_allow_html=True)
    actor_type = actor.get("type", "Unknown")
    sophistication = actor.get("sophistication", "Unknown")
    motivation = actor.get("motivation", "Unknown")
    actor_analysis = actor.get("analysis", "")
    soph_color = {"Low": "#00ff88", "Medium": "#ffaa00", "High": "#ff4444", "Nation-State": "#ff0055"}.get(sophistication, "#8b949e")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;
                    padding:0.8rem;text-align:center;">
            <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;">ACTOR TYPE</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:#00d4ff;">{actor_type}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;
                    padding:0.8rem;text-align:center;">
            <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;">SOPHISTICATION</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:{soph_color};">{sophistication}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;
                    padding:0.8rem;text-align:center;">
            <div style="font-size:0.65rem;color:#4a7a9b;letter-spacing:2px;">MOTIVATION</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;color:#ffaa00;">{motivation}</div>
        </div>""", unsafe_allow_html=True)
    if actor_analysis:
        st.markdown(f'<div class="info-line" style="margin-top:0.5rem;">{actor_analysis}</div>', unsafe_allow_html=True)

    # ── IOCs ──────────────────────────────────────────────────────────────────
    if iocs:
        st.markdown('<div class="section-hdr">🔴 INDICATORS OF COMPROMISE (IOCs)</div>', unsafe_allow_html=True)
        for ioc in iocs:
            if ioc:
                st.markdown(_bullet(ioc, "#ff4444"), unsafe_allow_html=True)

    # ── False Positive ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#0d1526;border:1px solid {fp_color}44;border-radius:8px;
                padding:0.7rem 1.2rem;font-family:'Share Tech Mono',monospace;
                font-size:0.78rem;color:#c8d6e5;line-height:1.8;margin:0.8rem 0;">
        <span style="color:{fp_color};font-weight:700;">False Positive Likelihood: {fp_likelihood}</span>
        &nbsp;—&nbsp; {fp_explanation}
    </div>""", unsafe_allow_html=True)

    # ── Related Threats ───────────────────────────────────────────────────────
    if related:
        badges = " ".join(f'<span style="background:#1e3a5f;color:#00d4ff;font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;padding:3px 10px;border-radius:12px;margin-right:4px;">{t}</span>' for t in related)
        st.markdown(f'<div style="margin:0.5rem 0;">Related: {badges}</div>', unsafe_allow_html=True)


def render_ir_playbook(expl: dict):
    """Render the Incident Response playbook section."""
    sev = expl.get("severity", "MEDIUM")
    sev_color = SEVERITY_COLOR.get(sev, "#8b949e")

    immediate = expl.get("immediate_actions", [])
    investigation = expl.get("investigation_steps", [])
    containment = expl.get("containment_eradication", [])
    remediation = expl.get("long_term_remediation", [])
    analyst_notes = expl.get("analyst_notes", "")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-hdr">🚨 IMMEDIATE ACTIONS (0–15 min)</div>', unsafe_allow_html=True)
        for i, action in enumerate(immediate, 1):
            if action:
                st.markdown(_bullet(f"<b style='color:#ff4444;'>{i}.</b> {action}", "#ff4444"), unsafe_allow_html=True)

        st.markdown('<div class="section-hdr">🔍 INVESTIGATION STEPS</div>', unsafe_allow_html=True)
        for i, step in enumerate(investigation, 1):
            if step:
                st.markdown(_bullet(f"<b style='color:#ffaa00;'>{i}.</b> {step}", "#ffaa00"), unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-hdr">🛡️ CONTAINMENT & ERADICATION</div>', unsafe_allow_html=True)
        for i, step in enumerate(containment, 1):
            if step:
                st.markdown(_bullet(f"<b style='color:#00d4ff;'>{i}.</b> {step}", "#00d4ff"), unsafe_allow_html=True)

        st.markdown('<div class="section-hdr">🔧 LONG-TERM REMEDIATION</div>', unsafe_allow_html=True)
        for i, step in enumerate(remediation, 1):
            if step:
                st.markdown(_bullet(f"<b style='color:#00ff88;'>{i}.</b> {step}", "#00ff88"), unsafe_allow_html=True)

    if analyst_notes:
        st.markdown('<div class="section-hdr">📋 ANALYST NOTES</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:8px;
                    padding:0.8rem 1.2rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.78rem;color:#8ab0c8;line-height:1.9;">
            {analyst_notes}
        </div>""", unsafe_allow_html=True)


def _run_analysis(df: pd.DataFrame, sensitivity: float) -> pd.DataFrame:
    detector = ThreatDetector(sensitivity=sensitivity)
    return detector.analyze(df)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🛡️ THREAT HUNTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("**📁 Data Source**")
    data_mode = st.radio("Mode", ["📂 Upload / Sample", "📡 Live Feed"], horizontal=True)

    uploaded_file = None
    use_sample = False
    live_feed_active = False
    _LIVE_FILE = os.path.join(os.path.dirname(__file__), "live_feed.csv")

    if data_mode == "📂 Upload / Sample":
        uploaded_file = st.file_uploader(
            "Upload Log File", type=["csv", "json", "txt", "log"],
            help="CSV, JSON, or syslog text format",
        )
        use_sample = st.button("⚡ Use Sample Data", use_container_width=True)
    else:
        live_feed_active = True
        if os.path.exists(_LIVE_FILE):
            _live_size = os.path.getsize(_LIVE_FILE)
            _live_rows = max(0, sum(1 for _ in open(_LIVE_FILE)) - 1)
            st.markdown(f"""
            <div style="background:#051a0d;border:1px solid #00ff88;border-radius:8px;
                        padding:0.5rem 1rem;font-family:'Share Tech Mono',monospace;
                        font-size:0.72rem;color:#00ff88;text-align:center;line-height:1.9;">
                📡 LIVE FEED CONNECTED<br>
                <span style="color:#8ab0c8;">{_live_rows:,} events · {_live_size/1024:.1f} KB</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#1a1200;border:1px solid #ffaa00;border-radius:8px;
                        padding:0.6rem 1rem;font-family:'Share Tech Mono',monospace;
                        font-size:0.72rem;color:#ffaa00;line-height:1.8;">
                ⚠️ No live feed found.<br>Run in a terminal:<br>
                <code style="color:#00d4ff;">python live_log_generator.py</code>
            </div>""", unsafe_allow_html=True)
        refresh_secs = st.slider("Auto-refresh every", 5, 60, 10, step=5,
                                 format="%d sec", key="_live_refresh")
        st.caption(f"Dashboard refreshes every {refresh_secs}s automatically")

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    # ── AI Engine status ──────────────────────────────────────────────────────
    st.markdown("**🤖 AI Engine**")
    backup_key = st.text_input(
        "Backup AI Key",
        type="password",
        placeholder="Paste any AI API key here…",
        label_visibility="collapsed",
        help="Optional — the engine has built-in keys. Add yours as backup.",
        key="_backup_key",
    )
    user_key = backup_key or ""

    if pool_ready(user_key):
        st.markdown("""
        <div style="background:#051a0d;border:1px solid #00ff88;border-radius:8px;
                    padding:0.5rem 1rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.72rem;color:#00ff88;text-align:center;">
            ✅ AI Analysis Engine Active
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1a1200;border:1px solid #ffaa00;border-radius:8px;
                    padding:0.5rem 1rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.72rem;color:#ffaa00;text-align:center;">
            ⚠️ AI engines exhausted — rule-based fallback
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown("**⚙️ Detection Settings**")
    sensitivity_raw = st.slider("Sensitivity", 1, 10, 5, help="Higher = more alerts detected")
    sensitivity = sensitivity_raw / 20.0
    st.session_state["_sensitivity"] = sensitivity

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    threat_filter = st.multiselect(
        "Filter Threat Types",
        ["Port Scan", "Brute Force", "Data Exfiltration", "C2 / Suspicious", "Anomalous Traffic"],
        default=["Port Scan", "Brute Force", "Data Exfiltration", "C2 / Suspicious", "Anomalous Traffic"],
    )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""<div class="cyber-header">
    <div class="cyber-title">⬡ AI THREAT HUNTER ⬡</div>
    <div class="cyber-subtitle">Real-Time Anomaly Detection · MITRE ATT&CK Mapping · AI Incident Response</div>
</div>""", unsafe_allow_html=True)

# ── Load / analyse data ───────────────────────────────────────────────────────
if "df_analysed" not in st.session_state:
    st.session_state["df_analysed"] = None
if "explainer" not in st.session_state:
    st.session_state["explainer"] = None

trigger_analysis = False

if live_feed_active:
    if os.path.exists(_LIVE_FILE):
        try:
            raw_df = pd.read_csv(_LIVE_FILE, parse_dates=["timestamp"])
            if len(raw_df) >= 10:
                trigger_analysis = True
                # Auto-refresh by scheduling a rerun after the chosen interval
                time.sleep(0)  # yield to Streamlit
            else:
                st.info("Live feed starting up… waiting for more events.")
                st.stop()
        except Exception as e:
            st.warning(f"Could not read live_feed.csv: {e}")
            st.stop()
    else:
        st.markdown("""
        <div style="background:#0d1526;border:2px dashed #1e3a5f;border-radius:16px;
                    padding:2.5rem;text-align:center;margin:2rem 0;">
            <div style="font-size:3rem;">📡</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:1rem;
                        color:#00d4ff;margin:0.8rem 0;">LIVE FEED NOT STARTED</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
                        color:#8ab0c8;line-height:2;">
                Open a new terminal and run:<br>
                <code style="color:#00ff88;font-size:0.9rem;">
                    cd "C:\\ps\\Projects\\Cyber Security\\ai_threat_hunter"<br>
                    python live_log_generator.py
                </code><br><br>
                Then switch back here — the dashboard will connect automatically.
            </div>
        </div>""", unsafe_allow_html=True)
        st.stop()
elif use_sample or (uploaded_file is None and st.session_state["df_analysed"] is None):
    with st.spinner("Generating sample logs…"):
        raw_df = generate_sample_logs(n_normal=500)
    trigger_analysis = True
elif uploaded_file is not None:
    parser = LogParser()
    ext = Path(uploaded_file.name).suffix.lower()
    with st.spinner("Parsing log file…"):
        raw_df = parser.parse_csv(uploaded_file) if ext == ".csv" else (
            parser.parse_json(uploaded_file) if ext == ".json" else parser.parse_text(uploaded_file)
        )
    trigger_analysis = True

if trigger_analysis:
    with st.spinner("Running ML anomaly detection…"):
        st.session_state["df_analysed"] = _run_analysis(raw_df, sensitivity)
    st.session_state["explainer"] = ThreatExplainer(user_key=user_key)

df = st.session_state["df_analysed"]
if df is None:
    st.info("Upload a log file or click **⚡ Use Sample Data** to begin.")
    st.stop()

# ── Persist live-feed state so tab is restored on page load ──────────────────
if live_feed_active:
    st.session_state["_live_feed_on"] = True
    st.session_state["_live_refresh_secs"] = refresh_secs
elif "_live_feed_on" not in st.session_state:
    st.session_state["_live_feed_on"] = False

threats_df = df[df["is_anomaly"] & df["anomaly_label"].isin(threat_filter)].copy()
stats = ThreatDetector().get_threat_stats(df)
max_risk = int(df["risk_score"].max())
risk_class = "critical" if max_risk >= 70 else ("warning" if max_risk >= 40 else "safe")
risk_val_class = "red" if max_risk >= 70 else ("orange" if max_risk >= 40 else "green")

# ── Metric Row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(_metric_card("Total Events", f"{stats['total_events']:,}", "safe", "cyan"), unsafe_allow_html=True)
with c2:
    st.markdown(_metric_card("Threats Detected", stats["threats_detected"],
                             "critical" if stats["threats_detected"] else "safe",
                             "red" if stats["threats_detected"] else "green"), unsafe_allow_html=True)
with c3:
    st.markdown(_metric_card("Peak Risk Score", f"{max_risk}/100", risk_class, risk_val_class), unsafe_allow_html=True)
with c4:
    critical_count = len(threats_df[threats_df["risk_score"] >= 70])
    st.markdown(_metric_card("Critical Alerts", critical_count,
                             "critical" if critical_count else "safe",
                             "red" if critical_count else "green"), unsafe_allow_html=True)
with c5:
    unique_attackers = threats_df["source_ip"].nunique() if len(threats_df) else 0
    st.markdown(_metric_card("Unique Attackers", unique_attackers, "warning" if unique_attackers else "safe", "orange"), unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", "🚨 Threat Log", "🤖 AI Analysis",
    "🧭 Incident Response", "🕸️ Network Graph", "📡 Live Feed"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("#### Threat Timeline")
        plot_df = df[df["is_anomaly"]].copy()
        plot_df["bytes_sent_k"] = (plot_df["bytes_sent"] / 1000).clip(upper=500)
        fig_timeline = px.scatter(
            plot_df, x="timestamp", y="risk_score",
            color="anomaly_label", size="bytes_sent_k", size_max=30,
            color_discrete_map=COLOURS,
            hover_data=["source_ip", "dest_ip", "dest_port", "bytes_sent"],
            labels={"risk_score": "Risk Score", "anomaly_label": "Threat Type"},
        )
        fig_timeline.update_traces(marker=dict(opacity=0.85, line=dict(width=0.5, color="#0a0e1a")))
        fig_timeline.update_layout(**_PLOTLY_LAYOUT, height=340,
                                   legend=dict(orientation="h", yanchor="bottom", y=1.01),
                                   xaxis=dict(gridcolor="#1e3a5f"),
                                   yaxis=dict(gridcolor="#1e3a5f", range=[0, 105]))
        st.plotly_chart(fig_timeline, use_container_width=True)

    with col_right:
        st.markdown("#### Threat Distribution")
        dist = threats_df["anomaly_label"].value_counts().reset_index()
        dist.columns = ["type", "count"]
        fig_pie = px.pie(dist, values="count", names="type", color="type",
                         color_discrete_map=COLOURS, hole=0.55)
        fig_pie.update_traces(textfont_color="#c8d6e5", pull=[0.04] * len(dist))
        fig_pie.update_layout(**_PLOTLY_LAYOUT, height=300, showlegend=True,
                              legend=dict(orientation="v", font=dict(size=11)))
        st.plotly_chart(fig_pie, use_container_width=True)

    col_bar, col_heat = st.columns(2)
    with col_bar:
        st.markdown("#### Top Attacker IPs")
        ip_counts = (threats_df.groupby("source_ip").size()
                     .sort_values(ascending=True).tail(8).reset_index())
        ip_counts.columns = ["source_ip", "count"]
        fig_bar = px.bar(ip_counts, x="count", y="source_ip", orientation="h",
                         color="count", color_continuous_scale=["#1e3a5f", "#ffaa00", "#ff4444"])
        fig_bar.update_layout(**_PLOTLY_LAYOUT, height=280, coloraxis_showscale=False,
                              xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_heat:
        st.markdown("#### Activity Heatmap (Hour of Day)")
        heat_df = threats_df.copy()
        heat_df["hour"] = heat_df["timestamp"].dt.hour
        heat_df["type_short"] = heat_df["anomaly_label"].str[:12]
        pivot = heat_df.groupby(["type_short", "hour"]).size().unstack(fill_value=0)
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values, x=[f"{h:02d}:00" for h in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[[0, "#0d1526"], [0.5, "#ffaa00"], [1, "#ff4444"]],
            showscale=False,
        ))
        fig_heat.update_layout(**_PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_heat, use_container_width=True)

    # MITRE ATT&CK heatmap
    st.markdown("#### MITRE ATT&CK Coverage")
    mitre_map = {
        "Port Scan":         ("Reconnaissance", "T1046"),
        "Brute Force":       ("Credential Access", "T1110"),
        "Data Exfiltration": ("Exfiltration", "T1048"),
        "C2 / Suspicious":   ("Command & Control", "T1071"),
        "Anomalous Traffic": ("Discovery", "T1040"),
    }
    mitre_counts = threats_df["anomaly_label"].value_counts().to_dict()
    mitre_rows = []
    for label, (tactic, tech) in mitre_map.items():
        count = mitre_counts.get(label, 0)
        if count > 0:
            mitre_rows.append({"Tactic": tactic, "Technique": tech, "Threat": label, "Count": count})
    if mitre_rows:
        mdf = pd.DataFrame(mitre_rows)
        fig_mitre = px.bar(mdf, x="Count", y="Tactic", color="Threat", orientation="h",
                           color_discrete_map=COLOURS, text="Technique",
                           labels={"Count": "Alert Count"})
        fig_mitre.update_traces(textposition="inside", textfont_size=10)
        fig_mitre.update_layout(**_PLOTLY_LAYOUT, height=260,
                                xaxis=dict(gridcolor="#1e3a5f"),
                                yaxis=dict(gridcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig_mitre, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — THREAT LOG
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"**{len(threats_df)} threats detected** — sorted by risk score")
    display_cols = ["timestamp", "source_ip", "dest_ip", "dest_port", "protocol",
                    "bytes_sent", "bytes_recv", "action", "anomaly_label", "risk_score"]
    show_df = threats_df[display_cols].sort_values("risk_score", ascending=False).head(200).copy()
    show_df["timestamp"] = show_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    st.dataframe(show_df, use_container_width=True, height=400)
    csv_buf = io.BytesIO()
    threats_df.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Download Threats CSV", data=csv_buf.getvalue(),
                       file_name="threats_export.csv", mime="text/csv", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI ANALYSIS (deep-dive single threat)
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 🤖 Deep-Dive AI Threat Analysis")
    if len(threats_df) == 0:
        st.info("No threats detected. Adjust sensitivity or upload a different log.")
    else:
        top_threats = threats_df.sort_values("risk_score", ascending=False).head(50)
        labels_for_select = [
            f"[{r['risk_score']}/100]  {r['anomaly_label']}  —  {r['source_ip']} → {r['dest_ip']}:{r['dest_port']}  ({r['timestamp'].strftime('%H:%M:%S')})"
            for _, r in top_threats.iterrows()
        ]
        selected_idx = st.selectbox("Select threat to analyse:", range(len(labels_for_select)),
                                    format_func=lambda i: labels_for_select[i])
        selected_row = top_threats.iloc[selected_idx]

        with st.spinner("🤖 AI Engine generating forensic report…"):
            expl = st.session_state["explainer"].explain(selected_row)

        col_expl, col_gauge = st.columns([4, 1])
        with col_gauge:
            risk = int(selected_row["risk_score"])
            bar_colour = "#ff4444" if risk >= 70 else ("#ffaa00" if risk >= 40 else "#00ff88")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number", value=risk,
                title={"text": "Risk Score", "font": {"color": "#c8d6e5", "size": 13}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#c8d6e5"}},
                    "bar": {"color": bar_colour},
                    "bgcolor": "#0d1526",
                    "steps": [{"range": [0, 40], "color": "#0d2a0d"},
                               {"range": [40, 70], "color": "#2a2000"},
                               {"range": [70, 100], "color": "#2a0000"}],
                    "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.85, "value": risk},
                },
                number={"font": {"color": bar_colour, "size": 36}},
            ))
            fig_gauge.update_layout(**_PLOTLY_LAYOUT, height=240)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_expl:
            render_threat_report(expl, selected_row)

        st.markdown("---")
        st.markdown("#### Risk Score Distribution")
        fig_hist = px.histogram(threats_df, x="risk_score", nbins=20,
                                color="anomaly_label", color_discrete_map=COLOURS,
                                labels={"risk_score": "Risk Score"})
        fig_hist.update_layout(**_PLOTLY_LAYOUT, height=260, bargap=0.05,
                               xaxis=dict(gridcolor="#1e3a5f"), yaxis=dict(gridcolor="#1e3a5f"))
        st.plotly_chart(fig_hist, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INCIDENT RESPONSE PLAYBOOK
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🧭 AI-Generated Incident Response Playbook")
    if len(threats_df) == 0:
        st.info("No threats to generate playbook for.")
    else:
        top_critical = threats_df.sort_values("risk_score", ascending=False).head(20)
        labels_ir = [
            f"[{r['risk_score']}/100]  {r['anomaly_label']}  —  {r['source_ip']} → {r['dest_ip']}:{r['dest_port']}"
            for _, r in top_critical.iterrows()
        ]
        ir_idx = st.selectbox("Generate playbook for:", range(len(labels_ir)),
                              format_func=lambda i: labels_ir[i], key="ir_select")
        ir_row = top_critical.iloc[ir_idx]

        with st.spinner("🧭 Generating incident response playbook…"):
            ir_expl = st.session_state["explainer"].explain(ir_row)

        sev = ir_expl.get("severity", "MEDIUM")
        sev_color = SEVERITY_COLOR.get(sev, "#8b949e")
        st.markdown(f"""
        <div style="background:#0d1526;border-left:5px solid {sev_color};border-radius:0 12px 12px 0;
                    padding:0.8rem 1.4rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.82rem;color:#c8d6e5;line-height:1.8;margin-bottom:1rem;">
            <b style="color:{sev_color};">{ir_expl.get('title','')}</b><br>
            MITRE {ir_expl.get('mitre_attack',{}).get('technique_id','')} ·
            {ir_expl.get('mitre_attack',{}).get('technique_name','')} ·
            Kill Chain: {ir_expl.get('kill_chain_phase','')}
        </div>""", unsafe_allow_html=True)

        render_ir_playbook(ir_expl)

        # Download playbook
        st.markdown("---")
        playbook_lines = [
            "AI-GENERATED INCIDENT RESPONSE PLAYBOOK",
            "=" * 55,
            f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Threat    : {ir_expl.get('title','')}",
            f"Severity  : {sev}  |  AI Confidence: {ir_expl.get('confidence',0)}%",
            f"MITRE     : {ir_expl.get('mitre_attack',{}).get('technique_id','')} — {ir_expl.get('mitre_attack',{}).get('technique_name','')}",
            f"Kill Chain: {ir_expl.get('kill_chain_phase','')}",
            "",
            "EXECUTIVE SUMMARY", "-" * 40,
            ir_expl.get("executive_summary", ""),
            "",
            "IMMEDIATE ACTIONS (0-15 min)", "-" * 40,
        ]
        for i, a in enumerate(ir_expl.get("immediate_actions", []), 1):
            playbook_lines.append(f"  {i}. {a}")
        playbook_lines += ["", "INVESTIGATION STEPS", "-" * 40]
        for i, s in enumerate(ir_expl.get("investigation_steps", []), 1):
            playbook_lines.append(f"  {i}. {s}")
        playbook_lines += ["", "CONTAINMENT & ERADICATION", "-" * 40]
        for i, s in enumerate(ir_expl.get("containment_eradication", []), 1):
            playbook_lines.append(f"  {i}. {s}")
        playbook_lines += ["", "LONG-TERM REMEDIATION", "-" * 40]
        for i, s in enumerate(ir_expl.get("long_term_remediation", []), 1):
            playbook_lines.append(f"  {i}. {s}")
        playbook_lines += ["", "ANALYST NOTES", "-" * 40, ir_expl.get("analyst_notes", "")]

        st.download_button(
            "📥 Download IR Playbook",
            data="\n".join(playbook_lines),
            file_name=f"ir_playbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain", use_container_width=True,
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — NETWORK GRAPH
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 🕸️ Network Connection Graph")
    st.caption("Node size = connection count · Red = threat source · Blue = normal")

    edges = (df.groupby(["source_ip", "dest_ip"])
               .agg(count=("is_anomaly", "size"), threat=("is_anomaly", "sum"))
               .reset_index())
    node_counts = pd.concat([
        df.groupby("source_ip").size().rename("cnt"),
        df.groupby("dest_ip").size().rename("cnt"),
    ]).groupby(level=0).sum()
    threat_nodes = set(df[df["is_anomaly"]]["source_ip"].unique())
    all_nodes = list(node_counts.index)
    np.random.seed(7)
    angles = np.linspace(0, 2 * np.pi, len(all_nodes), endpoint=False)
    radii = np.random.uniform(0.3, 1.0, len(all_nodes))
    node_x = [r * np.cos(a) for a, r in zip(angles, radii)]
    node_y = [r * np.sin(a) for a, r in zip(angles, radii)]
    node_pos = {n: (x, y) for n, x, y in zip(all_nodes, node_x, node_y)}

    edge_traces = []
    for _, e in edges.iterrows():
        if e["source_ip"] not in node_pos or e["dest_ip"] not in node_pos:
            continue
        x0, y0 = node_pos[e["source_ip"]]
        x1, y1 = node_pos[e["dest_ip"]]
        colour = "#ff4444" if e["threat"] > 0 else "#1e3a5f"
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None], mode="lines",
            line=dict(width=min(3, 0.5 + e["count"] / 10), color=colour),
            hoverinfo="none", showlegend=False,
        ))

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=all_nodes, textposition="top center",
        textfont=dict(size=8, color="#c8d6e5"),
        hovertext=[f"{n}<br>Connections: {node_counts.get(n,0)}" for n in all_nodes],
        hoverinfo="text",
        marker=dict(
            size=[max(8, min(40, node_counts.get(n, 1) / 3)) for n in all_nodes],
            color=["#ff4444" if n in threat_nodes else "#00d4ff" for n in all_nodes],
            line=dict(width=1, color="#0a0e1a"), opacity=0.9,
        ),
        showlegend=False,
    )
    fig_net = go.Figure(data=edge_traces + [node_trace])
    fig_net.update_layout(
        **_PLOTLY_LAYOUT, height=520,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    st.plotly_chart(fig_net, use_container_width=True)
    st.caption("🔴 Red nodes = threat sources  |  🔵 Blue = normal hosts  |  Red edges = attack traffic")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LIVE FEED  (fragment — only this panel refreshes, page stays still)
# ═══════════════════════════════════════════════════════════════════════════════

_LIVE_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "live_feed.csv")


@st.fragment(run_every="5s")
def _live_feed_panel():
    """Runs every 5 s independently — does NOT trigger a full-page rerun."""
    _is_live = st.session_state.get("_live_feed_on", False)
    _secs    = st.session_state.get("_live_refresh_secs", 5)

    if not _is_live:
        st.markdown("""
        <div style="background:#0d1526;border:2px dashed #1e3a5f;border-radius:16px;
                    padding:3rem;text-align:center;margin:2rem 0;">
            <div style="font-size:3rem;">📡</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;font-weight:700;
                        color:#00d4ff;letter-spacing:2px;margin:0.8rem 0;">ENABLE LIVE FEED MODE</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.8rem;
                        color:#8ab0c8;line-height:2.2;">
                In the sidebar → Data Source → switch to
                <b style="color:#00ff88;">📡 Live Feed</b><br>
                Then open a second terminal and run:<br><br>
                <code style="color:#00ff88;background:#0a0e1a;padding:6px 18px;border-radius:6px;">
                    python live_log_generator.py
                </code>
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Read CSV fresh every tick ─────────────────────────────────────────────
    if not os.path.exists(_LIVE_FILE_PATH):
        st.warning("live_feed.csv not found. Start live_log_generator.py first.")
        return

    try:
        live_raw = pd.read_csv(_LIVE_FILE_PATH, parse_dates=["timestamp"])
    except Exception as e:
        st.error(f"Could not read live feed: {e}")
        return

    if len(live_raw) < 10:
        st.info(f"📡 Waiting for events… ({len(live_raw)} so far)")
        return

    # ── Run ML detection on latest data ──────────────────────────────────────
    _sensitivity = st.session_state.get("_sensitivity", 0.25)
    try:
        _det = ThreatDetector(sensitivity=_sensitivity)
        live_df = _det.analyze(live_raw)
    except Exception as e:
        st.error(f"Detection error: {e}")
        return

    live_threats = live_df[live_df["is_anomaly"]].copy()
    _colours = {
        "Port Scan": "#ffaa00", "Brute Force": "#ff4444",
        "Data Exfiltration": "#ff2277", "C2 / Suspicious": "#aa44ff",
        "Anomalous Traffic": "#00d4ff", "normal": "#1e3a5f",
    }

    # ── Metrics row ───────────────────────────────────────────────────────────
    now_ts     = pd.Timestamp.now()
    last_60    = live_df[live_df["timestamp"] >= now_ts - pd.Timedelta(seconds=60)]
    threats_60 = last_60[last_60["is_anomaly"]]
    total_mb   = live_df["bytes_sent"].sum() / 1_000_000
    attackers  = live_threats["source_ip"].nunique()

    lc1, lc2, lc3, lc4, lc5 = st.columns(5)
    with lc1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Total Events</div>
            <div class="metric-value cyan">{len(live_df):,}</div>
        </div>""", unsafe_allow_html=True)
    with lc2:
        cls = "critical" if len(live_threats) else "safe"
        vcls = "red" if len(live_threats) else "green"
        st.markdown(f"""<div class="metric-card {cls}">
            <div class="metric-label">Threats Found</div>
            <div class="metric-value {vcls}">{len(live_threats)}</div>
        </div>""", unsafe_allow_html=True)
    with lc3:
        t60_cls = "critical" if len(threats_60) else "safe"
        t60_vcls = "red" if len(threats_60) else "green"
        st.markdown(f"""<div class="metric-card {t60_cls}">
            <div class="metric-label">Threats (last 60s)</div>
            <div class="metric-value {t60_vcls}">{len(threats_60)}</div>
        </div>""", unsafe_allow_html=True)
    with lc4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Data Exfiltrated</div>
            <div class="metric-value orange">{total_mb:.1f} MB</div>
        </div>""", unsafe_allow_html=True)
    with lc5:
        a_cls = "warning" if attackers else "safe"
        a_vcls = "orange" if attackers else "green"
        st.markdown(f"""<div class="metric-card {a_cls}">
            <div class="metric-label">Active Attackers</div>
            <div class="metric-value {a_vcls}">{attackers}</div>
        </div>""", unsafe_allow_html=True)

    # ── Rolling scatter (last 300 events) ────────────────────────────────────
    st.markdown("#### 📈 Rolling Event Stream")
    recent300 = live_df.sort_values("timestamp", ascending=False).head(300).copy()
    fig_live = px.scatter(
        recent300, x="timestamp", y="risk_score",
        color="anomaly_label", size_max=20,
        color_discrete_map=_colours,
        hover_data=["source_ip", "dest_ip", "dest_port"],
        labels={"risk_score": "Risk Score", "anomaly_label": "Type"},
    )
    fig_live.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,21,38,0.6)",
        font=dict(color="#c8d6e5", family="Rajdhani"),
        margin=dict(l=10, r=10, t=30, b=10), height=280,
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f", range=[0, 105]),
    )
    st.plotly_chart(fig_live, use_container_width=True, key="live_scatter")

    # ── Recent alerts feed ────────────────────────────────────────────────────
    col_alerts, col_table = st.columns([1, 2])

    with col_alerts:
        st.markdown("#### 🚨 Latest Alerts")
        recent_thr = live_threats.sort_values("timestamp", ascending=False).head(12)
        if len(recent_thr) == 0:
            st.markdown("""<div style="background:#051a0d;border:1px solid #00ff88;
                border-radius:8px;padding:1rem;font-family:'Share Tech Mono',monospace;
                font-size:0.78rem;color:#00ff88;text-align:center;">
                ✅ No threats in current window</div>""", unsafe_allow_html=True)
        for _, row in recent_thr.iterrows():
            sev_c = "#ff4444" if row["risk_score"] >= 70 else "#ffaa00"
            lbl   = row["anomaly_label"]
            col_c = _colours.get(lbl, "#8b949e")
            st.markdown(f"""
            <div style="background:#0d1526;border-left:4px solid {sev_c};
                        border-radius:0 8px 8px 0;padding:0.45rem 0.9rem;
                        margin-bottom:0.3rem;font-family:'Share Tech Mono',monospace;
                        font-size:0.72rem;color:#c8d6e5;line-height:1.7;">
                <b style="color:{sev_c};">[{row['risk_score']}/100]</b>
                <span style="color:{col_c};"> {lbl}</span><br>
                {row['source_ip']} → {row['dest_ip']}:{row['dest_port']}
                <span style="color:#4a7a9b;"> {row['timestamp'].strftime('%H:%M:%S')}</span>
            </div>""", unsafe_allow_html=True)

    with col_table:
        st.markdown("#### 📋 Latest 40 Events")
        live_cols = ["timestamp", "source_ip", "dest_ip", "dest_port",
                     "protocol", "bytes_sent", "action", "anomaly_label", "risk_score"]
        live_show = recent300.head(40)[live_cols].copy()
        live_show["timestamp"] = live_show["timestamp"].dt.strftime("%H:%M:%S")
        st.dataframe(live_show, use_container_width=True, height=340, key="live_table")

    # ── Status bar ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                color:#4a7a9b;text-align:center;padding:0.4rem;margin-top:0.5rem;
                background:#0d1526;border-radius:8px;border:1px solid #1e3a5f;">
        🔄 Panel refreshes every 5s (page stays still) &nbsp;·&nbsp;
        📊 {len(live_df):,} total events &nbsp;·&nbsp;
        🚨 {len(live_threats)} threats &nbsp;·&nbsp;
        🕒 {datetime.now().strftime('%H:%M:%S')}
    </div>""", unsafe_allow_html=True)


with tab6:
    # Auto-click this tab if live feed was active when page last loaded
    import streamlit.components.v1 as _stc
    if st.session_state.get("_live_feed_on"):
        _stc.html("""
        <script>
        (function() {
            function clickLiveTab() {
                const tabs = window.parent.document.querySelectorAll('[data-baseweb="tab"]');
                if (tabs.length >= 6) {
                    tabs[5].click();   // index 5 = 6th tab = Live Feed
                    return true;
                }
                return false;
            }
            // Try immediately, then retry until tabs are rendered
            if (!clickLiveTab()) {
                const iv = setInterval(function() {
                    if (clickLiveTab()) clearInterval(iv);
                }, 100);
                setTimeout(function() { clearInterval(iv); }, 3000);
            }
        })();
        </script>
        """, height=0)

    _live_feed_panel()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem;color:#1e3a5f;font-size:0.75rem;
            letter-spacing:2px;border-top:1px solid #1e3a5f;margin-top:2rem;">
    ⬡ AI THREAT HUNTER · ISOLATION FOREST · MITRE ATT&CK · CYBER SECURITY EDITION 2026 ⬡
</div>
""", unsafe_allow_html=True)
