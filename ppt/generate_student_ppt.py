"""
Student-style 7-slide PPT — Cyber Security Suite + DNS Spoofing & Phishing
Core concepts gathered from:
  - Cyber_Security_Suite_5_Slide_Presentation.pptx
  - DNS_Spoofing_Phishing_Algorithm_Diagrams.pptx
Run:  python ppt/generate_student_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "Cyber_Security_Suite_Student.pptx")

# ── Palette (clean student look) ──────────────────────────────────────────────
NAVY    = RGBColor(0x0D, 0x2B, 0x55)
BLUE    = RGBColor(0x1A, 0x5C, 0xB8)
TEAL    = RGBColor(0x00, 0x7A, 0x6E)
RED     = RGBColor(0xC0, 0x26, 0x26)
GREEN   = RGBColor(0x2E, 0x7D, 0x32)
ORANGE  = RGBColor(0xD4, 0x6A, 0x00)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LGREY   = RGBColor(0xF2, 0xF4, 0xF8)
MGREY   = RGBColor(0xB0, 0xBB, 0xCC)
DARK    = RGBColor(0x1C, 0x1C, 0x2E)
LBLUE   = RGBColor(0xDC, 0xEA, 0xFD)
LTEAL   = RGBColor(0xD8, 0xF2, 0xEF)
LRED    = RGBColor(0xFC, 0xE8, 0xE8)
LGRN    = RGBColor(0xE4, 0xF4, 0xE5)
LORANGE = RGBColor(0xFD, 0xF0, 0xDC)
CYAN    = RGBColor(0x00, 0xBC, 0xD4)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
W, H = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]


# ── Helpers ───────────────────────────────────────────────────────────────────

def box(sl, x, y, w, h, fill, border=None, bw=1.0):
    sp = sl.shapes.add_shape(1, x, y, w, h)
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if border:
        sp.line.color.rgb = border; sp.line.width = Pt(bw)
    else:
        sp.line.fill.background()
    return sp

def oval(sl, x, y, w, h, fill):
    sp = sl.shapes.add_shape(9, x, y, w, h)
    sp.fill.solid(); sp.fill.fore_color.rgb = fill
    sp.line.fill.background()
    return sp

def t(sl, text, x, y, w, h, *,
      size=13, bold=False, color=DARK, align=PP_ALIGN.LEFT, italic=False):
    sh = sl.shapes.add_textbox(x, y, w, h)
    sh.word_wrap = True
    sh.fill.background()
    tf = sh.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size); r.font.bold = bold
    r.font.italic = italic; r.font.color.rgb = color
    return sh

def multiline(sl, lines, x, y, w, h):
    """lines = [(text, size, bold, color, align)]"""
    sh = sl.shapes.add_textbox(x, y, w, h)
    sh.word_wrap = True; sh.fill.background()
    tf = sh.text_frame; tf.word_wrap = True
    first = True
    for text, size, bold, color, align in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False; p.alignment = align
        r = p.add_run()
        r.text = text; r.font.size = Pt(size)
        r.font.bold = bold; r.font.color.rgb = color

def header(sl, title, subtitle="", accent=NAVY):
    """Standard slide header bar."""
    box(sl, 0, 0, W, Inches(1.05), accent)
    box(sl, 0, Inches(1.05), Inches(0.07), H - Inches(1.05), accent)  # left stripe
    t(sl, title, Inches(0.3), Inches(0.14), W - Inches(0.6), Inches(0.55),
      size=24, bold=True, color=WHITE)
    if subtitle:
        t(sl, subtitle, Inches(0.3), Inches(0.68), W - Inches(0.6), Inches(0.33),
          size=11, color=MGREY)

def footer(sl, num, total=6, names="Varunprasad V  &  Sakthivel Rajan"):
    FH = Inches(0.26)
    box(sl, 0, H - FH, W, FH, LGREY)
    t(sl, names, Inches(0.3), H - FH + Inches(0.04),
      W - Inches(2.5), FH, size=8, color=MGREY)
    t(sl, f"Slide {num} / {total}", W - Inches(1.5), H - FH + Inches(0.04),
      Inches(1.3), FH, size=8, color=MGREY, align=PP_ALIGN.RIGHT)

def bullet(sl, items, x, y, w, row_h=Inches(0.52), *,
           dot_color=BLUE, size=11.5):
    """Simple bullet list."""
    for i, (label, body) in enumerate(items):
        ry = y + i * row_h
        oval(sl, x, ry + Inches(0.14), Inches(0.18), Inches(0.18), dot_color)
        if label:
            multiline(sl, [
                (label, size, True,  dot_color, PP_ALIGN.LEFT),
                (body,  size - 1, False, DARK, PP_ALIGN.LEFT),
            ], x + Inches(0.28), ry, w - Inches(0.3), row_h)
        else:
            t(sl, body, x + Inches(0.28), ry + Inches(0.04),
              w - Inches(0.3), row_h, size=size, color=DARK)

def step_box(sl, x, y, w, h, num, title, body, fill, accent):
    box(sl, x, y, w, h, fill, accent, 1.5)
    box(sl, x, y, Inches(0.5), h, accent)
    t(sl, str(num), x, y + h * 0.25, Inches(0.5), h * 0.5,
      size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    multiline(sl, [
        (title, 11, True,  accent, PP_ALIGN.LEFT),
        (body,  10, False, DARK,   PP_ALIGN.LEFT),
    ], x + Inches(0.58), y + Inches(0.08), w - Inches(0.68), h - Inches(0.1))

def tag(sl, x, y, w, label, fill):
    box(sl, x, y, w, Inches(0.28), fill)
    t(sl, label, x + Inches(0.1), y + Inches(0.04), w - Inches(0.2), Inches(0.22),
      size=9, bold=True, color=WHITE)


# ════════════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, LGREY)
box(sl, 0, 0, W, Inches(4.6), NAVY)        # dark top half
box(sl, 0, Inches(4.6), Inches(0.07), H - Inches(4.6) - Inches(0.26), NAVY)

# Logo badge
oval(sl, Inches(0.45), Inches(0.4), Inches(1.3), Inches(1.3), CYAN)
oval(sl, Inches(0.62), Inches(0.57), Inches(0.96), Inches(0.96), NAVY)
t(sl, "CS", Inches(0.45), Inches(0.55), Inches(1.3), Inches(0.9),
  size=32, bold=True, color=CYAN, align=PP_ALIGN.CENTER)

# Title
t(sl, "CYBER SECURITY SUITE", Inches(2.1), Inches(0.4), Inches(9), Inches(0.65),
  size=36, bold=True, color=WHITE)
t(sl, "Two AI-Powered Tools. One Security Platform.",
  Inches(2.1), Inches(1.0), Inches(9), Inches(0.4),
  size=15, color=MGREY)

# Cyan line
box(sl, Inches(2.1), Inches(1.52), Inches(5.5), Inches(0.05), CYAN)

t(sl, "2026 Cyber Security Competition",
  Inches(2.1), Inches(1.65), Inches(7), Inches(0.35),
  size=12, color=MGREY, italic=True)

# Three topic cards
CARD_W = (W - Inches(0.6)) / 3 - Inches(0.1)
GAP    = Inches(0.15)
CARD_H = Inches(2.1)
CARD_Y = Inches(2.3)

cover_cards = [
    ("01", "DEEPFAKE DETECTOR",   RGBColor(0x14,0x0C,0x0C), RED,
     "Detects AI-generated and manipulated media\nImages  •  Videos  •  PDFs  •  Screenshots\nGroq  •  Claude  •  Gemini  •  Heuristic fallback"),
    ("02", "AI THREAT HUNTER",    RGBColor(0x07,0x14,0x14), TEAL,
     "Detects unusual network behaviour using ML\nCSV  •  JSON  •  Syslog  •  Live Feed\nIsolation Forest  •  MITRE ATT&CK  •  IR Playbook"),
    ("03", "DNS SPOOFING & PHISHING", RGBColor(0x14,0x0A,0x00), ORANGE,
     "How attackers redirect DNS to fake servers\nAttack chain  •  Decision flow  •  Defences\nDNSSEC  •  Passkeys  •  DoH / DoT  •  MFA"),
]
for i, (num, label, bg_dark, accent, body) in enumerate(cover_cards):
    cx = Inches(0.3) + i * (CARD_W + GAP)
    box(sl, cx, CARD_Y, CARD_W, CARD_H, bg_dark, accent, 1.8)
    box(sl, cx, CARD_Y, CARD_W, Inches(0.38), accent)
    t(sl, f"{num}   {label}", cx + Inches(0.12), CARD_Y + Inches(0.07),
      CARD_W - Inches(0.2), Inches(0.28), size=11, bold=True, color=WHITE)
    t(sl, body, cx + Inches(0.12), CARD_Y + Inches(0.48),
      CARD_W - Inches(0.2), Inches(1.55), size=10.5, color=MGREY)

# School + Team names
box(sl, Inches(0.3), Inches(4.6), W - Inches(0.6), Inches(1.62), LGREY, MGREY, 0.5)
t(sl, "Sitadevi Garodia Hindu Vidyalaya Mat.Hr.Sec.School",
  Inches(0.5), Inches(4.68), W - Inches(1.0), Inches(0.42),
  size=14, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
box(sl, Inches(0.3), Inches(5.1), W - Inches(0.6), Inches(0.04), CYAN)
t(sl, "Varunprasad V  &  Sakthivel Rajan",
  Inches(0.5), Inches(5.18), W - Inches(1.0), Inches(0.36),
  size=12, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
t(sl, "Cyber Security Suite  |  2026 Competition Project",
  Inches(0.5), Inches(5.54), W - Inches(1.0), Inches(0.3),
  size=10, color=MGREY, align=PP_ALIGN.CENTER)

footer(sl, 1)


# ════════════════════════════════════════════════════════════════════
# SLIDE 2 — THE PROBLEM
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, WHITE)
header(sl, "The Problem", "Three real threats that this project addresses", RED)

problems = [
    (RED,    "🎭", "Deepfake Crisis",
     "500,000+ deepfake videos circulate online. AI-generated media is used for\nidentity fraud, disinformation, and financial scams — costing billions each year.",
     "Traditional detectors fail when one API goes down — no fallback."),
    (NAVY,   "🌐", "Network Intrusions",
     "Cyberattacks rose 38% in 2023. Most organisations cannot detect intrusions\nin real time — conventional tools need months of labelled data before alerting.",
     "Zero-day threats go undetected until after damage is done."),
    (ORANGE, "🎣", "DNS Spoofing & Phishing",
     "Attackers redirect DNS to fake servers. Victims land on convincing clones\nand submit credentials — browser shows the real site name throughout.",
     "Even a valid certificate check can be bypassed with a look-alike domain."),
]

BOX_H = Inches(1.55)
for i, (accent, icon, title, body, note) in enumerate(problems):
    py = Inches(1.2) + i * (BOX_H + Inches(0.1))
    box(sl, Inches(0.3), py, W - Inches(0.6), BOX_H, LGREY, accent, 1.5)
    box(sl, Inches(0.3), py, Inches(0.6), BOX_H, accent)
    t(sl, icon, Inches(0.3), py + Inches(0.42), Inches(0.6), Inches(0.6),
      size=22, align=PP_ALIGN.CENTER, color=WHITE)
    t(sl, title, Inches(1.0), py + Inches(0.1), Inches(4.5), Inches(0.4),
      size=13, bold=True, color=accent)
    t(sl, body, Inches(1.0), py + Inches(0.5), Inches(7.5), Inches(0.72),
      size=10.5, color=DARK)
    t(sl, f"  ! {note}", Inches(8.7), py + Inches(0.5), Inches(4.0), Inches(0.72),
      size=9.5, color=accent, italic=True)

footer(sl, 2)


# ════════════════════════════════════════════════════════════════════
# SLIDE 3 — DEEPFAKE DETECTOR
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, WHITE)
header(sl, "Deepfake Detector", "AI vision forensics — 7 analysis dimensions", RED)

# Pipeline
steps = [
    ("📥", "Upload",     "Image/Video\nPDF/Screenshot"),
    ("⚙️", "Preprocess", "OpenCV\nPIL resize"),
    ("🤖", "AI Vision",  "Groq → Claude\n→ Gemini"),
    ("🔬", "7 Dims",     "Forensic\nanalysis"),
    ("📋", "Report",     "Verdict + score\nDownload .txt"),
]
n = len(steps)
ARW = Inches(0.28)
SW2 = W - Inches(0.6)
bw = (SW2 - ARW * (n - 1)) / n
px = Inches(0.3)
for i, (icon, title, sub) in enumerate(steps):
    box(sl, px, Inches(1.2), bw, Inches(0.95), LRED, RED, 1.2)
    multiline(sl, [
        (icon,  13, True,  RED,   PP_ALIGN.CENTER),
        (title, 10, True,  DARK,  PP_ALIGN.CENTER),
        (sub,    8, False, MGREY, PP_ALIGN.CENTER),
    ], px + Inches(0.04), Inches(1.22), bw - Inches(0.08), Inches(0.9))
    px += bw
    if i < n - 1:
        t(sl, "›", px, Inches(1.5), ARW, Inches(0.4),
          size=20, bold=True, color=RED, align=PP_ALIGN.CENTER)
        px += ARW

# 7 Dimensions — 2 columns
dims = [
    ("01", "Facial Forensics",    "Skin texture, eye asymmetry, hair boundaries"),
    ("02", "GAN Artifacts",       "Checkerboard patterns, spectral anomalies"),
    ("03", "Noise & Compression", "JPEG DCT blocks, sensor noise, double-compression"),
    ("04", "Lighting & Shadows",  "Specular highlights, shadow direction"),
    ("05", "Background & Depth",  "Semantic coherence, depth-of-field checks"),
    ("06", "Colour & Chromatic",  "HSV channels, colour temperature, saturation"),
    ("07", "Document / Text",     "Font consistency, QR codes, metadata"),
]
tag(sl, Inches(0.3), Inches(2.28), Inches(3.6), "  7-DIMENSION ANALYSIS", RED)
half = (W - Inches(0.7)) / 2
for i, (num, name, detail) in enumerate(dims):
    col = i % 2; row = i // 2
    cx = Inches(0.3) + col * (half + Inches(0.1))
    cy = Inches(2.6) + row * Inches(0.95)
    bg = LRED if row % 2 == 0 else WHITE
    box(sl, cx, cy, half, Inches(0.9), bg, RGBColor(0xF0, 0xC0, 0xC0), 0.7)
    box(sl, cx, cy, Inches(0.44), Inches(0.9), RED)
    t(sl, num, cx, cy + Inches(0.24), Inches(0.44), Inches(0.44),
      size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    t(sl, name, cx + Inches(0.5), cy + Inches(0.08), half - Inches(0.58), Inches(0.33),
      size=10.5, bold=True, color=RED)
    t(sl, detail, cx + Inches(0.5), cy + Inches(0.44), half - Inches(0.58), Inches(0.4),
      size=9, color=DARK)

# Verdict strip
box(sl, Inches(0.3), Inches(6.47), W - Inches(0.6), Inches(0.47), NAVY)
t(sl, "Verdict:   FAKE  |  AUTHENTIC  |  INCONCLUSIVE   —   with AI confidence score 0–100%  &  manipulation type",
  Inches(0.5), Inches(6.52), W - Inches(1.0), Inches(0.38),
  size=10.5, color=WHITE, bold=False)

footer(sl, 3)


# ════════════════════════════════════════════════════════════════════
# SLIDE 4 — AI THREAT HUNTER
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, WHITE)
header(sl, "AI Threat Hunter", "Isolation Forest anomaly detection — no labelled data needed", TEAL)

# Pipeline
steps2 = [
    ("📥", "Ingest",    "CSV / JSON\nSyslog / Live"),
    ("🧮", "Features",  "10 engineered\nlog1p encoded"),
    ("🌲", "Iso Forest","Anomaly\nscore 0-100"),
    ("🎯", "Classify",  "5 threat\ntypes"),
    ("📊", "Dashboard", "6 tabs\n+ IR export"),
]
bw2 = (W - Inches(0.6) - ARW * (len(steps2)-1)) / len(steps2)
px = Inches(0.3)
for i, (icon, title, sub) in enumerate(steps2):
    box(sl, px, Inches(1.2), bw2, Inches(0.95), LTEAL, TEAL, 1.2)
    multiline(sl, [
        (icon,  13, True,  TEAL,  PP_ALIGN.CENTER),
        (title, 10, True,  DARK,  PP_ALIGN.CENTER),
        (sub,    8, False, MGREY, PP_ALIGN.CENTER),
    ], px + Inches(0.04), Inches(1.22), bw2 - Inches(0.08), Inches(0.9))
    px += bw2
    if i < len(steps2) - 1:
        t(sl, "›", px, Inches(1.5), ARW, Inches(0.4),
          size=20, bold=True, color=TEAL, align=PP_ALIGN.CENTER)
        px += ARW

# Left: Threat types
half2 = (W - Inches(0.7)) / 2
tag(sl, Inches(0.3), Inches(2.28), half2, "  5 THREAT TYPES — MITRE ATT&CK MAPPED", TEAL)

threats = [
    ("🔍 Port Scan",        "TA0043 / T1046",      "1 IP → 50+ ports, high DENY"),
    ("🔑 Brute Force",      "TA0006 / T1110.001",  "High-freq logins, port 22/3389"),
    ("📤 Data Exfiltration","TA0010 / T1048.003",  "Outbound > 1 MB, external IP"),
    ("📡 C2 / Suspicious",  "TA0011 / T1071.001",  "Beaconing to 4444/1337/9001"),
    ("⚠️ Anomalous Traffic","TA0007 / T1040",       "Statistical outlier, no rule match"),
]
for i, (name, mitre, detail) in enumerate(threats):
    ry = Inches(2.6) + i * Inches(0.78)
    bg = LTEAL if i % 2 == 0 else WHITE
    box(sl, Inches(0.3), ry, half2, Inches(0.74), bg, RGBColor(0xA0, 0xD5, 0xD0), 0.7)
    t(sl, name,   Inches(0.42), ry + Inches(0.06), half2 - Inches(0.3), Inches(0.3),
      size=10.5, bold=True, color=TEAL)
    t(sl, mitre,  Inches(0.42), ry + Inches(0.38), Inches(2.4), Inches(0.3),
      size=9, bold=True, color=NAVY)
    t(sl, detail, Inches(2.9),  ry + Inches(0.38), half2 - Inches(2.68), Inches(0.3),
      size=9.5, color=DARK)

# Right: IR Playbook phases
tag(sl, Inches(0.3) + half2 + Inches(0.1), Inches(2.28),
    half2, "  INCIDENT RESPONSE PLAYBOOK", NAVY)
ir = [
    ("0–15 min",  "Immediate",   "Block IP, isolate endpoint, preserve logs"),
    ("15–60 min", "Investigate", "SIEM pull, EDR check, lateral movement hunt"),
    ("1–4 hrs",   "Contain",     "Revoke creds, patch service, clean malware"),
    ("Days",      "Remediate",   "Detection rule, policy update, lessons learned"),
]
for i, (time, phase, action) in enumerate(ir):
    ry = Inches(2.6) + i * Inches(0.78)
    bg = LBLUE if i % 2 == 0 else WHITE
    rx2 = Inches(0.3) + half2 + Inches(0.1)
    box(sl, rx2, ry, half2, Inches(0.74), bg, RGBColor(0xA8, 0xC4, 0xE8), 0.7)
    box(sl, rx2, ry, Inches(0.9), Inches(0.74), NAVY)
    t(sl, time, rx2, ry + Inches(0.22), Inches(0.9), Inches(0.32),
      size=8, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    t(sl, phase,  rx2 + Inches(0.98), ry + Inches(0.06), half2 - Inches(1.1), Inches(0.3),
      size=10.5, bold=True, color=NAVY)
    t(sl, action, rx2 + Inches(0.98), ry + Inches(0.38), half2 - Inches(1.1), Inches(0.3),
      size=9.5, color=DARK)

footer(sl, 4)


# ════════════════════════════════════════════════════════════════════
# SLIDE 5 — DNS SPOOFING & PHISHING
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, WHITE)
header(sl, "DNS Spoofing & Phishing", "How a familiar website can betray you", ORANGE)

# Attack chain — 6 steps
tag(sl, Inches(0.3), Inches(1.18), Inches(5.0), "  ATTACK CHAIN — 6 STAGES", ORANGE)
attack_steps = [
    ("1", "Initial Access",         "Malicious link, bad router or poisoned resolver",   RGBColor(0xD4,0x6A,0x00)),
    ("2", "Name Resolution",        "Hostname goes to wrong IP — DNS answer spoofed",    RGBColor(0xBC,0x3A,0x00)),
    ("3", "Impersonation",          "Convincing replica login page served to victim",    RED),
    ("4", "Credential Submission",  "Victim enters password, 2FA code, or approval",     RGBColor(0x9C,0x27,0x27)),
    ("5", "Collection & Reuse",     "Attacker captures data and attempts account access",NAVY),
    ("6", "Persistence & Impact",   "Recovery info changed, data stolen, creds reused",  RGBColor(0x0D,0x2B,0x55)),
]
SW3 = Inches(5.6)
sh = Inches(0.72)
for i, (num, title, detail, col) in enumerate(attack_steps):
    col2 = i % 2; row = i // 2
    ax = Inches(0.3) + col2 * (SW3 / 2 + Inches(0.08))
    ay = Inches(1.52) + row * (sh + Inches(0.08))
    bg = LORANGE if i % 2 == 0 else WHITE
    box(sl, ax, ay, SW3 / 2, sh, bg, col, 1.2)
    box(sl, ax, ay, Inches(0.42), sh, col)
    t(sl, num, ax, ay + Inches(0.17), Inches(0.42), Inches(0.4),
      size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    t(sl, title, ax + Inches(0.5), ay + Inches(0.06), SW3/2 - Inches(0.6), Inches(0.3),
      size=10, bold=True, color=col)
    t(sl, detail, ax + Inches(0.5), ay + Inches(0.36), SW3/2 - Inches(0.6), Inches(0.3),
      size=9, color=DARK)

# How DNS gets spoofed — 5 ways
DX = Inches(6.1)
DW = W - Inches(6.4)
tag(sl, DX, Inches(1.18), DW, "  5 WAYS DNS GETS SPOOFED", RED)
spoof_ways = [
    "Compromised router or DNS settings",
    "Rogue or compromised resolver",
    "On-path interference with DNS traffic",
    "Cache poisoning of a resolver",
    "DNS hosting account compromise",
]
for i, way in enumerate(spoof_ways):
    ry = Inches(1.52) + i * Inches(0.6)
    bg = LRED if i % 2 == 0 else WHITE
    box(sl, DX, ry, DW, Inches(0.56), bg, RGBColor(0xF0,0xBB,0xBB), 0.6)
    oval(sl, DX + Inches(0.1), ry + Inches(0.17), Inches(0.22), Inches(0.22), RED)
    t(sl, way, DX + Inches(0.42), ry + Inches(0.1), DW - Inches(0.52), Inches(0.38),
      size=10.5, color=DARK)

# Key point callout
box(sl, Inches(0.3), Inches(4.78), W - Inches(0.6), Inches(0.46), LRED, RED, 1.2)
t(sl, "Key point:  The browser connects by IP address, not name — whoever controls the DNS answer controls the destination.",
  Inches(0.5), Inches(4.84), W - Inches(1.0), Inches(0.36),
  size=10.5, color=RED, bold=False, italic=True)

# Defence pipeline
tag(sl, Inches(0.3), Inches(5.38), Inches(3.5), "  DEFENCE PIPELINE", GREEN)
defences = [
    ("🛡️ Protect DNS",   "Reputable resolvers · DNSSEC · DoH / DoT"),
    ("🔒 Secure Infra",  "Strong creds · MFA · patches · change alerts"),
    ("🗝️ Strong Auth",   "Passkeys · no password reuse · password manager"),
    ("📡 Monitor",       "DNS changes · cert warnings · odd login alerts"),
]
dw = (W - Inches(0.6)) / len(defences)
for i, (title, body) in enumerate(defences):
    dx2 = Inches(0.3) + i * dw
    box(sl, dx2, Inches(5.68), dw - Inches(0.06), Inches(0.76),
        LGRN, GREEN, 0.8)
    multiline(sl, [
        (title, 10, True,  GREEN, PP_ALIGN.CENTER),
        (body,   8, False, DARK,  PP_ALIGN.CENTER),
    ], dx2 + Inches(0.06), Inches(5.72), dw - Inches(0.16), Inches(0.68))

footer(sl, 5)


# ════════════════════════════════════════════════════════════════════
# SLIDE 6 — DEMO & KEY TAKEAWAYS  (PPT1 demo + PPT2 DNS insights)
# ════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
box(sl, 0, 0, W, H, WHITE)
header(sl, "Demo & Key Takeaways", "Live demonstration steps  +  DNS Spoofing & Phishing insights", NAVY)

MGREY2 = RGBColor(0xCC, 0xD5, 0xE0)
half3 = (W - Inches(0.7)) / 2

# ── LEFT: Demo steps ──────────────────────────────────────────────
tag(sl, Inches(0.3), Inches(1.18), half3, "  QUICK DEMO STEPS", NAVY)

demo = [
    (RED,   "Deepfake Detector",  "Home → Deepfake Detector → Analyze Demo"),
    (RED,   "Show verdict",        "FAKE / confidence % — manipulation type listed"),
    (RED,   "Expand report",       "7-dimension breakdown + download .txt"),
    (TEAL,  "AI Threat Hunter",   "Home → AI Threat Hunter → Use Sample Data"),
    (TEAL,  "Overview tab",        "Red dots = attacks · heatmap shows 2-4 AM cluster"),
    (TEAL,  "IR Playbook tab",     "Select threat → AI report → download .txt"),
    (NAVY,  "Live Feed",           "Run live_log_generator.py → new attack every 20-45s"),
]
for i, (col, title, body) in enumerate(demo):
    ry = Inches(1.52) + i * Inches(0.68)
    bg = LGREY if i % 2 == 0 else WHITE
    box(sl, Inches(0.3), ry, half3, Inches(0.64), bg, MGREY2, 0.5)
    oval(sl, Inches(0.37), ry + Inches(0.18), Inches(0.28), Inches(0.28), col)
    t(sl, str(i + 1), Inches(0.37), ry + Inches(0.18), Inches(0.28), Inches(0.28),
      size=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    multiline(sl, [
        (title, 10,   True,  col,  PP_ALIGN.LEFT),
        (body,  9.5, False, DARK, PP_ALIGN.LEFT),
    ], Inches(0.74), ry + Inches(0.06), half3 - Inches(0.52), Inches(0.56))

# ── RIGHT: PPT2 — DNS Spoofing & Phishing takeaways ───────────────
RX3 = Inches(0.4) + half3
RW3 = half3 - Inches(0.1)

tag(sl, RX3, Inches(1.18), RW3, "  DNS SPOOFING & PHISHING — KEY INSIGHTS", ORANGE)

# Key takeaway callout box
box(sl, RX3, Inches(1.52), RW3, Inches(0.78), LORANGE, ORANGE, 1.5)
box(sl, RX3, Inches(1.52), Inches(0.07), Inches(0.78), ORANGE)
t(sl, "DNS spoofing steers the name to the wrong place.\nPhishing exploits trust in what appears.\nProtect DNS and use authentication an impostor cannot fool.",
  RX3 + Inches(0.18), Inches(1.57), RW3 - Inches(0.26), Inches(0.68),
  size=10, color=DARK, italic=True)

# Decision flow: where attack succeeds or fails
tag(sl, RX3, Inches(2.42), RW3, "  WHERE ATTACK SUCCEEDS OR FAILS", RED)
flow = [
    (RED,    "Victim opens impostor page",        "Browser shows real hostname — no visible sign"),
    (RED,    "No valid certificate?",             "Connection blocked — attack fails here"),
    (ORANGE, "No passkey / origin-checking mgr?", "Credentials stolen — attack succeeds"),
    (GREEN,  "Passkey or manager present?",        "Autofill refused — attack is blocked"),
]
for i, (col, label, detail) in enumerate(flow):
    ry = Inches(2.74) + i * Inches(0.65)
    bg = LRED if i % 2 == 0 else WHITE
    box(sl, RX3, ry, RW3, Inches(0.61), bg, RGBColor(0xF0, 0xC0, 0xBB), 0.6)
    box(sl, RX3, ry, Inches(0.07), Inches(0.61), col)
    t(sl, label,  RX3 + Inches(0.18), ry + Inches(0.04), RW3 - Inches(0.26), Inches(0.28),
      size=9.5, bold=True, color=col)
    t(sl, detail, RX3 + Inches(0.18), ry + Inches(0.32), RW3 - Inches(0.26), Inches(0.26),
      size=9, color=DARK)

# Defence pipeline — 5 steps from PPT2
tag(sl, RX3, Inches(5.4), RW3, "  DEFENCE PIPELINE", GREEN)
defences = [
    ("🛡️", "Protect DNS",   "DNSSEC · DoH / DoT · reputable resolvers"),
    ("🔒", "Secure Infra",  "MFA · strong creds · patch · change alerts"),
    ("🗝️", "Strong Auth",   "Passkeys · password manager · no reuse"),
    ("📡", "Monitor",       "DNS changes · cert warnings · odd logins"),
    ("🔄", "Respond",       "Change passwords · revoke sessions · notify"),
]
dw = RW3 / len(defences)
for i, (icon, title, body) in enumerate(defences):
    dx2 = RX3 + i * dw
    box(sl, dx2, Inches(5.72), dw - Inches(0.04), Inches(0.9),
        LGRN if i % 2 == 0 else WHITE, GREEN, 0.7)
    multiline(sl, [
        (icon,   13, True,  GREEN, PP_ALIGN.CENTER),
        (title,   8, True,  GREEN, PP_ALIGN.CENTER),
        (body,    7, False, DARK,  PP_ALIGN.CENTER),
    ], dx2 + Inches(0.03), Inches(5.74), dw - Inches(0.1), Inches(0.86))

# Thank you banner
box(sl, Inches(0.3), Inches(6.74), W - Inches(0.6), Inches(0.46), NAVY)
t(sl, "Thank You",
  Inches(0.3), Inches(6.78), W * 0.35, Inches(0.38),
  size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
t(sl, "Varunprasad V  &  Sakthivel Rajan  |  2026 Cyber Security Competition",
  W * 0.35, Inches(6.81), W * 0.6, Inches(0.34),
  size=10, color=MGREY, align=PP_ALIGN.RIGHT)

footer(sl, 6, total=6)


# ── Save ─────────────────────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f"PPT generated: {OUTPUT}")
