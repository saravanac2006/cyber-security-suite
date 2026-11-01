# 🔍 Deepfake Detector

> AI-powered media forensics tool that detects manipulated images, deepfakes, and AI-generated content using multi-provider vision AI with automatic key rotation.

---

## 📸 What It Detects

| Manipulation Type | Description |
|---|---|
| **Deepfake Face Swap** | AI-replaced faces using GAN / diffusion models |
| **GAN-Generated Image** | Fully synthetic images from generative networks |
| **Image Splicing** | Regions copied from other photos |
| **Inpainting** | Object removal / background fill using AI |
| **Screenshot Fakery** | Manipulated document or chat screenshots |
| **Metadata Mismatch** | Camera/creation metadata inconsistencies |
| **QR Code Threats** | Malicious URLs embedded in QR codes |

---

## 🚀 Quick Start

```bash
cd deepfake_detector
pip install -r requirements.txt
python -m streamlit run app.py
```

Open **http://localhost:8501**

---

## 🧠 How It Works

```
Upload Image / PDF / Video Frame
          ↓
  Pre-processing (OpenCV)
  └── Resize, normalize, extract frames
          ↓
  AI Vision Analysis (3 providers, auto-rotation)
  ├── Groq  →  Llama 3.2 Vision
  ├── Claude →  claude-3-5-sonnet (vision)
  └── Gemini → gemini-1.5-pro-vision
          ↓
  Rich JSON Response (12 analysis sections)
          ↓
  Structured Forensic Report
```

---

## 📊 7-Dimension AI Analysis

Each image is scored across 7 forensic dimensions:

| Dimension | What's Checked |
|---|---|
| **Facial Biometrics** | Skin texture, symmetry, eye consistency, hair edges |
| **GAN Artifacts** | Checkerboard patterns, frequency anomalies |
| **Compression Analysis** | JPEG double-compression, blocking artefacts |
| **Lighting & Shadows** | Consistency of light sources and reflections |
| **Semantic Coherence** | Object boundaries, background plausibility |
| **Metadata Integrity** | EXIF data, creation timestamps, camera info |
| **Statistical Noise** | Sensor noise patterns, noise floor uniformity |

---

## 📄 Supported Input Formats

| Format | Notes |
|---|---|
| **Images** | JPG, PNG, WEBP, BMP, TIFF |
| **PDF** | All pages scanned; QR codes extracted |
| **Video** | Key frame extraction (first / middle / last) |

---

## 🔑 AI Key Rotation

The app maintains an internal pool of AI keys across three providers. Keys are tried in order — **Groq → Claude → Gemini** — and exhausted keys are automatically skipped.

```
Sidebar: "Backup AI Key" input
└── Paste any working key (any provider)
└── Auto-detected by prefix (gsk_ / sk-ant- / AIza)
└── Saved to keys_config.json if successful
```

No key? The app shows a clear "engines exhausted" warning and still runs heuristic analysis.

---

## 📋 AI Report Structure

Every analysis returns:

```
Executive Summary
├── Manipulation Type           (e.g. "Deepfake Face Swap")
├── Risk Level                  (LOW / MEDIUM / HIGH / CRITICAL)
├── AI Confidence               (0–100%)
└── Summary paragraph

Primary Indicators              (top 5 evidence points)

Signals
├── Manipulation Signals        (what's suspicious)
└── Authenticity Signals        (what looks genuine)

Dimension-by-Dimension Analysis (7 sections, each with score + evidence)

Provenance Assessment           (origin hypothesis)
Recommendation                  (actionable conclusion)
Analyst Notes                   (caveats and limitations)
```

---

## 🗂️ File Structure

```
deepfake_detector/
├── app.py                      # Main Streamlit app
├── requirements.txt
└── core/
    ├── gemini_analyzer.py      # Gemini API + shared prompt/parser
    ├── groq_analyzer.py        # Groq Llama vision
    ├── claude_analyzer.py      # Anthropic Claude vision
    ├── key_rotator.py          # Multi-provider key pool
    ├── detector.py             # Heuristic pre-checks
    ├── audio_processor.py      # Audio track analysis
    └── video_processor.py      # Frame extraction
```

---

## 🎯 Demo Walkthrough

1. **Start the app** — `python -m streamlit run app.py`
2. **Upload an image** — drag any JPG/PNG into the uploader
3. **Watch the AI analyse** — status card shows which engine is active
4. **Read the report:**
   - Verdict banner (AUTHENTIC / MANIPULATED) with confidence %
   - Primary indicators list
   - 7-dimension breakdown
   - Provenance assessment
5. **QR code** — if detected, URL is shown with risk classification
6. **Download report** — JSON export of full analysis
7. **Try a PDF** — upload a document; every page is scanned

---

## ⚡ Performance

| Input | Typical Analysis Time |
|---|---|
| Single image (< 2 MB) | 8–15 seconds |
| PDF (10 pages) | 30–60 seconds |
| Video (key frames) | 20–40 seconds |

Times depend on the AI provider response speed and key availability.

---

## ⚠️ Limitations

- Video analysis uses extracted frames only (not full temporal analysis)
- Audio deepfake detection is metadata-based, not waveform AI
- Very small images (< 100×100 px) may return low-confidence results
- AI analysis reflects the model's knowledge cutoff and training data
