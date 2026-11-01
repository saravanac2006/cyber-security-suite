import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import pandas as pd
import cv2
from datetime import datetime

from core.detector import DeepfakeDetector
from core.video_processor import VideoProcessor
from core.gemini_analyzer import GeminiAnalyzer, GEMINI_AVAILABLE
from core.groq_analyzer import GroqAnalyzer, GROQ_AVAILABLE, list_groq_models
from core.claude_analyzer import ClaudeAnalyzer, CLAUDE_AVAILABLE
from core.key_rotator import next_available, mark_key, build_candidate_list, detect_provider, save_user_key, pool_stats

try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deepfake Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e1a !important;
    color: #c9d1d9 !important;
}
[data-testid="stSidebar"] {
    background-color: #0d1526 !important;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

.main-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d4ff 0%, #00ff88 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: 3px;
    margin-bottom: 0;
}
.sub-title {
    font-family: 'Share Tech Mono', monospace;
    color: #4a9eff;
    text-align: center;
    font-size: 0.95rem;
    letter-spacing: 4px;
    margin-top: 4px;
    margin-bottom: 1.5rem;
}

.verdict-fake {
    background: linear-gradient(135deg, #1a0505 0%, #2d0a0a 100%);
    border: 2px solid #ff4444;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(255,68,68,0.3);
    margin-bottom: 1.5rem;
}
.verdict-real {
    background: linear-gradient(135deg, #051a0d 0%, #0a2d1a 100%);
    border: 2px solid #00ff88;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(0,255,136,0.3);
    margin-bottom: 1.5rem;
}
.verdict-uncertain {
    background: linear-gradient(135deg, #1a1200 0%, #2d2000 100%);
    border: 2px solid #ffaa00;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(255,170,0,0.3);
    margin-bottom: 1.5rem;
}
.verdict-label-uncertain {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    color: #ffaa00;
    letter-spacing: 8px;
    text-shadow: 0 0 20px rgba(255,170,0,0.7);
    margin: 0;
}
.risk-badge-uncertain {
    display: inline-block;
    background: #ffaa00;
    color: #0a0e1a;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 4px 16px;
    border-radius: 20px;
    letter-spacing: 2px;
    margin-top: 0.5rem;
}
.verdict-label-fake {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    color: #ff4444;
    letter-spacing: 8px;
    text-shadow: 0 0 20px rgba(255,68,68,0.7);
    margin: 0;
}
.verdict-label-real {
    font-family: 'Rajdhani', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    color: #00ff88;
    letter-spacing: 8px;
    text-shadow: 0 0 20px rgba(0,255,136,0.7);
    margin: 0;
}
.confidence-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.4rem;
    color: #c9d1d9;
    margin-top: 0.5rem;
}
.risk-badge-high {
    display: inline-block;
    background: #ff4444;
    color: white;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 4px 16px;
    border-radius: 20px;
    letter-spacing: 2px;
    margin-top: 0.5rem;
}
.risk-badge-low {
    display: inline-block;
    background: #00ff88;
    color: #0a0e1a;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 4px 16px;
    border-radius: 20px;
    letter-spacing: 2px;
    margin-top: 0.5rem;
}

.metric-card {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #4a9eff;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #00d4ff;
}

.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: 2px;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
    margin: 1.5rem 0 1rem 0;
}

.progress-row {
    margin-bottom: 0.6rem;
}
.progress-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: #8b949e;
    display: flex;
    justify-content: space-between;
    margin-bottom: 3px;
}
.progress-bar-bg {
    background: #1e3a5f;
    border-radius: 6px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.progress-bar-fill-fake {
    background: linear-gradient(90deg, #ff6b35, #ff4444);
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s ease;
}
.progress-bar-fill-real {
    background: linear-gradient(90deg, #00d4ff, #00ff88);
    height: 100%;
    border-radius: 6px;
}

.report-card {
    background: #0d1526;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
}
.report-section-title {
    color: #00d4ff;
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 1rem;
    margin-bottom: 0.3rem;
}

.upload-zone {
    background: #0d1526;
    border: 2px dashed #1e3a5f;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1rem;
}
.frame-badge-fake {
    background: rgba(255,68,68,0.2);
    border: 1px solid #ff4444;
    color: #ff4444;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 10px;
    display: inline-block;
}
.frame-badge-real {
    background: rgba(0,255,136,0.1);
    border: 1px solid #00ff88;
    color: #00ff88;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 10px;
    display: inline-block;
}
.demo-banner {
    background: linear-gradient(135deg, #0d1526, #101f3a);
    border: 1px solid #00d4ff44;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 2rem 0;
}
.stTabs [data-baseweb="tab-list"] {
    background: #0d1526;
    border-radius: 8px;
    border: 1px solid #1e3a5f;
}
.stTabs [data-baseweb="tab"] {
    color: #8b949e !important;
    font-family: 'Share Tech Mono', monospace;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
}
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

@st.cache_resource
def get_detector():
    return DeepfakeDetector()

@st.cache_resource
def get_video_processor():
    return VideoProcessor()


def render_progress_bar(label: str, score: float, is_fake_direction: bool = True):
    pct = int(score * 100)
    fill_class = "progress-bar-fill-fake" if score > 0.5 else "progress-bar-fill-real"
    color = "#ff4444" if score > 0.5 else "#00ff88"
    st.markdown(f"""
    <div class="progress-row">
        <div class="progress-label">
            <span>{label}</span>
            <span style="color:{color};">{pct}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="{fill_class}" style="width:{pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def build_gauge(score: float) -> go.Figure:
    color = "#ff4444" if score > 0.5 else "#00ff88"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 1),
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Deepfake Probability", "font": {"color": "#8b949e", "size": 14}},
        number={"suffix": "%", "font": {"color": color, "size": 36}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1e3a5f", "tickfont": {"color": "#8b949e"}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#0d1526",
            "bordercolor": "#1e3a5f",
            "steps": [
                {"range": [0, 30], "color": "#0a1f0d"},
                {"range": [30, 60], "color": "#1a1a0d"},
                {"range": [60, 100], "color": "#1a0505"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.9, "value": score * 100},
        },
    ))
    fig.update_layout(
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1d9"},
        height=280,
        margin=dict(l=30, r=30, t=30, b=10),
    )
    return fig


def build_fft_heatmap(fft_magnitude: np.ndarray) -> go.Figure:
    small = fft_magnitude[::4, ::4] if fft_magnitude.shape[0] > 64 else fft_magnitude
    fig = go.Figure(go.Heatmap(z=small, colorscale="Viridis", showscale=True))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        title={"text": "FFT Magnitude Spectrum", "font": {"color": "#00d4ff"}},
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
        xaxis={"title": "Frequency X", "showgrid": False},
        yaxis={"title": "Frequency Y", "showgrid": False},
    )
    return fig


def build_noise_histogram(img: np.ndarray) -> go.Figure:
    import cv2 as _cv2
    gray = _cv2.cvtColor(img, _cv2.COLOR_RGB2GRAY).astype(np.float32)
    lap = _cv2.Laplacian(gray, _cv2.CV_32F).flatten()
    fig = go.Figure(go.Histogram(x=lap, nbinsx=80, marker_color="#00d4ff", opacity=0.75))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        title={"text": "Noise Distribution (Laplacian)", "font": {"color": "#00d4ff"}},
        xaxis_title="Pixel Noise Value",
        yaxis_title="Count",
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def build_color_histogram(img: np.ndarray) -> go.Figure:
    import cv2 as _cv2
    hsv = _cv2.cvtColor(img, _cv2.COLOR_RGB2HSV)
    names = ["Hue", "Saturation", "Value"]
    colors = ["#ff6b35", "#00d4ff", "#00ff88"]
    fig = go.Figure()
    for i, (name, color) in enumerate(zip(names, colors)):
        channel = hsv[:, :, i].flatten()
        fig.add_trace(go.Histogram(x=channel, name=name, nbinsx=60,
                                   marker_color=color, opacity=0.6))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        barmode="overlay",
        title={"text": "HSV Channel Distributions", "font": {"color": "#00d4ff"}},
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        legend={"font": {"color": "#c9d1d9"}},
    )
    return fig


def build_frame_timeline(scores: list) -> go.Figure:
    colors = ["#ff4444" if s > 0.5 else "#00ff88" for s in scores]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(range(1, len(scores) + 1)),
        y=[s * 100 for s in scores],
        marker_color=colors,
        name="Frame Score",
    ))
    fig.add_hline(y=50, line_dash="dash", line_color="#ffaa00", annotation_text="Threshold 50%",
                  annotation_font_color="#ffaa00")
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1526",
        title={"text": "Per-Frame Deepfake Score", "font": {"color": "#00d4ff"}},
        xaxis_title="Frame #",
        yaxis_title="Deepfake Score (%)",
        yaxis_range=[0, 105],
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig


def render_verdict(result: dict):
    verdict = result.get("final_verdict", "REAL")
    confidence = result.get("confidence", 50.0)
    if verdict == "FAKE":
        card_class, label_class = "verdict-fake", "verdict-label-fake"
        icon, badge_class, badge_text = "⚠️", "risk-badge-high", "HIGH RISK"
    elif verdict == "UNCERTAIN":
        card_class, label_class = "verdict-uncertain", "verdict-label-uncertain"
        icon, badge_class, badge_text = "🔎", "risk-badge-uncertain", "NEEDS REVIEW"
    else:
        card_class, label_class = "verdict-real", "verdict-label-real"
        icon, badge_class, badge_text = "✅", "risk-badge-low", "LOW RISK"
    st.markdown(f"""
    <div class="{card_class}">
        <div style="font-size:2.5rem;">{icon}</div>
        <p class="{label_class}">{verdict}</p>
        <p class="confidence-text">Score: {confidence:.1f}%</p>
        <span class="{badge_class}">{badge_text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_report(result: dict, filename: str = "media"):
    verdict = result.get("final_verdict", "UNKNOWN")
    confidence = result.get("confidence", 0)
    breakdown = result.get("analysis_breakdown", {})
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    anomalies = []
    for dim, score in breakdown.items():
        if score > 0.5:
            anomalies.append(f"• {dim}: {score*100:.1f}% — suspicious pattern detected")

    if verdict == "FAKE":
        interpretation = "The media exhibits multiple statistical signatures consistent with AI-generated or manipulated content. The frequency spectrum, noise pattern, and compression artifacts deviate from natural photographic properties."
        recommendations = [
            "Do not share or republish this media without further verification.",
            "Cross-reference with original source using reverse image/video search.",
            "Submit to a certified forensic laboratory for confirmation.",
        ]
    else:
        interpretation = "The media appears to be authentic based on frequency analysis, noise distribution, and compression characteristics. No significant deepfake artifacts were detected."
        recommendations = [
            "Always verify media authenticity through multiple independent methods.",
            "Check metadata (EXIF) for creation date and device consistency.",
            "Use additional tools (FotoForensics, InVID) for secondary verification.",
        ]

    lines = [
        f"DEEPFAKE ANALYSIS REPORT",
        f"{'='*50}",
        f"File       : {filename}",
        f"Timestamp  : {timestamp}",
        f"Verdict    : {verdict}",
        f"Confidence : {confidence:.1f}%",
        "",
        "ANALYSIS BREAKDOWN",
        "-"*30,
    ]
    for dim, score in breakdown.items():
        lines.append(f"  {dim:<25} {score*100:.1f}%")
    lines += ["", "DETECTED ANOMALIES", "-"*30]
    lines += anomalies if anomalies else ["  None detected"]
    lines += ["", "INTERPRETATION", "-"*30, f"  {interpretation}", "", "RECOMMENDATIONS", "-"*30]
    lines += [f"  {r}" for r in recommendations]
    report_text = "\n".join(lines)

    st.markdown('<div class="section-header">ANALYSIS REPORT</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-card"><pre style="color:#c9d1d9;font-family:\'Share Tech Mono\',monospace;font-size:0.78rem;white-space:pre-wrap;">{report_text}</pre></div>', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name=f"deepfake_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
    )


def _signal_item(text: str, color: str) -> str:
    return f"""<div style="background:#0d1526;border-left:3px solid {color};
        padding:0.45rem 1rem;margin-bottom:0.35rem;border-radius:0 8px 8px 0;
        font-family:'Share Tech Mono',monospace;font-size:0.79rem;color:#c9d1d9;line-height:1.6;">
        {text}</div>"""


def _dim_label(key: str) -> str:
    return {
        "facial_forensics": "🧬 Facial Forensics",
        "texture_analysis": "🧱 Texture Analysis",
        "lighting_forensics": "💡 Lighting & Shadows",
        "background_analysis": "🌄 Background & Depth",
        "color_chromatic": "🎨 Color & Chromatic",
        "noise_compression": "📡 Noise & Compression",
        "document_text": "📄 Document / Text",
    }.get(key, key.replace("_", " ").title())


def render_ai_report(ai: dict):
    """Render the full AI forensic report — no heuristic values."""
    if not ai:
        st.markdown("""
        <div style="background:#0d1526;border:1px dashed #1e3a5f;border-radius:10px;
                    padding:1.5rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.8rem;color:#4a9eff;text-align:center;line-height:2;">
            🤖 AI Vision Engine is processing your media.<br>
            Add a Backup AI Key in the sidebar if analysis takes too long.
        </div>""", unsafe_allow_html=True)
        return

    if not ai.get("success"):
        if ai.get("quota_exhausted"):
            mins = ai.get("retry_after_mins", 60)
            st.markdown(f"""
            <div style="background:#1a1200;border:2px solid #ffaa00;border-radius:12px;
                        padding:1.2rem 1.5rem;font-family:'Share Tech Mono',monospace;font-size:0.82rem;">
                <div style="color:#ffaa00;font-size:1.1rem;font-weight:700;margin-bottom:0.5rem;">
                    ⏳ AI Engine Quota Exhausted
                </div>
                <div style="color:#c9d1d9;line-height:1.8;">
                    Daily limit reached. Retry in <b style="color:#ffaa00;">~{mins} minutes</b>.<br>
                    Add a Backup Key in the sidebar to continue using AI analysis.
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#1a0a0a;border:1px solid #ff444466;border-radius:10px;
                        padding:1rem;font-family:'Share Tech Mono',monospace;
                        font-size:0.78rem;color:#ff6b6b;">
            ⚠️ AI Engine error: {ai.get("error","Unknown error")[:300]}
            </div>""", unsafe_allow_html=True)
        return

    verdict = ai.get("verdict", "UNCERTAIN")
    confidence = ai.get("confidence", 0)
    manip_type = ai.get("manipulation_type", "Unknown")
    risk = ai.get("risk_level", "MEDIUM")
    exec_summary = ai.get("executive_summary", "")
    primary = ai.get("primary_indicators", [])
    auth_signals = ai.get("authenticity_signals", [])
    manip_signals = ai.get("manipulation_signals", [])
    findings = ai.get("detailed_findings", {})
    provenance = ai.get("provenance_assessment", "")
    recommendation = ai.get("recommendation", "")
    analyst_notes = ai.get("analyst_notes", "")

    accent = "#ff4444" if verdict == "FAKE" else ("#ffaa00" if verdict == "UNCERTAIN" else "#00ff88")
    risk_color = {"HIGH": "#ff4444", "MEDIUM": "#ffaa00", "LOW": "#00ff88"}.get(risk, "#ffaa00")

    # ── Executive Summary banner ─────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1526,#101f3a);
                border:2px solid {accent};border-radius:16px;padding:1.5rem 2rem;
                box-shadow:0 0 30px {accent}22;margin-bottom:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                            color:#8b949e;letter-spacing:3px;margin-bottom:4px;">MANIPULATION TYPE</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.3rem;
                            font-weight:700;color:{accent};">{manip_type}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                            color:#8b949e;letter-spacing:3px;margin-bottom:4px;">RISK LEVEL</div>
                <div style="background:{risk_color};color:#0a0e1a;font-family:'Rajdhani',sans-serif;
                            font-size:1rem;font-weight:700;padding:3px 14px;border-radius:20px;
                            letter-spacing:2px;">{risk}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                            color:#8b949e;letter-spacing:3px;margin-bottom:4px;">AI CONFIDENCE</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;
                            font-weight:700;color:{accent};">{confidence}%</div>
            </div>
        </div>
        <hr style="border-color:#1e3a5f;margin:1rem 0;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.84rem;
                    color:#c9d1d9;line-height:1.9;border-left:4px solid {accent};
                    padding-left:1.2rem;">
            {exec_summary}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Primary indicators ───────────────────────────────────────────────────
    if primary:
        st.markdown('<div class="section-header">🚨 PRIMARY INDICATORS</div>', unsafe_allow_html=True)
        for i, ind in enumerate(primary, 1):
            if ind and ind.lower() not in ("none", "n/a", ""):
                st.markdown(_signal_item(f"<b style='color:{accent};'>#{i}</b> &nbsp; {ind}", accent),
                            unsafe_allow_html=True)

    # ── Signal columns ───────────────────────────────────────────────────────
    col_m, col_a = st.columns(2)
    with col_m:
        if manip_signals:
            st.markdown('<div class="section-header">⚠️ MANIPULATION SIGNALS</div>', unsafe_allow_html=True)
            for s in manip_signals:
                if s:
                    st.markdown(_signal_item(s, "#ff4444"), unsafe_allow_html=True)
    with col_a:
        if auth_signals:
            st.markdown('<div class="section-header">✅ AUTHENTICITY SIGNALS</div>', unsafe_allow_html=True)
            for s in auth_signals:
                if s:
                    st.markdown(_signal_item(s, "#00ff88"), unsafe_allow_html=True)

    # ── Per-dimension findings ────────────────────────────────────────────────
    if findings:
        st.markdown('<div class="section-header">🔬 DIMENSION-BY-DIMENSION ANALYSIS</div>',
                    unsafe_allow_html=True)
        applicable = {k: v for k, v in findings.items() if v.get("applicable", True)}
        for key, info in applicable.items():
            status = info.get("status", "CLEAN")
            score = info.get("score", 0)
            explanation = info.get("explanation", "")
            evidence = info.get("evidence", [])
            color = {"SUSPICIOUS": "#ff4444", "MODERATE": "#ffaa00", "CLEAN": "#00ff88"}.get(status, "#8b949e")
            label = _dim_label(key)
            pct = int(score * 100)
            fill = "progress-bar-fill-fake" if score > 0.5 else "progress-bar-fill-real"
            header = f"{label} — <span style='color:{color};'>{status}</span>"
            with st.expander(f"{label}  ·  {status}  ·  {pct}% suspicion"):
                st.markdown(f"""
                <div class="progress-row" style="margin-bottom:0.8rem;">
                    <div class="progress-label">
                        <span style="color:{color};">Suspicion Level</span>
                        <span style="color:{color};">{pct}%</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="{fill}" style="width:{pct}%;"></div>
                    </div>
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.82rem;
                            color:#c9d1d9;line-height:1.9;margin-bottom:0.8rem;">
                    {explanation}
                </div>""", unsafe_allow_html=True)
                if evidence:
                    st.markdown("**Evidence observed:**")
                    for ev in evidence:
                        if ev:
                            st.markdown(_signal_item(ev, color), unsafe_allow_html=True)

    # ── Provenance, recommendation, analyst notes ────────────────────────────
    extra_parts = []
    if provenance:
        extra_parts.append(("🧾 PROVENANCE ASSESSMENT", provenance))
    if recommendation:
        extra_parts.append(("💡 RECOMMENDATION", recommendation))
    if analyst_notes:
        extra_parts.append(("📋 ANALYST NOTES", analyst_notes))

    for title, body in extra_parts:
        st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;
                    padding:1rem 1.4rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.82rem;color:#c9d1d9;line-height:1.9;">
            {body}
        </div>""", unsafe_allow_html=True)


def build_ela_heatmap(ela_map: np.ndarray) -> go.Figure:
    fig = go.Figure(go.Heatmap(z=ela_map, colorscale="Hot", showscale=True))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0a0e1a", plot_bgcolor="#0d1526",
        title={"text": "ELA Map (brighter = higher error = suspicious)", "font": {"color": "#00d4ff"}},
        margin=dict(l=20, r=20, t=50, b=20), height=300,
    )
    return fig


def detect_qr_codes(img: np.ndarray) -> list:
    detector = cv2.QRCodeDetector()
    try:
        data, points, _ = detector.detectAndDecode(img)
        if data:
            return [data]
        # Try multi-detect
        retval, decoded, points, _ = detector.detectAndDecodeMulti(img)
        if retval and decoded:
            return [d for d in decoded if d]
    except Exception:
        pass
    return []


def render_technical_tabs(result: dict, img: np.ndarray):
    freq_data = result.get("frequency") or (result.get("frame_results", [{}])[0].get("frequency") if result.get("frame_results") else {})
    ela_data = result.get("ela") or (result.get("frame_results", [{}])[0].get("ela") if result.get("frame_results") else {})

    tab_freq, tab_ela, tab_noise, tab_color, tab_qr = st.tabs([
        "📡 Frequency", "🔬 ELA Analysis", "📊 Noise", "🎨 Color", "🔲 QR / Document"
    ])

    with tab_freq:
        if freq_data and "fft_magnitude" in freq_data:
            st.plotly_chart(build_fft_heatmap(freq_data["fft_magnitude"]), use_container_width=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("High-Freq Ratio", f"{freq_data.get('high_freq_ratio', 0):.3f}")
            c2.metric("Spike Score", f"{freq_data.get('spike_score', 0)*100:.1f}%")
            c3.metric("Frequency Score", f"{freq_data.get('score', 0)*100:.1f}%")
        else:
            st.info("Frequency data unavailable.")

    with tab_ela:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#8b949e;
                    line-height:1.7;margin-bottom:1rem;">
        <b style="color:#00d4ff;">Error Level Analysis (ELA)</b> re-saves the image at two JPEG
        quality levels and maps the difference. Real photos show <b>non-uniform</b> error distribution
        (brighter in textured/edge regions). GAN-generated or manipulated images show
        <b>unnaturally uniform</b> ELA because they were never captured by a camera sensor.
        </div>""", unsafe_allow_html=True)
        if ela_data and "ela_map" in ela_data:
            st.plotly_chart(build_ela_heatmap(ela_data["ela_map"]), use_container_width=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("ELA Patch CV", f"{ela_data.get('ela_patch_cv', 0):.3f}", help="Higher = more natural")
            c2.metric("ELA Mean", f"{ela_data.get('ela_mean', 0):.2f}")
            c3.metric("ELA Score", f"{ela_data.get('score', 0)*100:.1f}%")
        else:
            st.info("ELA data unavailable.")

    with tab_noise:
        st.plotly_chart(build_noise_histogram(img), use_container_width=True)

    with tab_color:
        st.plotly_chart(build_color_histogram(img), use_container_width=True)

    with tab_qr:
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;color:#8b949e;
                    line-height:1.7;margin-bottom:1rem;">
        <b style="color:#00d4ff;">QR Code & Document Validation</b> — scans the image for embedded
        QR codes. For identity documents and certificates, the QR code encodes the authentic data.
        If the QR code is absent, unreadable, or the decoded URL is suspicious, the document
        authenticity is in question.
        </div>""", unsafe_allow_html=True)

        qr_results = detect_qr_codes(img)
        if qr_results:
            st.success(f"✅ {len(qr_results)} QR code(s) detected")
            for i, qr in enumerate(qr_results):
                st.markdown(f"""
                <div style="background:#0d1526;border:1px solid #00ff88;border-radius:8px;
                            padding:0.8rem 1.2rem;font-family:'Share Tech Mono',monospace;
                            font-size:0.8rem;color:#c9d1d9;margin-bottom:0.5rem;word-break:break-all;">
                    <span style="color:#00ff88;">QR #{i+1}:</span> {qr}
                </div>""", unsafe_allow_html=True)
                if qr.startswith("http"):
                    st.markdown(f"**URL detected** — verify this domain is legitimate before trusting the document.")
        else:
            st.markdown("""
            <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:8px;
                        padding:1rem;font-family:'Share Tech Mono',monospace;
                        font-size:0.8rem;color:#8b949e;">
                ⚠️ No QR code detected in this image. If this is a document that should contain a
                verification QR code, its absence or illegibility is suspicious.
            </div>""", unsafe_allow_html=True)


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0;">
        <div style="font-size:3rem;">🔍</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;font-weight:700;
                    background:linear-gradient(135deg,#00d4ff,#00ff88);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            DEEPFAKE DETECTOR
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                    color:#4a9eff;letter-spacing:3px;">v2.0 · AI VISION EDITION</div>
    </div>
    <hr style="border-color:#1e3a5f;margin:0.5rem 0 1rem 0;">
    """, unsafe_allow_html=True)

    st.markdown("**📁 Upload Media**")
    media_type = st.radio("Media type", ["Image", "Video", "PDF / Document", "Screenshot"], horizontal=False)

    uploaded = None
    if media_type == "Image":
        uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
                                    label_visibility="collapsed")
    elif media_type == "Video":
        uploaded = st.file_uploader("Upload video", type=["mp4", "avi", "mov", "mkv"],
                                    label_visibility="collapsed")
    elif media_type == "PDF / Document":
        if PDF_SUPPORT:
            uploaded = st.file_uploader("Upload PDF", type=["pdf"],
                                        label_visibility="collapsed")
        else:
            st.warning("Install PyMuPDF: `pip install PyMuPDF`")
    elif media_type == "Screenshot":
        uploaded = st.file_uploader("Upload screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"],
                                    label_visibility="collapsed")
        st.markdown("""
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                    color:#8b949e;line-height:1.6;padding:0.5rem;
                    border:1px solid #1e3a5f;border-radius:8px;margin-top:0.5rem;">
        Screenshots are screen captures — they contain images that may include deepfakes.
        The detector analyses the visual content inside the screenshot for synthetic artifacts.
        </div>""", unsafe_allow_html=True)

    # ── AI Engine status ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**🤖 AI Engine**")

    stats = pool_stats(st.session_state.get("_backup_key", ""))
    ok_count = stats["ok"]
    total = stats["total"]

    if ok_count > 0:
        st.markdown(f"""
        <div style="background:#051a0d;border:1px solid #00ff88;border-radius:8px;
                    padding:0.6rem 1rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.75rem;color:#00ff88;text-align:center;line-height:1.8;">
            ✅ AI Vision Analysis Active<br>
            <span style="color:#8b949e;font-size:0.65rem;">{ok_count} of {total} engines ready</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1a1200;border:1px solid #ffaa00;border-radius:8px;
                    padding:0.6rem 1rem;font-family:'Share Tech Mono',monospace;
                    font-size:0.75rem;color:#ffaa00;text-align:center;line-height:1.8;">
            ⚠️ All AI engines exhausted<br>
            <span style="color:#8b949e;font-size:0.65rem;">Using heuristic analysis</span>
        </div>""", unsafe_allow_html=True)

    # ── Backup key input ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**🔑 Backup Key** *(optional)*")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;
                color:#8b949e;line-height:1.6;margin-bottom:0.5rem;">
    If all engines are exhausted, paste your own API key here.
    It will be tested and saved automatically.
    </div>""", unsafe_allow_html=True)

    backup_key_input = st.text_input(
        "Backup API Key",
        type="password",
        placeholder="Paste any AI API key here…",
        label_visibility="collapsed",
        help="Accepts any vision AI API key — auto-detected and saved on success",
        key="_backup_key_input",
    )
    if backup_key_input:
        st.session_state["_backup_key"] = backup_key_input
    else:
        st.session_state.setdefault("_backup_key", "")

    # ── Settings ──────────────────────────────────────────────────────────────
    st.markdown("---")
    sensitivity = st.slider("🎚️ Detection Sensitivity", 1, 10, 5,
                             help="Higher = more sensitive, more false positives")
    mode = st.radio("⚡ Analysis Mode", ["Fast", "Thorough"], horizontal=True)
    max_frames = 10 if mode == "Fast" else 30

    demo_btn = st.button("🧪 Analyze Demo (Synthetic Fake)", use_container_width=True)

    st.markdown("---")
    with st.expander("ℹ️ How it works"):
        st.markdown("""
**Multi-layered AI analysis:**

🤖 **Vision AI** — Multiple AI engines analyse the image for GAN artifacts, manipulation traces, and synthetic patterns.

🔬 **Frequency Domain** — Real photos follow 1/f distribution. Synthetic images deviate from this natural pattern.

🧩 **Compression Artifacts** — Deepfakes show unnatural DCT block boundaries at 8-pixel intervals.

📡 **Noise Pattern** — AI outputs show unnaturally uniform noise vs. organic camera sensor noise.

🎨 **Color Distribution** — Synthetic images have distinctive HSV channel distributions.

⏱️ **Temporal Consistency** — Frame-to-frame consistency checks for video deepfakes.
        """)

# ── header ────────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🔍 DEEPFAKE DETECTOR</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-POWERED MEDIA AUTHENTICITY ANALYSIS</p>', unsafe_allow_html=True)

# ── main logic ────────────────────────────────────────────────────────────────

detector = get_detector()
vp = get_video_processor()

# Apply sensitivity as threshold adjustment
threshold_adj = (sensitivity - 5) * 0.04  # -0.16 to +0.16

if "result" not in st.session_state:
    st.session_state.result = None
if "display_img" not in st.session_state:
    st.session_state.display_img = None
if "frames" not in st.session_state:
    st.session_state.frames = None
if "media_name" not in st.session_state:
    st.session_state.media_name = "unknown"

_backup_key = st.session_state.get("_backup_key", "")


def _apply_sensitivity(res: dict) -> dict:
    key = "final_score" if "final_score" in res else "overall_score"
    adj = float(res[key]) - threshold_adj
    from core.detector import THRESHOLD_FAKE, THRESHOLD_UNCERTAIN
    if adj >= THRESHOLD_FAKE:
        res["final_verdict"] = "FAKE"
    elif adj >= THRESHOLD_UNCERTAIN:
        res["final_verdict"] = "UNCERTAIN"
    else:
        res["final_verdict"] = "REAL"
    res["confidence"] = float(np.clip(adj * 100, 0, 100))
    res["is_fake"] = res["final_verdict"] == "FAKE"
    res["summary"] = detector.generate_summary(res)
    res["gemini"] = None
    return res


def _build_analyzer(provider: str, key: str):
    """Instantiate the right analyzer for the given provider and key."""
    if provider == "groq" and GROQ_AVAILABLE:
        models, err = list_groq_models(key)
        if err or not models:
            return None
        return GroqAnalyzer(key, models[0])
    if provider == "gemini" and GEMINI_AVAILABLE:
        from core.gemini_analyzer import list_available_models, GeminiAnalyzer as _GA
        models, err = list_available_models(key)
        if err or not models:
            return None
        return _GA(key, models[0])
    if provider == "claude" and CLAUDE_AVAILABLE:
        from core.claude_analyzer import list_claude_models, ClaudeAnalyzer as _CA
        models, err = list_claude_models(key)
        if err or not models:
            return None
        return _CA(key, models[0])
    return None


def _run_ai_analysis(res: dict, img: np.ndarray) -> dict:
    """Rotate through the key pool until one succeeds, then use heuristics as last resort."""
    candidates = build_candidate_list(_backup_key)
    user_key_used = False

    for provider, key in candidates:
        from core.key_rotator import get_key_status
        if get_key_status(key) != "ok":
            continue

        spinner_label = "🤖 AI Vision analysing image..."
        try:
            analyzer = _build_analyzer(provider, key)
            if analyzer is None:
                mark_key(key, "invalid")
                continue
        except Exception:
            mark_key(key, "invalid")
            continue

        with st.spinner(spinner_label):
            ai_result = analyzer.analyze(img)

        if ai_result.get("quota_exhausted"):
            mark_key(key, "exhausted")
            continue

        if not ai_result.get("success"):
            err_msg = ai_result.get("error", "")
            if "invalid" in err_msg.lower() or "401" in err_msg or "403" in err_msg:
                mark_key(key, "invalid")
            continue

        # Success — if this was the user's backup key, save it
        if key == _backup_key.strip() and _backup_key.strip():
            save_user_key(key, provider)
            st.sidebar.success("✅ Key saved to AI engine pool")

        res["gemini"] = ai_result
        res["final_verdict"] = ai_result["verdict"]
        res["confidence"] = float(ai_result["confidence"])
        res["is_fake"] = ai_result["verdict"] == "FAKE"
        return res

    # All engines failed — heuristics only
    res["gemini"] = None
    return res


# Trigger analysis
if demo_btn:
    with st.spinner("🧪 Generating synthetic fake and analyzing..."):
        fake_img = DeepfakeDetector.generate_synthetic_fake()
        result = _apply_sensitivity(detector.analyze_image(fake_img))
        result = _run_ai_analysis(result, fake_img)
        st.session_state.result = result
        st.session_state.display_img = fake_img
        st.session_state.frames = None
        st.session_state.media_name = "synthetic_fake_demo"

elif uploaded is not None:

    if media_type in ("Image", "Screenshot"):
        label = "🖼️ Analyzing screenshot..." if media_type == "Screenshot" else "🔍 Analyzing image..."
        with st.spinner(label):
            img_bytes = uploaded.read()
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            img_arr = np.array(pil_img)
            result = _apply_sensitivity(detector.analyze_image(img_arr))
        result = _run_ai_analysis(result, img_arr)
        st.session_state.result = result
        st.session_state.display_img = img_arr
        st.session_state.frames = None
        st.session_state.media_name = uploaded.name

    elif media_type == "Video":
        with st.spinner(f"🎬 Extracting {max_frames} frames and analyzing video..."):
            frames = vp.extract_frames_from_upload(uploaded, max_frames=max_frames)
            if not frames:
                st.error("Could not extract frames from video. Try a different format.")
            else:
                result = _apply_sensitivity(detector.analyze_video_frames(frames))
                # For video, run Gemini on the first representative frame
                result = _run_ai_analysis(result, frames[0])
                st.session_state.result = result
                st.session_state.display_img = frames[0]
                st.session_state.frames = frames
                st.session_state.media_name = uploaded.name

    elif media_type == "PDF / Document" and PDF_SUPPORT:
        with st.spinner("📄 Extracting images from PDF and analyzing..."):
            pdf_bytes = uploaded.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pdf_frames = []
            for page_num in range(min(len(doc), 5)):  # analyse first 5 pages
                page = doc[page_num]
                mat = fitz.Matrix(2.0, 2.0)  # 2× zoom for quality
                pix = page.get_pixmap(matrix=mat)
                img_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:  # RGBA
                    img_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGBA2RGB)
                pdf_frames.append(img_arr)
            doc.close()
            if not pdf_frames:
                st.error("No pages found in PDF.")
            else:
                if len(pdf_frames) == 1:
                    result = _apply_sensitivity(detector.analyze_image(pdf_frames[0]))
                else:
                    result = _apply_sensitivity(detector.analyze_video_frames(pdf_frames))
                result = _run_ai_analysis(result, pdf_frames[0])
                st.session_state.result = result
                st.session_state.display_img = pdf_frames[0]
                st.session_state.frames = pdf_frames if len(pdf_frames) > 1 else None
                st.session_state.media_name = uploaded.name

# ── render results ────────────────────────────────────────────────────────────

result = st.session_state.result

if result is None:
    st.markdown("""
    <div class="demo-banner">
        <div style="font-size:4rem;">🛡️</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.8rem;font-weight:700;color:#00d4ff;letter-spacing:3px;">
            READY TO ANALYZE
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.85rem;color:#8b949e;margin-top:0.8rem;">
            Upload an image or video in the sidebar, or click <b style="color:#00d4ff;">Analyze Demo</b> to see the system in action.
        </div>
        <br>
        <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
            <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;padding:1rem 1.5rem;text-align:center;">
                <div style="font-size:1.5rem;">📸</div>
                <div style="color:#4a9eff;font-family:'Share Tech Mono',monospace;font-size:0.7rem;">IMAGES</div>
                <div style="color:#8b949e;font-size:0.75rem;">JPG, PNG, WEBP</div>
            </div>
            <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;padding:1rem 1.5rem;text-align:center;">
                <div style="font-size:1.5rem;">🎬</div>
                <div style="color:#4a9eff;font-family:'Share Tech Mono',monospace;font-size:0.7rem;">VIDEOS</div>
                <div style="color:#8b949e;font-size:0.75rem;">MP4, AVI, MOV</div>
            </div>
            <div style="background:#0d1526;border:1px solid #1e3a5f;border-radius:10px;padding:1rem 1.5rem;text-align:center;">
                <div style="font-size:1.5rem;">🧪</div>
                <div style="color:#4a9eff;font-family:'Share Tech Mono',monospace;font-size:0.7rem;">DEMO MODE</div>
                <div style="color:#8b949e;font-size:0.75rem;">Synthetic fake</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    display_img = st.session_state.display_img
    frames = st.session_state.frames
    media_name = st.session_state.media_name
    is_video = frames is not None

    # ── Row 1: Verdict + Image ─────────────────────────────────────────────
    verdict_col, img_col = st.columns([3, 2])
    with verdict_col:
        render_verdict(result)
    with img_col:
        if display_img is not None:
            st.image(display_img, caption=media_name, use_column_width=True)
            # QR codes only — not heuristic
            qr_results = detect_qr_codes(display_img)
            if qr_results:
                st.success(f"🔲 {len(qr_results)} QR code(s) detected in media")
                for i, qr in enumerate(qr_results):
                    st.markdown(f"""
                    <div style="background:#0d1526;border:1px solid #00ff88;border-radius:8px;
                                padding:0.5rem 0.8rem;font-family:'Share Tech Mono',monospace;
                                font-size:0.72rem;color:#c9d1d9;margin-bottom:0.3rem;word-break:break-all;">
                        <span style="color:#00ff88;">QR #{i+1}:</span> {qr}
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 2: Full AI Report ──────────────────────────────────────────────
    st.markdown('<div class="section-header">🤖 AI FORENSIC REPORT</div>', unsafe_allow_html=True)
    render_ai_report(result.get("gemini"))

    # ── Row 3: Frame thumbnails (video only) ───────────────────────────────
    if is_video and frames:
        st.markdown("---")
        st.markdown('<div class="section-header">🎬 ANALYZED FRAMES</div>', unsafe_allow_html=True)
        cols_per_row = 4
        for row_start in range(0, min(len(frames), 12), cols_per_row):
            row_frames = frames[row_start: row_start + cols_per_row]
            cols = st.columns(cols_per_row)
            for col, frm in zip(cols, row_frames):
                with col:
                    st.image(frm, use_column_width=True)
                    st.markdown(f'<div style="text-align:center;font-family:\'Share Tech Mono\',monospace;'
                                f'font-size:0.65rem;color:#8b949e;">Frame {row_start + row_frames.index(frm)+1}</div>',
                                unsafe_allow_html=True)

    # ── Download report ────────────────────────────────────────────────────
    st.markdown("---")
    ai_data = result.get("gemini") or {}
    if ai_data.get("success"):
        report_lines = [
            "AI FORENSIC DEEPFAKE ANALYSIS REPORT",
            "=" * 55,
            f"File       : {media_name}",
            f"Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Verdict    : {ai_data.get('verdict', 'UNKNOWN')}",
            f"Confidence : {ai_data.get('confidence', 0)}%",
            f"Risk Level : {ai_data.get('risk_level', 'MEDIUM')}",
            f"Manip Type : {ai_data.get('manipulation_type', 'Unknown')}",
            "",
            "EXECUTIVE SUMMARY",
            "-" * 40,
            ai_data.get("executive_summary", ""),
            "",
            "PRIMARY INDICATORS",
            "-" * 40,
        ]
        for i, ind in enumerate(ai_data.get("primary_indicators", []), 1):
            if ind:
                report_lines.append(f"  {i}. {ind}")
        report_lines += ["", "MANIPULATION SIGNALS", "-" * 40]
        for s in ai_data.get("manipulation_signals", []):
            if s:
                report_lines.append(f"  • {s}")
        report_lines += ["", "AUTHENTICITY SIGNALS", "-" * 40]
        for s in ai_data.get("authenticity_signals", []):
            if s:
                report_lines.append(f"  • {s}")
        report_lines += ["", "DETAILED FINDINGS", "-" * 40]
        for key, info in ai_data.get("detailed_findings", {}).items():
            if info.get("applicable"):
                report_lines.append(f"\n  [{_dim_label(key)}] — {info.get('status','CLEAN')} ({int(info.get('score',0)*100)}%)")
                report_lines.append(f"  {info.get('explanation','')}")
                for ev in info.get("evidence", []):
                    if ev:
                        report_lines.append(f"    → {ev}")
        report_lines += [
            "", "PROVENANCE", "-" * 40,
            ai_data.get("provenance_assessment", ""),
            "", "RECOMMENDATION", "-" * 40,
            ai_data.get("recommendation", ""),
            "", "ANALYST NOTES", "-" * 40,
            ai_data.get("analyst_notes", ""),
        ]
        report_text = "\n".join(report_lines)
        st.download_button(
            label="📥 Download Full AI Report",
            data=report_text,
            file_name=f"ai_forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("🔄 Analyze Another File", use_container_width=True):
        st.session_state.result = None
        st.session_state.display_img = None
        st.session_state.frames = None
        st.rerun()

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem 0;
            font-family:'Share Tech Mono',monospace;font-size:0.7rem;
            color:#1e3a5f;letter-spacing:2px;">
    DEEPFAKE DETECTOR · AI VISION FORENSICS · CYBER SECURITY EDITION 2026
</div>
""", unsafe_allow_html=True)
