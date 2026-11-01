"""
Cyber Security Suite — PDF Generator (Light Theme, Print-Ready, Max 5 pages)
Run:  python generate_pdf.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
import datetime, os

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "Cyber_Security_Suite_Project.pdf")
W, H = A4
BODY_W = W - 30 * mm   # usable width

# ── Colour palette ─────────────────────────────────────────────────────────────
WHITE      = colors.white
NAVY       = colors.HexColor("#0f3460")
BLUE       = colors.HexColor("#1565c0")
TEAL       = colors.HexColor("#00695c")
DARK_RED   = colors.HexColor("#b71c1c")
DARK_GREEN = colors.HexColor("#2e7d32")
LIGHT_BLUE = colors.HexColor("#e3f2fd")
LIGHT_TEAL = colors.HexColor("#e0f7fa")
LIGHT_RED  = colors.HexColor("#ffebee")
LIGHT_GREY = colors.HexColor("#f5f5f5")
MID_GREY   = colors.HexColor("#bdbdbd")
DIM        = colors.HexColor("#546e7a")
BLACK      = colors.HexColor("#212121")
ORANGE     = colors.HexColor("#e65100")


# ── Paragraph styles ────────────────────────────────────────────────────────────
def S(name, **kw):
    base = dict(fontName="Helvetica", fontSize=8.5, textColor=BLACK,
                leading=13, spaceAfter=3, spaceBefore=0,
                leftIndent=0, rightIndent=0, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)

COVER_MAIN   = S("CM", fontName="Helvetica-Bold", fontSize=30, textColor=WHITE,
                  leading=36, alignment=TA_CENTER, spaceAfter=4)
COVER_SUB    = S("CS", fontName="Helvetica-Bold", fontSize=14, textColor=LIGHT_BLUE,
                  leading=18, alignment=TA_CENTER, spaceAfter=6)
COVER_BODY   = S("CB", fontSize=9, textColor=LIGHT_BLUE, leading=14,
                  alignment=TA_CENTER, spaceAfter=4)
SEC_HDR      = S("SH", fontName="Helvetica-Bold", fontSize=13, textColor=WHITE,
                  leading=18, spaceAfter=0, alignment=TA_LEFT)
H2           = S("H2", fontName="Helvetica-Bold", fontSize=10.5, textColor=NAVY,
                  leading=14, spaceAfter=3, spaceBefore=5)
H3           = S("H3", fontName="Helvetica-Bold", fontSize=9, textColor=TEAL,
                  leading=13, spaceAfter=2, spaceBefore=4)
BODY         = S("BD", fontSize=8.5, textColor=BLACK, leading=13,
                  spaceAfter=4, alignment=TA_JUSTIFY)
TH           = S("TH", fontName="Helvetica-Bold", fontSize=7.5, textColor=WHITE, leading=11)
TD           = S("TD", fontSize=8, textColor=BLACK, leading=12)
TK           = S("TK", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, leading=12)
MONO         = S("MO", fontName="Courier", fontSize=8, textColor=DARK_GREEN,
                  leading=12, spaceAfter=3)
CAPTION      = S("CA", fontSize=7, textColor=DIM, leading=10,
                  alignment=TA_CENTER, spaceAfter=6)


# ── Helpers ────────────────────────────────────────────────────────────────────
def sp(n=3):
    return Spacer(1, n * mm)

def hr(col=MID_GREY, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness,
                      color=col, spaceAfter=3, spaceBefore=3)

def p(text, style=None):
    return Paragraph(text, style or BODY)

def h2(t):
    return Paragraph(t, H2)

def sec_bar(title, bg=NAVY):
    """Section header as a full-width coloured table row."""
    row = [[Paragraph(title, SEC_HDR)]]
    t = Table(row, colWidths=[BODY_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), bg),
        ("TOPPADDING",    (0,0),(0,0), 7),
        ("BOTTOMPADDING", (0,0),(0,0), 7),
        ("LEFTPADDING",   (0,0),(0,0), 10),
        ("RIGHTPADDING",  (0,0),(0,0), 10),
    ]))
    return t

def kv_table(rows, lw=48*mm):
    """Two-column key/value table."""
    rw = BODY_W - lw
    data = [[Paragraph(k, TK), Paragraph(v, TD)] for k, v in rows]
    t = Table(data, colWidths=[lw, rw])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [LIGHT_GREY, WHITE]),
        ("GRID",          (0,0),(-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t

def data_table(headers, rows, col_widths, hdr_bg=NAVY):
    """Multi-column table with coloured header."""
    hdr = [Paragraph(h, TH) for h in headers]
    body_rows = [[Paragraph(str(c), TD) for c in row] for row in rows]
    t = Table([hdr] + body_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1, 0), hdr_bg),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT_GREY, WHITE]),
        ("GRID",          (0,0),(-1,-1), 0.4, MID_GREY),
        ("LINEBELOW",     (0,0),(-1, 0), 1.0, hdr_bg),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 5),
        ("RIGHTPADDING",  (0,0),(-1,-1), 5),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t

def _hex(color_obj):
    """Return plain 6-digit hex string for a ReportLab color, e.g. 'b71c1c'."""
    r = int(color_obj.red * 255)
    g = int(color_obj.green * 255)
    b = int(color_obj.blue * 255)
    return f"{r:02x}{g:02x}{b:02x}"

def pipeline_row(steps, accent):
    """Horizontal pipeline as a simple table. No custom drawing."""
    n = len(steps)
    acc_hex = _hex(accent)
    # Build interleaved: [step, arrow, step, arrow, ...]
    cells = []
    for i, (icon, label, sub) in enumerate(steps):
        cell = Paragraph(
            f'<b><font color="#{acc_hex}">{icon}</font></b><br/>'
            f'<b>{label}</b><br/>'
            f'<font color="#546e7a" size="6">{sub}</font>',
            S("pip", fontSize=7.5, leading=11, alignment=TA_CENTER)
        )
        cells.append(cell)
        if i < n - 1:
            arrow = Paragraph(
                f'<font color="#{acc_hex}" size="14"><b>›</b></font>',
                S("ar", fontSize=14, leading=14, alignment=TA_CENTER)
            )
            cells.append(arrow)

    # Column widths: steps get equal share, arrows get a small fixed width
    arrow_w = 8 * mm
    step_w = (BODY_W - arrow_w * (n - 1)) / n
    widths = []
    for i in range(2 * n - 1):
        widths.append(step_w if i % 2 == 0 else arrow_w)

    t = Table([cells], colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LIGHT_GREY),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("BOX",           (0,0),(-1,-1), 0.5, MID_GREY),
    ]))
    return t


# ── Page callbacks ──────────────────────────────────────────────────────────────
def page_header_footer(canv, doc):
    canv.saveState()
    # Header bar
    canv.setFillColor(NAVY)
    canv.rect(0, H - 11 * mm, W, 11 * mm, fill=1, stroke=0)
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 7.5)
    canv.drawString(15 * mm, H - 7 * mm,
                    "CYBER SECURITY SUITE  |  AI-POWERED FORENSICS & THREAT INTELLIGENCE")
    canv.setFont("Helvetica", 7)
    canv.drawRightString(W - 15 * mm, H - 7 * mm, f"Page {doc.page}")
    # Footer bar
    canv.setFillColor(LIGHT_GREY)
    canv.rect(0, 0, W, 8 * mm, fill=1, stroke=0)
    canv.setStrokeColor(MID_GREY)
    canv.setLineWidth(0.5)
    canv.line(0, 8 * mm, W, 8 * mm)
    canv.setFillColor(DIM)
    canv.setFont("Helvetica", 6.5)
    canv.drawCentredString(W / 2, 3 * mm,
        "Deepfake Detector  |  AI Threat Hunter  |  MITRE ATT&CK Framework  |  2026")
    canv.restoreState()


# ════════════════════════════════════════════════════════════════════
# COVER PAGE  — built entirely with Table flowables, no canvas drawing
# ════════════════════════════════════════════════════════════════════

def make_cover():
    """Returns a list of flowables that form the cover page."""
    items = []

    # ── Top navy banner (title only) ──────────────────────────────────────────
    banner_data = [
        [Paragraph("CYBER SECURITY",
                   S("ct", fontSize=32, fontName="Helvetica-Bold", textColor=WHITE,
                     leading=38, alignment=TA_CENTER))],
        [Paragraph("AI SUITE",
                   S("ct2", fontSize=20, fontName="Helvetica-Bold",
                     textColor=colors.HexColor("#90caf9"),
                     leading=26, alignment=TA_CENTER))],
        [Paragraph("AI-Powered Threat Detection  &amp;  Media Forensics Platform",
                   S("cs", fontSize=11, fontName="Helvetica-Bold", textColor=LIGHT_BLUE,
                     leading=16, alignment=TA_CENTER))],
        [Paragraph("Deepfake Detector  ·  AI Threat Hunter  ·  MITRE ATT&amp;CK Integration",
                   S("cd", fontSize=9, textColor=colors.HexColor("#90caf9"),
                     leading=13, alignment=TA_CENTER))],
    ]
    banner_t = Table(banner_data, colWidths=[BODY_W])
    banner_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(0,0), 20),
        ("BOTTOMPADDING", (0,0),(0,0), 4),
        ("TOPPADDING",    (0,1),(0,1), 0),
        ("BOTTOMPADDING", (0,1),(0,1), 8),
        ("TOPPADDING",    (0,2),(0,2), 6),
        ("BOTTOMPADDING", (0,2),(0,2), 4),
        ("TOPPADDING",    (0,3),(0,3), 0),
        ("BOTTOMPADDING", (0,3),(0,3), 20),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("LINEBELOW",     (0,3),(0,3), 2, colors.HexColor("#00bcd4")),
    ]))
    items.append(banner_t)
    items.append(sp(5))

    # ── Two tool cards ────────────────────────────────────────────────────────
    half = BODY_W / 2
    card_data = [
        [
            Paragraph("<b>01  DEEPFAKE DETECTOR</b>",
                      S("ct1", fontSize=10, fontName="Helvetica-Bold",
                        textColor=DARK_RED, leading=14)),
            Paragraph("<b>02  AI THREAT HUNTER</b>",
                      S("ct2", fontSize=10, fontName="Helvetica-Bold",
                        textColor=BLUE, leading=14)),
        ],
        [
            Paragraph(
                "AI Vision Forensics · Media Authenticity<br/>"
                "OpenCV · PyMuPDF · Groq · Claude · Gemini",
                S("cd1", fontSize=8, textColor=DIM, leading=13)),
            Paragraph(
                "Isolation Forest · MITRE ATT&amp;CK · IR Playbook<br/>"
                "Scikit-learn · Plotly · Anthropic API · Streamlit",
                S("cd2", fontSize=8, textColor=DIM, leading=13)),
        ],
        [
            Paragraph(
                "<b>Input:</b> Images · Videos · PDFs · Screenshots<br/>"
                "<b>Output:</b> AI Forensic Report (.txt download)",
                S("cb1", fontSize=8, textColor=BLACK, leading=13)),
            Paragraph(
                "<b>Input:</b> CSV · JSON · Syslog · Live Feed<br/>"
                "<b>Output:</b> Threat Dashboard · IR Playbook (.txt)",
                S("cb2", fontSize=8, textColor=BLACK, leading=13)),
        ],
    ]
    cards_t = Table(card_data, colWidths=[half, half])
    cards_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1), LIGHT_RED),
        ("BACKGROUND",    (1,0),(1,-1), LIGHT_BLUE),
        ("BOX",           (0,0),(0,-1), 1.5, DARK_RED),
        ("BOX",           (1,0),(1,-1), 1.5, BLUE),
        ("LINEAFTER",     (0,0),(0,-1), 0.5, MID_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    items.append(cards_t)
    items.append(sp(6))

    # ── Why This Project Matters ──────────────────────────────────────────────
    imp_title = Table(
        [[Paragraph("WHY THIS PROJECT MATTERS",
                    S("it", fontName="Helvetica-Bold", fontSize=10, textColor=WHITE,
                      leading=14, alignment=TA_LEFT))]],
        colWidths=[BODY_W]
    )
    imp_title.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,0), NAVY),
        ("TOPPADDING",    (0,0),(0,0), 6),
        ("BOTTOMPADDING", (0,0),(0,0), 6),
        ("LEFTPADDING",   (0,0),(0,0), 10),
        ("RIGHTPADDING",  (0,0),(0,0), 10),
        ("LINEBELOW",     (0,0),(0,0), 2, ORANGE),
    ]))
    items.append(imp_title)

    importance_rows = [
        [
            Paragraph("<b>Deepfake Crisis</b>",
                      S("ik", fontName="Helvetica-Bold", fontSize=8.5, textColor=DARK_RED, leading=12)),
            Paragraph(
                "Over <b>500,000 deepfake videos</b> circulate online. AI-generated media is used "
                "for fraud, disinformation and identity theft — costing billions annually. "
                "Traditional detection tools rely on single-vendor APIs with no fallback, "
                "failing when one service goes down.",
                S("iv", fontSize=8.5, textColor=BLACK, leading=13)),
        ],
        [
            Paragraph("<b>Cyber Threat Surge</b>",
                      S("ik2", fontName="Helvetica-Bold", fontSize=8.5, textColor=BLUE, leading=12)),
            Paragraph(
                "Cyberattacks increased by <b>38% in 2023</b>. Most organisations lack the tools "
                "to detect intrusions in real time. Conventional SIEM systems require months of "
                "labelled data before they can detect threats — leaving networks exposed on day one.",
                S("iv2", fontSize=8.5, textColor=BLACK, leading=13)),
        ],
        [
            Paragraph("<b>Our Solution</b>",
                      S("ik3", fontName="Helvetica-Bold", fontSize=8.5, textColor=DARK_GREEN, leading=12)),
            Paragraph(
                "This suite directly addresses both challenges with <b>zero vendor dependency</b>, "
                "<b>no labelled training data</b>, and <b>real-time AI analysis</b>. "
                "MITRE ATT&amp;CK mapping and automated IR playbooks mean any analyst — regardless "
                "of experience — can respond effectively within minutes of an alert.",
                S("iv3", fontSize=8.5, textColor=BLACK, leading=13)),
        ],
        [
            Paragraph("<b>Real-World Impact</b>",
                      S("ik4", fontName="Helvetica-Bold", fontSize=8.5, textColor=TEAL, leading=12)),
            Paragraph(
                "Built for immediate deployment: works on any network log format, any media type, "
                "with graceful degradation when APIs are unavailable. From raw data to a "
                "downloadable forensic report or IR playbook in <b>under 10 seconds</b>.",
                S("iv4", fontSize=8.5, textColor=BLACK, leading=13)),
        ],
    ]
    imp_t = Table(importance_rows, colWidths=[38*mm, BODY_W - 38*mm])
    imp_t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [LIGHT_GREY, WHITE]),
        ("GRID",           (0,0),(-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",     (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 6),
        ("LEFTPADDING",    (0,0),(-1,-1), 8),
        ("RIGHTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",         (0,0),(-1,-1), "TOP"),
    ]))
    items.append(imp_t)
    items.append(sp(6))

    # ── Technology chips ──────────────────────────────────────────────────────
    chips = ["Streamlit", "Python 3.10+", "OpenCV", "Isolation Forest",
             "MITRE ATT&CK", "Plotly", "PyMuPDF", "Scikit-Learn",
             "Groq API", "Claude API", "Gemini API", "Pandas / NumPy"]
    chip_rows = [chips[:6], chips[6:]]
    chip_data = []
    for row in chip_rows:
        chip_data.append([
            Paragraph(f"<b>{c}</b>",
                      S(f"ch{i}", fontSize=7.5, alignment=TA_CENTER,
                        leading=10, textColor=BLUE))
            for i, c in enumerate(row)
        ])
    chip_t = Table(chip_data, colWidths=[BODY_W / 6] * 6)
    chip_t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#e8eaf6")),
        ("GRID",          (0,0),(-1,-1), 0.4, MID_GREY),
        ("BOX",           (0,0),(-1,-1), 0.5, MID_GREY),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
    ]))
    items.append(chip_t)

    return items


# ════════════════════════════════════════════════════════════════════
# BUILD STORY
# ════════════════════════════════════════════════════════════════════
story = []

# ── PAGE 1: COVER ────────────────────────────────────────────────────────────
story += make_cover()
story.append(PageBreak())

# ── PAGE 2: OVERVIEW + DEEPFAKE DETECTOR ─────────────────────────────────────
story += [
    sec_bar("PROJECT OVERVIEW", NAVY),
    sp(3),
    p("The <b>Cyber Security Suite</b> is an integrated AI-powered platform combining two tools under "
      "a single Streamlit application. Built for the 2026 Cyber Security Competition, it addresses two "
      "critical modern security challenges: <b>detecting AI-manipulated media</b> and "
      "<b>identifying network intrusions in real time</b>."),
    sp(3),
]

# Two-col overview
ov = Table([
    [Paragraph("<b>DEEPFAKE DETECTOR</b>",
               S("a", fontName="Helvetica-Bold", fontSize=10, textColor=DARK_RED, leading=14)),
     Paragraph("<b>AI THREAT HUNTER</b>",
               S("b", fontName="Helvetica-Bold", fontSize=10, textColor=BLUE, leading=14))],
    [Paragraph("Analyses images, videos and PDFs using multi-provider AI vision APIs "
               "to detect GAN-generated faces, splicing, inpainting and document fakery "
               "across 7 forensic dimensions.", TD),
     Paragraph("Ingests network logs and applies Isolation Forest unsupervised ML to detect "
               "port scans, brute force, data exfiltration and C2 beaconing — mapped to MITRE ATT&CK.", TD)],
    [Paragraph("<b>Input:</b> Images · Videos · PDFs · Screenshots", TD),
     Paragraph("<b>Input:</b> CSV · JSON · Syslog · Live Feed", TD)],
    [Paragraph("<b>Output:</b> AI Forensic Report (.txt)", TD),
     Paragraph("<b>Output:</b> Threat Dashboard + IR Playbook (.txt)", TD)],
], colWidths=[BODY_W / 2, BODY_W / 2])
ov.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(0,-1), LIGHT_RED),
    ("BACKGROUND",    (1,0),(1,-1), LIGHT_BLUE),
    ("BACKGROUND",    (0,0),(0, 0), colors.HexColor("#ffcdd2")),
    ("BACKGROUND",    (1,0),(1, 0), colors.HexColor("#bbdefb")),
    ("GRID",          (0,0),(-1,-1), 0.4, MID_GREY),
    ("TOPPADDING",    (0,0),(-1,-1), 5),
    ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ("RIGHTPADDING",  (0,0),(-1,-1), 8),
    ("VALIGN",        (0,0),(-1,-1), "TOP"),
]))
story += [ov, sp(2)]

story += [
    Paragraph("Architecture", H2),
    kv_table([
        ("Entry Point",   "Home.py — Streamlit landing with tool selector cards"),
        ("Core Isolation","sys.modules['core*'] flushed between pages — prevents package collision"),
        ("AI Key Pool",   "Groq (Llama Vision) → Claude (claude-3.5-sonnet) → Gemini (gemini-1.5-pro)"),
        ("Launch",        "python -m streamlit run Home.py"),
    ]),
    sp(3),
    sec_bar("01  |  DEEPFAKE DETECTOR", DARK_RED),
    sp(2),
    p("Analyses <b>images, videos, PDFs and screenshots</b> for signs of manipulation using "
      "multi-provider AI vision APIs across 7 forensic dimensions. Heuristic fallback runs "
      "when no AI key is available."),
    sp(2),
    Paragraph("Analysis Pipeline", H2),
    pipeline_row([
        ("Upload", "Image/Video/PDF", "Sidebar uploader"),
        ("Preprocess", "OpenCV · PIL", "Resize, normalise"),
        ("AI Vision", "3 providers", "Key rotation"),
        ("7 Dimensions", "Forensic analysis", "Structured JSON"),
        ("Report", "Verdict + Score", "Download .txt"),
    ], DARK_RED),
    sp(2),
    Paragraph("7-Dimension Analysis", H2),
    data_table(
        ["#", "Dimension", "What Is Analysed"],
        [
            ["1", "Facial Forensics",    "Skin texture, eye asymmetry, hair boundary artefacts, geometry"],
            ["2", "GAN Artifacts",       "Checkerboard patterns, spectral anomalies, upsampling traces"],
            ["3", "Noise & Compression", "JPEG DCT blocks, sensor noise distribution, double-compression"],
            ["4", "Lighting & Shadows",  "Specular highlight consistency, shadow direction, reflections"],
            ["5", "Background & Depth",  "Semantic coherence, depth-of-field naturalism, boundaries"],
            ["6", "Colour & Chromatic",  "HSV channel distribution, colour temperature, saturation"],
            ["7", "Document / Text",     "Font consistency, QR code validity, metadata timestamps"],
        ],
        [8*mm, 42*mm, BODY_W - 50*mm], DARK_RED
    ),
    sp(2),
    Paragraph("Key Features", H2),
    kv_table([
        ("AI Key Rotation", "Groq → Claude → Gemini — exhausted keys skipped automatically"),
        ("Fallback",        "Heuristic analysis (FFT + ELA + noise) runs when all AI keys unavailable"),
        ("QR Detection",    "OpenCV QRCodeDetector scans every image; URLs classified for risk"),
        ("PDF + Report",    "PyMuPDF scans up to 5 pages; findings exported as downloadable .txt"),
    ]),
    PageBreak(),
]

# ── PAGE 3: AI THREAT HUNTER ─────────────────────────────────────────────────
story += [
    sec_bar("02  |  AI THREAT HUNTER", TEAL),
    sp(3),
    p("Applies <b>Isolation Forest unsupervised ML</b> to network logs — no labelled training data required. "
      "Every detected threat is mapped to <b>MITRE ATT&CK</b> with a full AI forensic report "
      "and downloadable incident response playbook."),
    sp(3),
    Paragraph("Detection Pipeline", H2),
    pipeline_row([
        ("Ingest", "CSV/JSON/Live", "Upload or stream"),
        ("Features", "10 engineered", "Log1p + encoding"),
        ("Iso Forest", "Anomaly score", "0–100 risk"),
        ("Classify", "5 threat types", "Pattern rules"),
        ("AI Report", "MITRE + IR", "Forensic JSON"),
        ("Dashboard", "6 tabs", "Export .txt"),
    ], TEAL),
    sp(3),
    Paragraph("Feature Engineering — 10 Features", H2),
    data_table(
        ["Feature", "Encoding", "Threat Signal"],
        [
            ["bytes_sent",       "log1p(bytes_sent)",     "Large values signal data exfiltration"],
            ["bytes_recv",       "log1p(bytes_recv)",      "Response volume anomalies"],
            ["send/recv ratio",  "log1p(sent/recv+1)",     "Asymmetric traffic = exfil or scan"],
            ["dest_port",        "Raw port number",        "Unusual ports signal C2 activity"],
            ["source_port",      "Raw source port",        "Ephemeral vs. fixed port patterns"],
            ["protocol",         "Label-encoded TCP/UDP",  "Protocol switches indicate evasion"],
            ["action",           "Label-encoded DENY/ALLOW","High deny rate = brute force"],
            ["conn_rate",        "Connections per src IP", "Frequency anomaly = port scan"],
            ["unique_ports",     "Distinct dest ports/IP", "Many ports = network scan T1046"],
            ["duration",         "log1p(duration) optional","Long sessions = C2 persistence"],
        ],
        [35*mm, 45*mm, BODY_W - 80*mm], TEAL
    ),
    sp(3),
    Paragraph("MITRE ATT&CK Mapping — 5 Threat Types", H2),
    data_table(
        ["Threat Type", "Detection Pattern", "Tactic ID", "Technique"],
        [
            ["Port Scan",         "One IP → 50+ ports, tiny bytes, DENY",       "TA0043 / T1046",     "Network Service Discovery"],
            ["Brute Force",       "High-freq logins to port 22/3389, DENY",      "TA0006 / T1110.001", "Password Guessing"],
            ["Data Exfiltration", "Outbound > 1 MB per event, external IP",      "TA0010 / T1048.003", "Exfil via Unencrypted Protocol"],
            ["C2 / Suspicious",   "Beaconing to ports 4444 / 1337 / 9001",       "TA0011 / T1071.001", "Application Layer Protocol"],
            ["Anomalous Traffic", "Statistical outlier, unclassified",            "TA0007 / T1040",     "Network Sniffing"],
        ],
        [32*mm, 55*mm, 34*mm, BODY_W - 121*mm], TEAL
    ),
    sp(3),
    Paragraph("Dashboard Tabs", H2),
    data_table(
        ["Tab", "Content"],
        [
            ["Overview",          "Threat timeline scatter, distribution pie, top attacker IPs, heatmap, MITRE bar"],
            ["Threat Log",        "Sortable table of all detected threats, risk-coloured, CSV export"],
            ["AI Analysis",       "Select any threat → full AI forensic report + MITRE + risk gauge"],
            ["Incident Response", "AI-generated IR playbook → download as .txt for SOC handoff"],
            ["Network Graph",     "Force-directed graph: red nodes = attackers, red edges = attack paths"],
            ["Live Feed",         "@st.fragment 5s refresh from live_feed.csv — full page never reloads"],
        ],
        [35*mm, BODY_W - 35*mm], TEAL
    ),
    PageBreak(),
]

# ── PAGE 4: AI ANALYSIS, IR PLAYBOOK & LIVE FEED ────────────────────────────
story += [
    sec_bar("AI FORENSIC ANALYSIS  &  INCIDENT RESPONSE", NAVY),
    sp(3),
    p("When a threat is selected, the AI generates a 12-section forensic report using Claude AI "
      "(with key rotation and rule-based fallback). The IR playbook is ready to hand to any SOC analyst."),
    sp(3),
    Paragraph("AI Threat Report — 12 Sections", H2),
    data_table(
        ["Section", "Content"],
        [
            ["Severity & Confidence",    "CRITICAL / HIGH / MEDIUM / LOW  +  AI confidence 0–100%"],
            ["Threat Title",             "Human-readable name, e.g. 'Coordinated Port Scan — 185.220.x.x'"],
            ["MITRE ATT&CK",             "Tactic ID + Name  →  Technique ID + Name  →  Sub-technique"],
            ["Kill Chain Phase",         "Reconnaissance / Weaponisation / Delivery / Exploitation / C2 / Exfiltration"],
            ["Executive Summary",        "2–3 sentence plain-language description of the incident"],
            ["Evidence Analysis",        "Specific packet-level evidence supporting the classification"],
            ["Impact Assessment",        "Business risk: data loss, system compromise, service disruption"],
            ["Threat Actor Profile",     "Type · Sophistication (Low / Medium / High / Nation-State) · Motivation"],
            ["Indicators of Compromise", "IPs, ports, byte patterns, timing signatures as IOCs"],
            ["False Positive Assessment","Likelihood this is benign traffic with explanation"],
            ["Related Threat Types",     "Other attacks commonly paired with this technique"],
            ["Analyst Notes",            "Caveats, confidence limitations, edge cases"],
        ],
        [50*mm, BODY_W - 50*mm], NAVY
    ),
    sp(3),
    Paragraph("Incident Response Playbook", H2),
    data_table(
        ["Phase", "Timeframe", "Actions"],
        [
            ["Immediate Actions",         "0 – 15 min",  "Block IP at firewall, isolate endpoint, preserve logs"],
            ["Investigation Steps",       "15 – 60 min", "SIEM log pull, EDR check, lateral movement hunt"],
            ["Containment & Eradication", "1 – 4 hrs",   "Revoke credentials, patch exploited service, clean malware"],
            ["Long-term Remediation",     "Days",         "Deploy detection rule, update policy, lessons learned"],
        ],
        [50*mm, 22*mm, BODY_W - 72*mm], NAVY
    ),
    sp(3),
    Paragraph("Live Feed — Real-Time Demonstration", H2),
    kv_table([
        ("Generator",       "live_log_generator.py writes to live_feed.csv at 0.5–1.5s intervals"),
        ("Attack Injection", "Port Scan / Brute Force / Data Exfil / C2 beacon injected every 20–45s"),
        ("Refresh Method",  "@st.fragment(run_every='5s') — only the Live Feed panel re-runs"),
        ("Start",           "Terminal 1: python -m streamlit run Home.py  |  Terminal 2: python live_log_generator.py"),
    ]),
    PageBreak(),
]

# ── PAGE 5: TECH STACK & DEMO ────────────────────────────────────────────────
story += [
    sec_bar("TECHNOLOGY STACK  &  COMPETITION DEMO SCRIPT", DARK_GREEN),
    sp(3),
    Paragraph("Full Technology Stack", H2),
    data_table(
        ["Library", "Version", "Purpose"],
        [
            ["Streamlit",         "1.39+", "Web UI — multi-page, fragments, session state"],
            ["Scikit-learn",      "1.4+",  "Isolation Forest unsupervised anomaly detection"],
            ["OpenCV",            "4.x",   "Image preprocessing, QR detection, video frame extraction"],
            ["Plotly",            "5.x",   "Interactive scatter, bar, pie, heatmap, network graph, gauge"],
            ["Anthropic / Groq / GenAI", "Latest", "Claude · Llama Vision · Gemini — AI vision APIs"],
            ["PyMuPDF (fitz)",    "1.24+", "PDF page rasterisation at 2x zoom"],
            ["Pandas / NumPy",    "2.x",   "Data ingestion, feature engineering, statistics"],
            ["Pillow (PIL)",      "10.x",  "Image loading, format conversion, preprocessing"],
        ],
        [48*mm, 18*mm, BODY_W - 66*mm], DARK_GREEN
    ),
    sp(3),
    Paragraph("2-Minute Demo — Deepfake Detector", H2),
    data_table(
        ["Step", "Action"],
        [
            ["1", "Home → Launch Deepfake Detector → Sidebar: Analyze Demo"],
            ["2", "Point to verdict banner: FAKE / confidence % — AI manipulation type shown"],
            ["3", "Expand AI Forensic Report → primary indicators + 7-dimension breakdown"],
            ["4", "Upload a real photo → shows AUTHENTIC with different evidence signals"],
            ["5", "Upload a PDF → multi-page scan with QR code detection result"],
            ["6", "Click Download Report → show the .txt forensic output"],
        ],
        [12*mm, BODY_W - 12*mm], DARK_GREEN
    ),
    sp(4),
    Paragraph("2-Minute Demo — AI Threat Hunter", H2),
    data_table(
        ["Step", "Action"],
        [
            ["1",  "Home → Launch AI Threat Hunter → Use Sample Data"],
            ["2",  "Overview tab: timeline — red dots are attacks, dot size = data volume"],
            ["3",  "Heatmap: attacks cluster at 2–4 AM — classic attacker behaviour"],
            ["4",  "AI Analysis tab: select highest risk alert (Data Exfiltration, 90+/100)"],
            ["5",  "MITRE mapping: TA0010 → T1048.003 · Kill Chain: Exfiltration phase"],
            ["6",  "Incident Response tab → download IR playbook as .txt"],
            ["7",  "Sidebar → Live Feed mode → Terminal 2: python live_log_generator.py"],
            ["8",  "Live Feed tab: new attack appears every 20–45s, panel refreshes every 5s"],
        ],
        [12*mm, BODY_W - 12*mm], DARK_GREEN
    ),
    sp(4),
    hr(NAVY, 1.5),
    Paragraph(
        "Cyber Security Suite  ·  AI Threat Hunter + Deepfake Detector  ·  "
        "MITRE ATT&CK  ·  Isolation Forest  ·  Edition 2026",
        S("ft", fontSize=7.5, textColor=DIM, alignment=TA_CENTER, leading=11)
    ),
]


# ── Build ────────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=15*mm, rightMargin=15*mm,
    topMargin=13*mm,  bottomMargin=10*mm,
    title="Cyber Security Suite — Project Explanation",
    author="Cyber Security Competition 2026",
    subject="AI Threat Hunter & Deepfake Detector",
)

doc.build(story, onFirstPage=page_header_footer, onLaterPages=page_header_footer)
print(f"PDF generated: {OUTPUT}")
