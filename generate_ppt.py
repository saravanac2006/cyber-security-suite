"""
Cyber Security Suite — PowerPoint Generator (Rich Edition)
Run:  python generate_ppt.py
Output: Cyber_Security_Suite_Project.pptx
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "Cyber_Security_Suite_Project.pptx")

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY       = RGBColor(0x0D, 0x2B, 0x55)   # deep navy
NAVY2      = RGBColor(0x12, 0x3A, 0x6E)   # mid navy
BLUE       = RGBColor(0x15, 0x65, 0xC0)
TEAL       = RGBColor(0x00, 0x7A, 0x6E)
RED        = RGBColor(0xC6, 0x28, 0x28)
GREEN      = RGBColor(0x2E, 0x7D, 0x32)
ORANGE     = RGBColor(0xE6, 0x51, 0x00)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE  = RGBColor(0xF4, 0xF7, 0xFB)
LIGHT_BLUE = RGBColor(0xDE, 0xEA, 0xFD)
LIGHT_RED  = RGBColor(0xFD, 0xE8, 0xE8)
LIGHT_TEAL = RGBColor(0xDB, 0xF2, 0xEF)
LIGHT_GRN  = RGBColor(0xE4, 0xF4, 0xE4)
GREY       = RGBColor(0xE8, 0xEC, 0xF1)
MID_GREY   = RGBColor(0xB0, 0xBE, 0xCC)
DARK       = RGBColor(0x1A, 0x1A, 0x2E)
CYAN       = RGBColor(0x00, 0xBC, 0xD4)
GOLD       = RGBColor(0xF5, 0xA6, 0x23)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
W = prs.slide_width
H = prs.slide_height
BLANK = prs.slide_layouts[6]


# ── Core drawing helpers ───────────────────────────────────────────────────────

def rgb_hex(c: RGBColor) -> str:
    return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"

def add_rect(slide, x, y, w, h, fill, alpha=None):
    sp = slide.shapes.add_shape(1, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return sp

def add_rect_outline(slide, x, y, w, h, fill, line_color, line_pt=1.5):
    sp = slide.shapes.add_shape(1, x, y, w, h)
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.color.rgb = line_color
    sp.line.width = Pt(line_pt)
    return sp

def add_oval(slide, x, y, w, h, fill):
    sp = slide.shapes.add_shape(9, x, y, w, h)   # 9 = oval
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return sp

def txt(slide, text, x, y, w, h, *,
        size=16, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
        italic=False, wrap=True, bg=None):
    shape = slide.shapes.add_textbox(x, y, w, h)
    shape.word_wrap = wrap
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    else:
        shape.fill.background()
    tf = shape.text_frame
    tf.word_wrap = wrap
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return shape

def txt_box(slide, lines, x, y, w, h, bg=None):
    """lines = [(text, size, bold, color, align)]"""
    shape = slide.shapes.add_textbox(x, y, w, h)
    shape.word_wrap = True
    if bg:
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg
    else:
        shape.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    first = True
    for text, size, bold, color, align in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return shape

def logo_badge(slide, x, y, size_in, letter, fill, text_color=WHITE):
    """Circular badge with a single letter — used as icon."""
    add_oval(slide, x, y, size_in, size_in, fill)
    txt(slide, letter, x, y + size_in * 0.18, size_in, size_in * 0.65,
        size=int(size_in / Inches(1) * 30), bold=True,
        color=text_color, align=PP_ALIGN.CENTER)

def slide_footer(slide, page_num, total=7):
    """Thin footer bar with page number and brand."""
    FH = Inches(0.28)
    add_rect(slide, 0, H - FH, W, FH, NAVY)
    txt(slide, "CYBER SECURITY SUITE  |  AI-Powered Threat Detection & Media Forensics",
        Inches(0.35), H - FH + Inches(0.04), W - Inches(2), FH,
        size=8, color=MID_GREY, align=PP_ALIGN.LEFT)
    txt(slide, f"{page_num} / {total}",
        W - Inches(1.1), H - FH + Inches(0.04), Inches(0.9), FH,
        size=8, color=MID_GREY, align=PP_ALIGN.RIGHT)

def section_pill(slide, x, y, w, label, fill):
    """Small coloured label pill above a section."""
    PH = Inches(0.27)
    add_rect(slide, x, y, w, PH, fill)
    txt(slide, label, x + Inches(0.12), y + Inches(0.04), w - Inches(0.24), PH,
        size=9, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

def icon_circle(slide, x, y, r, fill, icon, icon_size=22):
    """Small icon circle — pass an emoji/symbol as icon string."""
    add_oval(slide, x, y, r, r, fill)
    txt(slide, icon, x, y + r * 0.1, r, r * 0.8,
        size=icon_size, color=WHITE, align=PP_ALIGN.CENTER)

def bullet_rows(slide, items, x, y, w, row_h, *,
                icon_color=BLUE, text_color=DARK, size=12,
                alt_fill=None, icon="▸"):
    """Render a list of (icon_label, body) rows."""
    for i, (label, body) in enumerate(items):
        ry = y + i * row_h
        if alt_fill and i % 2 == 0:
            add_rect(slide, x, ry, w, row_h, alt_fill)
        txt(slide, icon, x + Inches(0.08), ry + Inches(0.05),
            Inches(0.25), row_h, size=size + 1, bold=True, color=icon_color)
        if label:
            txt_box(slide, [
                (label, size, True, icon_color, PP_ALIGN.LEFT),
                (body,  size - 1, False, text_color, PP_ALIGN.LEFT),
            ], x + Inches(0.35), ry + Inches(0.03), w - Inches(0.45), row_h)
        else:
            txt(slide, body, x + Inches(0.35), ry + Inches(0.05),
                w - Inches(0.45), row_h, size=size, color=text_color)

def pipeline_strip(slide, steps, x, y, w, h, fill, accent):
    """Horizontal pipeline boxes with arrows."""
    n = len(steps)
    ARW = Inches(0.3)
    bw = (w - ARW * (n - 1)) / n
    px = x
    for i, (icon, title, sub) in enumerate(steps):
        add_rect_outline(slide, px, y, bw, h, fill, accent, 1.2)
        txt_box(slide, [
            (icon,  14, True,  accent,     PP_ALIGN.CENTER),
            (title, 10, True,  DARK,       PP_ALIGN.CENTER),
            (sub,   8,  False, MID_GREY,   PP_ALIGN.CENTER),
        ], px + Inches(0.04), y + Inches(0.06), bw - Inches(0.08), h)
        px += bw
        if i < n - 1:
            txt(slide, "›", px, y + h * 0.15, ARW, h * 0.7,
                size=20, bold=True, color=accent, align=PP_ALIGN.CENTER)
            px += ARW


# ════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER  (dark full-bleed)
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)

# Full dark background
add_rect(sl, 0, 0, W, H, DARK)

# Left accent stripe
add_rect(sl, 0, 0, Inches(0.18), H, CYAN)

# Right decorative panel
add_rect(sl, W - Inches(3.8), 0, Inches(3.8), H, NAVY)
add_rect(sl, W - Inches(3.8), 0, Inches(0.04), H, CYAN)

# ── Logo badge (top-left) ─────────────────────────────────────────
BADGE = Inches(1.2)
add_oval(sl, Inches(0.45), Inches(0.38), BADGE, BADGE, CYAN)
add_oval(sl, Inches(0.58), Inches(0.51), BADGE * 0.77, BADGE * 0.77, DARK)
txt(sl, "CS", Inches(0.45), Inches(0.48), BADGE, BADGE * 0.7,
    size=28, bold=True, color=CYAN, align=PP_ALIGN.CENTER)

# Brand label next to logo
txt(sl, "CYBER SECURITY SUITE", Inches(1.85), Inches(0.55), Inches(5), Inches(0.45),
    size=13, bold=True, color=CYAN, align=PP_ALIGN.LEFT)
txt(sl, "2026 EDITION", Inches(1.85), Inches(0.95), Inches(4), Inches(0.3),
    size=9, color=MID_GREY, align=PP_ALIGN.LEFT)

# ── Main title ────────────────────────────────────────────────────
txt(sl, "AI-POWERED", Inches(0.45), Inches(1.8), Inches(8.5), Inches(0.7),
    size=44, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
txt(sl, "CYBER SECURITY", Inches(0.45), Inches(2.4), Inches(8.5), Inches(0.95),
    size=56, bold=True, color=CYAN, align=PP_ALIGN.LEFT)
txt(sl, "SUITE", Inches(0.45), Inches(3.25), Inches(8.5), Inches(0.85),
    size=56, bold=True, color=WHITE, align=PP_ALIGN.LEFT)

# Cyan underline
add_rect(sl, Inches(0.45), Inches(4.05), Inches(5.5), Inches(0.06), CYAN)

txt(sl, "Threat Detection  ·  Media Forensics  ·  Incident Response",
    Inches(0.45), Inches(4.25), Inches(8.5), Inches(0.4),
    size=15, color=MID_GREY, align=PP_ALIGN.LEFT)

# ── Right panel — two tool cards ──────────────────────────────────
PX = W - Inches(3.55)
PW = Inches(3.25)

# Deepfake card
add_rect_outline(sl, PX, Inches(1.2), PW, Inches(2.1), RGBColor(0x1A, 0x0C, 0x0C), RED, 1.5)
icon_circle(sl, PX + Inches(0.18), Inches(1.32), Inches(0.55), RED, "🔍", 18)
txt(sl, "DEEPFAKE DETECTOR", PX + Inches(0.88), Inches(1.35), PW - Inches(1.0), Inches(0.38),
    size=12, bold=True, color=RED)
txt(sl, "AI Vision Forensics\nImages · Videos · PDFs\nGroq · Claude · Gemini",
    PX + Inches(0.18), Inches(1.78), PW - Inches(0.36), Inches(1.42),
    size=11, color=MID_GREY, align=PP_ALIGN.LEFT)

# Threat Hunter card
add_rect_outline(sl, PX, Inches(3.5), PW, Inches(2.1), RGBColor(0x08, 0x16, 0x1A), TEAL, 1.5)
icon_circle(sl, PX + Inches(0.18), Inches(3.62), Inches(0.55), TEAL, "🛡️", 18)
txt(sl, "AI THREAT HUNTER", PX + Inches(0.88), Inches(3.65), PW - Inches(1.0), Inches(0.38),
    size=12, bold=True, color=TEAL)
txt(sl, "Isolation Forest · MITRE ATT&CK\nCSV · JSON · Live Feed\nIR Playbook · Dashboard",
    PX + Inches(0.18), Inches(4.08), PW - Inches(0.36), Inches(1.42),
    size=11, color=MID_GREY, align=PP_ALIGN.LEFT)

# ── Bottom strip with tech chips ──────────────────────────────────
add_rect(sl, Inches(0.45), Inches(5.5), Inches(9.0), Inches(0.03), CYAN)
chips = ["Python 3.10", "Streamlit", "OpenCV", "Scikit-learn",
         "MITRE ATT&CK", "Plotly", "Anthropic API", "Groq API", "Gemini API"]
cw = Inches(8.8) / len(chips)
for i, c in enumerate(chips):
    txt(sl, c, Inches(0.45) + i * cw, Inches(5.6), cw, Inches(0.35),
        size=9, color=MID_GREY, align=PP_ALIGN.CENTER)

slide_footer(sl, 1)


# ════════════════════════════════════════════════════════════════════
# SLIDE 2 — WHY THIS PROJECT MATTERS
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, RED)          # left accent
add_rect(sl, 0, 0, W, Inches(1.1), NAVY)           # header bar

# Header
icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), CYAN, "!", 22)
txt(sl, "WHY THIS PROJECT MATTERS", Inches(1.08), Inches(0.3), Inches(9), Inches(0.5),
    size=26, bold=True, color=WHITE)
txt(sl, "Two critical problems solved with one integrated AI platform",
    Inches(1.08), Inches(0.75), Inches(9), Inches(0.3),
    size=12, color=MID_GREY)

# 4 cards 2×2
CARD_W = (W - Inches(0.8)) / 2 - Inches(0.1)
CARD_H = Inches(2.6)
gap = Inches(0.12)
cards = [
    (RED,   LIGHT_RED,  "🔍", "500,000+",  "Deepfake videos online",
     "AI-generated media drives fraud, disinformation and identity theft — costing billions annually."),
    (TEAL,  LIGHT_TEAL, "📈", "38%",       "Rise in cyberattacks (2023)",
     "Most organisations lack real-time intrusion detection — gaps left for months without alerting."),
    (BLUE,  LIGHT_BLUE, "⚡", "Zero",      "Labelled training data needed",
     "Isolation Forest detects threats unsupervised on day one — no setup delay, no labelling cost."),
    (GREEN, LIGHT_GRN,  "⏱️", "< 10 sec",  "Raw data to forensic report",
     "From upload to downloadable AI report or IR playbook with MITRE ATT&CK mapping built in."),
]
positions = [
    (Inches(0.3),              Inches(1.25)),
    (Inches(0.3) + CARD_W + gap, Inches(1.25)),
    (Inches(0.3),              Inches(1.25) + CARD_H + gap),
    (Inches(0.3) + CARD_W + gap, Inches(1.25) + CARD_H + gap),
]
for (cx, cy), (accent, bg, icon, stat, stat_lbl, body) in zip(positions, cards):
    add_rect_outline(sl, cx, cy, CARD_W, CARD_H, bg, accent, 2)
    add_rect(sl, cx, cy, CARD_W, Inches(0.38), accent)  # coloured top bar
    icon_circle(sl, cx + CARD_W - Inches(0.72), cy + Inches(0.45), Inches(0.58), accent, icon, 18)
    txt(sl, stat,     cx + Inches(0.18), cy + Inches(0.45), CARD_W - Inches(1.0), Inches(0.62),
        size=34, bold=True, color=accent)
    txt(sl, stat_lbl, cx + Inches(0.18), cy + Inches(1.02), CARD_W - Inches(1.0), Inches(0.3),
        size=10, bold=True, color=DARK)
    txt(sl, body,     cx + Inches(0.18), cy + Inches(1.35), CARD_W - Inches(0.36), Inches(1.2),
        size=11, color=RGBColor(0x44, 0x44, 0x44))

slide_footer(sl, 2)


# ════════════════════════════════════════════════════════════════════
# SLIDE 3 — DEEPFAKE DETECTOR
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, RED)
add_rect(sl, 0, 0, W, Inches(1.1), RED)

icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), WHITE, "🔍", 20)
txt(sl, "DEEPFAKE DETECTOR", Inches(1.08), Inches(0.28), Inches(9), Inches(0.52),
    size=28, bold=True, color=WHITE)
txt(sl, "Multi-provider AI vision forensics across 7 dimensions — images, videos, PDFs, screenshots",
    Inches(1.08), Inches(0.76), Inches(10), Inches(0.3), size=12, color=RGBColor(0xFF, 0xCC, 0xCC))

# Pipeline
pipeline_strip(sl,
    [("📥", "Upload",    "Image / Video / PDF"),
     ("⚙️", "Preprocess","OpenCV · PIL"),
     ("🤖", "AI Vision", "3 providers"),
     ("🔬", "7 Dims",    "Forensic JSON"),
     ("📄", "Report",    "Verdict + .txt")],
    Inches(0.3), Inches(1.22), W - Inches(0.6), Inches(1.05),
    LIGHT_RED, RED)

# 7 Dimensions — two columns of coloured chips
DIM_LABELS = [
    ("01", "Facial Forensics",    "Skin texture · Eye asymmetry · Hair boundaries"),
    ("02", "GAN Artifacts",       "Checkerboard · Spectral anomalies · Upsampling"),
    ("03", "Noise & Compression", "JPEG DCT blocks · Sensor noise · Double-compression"),
    ("04", "Lighting & Shadows",  "Specular highlights · Shadow direction"),
    ("05", "Background & Depth",  "Semantic coherence · Depth-of-field naturalism"),
    ("06", "Colour & Chromatic",  "HSV channels · Colour temperature · Saturation"),
    ("07", "Document / Text",     "Font consistency · QR codes · Metadata"),
]
section_pill(sl, Inches(0.3), Inches(2.4), Inches(3.5), "  7-DIMENSION ANALYSIS", RED)
col1, col2 = DIM_LABELS[:4], DIM_LABELS[3:]
col_x = [Inches(0.3), Inches(0.3) + (W - Inches(0.6)) / 2 + Inches(0.05)]
for ci, col in enumerate([DIM_LABELS[:4], DIM_LABELS[3:]]):
    cx = col_x[ci]
    cw = (W - Inches(0.7)) / 2
    for ri, (num, name, detail) in enumerate(col):
        ry = Inches(2.72) + ri * Inches(0.92)
        bg = LIGHT_RED if ri % 2 == 0 else WHITE
        add_rect_outline(sl, cx, ry, cw, Inches(0.88), bg, RGBColor(0xF5, 0xC0, 0xC0), 0.8)
        add_rect(sl, cx, ry, Inches(0.42), Inches(0.88), RED)
        txt(sl, num, cx, ry + Inches(0.18), Inches(0.42), Inches(0.5),
            size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        txt(sl, name,   cx + Inches(0.48), ry + Inches(0.08), cw - Inches(0.56), Inches(0.36),
            size=11, bold=True, color=RED)
        txt(sl, detail, cx + Inches(0.48), ry + Inches(0.44), cw - Inches(0.56), Inches(0.4),
            size=9.5, color=RGBColor(0x55, 0x66, 0x77))

# Key features strip at bottom
add_rect(sl, Inches(0.3), Inches(6.62), W - Inches(0.6), Inches(0.55), NAVY)
feats = ["🔄 Key Rotation: Groq → Claude → Gemini",
         "🛡️ Heuristic Fallback (FFT + ELA)",
         "📸 QR Detection + URL Risk",
         "📄 PDF: 5 pages via PyMuPDF"]
fw = (W - Inches(0.6)) / len(feats)
for i, f in enumerate(feats):
    txt(sl, f, Inches(0.3) + i * fw + Inches(0.12), Inches(6.68), fw - Inches(0.2), Inches(0.42),
        size=9.5, color=WHITE)

slide_footer(sl, 3)


# ════════════════════════════════════════════════════════════════════
# SLIDE 4 — AI THREAT HUNTER
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, TEAL)
add_rect(sl, 0, 0, W, Inches(1.1), TEAL)

icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), WHITE, "🛡️", 20)
txt(sl, "AI THREAT HUNTER", Inches(1.08), Inches(0.28), Inches(9), Inches(0.52),
    size=28, bold=True, color=WHITE)
txt(sl, "Isolation Forest unsupervised ML — no labelled training data — MITRE ATT&CK mapped",
    Inches(1.08), Inches(0.76), Inches(10), Inches(0.3), size=12, color=RGBColor(0xAA, 0xDD, 0xD8))

# Pipeline
pipeline_strip(sl,
    [("📥", "Ingest",    "CSV / JSON / Live"),
     ("🧮", "Features",  "10 engineered"),
     ("🌲", "Iso Forest","Anomaly score"),
     ("🎯", "Classify",  "5 threat types"),
     ("📊", "Dashboard", "6 tabs + export")],
    Inches(0.3), Inches(1.22), W - Inches(0.6), Inches(1.05),
    LIGHT_TEAL, TEAL)

# Two columns: Threat types + Dashboard tabs
section_pill(sl, Inches(0.3),   Inches(2.42), Inches(5.5),  "  5 THREAT TYPES — MITRE ATT&CK MAPPED", TEAL)
section_pill(sl, Inches(6.05),  Inches(2.42), Inches(6.9),  "  DASHBOARD TABS",                         NAVY)

threats = [
    ("🔍 Port Scan",         "TA0043 · T1046",      "One IP → 50+ ports, high DENY"),
    ("🔑 Brute Force",       "TA0006 · T1110.001",  "Freq logins to 22/3389"),
    ("📤 Data Exfiltration", "TA0010 · T1048.003",  "Outbound > 1 MB, external IP"),
    ("📡 C2 / Suspicious",   "TA0011 · T1071.001",  "Beaconing to ports 4444/1337"),
    ("⚠️ Anomalous Traffic", "TA0007 · T1040",      "Statistical outlier, unclassified"),
]
tabs = [
    ("📈 Overview",     "Timeline · Pie · Heatmap · MITRE bar"),
    ("📋 Threat Log",   "Sortable table · CSV export"),
    ("🤖 AI Analysis",  "Select threat → forensic report + gauge"),
    ("🚨 IR Playbook",  "AI-generated response → download .txt"),
    ("🕸️ Net Graph",    "Force-directed · red = attacker nodes"),
    ("📡 Live Feed",    "@st.fragment 5s refresh, no page reload"),
]
for ri, (name, mitre, detail) in enumerate(threats):
    ry = Inches(2.75) + ri * Inches(0.72)
    bg = LIGHT_TEAL if ri % 2 == 0 else WHITE
    add_rect_outline(sl, Inches(0.3), ry, Inches(5.5), Inches(0.68), bg,
                     RGBColor(0xA8, 0xD8, 0xD4), 0.7)
    txt(sl, name,   Inches(0.42), ry + Inches(0.06), Inches(2.3), Inches(0.32),
        size=10, bold=True, color=TEAL)
    txt(sl, mitre,  Inches(0.42), ry + Inches(0.37), Inches(2.0), Inches(0.28),
        size=8.5, bold=True, color=NAVY)
    txt(sl, detail, Inches(2.65), ry + Inches(0.18), Inches(3.0), Inches(0.45),
        size=9.5, color=DARK)

for ri, (tab, detail) in enumerate(tabs):
    ry = Inches(2.75) + ri * Inches(0.6)
    bg = LIGHT_BLUE if ri % 2 == 0 else WHITE
    add_rect_outline(sl, Inches(6.05), ry, Inches(6.9), Inches(0.56), bg,
                     RGBColor(0xB0, 0xC8, 0xE8), 0.7)
    txt(sl, tab,    Inches(6.17), ry + Inches(0.05), Inches(2.0),  Inches(0.28),
        size=10, bold=True, color=NAVY)
    txt(sl, detail, Inches(6.17), ry + Inches(0.3),  Inches(6.6),  Inches(0.24),
        size=9.5, color=DARK)

slide_footer(sl, 4)


# ════════════════════════════════════════════════════════════════════
# SLIDE 5 — MITRE ATT&CK & AI FORENSIC REPORT
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, GOLD)
add_rect(sl, 0, 0, W, Inches(1.1), NAVY)

icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), GOLD, "🎯", 20)
txt(sl, "MITRE ATT&CK  &  AI FORENSIC REPORT", Inches(1.08), Inches(0.28), Inches(10), Inches(0.52),
    size=26, bold=True, color=WHITE)
txt(sl, "Every detected threat is automatically mapped — report generated in seconds",
    Inches(1.08), Inches(0.76), Inches(10), Inches(0.3), size=12, color=MID_GREY)

# Kill Chain strip
add_rect(sl, Inches(0.3), Inches(1.2), W - Inches(0.6), Inches(0.3), NAVY2)
txt(sl, "CYBER KILL CHAIN", Inches(0.42), Inches(1.24), Inches(2.4), Inches(0.24),
    size=9, bold=True, color=CYAN)
phases   = ["Recon", "Weaponise", "Deliver", "Exploit", "Install", "C2", "Impact"]
ph_cols  = [RED, RGBColor(0xC6,0x5C,0x00), ORANGE, GREEN, TEAL, BLUE, NAVY]
pw = (W - Inches(3.3)) / len(phases)
for i, (ph, col) in enumerate(zip(phases, ph_cols)):
    px2 = Inches(2.65) + i * pw
    add_rect(sl, px2, Inches(1.2), pw - Inches(0.04), Inches(0.3), col)
    txt(sl, ph, px2, Inches(1.22), pw - Inches(0.06), Inches(0.26),
        size=8.5, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Left: MITRE mapping table
section_pill(sl, Inches(0.3), Inches(1.62), Inches(6.6), "  MITRE ATT&CK THREAT MAPPING", NAVY)

mitre_rows = [
    ("🔍", "Port Scan",      "TA0043", "T1046",     "Network Service Discovery"),
    ("🔑", "Brute Force",    "TA0006", "T1110.001", "Password Guessing"),
    ("📤", "Data Exfil",     "TA0010", "T1048.003", "Exfil Unencrypted Protocol"),
    ("📡", "C2 Beaconing",   "TA0011", "T1071.001", "Application Layer Protocol"),
    ("⚠️", "Anomalous",      "TA0007", "T1040",     "Network Sniffing"),
]
hdrs = ["", "Threat", "Tactic", "Technique", "ATT&CK Name"]
hcols = [0.06, 0.2, 0.12, 0.17, 0.45]
row_h = Inches(0.52)
TABLE_Y = Inches(1.94)
TABLE_W = Inches(6.6)
# header row
px2 = Inches(0.3)
for h, r in zip(hdrs, hcols):
    cw = TABLE_W * r
    add_rect(sl, px2, TABLE_Y, cw, Inches(0.3), NAVY)
    txt(sl, h, px2 + Inches(0.04), TABLE_Y + Inches(0.04), cw - Inches(0.08), Inches(0.25),
        size=8.5, bold=True, color=WHITE)
    px2 += cw
for ri, (icon, threat, tac, tech, name) in enumerate(mitre_rows):
    ry = TABLE_Y + Inches(0.3) + ri * row_h
    bg = LIGHT_BLUE if ri % 2 == 0 else WHITE
    cells = [icon, threat, tac, tech, name]
    px2 = Inches(0.3)
    for ci, (cell, r) in enumerate(zip(cells, hcols)):
        cw = TABLE_W * r
        add_rect_outline(sl, px2, ry, cw, row_h, bg, MID_GREY, 0.4)
        col2 = NAVY if ci in (2, 3) else DARK
        sz = 9 if ci == 4 else 10
        txt(sl, cell, px2 + Inches(0.04), ry + Inches(0.08),
            cw - Inches(0.08), row_h - Inches(0.1),
            size=sz, bold=(ci == 1), color=col2)
        px2 += cw

# Right: 12-section report summary
section_pill(sl, Inches(7.1), Inches(1.62), Inches(5.9), "  AI FORENSIC REPORT — 12 SECTIONS", RED)
report_sections = [
    ("🔴", "Severity & Confidence",   "CRITICAL / HIGH / MEDIUM / LOW + 0-100%"),
    ("🎯", "MITRE ATT&CK",            "Tactic → Technique → Sub-technique"),
    ("🔗", "Kill Chain Phase",         "Recon → C2 → Exfil phase shown"),
    ("📝", "Executive Summary",        "2-3 sentence plain-language description"),
    ("🔬", "Evidence Analysis",        "Packet-level evidence for classification"),
    ("🏢", "Impact Assessment",        "Data loss · Compromise · Disruption risk"),
    ("👤", "Threat Actor Profile",     "Type · Sophistication · Motivation"),
    ("📌", "Indicators of Compromise", "IPs · Ports · Byte patterns · Timing"),
    ("🚨", "IR Playbook",              "4-phase response (0-15 min → days)"),
]
for ri, (icon, sec, detail) in enumerate(report_sections):
    ry = Inches(1.94) + ri * Inches(0.495)
    bg = RGBColor(0xFE, 0xF3, 0xF3) if ri % 2 == 0 else WHITE
    add_rect_outline(sl, Inches(7.1), ry, Inches(5.9), Inches(0.47), bg,
                     RGBColor(0xF0, 0xC0, 0xC0), 0.5)
    txt(sl, icon, Inches(7.15), ry + Inches(0.06), Inches(0.35), Inches(0.35), size=13, color=DARK)
    txt(sl, sec,    Inches(7.55), ry + Inches(0.04), Inches(2.1), Inches(0.24),
        size=9.5, bold=True, color=RED)
    txt(sl, detail, Inches(7.55), ry + Inches(0.26), Inches(5.3), Inches(0.22),
        size=8.5, color=DARK)

slide_footer(sl, 5)


# ════════════════════════════════════════════════════════════════════
# SLIDE 6 — TECHNOLOGY STACK
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, GREEN)
add_rect(sl, 0, 0, W, Inches(1.1), GREEN)

icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), WHITE, "⚙️", 20)
txt(sl, "TECHNOLOGY STACK", Inches(1.08), Inches(0.28), Inches(9), Inches(0.52),
    size=28, bold=True, color=WHITE)
txt(sl, "100% open-source · no proprietary frameworks · runs on any machine",
    Inches(1.08), Inches(0.76), Inches(10), Inches(0.3), size=12, color=RGBColor(0xAA, 0xDD, 0xAA))

tech = [
    ("🌐", "Streamlit",              "1.39+",  "Web UI — multi-page, fragments, session state"),
    ("🌲", "Scikit-learn",           "1.4+",   "Isolation Forest — unsupervised anomaly detection"),
    ("📷", "OpenCV",                 "4.x",    "Image preprocessing · QR detection · video frames"),
    ("📊", "Plotly",                 "5.x",    "Scatter · Pie · Heatmap · Network graph · Gauge"),
    ("🤖", "Anthropic / Groq / GenAI","latest","Claude · Llama Vision · Gemini — AI vision + text"),
    ("📄", "PyMuPDF (fitz)",         "1.24+",  "PDF rasterisation at 2× zoom — up to 5 pages"),
    ("🔢", "Pandas / NumPy",         "2.x",    "Ingestion · Feature engineering · Statistics"),
    ("🖼️", "Pillow (PIL)",           "10.x",   "Image loading · Format conversion · Preprocessing"),
]

CARD_W2 = (W - Inches(0.8)) / 2 - Inches(0.08)
CARD_H2 = Inches(0.76)
gap2 = Inches(0.1)
for i, (icon, lib, ver, desc) in enumerate(tech):
    col = i % 2
    row = i // 2
    cx = Inches(0.3) + col * (CARD_W2 + gap2)
    cy = Inches(1.25) + row * (CARD_H2 + Inches(0.06))
    bg = LIGHT_GRN if row % 2 == 0 else WHITE
    add_rect_outline(sl, cx, cy, CARD_W2, CARD_H2, bg, RGBColor(0xB8, 0xDA, 0xB8), 0.8)
    add_rect(sl, cx, cy, Inches(0.52), CARD_H2, GREEN)
    txt(sl, icon, cx, cy + CARD_H2 * 0.2, Inches(0.52), CARD_H2 * 0.6,
        size=18, color=WHITE, align=PP_ALIGN.CENTER)
    txt(sl, lib, cx + Inches(0.58), cy + Inches(0.06), Inches(2.2), Inches(0.32),
        size=12, bold=True, color=GREEN)
    txt(sl, f"v{ver}", cx + Inches(0.58) + Inches(2.22), cy + Inches(0.06), Inches(1.0), Inches(0.28),
        size=9, color=MID_GREY)
    txt(sl, desc, cx + Inches(0.58), cy + Inches(0.38), CARD_W2 - Inches(0.68), Inches(0.34),
        size=9.5, color=DARK)

# Architecture note at bottom
add_rect(sl, Inches(0.3), Inches(4.88), W - Inches(0.6), Inches(0.5), NAVY)
txt(sl,
    "Architecture:  Home.py  →  pages/1_Deepfake_Detector.py  ·  pages/2_AI_Threat_Hunter.py  ·  pages/3_Help.py    "
    "Launch: python -m streamlit run Home.py",
    Inches(0.5), Inches(4.94), W - Inches(1.0), Inches(0.4),
    size=10, color=CYAN)

slide_footer(sl, 6)


# ════════════════════════════════════════════════════════════════════
# SLIDE 7 — DEMO SCRIPT
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, OFF_WHITE)
add_rect(sl, 0, 0, Inches(0.18), H, CYAN)
add_rect(sl, 0, 0, W, Inches(1.1), NAVY)

icon_circle(sl, Inches(0.35), Inches(0.28), Inches(0.55), CYAN, "▶", 22)
txt(sl, "2-MINUTE DEMO SCRIPT", Inches(1.08), Inches(0.28), Inches(9), Inches(0.52),
    size=28, bold=True, color=WHITE)
txt(sl, "Follow these steps in order during the live demonstration",
    Inches(1.08), Inches(0.76), Inches(10), Inches(0.3), size=12, color=MID_GREY)

HALF = (W - Inches(0.8)) / 2

# Left — Deepfake Detector
add_rect(sl, Inches(0.3), Inches(1.2), HALF, Inches(0.38), RED)
icon_circle(sl, Inches(0.35), Inches(1.24), Inches(0.32), WHITE, "🔍", 13)
txt(sl, "  DEEPFAKE DETECTOR", Inches(0.72), Inches(1.26), HALF - Inches(0.5), Inches(0.32),
    size=13, bold=True, color=WHITE)

dd = [
    ("Home → Launch Deepfake Detector → Sidebar: Analyze Demo",                 RED),
    ("Verdict banner: FAKE / confidence % — manipulation type shown",            DARK),
    ("Expand AI Forensic Report → primary indicators + 7-dimension breakdown",   DARK),
    ("Upload a real photo → shows AUTHENTIC with different evidence signals",     DARK),
    ("Upload a PDF → multi-page scan with QR detection result",                  DARK),
    ("Download Report → show the .txt forensic output",                          RED),
]
for i, (step, col) in enumerate(dd):
    ry = Inches(1.62) + i * Inches(0.82)
    bg = LIGHT_RED if i % 2 == 0 else WHITE
    add_rect_outline(sl, Inches(0.3), ry, HALF, Inches(0.78), bg,
                     RGBColor(0xF0, 0xC0, 0xC0), 0.6)
    add_oval(sl, Inches(0.38), ry + Inches(0.22), Inches(0.32), Inches(0.32), RED)
    txt(sl, str(i + 1), Inches(0.38), ry + Inches(0.22), Inches(0.32), Inches(0.32),
        size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(sl, step, Inches(0.78), ry + Inches(0.15), HALF - Inches(0.55), Inches(0.5),
        size=10, color=col)

# Right — AI Threat Hunter
RX = Inches(0.3) + HALF + Inches(0.1)
add_rect(sl, RX, Inches(1.2), HALF, Inches(0.38), TEAL)
icon_circle(sl, RX + Inches(0.05), Inches(1.24), Inches(0.32), WHITE, "🛡️", 13)
txt(sl, "  AI THREAT HUNTER", RX + Inches(0.42), Inches(1.26), HALF - Inches(0.5), Inches(0.32),
    size=13, bold=True, color=WHITE)

th = [
    ("Home → Launch AI Threat Hunter → Use Sample Data",                         TEAL),
    ("Overview: timeline — red dots = attacks, dot size = data volume",           DARK),
    ("Heatmap: attacks cluster 2-4 AM — classic attacker behaviour",             DARK),
    ("AI Analysis: select highest risk (Data Exfiltration, 90+/100)",            DARK),
    ("MITRE: TA0010 → T1048.003  ·  Kill Chain: Exfiltration phase",             DARK),
    ("IR Playbook tab → download .txt  |  Live Feed: attacks every 20-45s",      TEAL),
]
for i, (step, col) in enumerate(th):
    ry = Inches(1.62) + i * Inches(0.82)
    bg = LIGHT_TEAL if i % 2 == 0 else WHITE
    add_rect_outline(sl, RX, ry, HALF, Inches(0.78), bg,
                     RGBColor(0xA8, 0xD8, 0xD4), 0.6)
    add_oval(sl, RX + Inches(0.08), ry + Inches(0.22), Inches(0.32), Inches(0.32), TEAL)
    txt(sl, str(i + 1), RX + Inches(0.08), ry + Inches(0.22), Inches(0.32), Inches(0.32),
        size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(sl, step, RX + Inches(0.48), ry + Inches(0.15), HALF - Inches(0.55), Inches(0.5),
        size=10, color=col)

slide_footer(sl, 7)


# ── Save ─────────────────────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f"PPT generated: {OUTPUT}")
