"""
Cyber Security Suite — PowerPoint Generator
Run:  python generate_ppt.py
Output: Cyber_Security_Suite_Project.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm

# ── Colours ────────────────────────────────────────────────────────────────────
NAVY       = RGBColor(0x0f, 0x34, 0x60)
BLUE       = RGBColor(0x15, 0x65, 0xc0)
TEAL       = RGBColor(0x00, 0x69, 0x5c)
DARK_RED   = RGBColor(0xb7, 0x1c, 0x1c)
DARK_GREEN = RGBColor(0x2e, 0x7d, 0x32)
WHITE      = RGBColor(0xff, 0xff, 0xff)
LIGHT_BLUE = RGBColor(0xe3, 0xf2, 0xfd)
LIGHT_RED  = RGBColor(0xff, 0xeb, 0xee)
LIGHT_TEAL = RGBColor(0xe0, 0xf7, 0xfa)
LIGHT_GREY = RGBColor(0xf5, 0xf5, 0xf5)
MID_GREY   = RGBColor(0xbd, 0xbd, 0xbd)
DIM        = RGBColor(0x54, 0x6e, 0x7a)
BLACK      = RGBColor(0x21, 0x21, 0x21)
ORANGE     = RGBColor(0xe6, 0x51, 0x00)
INDIGO     = RGBColor(0xe8, 0xea, 0xf6)

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "Cyber_Security_Suite_Project.pptx")

# Widescreen 16:9
prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

SW = prs.slide_width
SH = prs.slide_height

BLANK = prs.slide_layouts[6]   # completely blank layout


# ── Helper: add text box ────────────────────────────────────────────────────────
def txb(slide, text, x, y, w, h, *,
        size=18, bold=False, color=BLACK, align=PP_ALIGN.LEFT,
        bg=None, italic=False, wrap=True):
    shape = slide.shapes.add_textbox(x, y, w, h)
    shape.word_wrap = wrap
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    else:
        shape.fill.background()
    tf = shape.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return shape


def txb_multi(slide, lines, x, y, w, h, *,
              default_size=14, bg=None, wrap=True):
    """lines = list of (text, size, bold, color, align)"""
    shape = slide.shapes.add_textbox(x, y, w, h)
    shape.word_wrap = wrap
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    else:
        shape.fill.background()
    tf = shape.text_frame
    tf.word_wrap = wrap
    first = True
    for text, size, bold, color, align in lines:
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = align
        run = para.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return shape


def rect(slide, x, y, w, h, fill, line_color=None, line_width=Pt(0)):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        x, y, w, h
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape


def header_bar(slide, title, bg=NAVY, title_color=WHITE, subtitle=""):
    """Full-width header bar at top of slide."""
    bar_h = Inches(1.1)
    r = rect(slide, Inches(0), Inches(0), SW, bar_h, bg)
    txb(slide, title, Inches(0.4), Inches(0.12), SW - Inches(0.8), Inches(0.6),
        size=26, bold=True, color=title_color, align=PP_ALIGN.LEFT)
    if subtitle:
        txb(slide, subtitle, Inches(0.4), Inches(0.68), SW - Inches(0.8), Inches(0.35),
            size=13, bold=False, color=MID_GREY, align=PP_ALIGN.LEFT)


def footer_bar(slide):
    bar_h = Inches(0.3)
    rect(slide, Inches(0), SH - bar_h, SW, bar_h, LIGHT_GREY)
    txb(slide,
        "Deepfake Detector  |  AI Threat Hunter  |  MITRE ATT&CK  |  2026",
        Inches(0), SH - bar_h + Inches(0.04), SW, Inches(0.22),
        size=9, color=DIM, align=PP_ALIGN.CENTER)


def table_block(slide, headers, rows, x, y, w, col_ratios,
                hdr_bg=NAVY, hdr_color=WHITE, hdr_size=11,
                row_size=10, alt_bg=None):
    """Draw a table manually using rectangles and text boxes."""
    n_cols = len(headers)
    n_rows = len(rows)
    col_widths = [w * r for r in col_ratios]

    HDR_H = Inches(0.33)
    ROW_H = Inches(0.3)

    # Header row
    cx = x
    for i, h in enumerate(headers):
        cw = col_widths[i]
        rect(slide, cx, y, cw, HDR_H, hdr_bg)
        txb(slide, h, cx + Inches(0.05), y + Inches(0.04),
            cw - Inches(0.1), HDR_H,
            size=hdr_size, bold=True, color=hdr_color)
        cx += cw

    # Data rows
    for ri, row in enumerate(rows):
        row_y = y + HDR_H + ri * ROW_H
        bg = LIGHT_GREY if alt_bg and ri % 2 == 0 else WHITE
        cx = x
        for ci, cell in enumerate(row):
            cw = col_widths[ci]
            rect(slide, cx, row_y, cw, ROW_H, bg)
            txb(slide, str(cell), cx + Inches(0.05), row_y + Inches(0.03),
                cw - Inches(0.1), ROW_H,
                size=row_size, color=BLACK)
            cx += cw

    total_h = HDR_H + n_rows * ROW_H
    return total_h


# ════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)

# Navy banner background (top 45%)
rect(sl, 0, 0, SW, Inches(3.3), NAVY)

# Title
txb(sl, "CYBER SECURITY", Inches(0.5), Inches(0.3), SW - Inches(1), Inches(1.0),
    size=52, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
txb(sl, "AI SUITE", Inches(0.5), Inches(1.25), SW - Inches(1), Inches(0.65),
    size=30, bold=True, color=RGBColor(0x90, 0xca, 0xf9), align=PP_ALIGN.CENTER)
txb(sl, "AI-Powered Threat Detection  &  Media Forensics Platform",
    Inches(0.5), Inches(1.85), SW - Inches(1), Inches(0.45),
    size=16, bold=True, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)
txb(sl, "Deepfake Detector   ·   AI Threat Hunter   ·   MITRE ATT&CK Integration",
    Inches(0.5), Inches(2.3), SW - Inches(1), Inches(0.35),
    size=12, color=RGBColor(0x90, 0xca, 0xf9), align=PP_ALIGN.CENTER)

# Cyan underline
rect(sl, Inches(1.5), Inches(2.75), SW - Inches(3), Inches(0.05),
     RGBColor(0x00, 0xbc, 0xd4))

# Two tool cards
half = (SW - Inches(0.8)) / 2
# Left card — Deepfake
rect(sl, Inches(0.4), Inches(3.45), half, Inches(2.2), LIGHT_RED,
     DARK_RED, Pt(2))
txb(sl, "01  DEEPFAKE DETECTOR", Inches(0.5), Inches(3.55), half - Inches(0.2), Inches(0.45),
    size=14, bold=True, color=DARK_RED)
txb(sl,
    "AI Vision Forensics · Media Authenticity\n"
    "OpenCV · PyMuPDF · Groq · Claude · Gemini\n\n"
    "Input:  Images · Videos · PDFs · Screenshots\n"
    "Output: AI Forensic Report (.txt download)",
    Inches(0.5), Inches(4.0), half - Inches(0.2), Inches(1.6),
    size=11, color=BLACK)

# Right card — Threat Hunter
rect(sl, Inches(0.4) + half + Inches(0.0), Inches(3.45), half, Inches(2.2), LIGHT_BLUE,
     BLUE, Pt(2))
txb(sl, "02  AI THREAT HUNTER", Inches(0.4) + half + Inches(0.1), Inches(3.55),
    half - Inches(0.2), Inches(0.45),
    size=14, bold=True, color=BLUE)
txb(sl,
    "Isolation Forest · MITRE ATT&CK · IR Playbook\n"
    "Scikit-learn · Plotly · Anthropic API · Streamlit\n\n"
    "Input:  CSV · JSON · Syslog · Live Feed\n"
    "Output: Threat Dashboard · IR Playbook (.txt)",
    Inches(0.4) + half + Inches(0.1), Inches(4.0), half - Inches(0.2), Inches(1.6),
    size=11, color=BLACK)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 2 — WHY THIS PROJECT MATTERS
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "WHY THIS PROJECT MATTERS", NAVY, WHITE,
           "The real-world problems this suite solves")

# 4 cards in 2x2 grid
CARD_W = (SW - Inches(0.9)) / 2
CARD_H = Inches(2.6)
CARD_X = [Inches(0.4), Inches(0.5) + CARD_W]
CARD_Y = [Inches(1.25), Inches(3.95)]

cards = [
    (DARK_RED,   "Deepfake Crisis",
     "Over 500,000 deepfake videos circulate online. AI-generated media is used for "
     "fraud, disinformation and identity theft — costing billions annually. "
     "Traditional detection tools rely on single-vendor APIs with no fallback, "
     "failing when one service goes down."),
    (BLUE,       "Cyber Threat Surge",
     "Cyberattacks increased by 38% in 2023. Most organisations lack the tools "
     "to detect intrusions in real time. Conventional SIEM systems require months of "
     "labelled data before they can detect threats — leaving networks exposed on day one."),
    (DARK_GREEN, "Our Solution",
     "This suite addresses both challenges with zero vendor dependency, no labelled "
     "training data, and real-time AI analysis. MITRE ATT&CK mapping and automated "
     "IR playbooks mean any analyst can respond effectively within minutes of an alert."),
    (TEAL,       "Real-World Impact",
     "Built for immediate deployment: works on any network log format, any media type, "
     "with graceful degradation when APIs are unavailable. From raw data to a "
     "downloadable forensic report or IR playbook in under 10 seconds."),
]

BG_MAP = {
    DARK_RED: LIGHT_RED, BLUE: LIGHT_BLUE,
    DARK_GREEN: RGBColor(0xe8, 0xf5, 0xe9), TEAL: LIGHT_TEAL
}
positions = [(CARD_X[0], CARD_Y[0]), (CARD_X[1], CARD_Y[0]),
             (CARD_X[0], CARD_Y[1]), (CARD_X[1], CARD_Y[1])]

for (cx, cy), (accent, title, body) in zip(positions, cards):
    rect(sl, cx, cy, CARD_W - Inches(0.1), CARD_H, BG_MAP[accent], accent, Pt(2))
    txb(sl, title, cx + Inches(0.15), cy + Inches(0.1),
        CARD_W - Inches(0.4), Inches(0.4),
        size=14, bold=True, color=accent)
    txb(sl, body, cx + Inches(0.15), cy + Inches(0.55),
        CARD_W - Inches(0.4), CARD_H - Inches(0.7),
        size=11, color=BLACK)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 3 — PROJECT OVERVIEW & ARCHITECTURE
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "PROJECT OVERVIEW", NAVY, WHITE,
           "Integrated Streamlit platform — two tools, one application")

# Two-col overview
half2 = (SW - Inches(0.9)) / 2
LEFT_X = Inches(0.4)
RIGHT_X = Inches(0.45) + half2
TOP_Y = Inches(1.25)

# Headers
rect(sl, LEFT_X, TOP_Y, half2 - Inches(0.05), Inches(0.4),
     RGBColor(0xff, 0xcd, 0xd2))
txb(sl, "DEEPFAKE DETECTOR", LEFT_X + Inches(0.1), TOP_Y + Inches(0.05),
    half2 - Inches(0.25), Inches(0.32), size=13, bold=True, color=DARK_RED)
rect(sl, RIGHT_X, TOP_Y, half2 - Inches(0.05), Inches(0.4),
     RGBColor(0xbb, 0xde, 0xfb))
txb(sl, "AI THREAT HUNTER", RIGHT_X + Inches(0.1), TOP_Y + Inches(0.05),
    half2 - Inches(0.25), Inches(0.32), size=13, bold=True, color=BLUE)

# Body cards
dd_text = (
    "Analyses images, videos and PDFs using multi-provider AI vision APIs "
    "to detect GAN-generated faces, splicing, inpainting and document fakery "
    "across 7 forensic dimensions.\n\n"
    "Input:   Images · Videos · PDFs · Screenshots\n"
    "Output:  AI Forensic Report (.txt)"
)
th_text = (
    "Ingests network logs and applies Isolation Forest unsupervised ML to detect "
    "port scans, brute force, data exfiltration and C2 beaconing — mapped to MITRE ATT&CK.\n\n"
    "Input:   CSV · JSON · Syslog · Live Feed\n"
    "Output:  Threat Dashboard + IR Playbook (.txt)"
)
rect(sl, LEFT_X, TOP_Y + Inches(0.4), half2 - Inches(0.05), Inches(1.7), LIGHT_RED)
txb(sl, dd_text, LEFT_X + Inches(0.1), TOP_Y + Inches(0.45),
    half2 - Inches(0.25), Inches(1.6), size=11, color=BLACK)
rect(sl, RIGHT_X, TOP_Y + Inches(0.4), half2 - Inches(0.05), Inches(1.7), LIGHT_BLUE)
txb(sl, th_text, RIGHT_X + Inches(0.1), TOP_Y + Inches(0.45),
    half2 - Inches(0.25), Inches(1.6), size=11, color=BLACK)

# Architecture section
ARC_Y = TOP_Y + Inches(2.3)
rect(sl, Inches(0.4), ARC_Y, SW - Inches(0.8), Inches(0.35), NAVY)
txb(sl, "ARCHITECTURE", Inches(0.5), ARC_Y + Inches(0.06),
    SW - Inches(1.0), Inches(0.25), size=13, bold=True, color=WHITE)

table_block(
    sl,
    ["Component", "Details"],
    [
        ["Entry Point", "Home.py — Streamlit landing with tool selector cards"],
        ["Core Isolation", "sys.modules['core*'] flushed between pages — prevents package collision"],
        ["AI Key Pool", "Groq (Llama Vision) → Claude (claude-3.5-sonnet) → Gemini (gemini-1.5-pro)"],
        ["Launch Command", "python -m streamlit run Home.py"],
    ],
    Inches(0.4), ARC_Y + Inches(0.35), SW - Inches(0.8),
    [0.25, 0.75],
    hdr_bg=NAVY, hdr_size=10, row_size=10, alt_bg=True
)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 4 — DEEPFAKE DETECTOR — PIPELINE & FEATURES
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "01  |  DEEPFAKE DETECTOR", DARK_RED, WHITE,
           "Multi-provider AI vision forensics — images, videos, PDFs, screenshots")

# Analysis Pipeline (horizontal arrows)
steps = ["Upload\nImage/Video/PDF", "Preprocess\nOpenCV · PIL",
         "AI Vision\nKey Rotation", "7 Dimensions\nForensic JSON", "Report\nVerdict + .txt"]
arrows = ["›"] * 4
PIPE_Y = Inches(1.3)
PIPE_H = Inches(0.85)
n = len(steps)
arrow_w = Inches(0.35)
step_w = (SW - Inches(0.8) - arrow_w * (n - 1)) / n
px = Inches(0.4)
for i, step in enumerate(steps):
    rect(sl, px, PIPE_Y, step_w, PIPE_H, LIGHT_RED, DARK_RED, Pt(1))
    txb(sl, step, px + Inches(0.05), PIPE_Y + Inches(0.1),
        step_w - Inches(0.1), PIPE_H - Inches(0.15),
        size=10, bold=False, color=DARK_RED, align=PP_ALIGN.CENTER)
    px += step_w
    if i < n - 1:
        txb(sl, "›", px, PIPE_Y + Inches(0.2), arrow_w, PIPE_H,
            size=22, bold=True, color=DARK_RED, align=PP_ALIGN.CENTER)
        px += arrow_w

# Key Features
FEAT_Y = Inches(2.35)
rect(sl, Inches(0.4), FEAT_Y, SW - Inches(0.8), Inches(0.33), DARK_RED)
txb(sl, "KEY FEATURES", Inches(0.5), FEAT_Y + Inches(0.06),
    SW - Inches(1.0), Inches(0.25), size=13, bold=True, color=WHITE)
table_block(
    sl,
    ["Feature", "Detail"],
    [
        ["AI Key Rotation", "Groq → Claude → Gemini — exhausted keys skipped automatically"],
        ["Heuristic Fallback", "FFT + ELA + noise analysis runs when all AI keys are unavailable"],
        ["QR Detection", "OpenCV QRCodeDetector scans every image; URLs classified for risk"],
        ["PDF Support", "PyMuPDF rasterises up to 5 PDF pages; findings exported as .txt"],
    ],
    Inches(0.4), FEAT_Y + Inches(0.33), SW - Inches(0.8),
    [0.22, 0.78],
    hdr_bg=DARK_RED, hdr_size=10, row_size=10, alt_bg=True
)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 5 — 7-DIMENSION ANALYSIS
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "7-DIMENSION FORENSIC ANALYSIS", DARK_RED, WHITE,
           "Every image or video is checked across all 7 dimensions simultaneously")

table_block(
    sl,
    ["#", "Dimension", "What Is Analysed"],
    [
        ["1", "Facial Forensics",
         "Skin texture, eye asymmetry, hair boundary artefacts, geometry inconsistencies"],
        ["2", "GAN Artifacts",
         "Checkerboard patterns, spectral anomalies, upsampling traces in frequency domain"],
        ["3", "Noise & Compression",
         "JPEG DCT blocks, sensor noise distribution, double-compression signatures"],
        ["4", "Lighting & Shadows",
         "Specular highlight consistency, shadow direction matching, reflection analysis"],
        ["5", "Background & Depth",
         "Semantic coherence, depth-of-field naturalism, edge boundary analysis"],
        ["6", "Colour & Chromatic",
         "HSV channel distribution, colour temperature, saturation anomalies"],
        ["7", "Document / Text",
         "Font consistency, QR code validity, metadata timestamps, document structure"],
    ],
    Inches(0.4), Inches(1.25), SW - Inches(0.8),
    [0.05, 0.22, 0.73],
    hdr_bg=DARK_RED, hdr_size=11, row_size=11, alt_bg=True
)

# Verdict callout
rect(sl, Inches(0.4), Inches(6.5), SW - Inches(0.8), Inches(0.55),
     RGBColor(0xff, 0xf3, 0xe0))
txb(sl,
    "Final Verdict: FAKE | AUTHENTIC | INCONCLUSIVE  — with AI confidence score (0–100%) "
    "and primary manipulation type (GAN · Splicing · Inpainting · Identity Swap · Document Forgery)",
    Inches(0.5), Inches(6.55), SW - Inches(1.0), Inches(0.45),
    size=11, color=ORANGE, bold=False)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 6 — AI THREAT HUNTER — PIPELINE & FEATURES
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "02  |  AI THREAT HUNTER", TEAL, WHITE,
           "Isolation Forest anomaly detection — no labelled training data required")

# Pipeline
steps = ["Ingest\nCSV/JSON/Live", "Features\n10 engineered",
         "Iso Forest\nAnomaly score", "Classify\n5 threat types",
         "AI Report\nMITRE + IR", "Dashboard\n6 tabs"]
n = len(steps)
arrow_w = Inches(0.25)
step_w = (SW - Inches(0.8) - arrow_w * (n - 1)) / n
PIPE_Y = Inches(1.3)
PIPE_H = Inches(0.8)
px = Inches(0.4)
for i, step in enumerate(steps):
    rect(sl, px, PIPE_Y, step_w, PIPE_H, LIGHT_TEAL, TEAL, Pt(1))
    txb(sl, step, px + Inches(0.04), PIPE_Y + Inches(0.1),
        step_w - Inches(0.08), PIPE_H - Inches(0.15),
        size=10, color=TEAL, align=PP_ALIGN.CENTER)
    px += step_w
    if i < n - 1:
        txb(sl, "›", px, PIPE_Y + Inches(0.15), arrow_w, PIPE_H,
            size=20, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
        px += arrow_w

# Dashboard Tabs
TABS_Y = Inches(2.3)
rect(sl, Inches(0.4), TABS_Y, SW - Inches(0.8), Inches(0.33), TEAL)
txb(sl, "DASHBOARD TABS", Inches(0.5), TABS_Y + Inches(0.06),
    SW - Inches(1.0), Inches(0.25), size=13, bold=True, color=WHITE)
table_block(
    sl,
    ["Tab", "Content"],
    [
        ["Overview", "Threat timeline scatter, distribution pie, top attacker IPs, heatmap, MITRE bar"],
        ["Threat Log", "Sortable table of all detected threats, risk-coloured, CSV export"],
        ["AI Analysis", "Select any threat → full AI forensic report + MITRE + risk gauge"],
        ["Incident Response", "AI-generated IR playbook → download as .txt for SOC handoff"],
        ["Network Graph", "Force-directed graph: red nodes = attackers, red edges = attack paths"],
        ["Live Feed", "@st.fragment 5s refresh from live_feed.csv — full page never reloads"],
    ],
    Inches(0.4), TABS_Y + Inches(0.33), SW - Inches(0.8),
    [0.18, 0.82],
    hdr_bg=TEAL, hdr_size=10, row_size=10, alt_bg=True
)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 7 — MITRE ATT&CK MAPPING
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "MITRE ATT&CK MAPPING — 5 THREAT TYPES", TEAL, WHITE,
           "Every detected threat is automatically mapped to the MITRE ATT&CK framework")

table_block(
    sl,
    ["Threat Type", "Detection Pattern", "Tactic / Technique", "ATT&CK Name"],
    [
        ["Port Scan",
         "One IP → 50+ ports, tiny bytes, high DENY rate",
         "TA0043 / T1046",
         "Network Service Discovery"],
        ["Brute Force",
         "High-frequency logins to port 22/3389, all DENY",
         "TA0006 / T1110.001",
         "Password Guessing"],
        ["Data Exfiltration",
         "Outbound > 1 MB per event, external IP destination",
         "TA0010 / T1048.003",
         "Exfil via Unencrypted Protocol"],
        ["C2 / Suspicious",
         "Beaconing to ports 4444 / 1337 / 9001",
         "TA0011 / T1071.001",
         "Application Layer Protocol"],
        ["Anomalous Traffic",
         "Statistical outlier, no rule matches",
         "TA0007 / T1040",
         "Network Sniffing"],
    ],
    Inches(0.4), Inches(1.25), SW - Inches(0.8),
    [0.17, 0.35, 0.22, 0.26],
    hdr_bg=TEAL, hdr_size=11, row_size=11, alt_bg=True
)

# Kill Chain callout
KC_Y = Inches(5.05)
rect(sl, Inches(0.4), KC_Y, SW - Inches(0.8), Inches(0.35), NAVY)
txb(sl, "CYBER KILL CHAIN PHASES", Inches(0.5), KC_Y + Inches(0.07),
    SW - Inches(1.0), Inches(0.25), size=13, bold=True, color=WHITE)
phases = ["Reconnaissance", "Weaponisation", "Delivery", "Exploitation", "C2", "Exfiltration", "Impact"]
pw = (SW - Inches(0.8)) / len(phases)
for i, ph in enumerate(phases):
    col = DARK_RED if i % 2 == 0 else NAVY
    rect(sl, Inches(0.4) + i * pw, KC_Y + Inches(0.35), pw, Inches(0.55), col)
    txb(sl, ph, Inches(0.4) + i * pw + Inches(0.02),
        KC_Y + Inches(0.42), pw - Inches(0.04), Inches(0.45),
        size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 8 — 10-FEATURE ENGINEERING
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "FEATURE ENGINEERING — 10 FEATURES", TEAL, WHITE,
           "Isolation Forest operates on these engineered features — no labels needed")

table_block(
    sl,
    ["Feature", "Encoding", "Threat Signal"],
    [
        ["bytes_sent",        "log1p(bytes_sent)",        "Large values signal data exfiltration"],
        ["bytes_recv",        "log1p(bytes_recv)",        "Response volume anomalies"],
        ["send/recv ratio",   "log1p(sent/recv + 1)",     "Asymmetric traffic = exfil or scan"],
        ["dest_port",         "Raw port number",          "Unusual ports signal C2 activity"],
        ["source_port",       "Raw source port",          "Ephemeral vs. fixed port patterns"],
        ["protocol",          "Label-encoded TCP/UDP",    "Protocol switches indicate evasion"],
        ["action",            "Label-encoded DENY/ALLOW", "High deny rate = brute force attack"],
        ["conn_rate",         "Connections per src IP",   "Frequency anomaly = port scan"],
        ["unique_ports",      "Distinct dest ports/IP",   "Many ports = network scan T1046"],
        ["duration",          "log1p(duration) optional", "Long sessions = C2 persistence"],
    ],
    Inches(0.4), Inches(1.25), SW - Inches(0.8),
    [0.2, 0.28, 0.52],
    hdr_bg=TEAL, hdr_size=11, row_size=10, alt_bg=True
)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 9 — AI FORENSIC ANALYSIS & IR PLAYBOOK
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "AI FORENSIC ANALYSIS  &  INCIDENT RESPONSE", NAVY, WHITE,
           "12-section AI report + downloadable IR playbook for SOC handoff")

# 12-section report — two columns
sections_l = [
    "Severity & Confidence — CRITICAL / HIGH / MEDIUM / LOW + AI confidence 0-100%",
    "Threat Title — Human-readable, e.g. 'Coordinated Port Scan — 185.220.x.x'",
    "MITRE ATT&CK — Tactic ID + Name  →  Technique ID + Name",
    "Kill Chain Phase — Recon / Weaponisation / Delivery / Exploitation / C2 / Exfil",
    "Executive Summary — 2-3 sentence plain-language description",
    "Evidence Analysis — Specific packet-level evidence supporting classification",
]
sections_r = [
    "Impact Assessment — Data loss, system compromise, service disruption",
    "Threat Actor Profile — Type · Sophistication · Motivation",
    "Indicators of Compromise — IPs, ports, byte patterns, timing signatures",
    "False Positive Assessment — Likelihood benign with explanation",
    "Related Threat Types — Other attacks commonly paired with this technique",
    "Analyst Notes — Caveats, confidence limitations, edge cases",
]
COL_Y = Inches(1.25)
COL_H = Inches(2.2)
col_w = (SW - Inches(0.9)) / 2

rect(sl, Inches(0.4), COL_Y, col_w, COL_H,
     RGBColor(0xf3, 0xe5, 0xf5))
rect(sl, Inches(0.5) + col_w, COL_Y, col_w, COL_H,
     RGBColor(0xe8, 0xf5, 0xe9))

for i, s in enumerate(sections_l):
    txb(sl, f"  {i+1:02d}.  {s}",
        Inches(0.45), COL_Y + Inches(0.05) + i * Inches(0.34),
        col_w - Inches(0.1), Inches(0.33),
        size=9.5, color=BLACK)
for i, s in enumerate(sections_r):
    txb(sl, f"  {i+7:02d}.  {s}",
        Inches(0.55) + col_w, COL_Y + Inches(0.05) + i * Inches(0.34),
        col_w - Inches(0.1), Inches(0.33),
        size=9.5, color=BLACK)

# IR Playbook
PB_Y = Inches(3.6)
rect(sl, Inches(0.4), PB_Y, SW - Inches(0.8), Inches(0.33), NAVY)
txb(sl, "INCIDENT RESPONSE PLAYBOOK", Inches(0.5), PB_Y + Inches(0.06),
    SW - Inches(1.0), Inches(0.25), size=13, bold=True, color=WHITE)
table_block(
    sl,
    ["Phase", "Timeframe", "Actions"],
    [
        ["Immediate Actions",         "0 – 15 min",   "Block IP at firewall, isolate endpoint, preserve logs"],
        ["Investigation Steps",       "15 – 60 min",  "SIEM log pull, EDR check, lateral movement hunt"],
        ["Containment & Eradication", "1 – 4 hrs",    "Revoke credentials, patch exploited service, clean malware"],
        ["Long-term Remediation",     "Days",          "Deploy detection rule, update policy, lessons learned"],
    ],
    Inches(0.4), PB_Y + Inches(0.33), SW - Inches(0.8),
    [0.28, 0.15, 0.57],
    hdr_bg=NAVY, hdr_size=10, row_size=10, alt_bg=True
)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 10 — TECHNOLOGY STACK
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "TECHNOLOGY STACK", DARK_GREEN, WHITE,
           "All open-source — no proprietary frameworks required")

table_block(
    sl,
    ["Library / Tool", "Version", "Purpose"],
    [
        ["Streamlit",              "1.39+",  "Web UI — multi-page, fragments, session state"],
        ["Scikit-learn",           "1.4+",   "Isolation Forest unsupervised anomaly detection"],
        ["OpenCV",                 "4.x",    "Image preprocessing, QR detection, video frame extraction"],
        ["Plotly",                 "5.x",    "Interactive scatter, bar, pie, heatmap, network graph, gauge"],
        ["Anthropic / Groq / GenAI", "Latest", "Claude · Llama Vision · Gemini — AI vision & text APIs"],
        ["PyMuPDF (fitz)",         "1.24+",  "PDF page rasterisation at 2x zoom"],
        ["Pandas / NumPy",         "2.x",    "Data ingestion, feature engineering, statistics"],
        ["Pillow (PIL)",           "10.x",   "Image loading, format conversion, preprocessing"],
    ],
    Inches(0.4), Inches(1.25), SW - Inches(0.8),
    [0.27, 0.1, 0.63],
    hdr_bg=DARK_GREEN, hdr_size=11, row_size=11, alt_bg=True
)

# Tech chips
chips = ["Streamlit", "Python 3.10+", "OpenCV", "Isolation Forest",
         "MITRE ATT&CK", "Plotly", "PyMuPDF", "Scikit-Learn",
         "Groq API", "Claude API", "Gemini API", "Pandas / NumPy"]
CHIP_Y = Inches(5.75)
chip_w = (SW - Inches(0.8)) / 6
for i, chip in enumerate(chips):
    col_idx = i % 6
    row_idx = i // 6
    cx = Inches(0.4) + col_idx * chip_w
    cy = CHIP_Y + row_idx * Inches(0.5)
    rect(sl, cx, cy, chip_w - Inches(0.05), Inches(0.42), INDIGO, MID_GREY, Pt(0.5))
    txb(sl, chip, cx + Inches(0.05), cy + Inches(0.08),
        chip_w - Inches(0.15), Inches(0.3),
        size=10, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SLIDE 11 — DEMO SCRIPT
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
header_bar(sl, "2-MINUTE DEMO SCRIPT", NAVY, WHITE,
           "Presenter guide — follow these steps in order during the demonstration")

# Left: Deepfake Detector
DEMO_Y = Inches(1.25)
half3 = (SW - Inches(0.9)) / 2

rect(sl, Inches(0.4), DEMO_Y, half3 - Inches(0.05), Inches(0.35), DARK_RED)
txb(sl, "DEEPFAKE DETECTOR", Inches(0.5), DEMO_Y + Inches(0.07),
    half3 - Inches(0.25), Inches(0.25), size=12, bold=True, color=WHITE)

dd_steps = [
    "1.  Home → Launch Deepfake Detector → Sidebar: Analyze Demo",
    "2.  Show verdict banner: FAKE / confidence % — manipulation type displayed",
    "3.  Expand AI Forensic Report → primary indicators + 7-dimension breakdown",
    "4.  Upload a real photo → shows AUTHENTIC with different evidence signals",
    "5.  Upload a PDF → multi-page scan with QR code detection result",
    "6.  Click Download Report → show the .txt forensic output file",
]
for i, step in enumerate(dd_steps):
    bg = LIGHT_RED if i % 2 == 0 else WHITE
    rect(sl, Inches(0.4), DEMO_Y + Inches(0.35) + i * Inches(0.5),
         half3 - Inches(0.05), Inches(0.5), bg)
    txb(sl, step,
        Inches(0.5), DEMO_Y + Inches(0.4) + i * Inches(0.5),
        half3 - Inches(0.25), Inches(0.42),
        size=10, color=BLACK)

# Right: AI Threat Hunter
rect(sl, Inches(0.45) + half3, DEMO_Y, half3 - Inches(0.05), Inches(0.35), TEAL)
txb(sl, "AI THREAT HUNTER", Inches(0.55) + half3, DEMO_Y + Inches(0.07),
    half3 - Inches(0.25), Inches(0.25), size=12, bold=True, color=WHITE)

th_steps = [
    "1.  Home → Launch AI Threat Hunter → Use Sample Data",
    "2.  Overview tab: timeline — red dots are attacks, dot size = data volume",
    "3.  Heatmap: attacks cluster at 2–4 AM — classic attacker behaviour",
    "4.  AI Analysis tab: select highest risk alert (Data Exfiltration, 90+/100)",
    "5.  MITRE: TA0010 → T1048.003  ·  Kill Chain: Exfiltration phase shown",
    "6.  Incident Response tab → download IR playbook as .txt",
    "7.  Sidebar → Live Feed mode → Terminal 2: python live_log_generator.py",
    "8.  Live Feed tab: new attack every 20–45s, panel refreshes every 5s",
]
for i, step in enumerate(th_steps):
    bg = LIGHT_TEAL if i % 2 == 0 else WHITE
    rect(sl, Inches(0.45) + half3,
         DEMO_Y + Inches(0.35) + i * Inches(0.5),
         half3 - Inches(0.05), Inches(0.5), bg)
    txb(sl, step,
        Inches(0.55) + half3,
        DEMO_Y + Inches(0.4) + i * Inches(0.5),
        half3 - Inches(0.25), Inches(0.42),
        size=10, color=BLACK)

footer_bar(sl)


# ════════════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════════════
prs.save(OUTPUT)
print(f"PPT generated: {OUTPUT}")
