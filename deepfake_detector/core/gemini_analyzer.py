"""
Gemini Vision deepfake analyzer — uses the google-genai SDK (v1 API).
"""
import json
import re
import numpy as np
from PIL import Image

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


ANALYSIS_PROMPT = """You are a world-class digital forensics expert and deepfake analyst with over 20 years of experience
in GAN artifact detection, media forensics, and AI-generated content analysis.

Perform an exhaustive forensic examination of this image. Your report must be detailed, evidence-based,
and specific — cite exact visual observations, not generic statements.

Analyze EVERY dimension below:

FACIAL FORENSICS (if faces present):
- Skin pore patterns, micro-texture, sebaceous gland distribution
- Hair strand rendering: individual strands vs. blended mass
- Eye symmetry, catchlight consistency, iris texture, pupil shape
- Teeth rendering, gum line naturalness, dental spacing
- Ear structure, cartilage detail, helix/antihelix geometry
- Neck/jawline blending, under-chin shadow consistency
- Facial symmetry analysis (faces are naturally asymmetric; perfect symmetry = GAN)

TEXTURE & MATERIAL ANALYSIS:
- Skin smoothness vs. natural pore/texture randomness
- Clothing fabric weave, thread count rendering
- Hair texture continuity across boundaries
- Object surface material consistency

LIGHTING & SHADOW FORENSICS:
- Light source direction consistency across all face regions
- Catchlight position must match ambient light source
- Shadow directionality under nose, chin, around eyes
- Specular highlight placement on skin, glasses, hair
- Ambient occlusion in eye sockets, nostrils, ear canals

BACKGROUND & DEPTH:
- Depth-of-field gradient naturalness
- Background blur consistency (Gaussian vs. synthetic bokeh)
- Subject-background boundary edge analysis
- Repeated texture patterns (GAN tiling artifacts)
- Object boundary sharpness vs. background sharpness

FREQUENCY & SPECTRAL:
- Checkerboard artifacts from upsampling (GAN signature)
- Over-smooth frequency spectrum in skin regions
- Unnatural periodicity in textures

COMPRESSION & NOISE:
- JPEG block boundary alignment with content
- Noise pattern uniformity (camera sensors produce non-uniform noise)
- Sensor noise fingerprint consistency

COLOR & CHROMATIC:
- Skin tone consistency across lighting conditions
- Color fringing at high-contrast edges
- Saturation abnormalities in shadow regions
- White balance consistency

DOCUMENT/TEXT/MEDIA (if applicable):
- Font rendering consistency and kerning
- Text shadow/reflection consistency
- QR code integrity and alignment
- Watermark or metadata inconsistencies

PROVENANCE INDICATORS:
- Signs of original camera capture (lens distortion, chromatic aberration)
- Signs of AI generation (over-perfect compositions, uncanny valley)
- Editing traces (clone stamp, content-aware fill, patch tool)

IMPORTANT: Be exhaustive. If a face is present, analyze every feature. If text is present, analyze every character.
Every claim must cite a SPECIFIC visual observation. Do not write generic statements.

Respond ONLY with valid JSON — no markdown fences, no extra text:
{
  "verdict": "FAKE" | "REAL" | "UNCERTAIN",
  "confidence": <0-100>,
  "manipulation_type": "<one of: GAN Generated | Face Swap | Face Reenactment | Photoshop Edit | Inpainting | Text Manipulation | Composite | None Detected | Unknown>",
  "risk_level": "<HIGH | MEDIUM | LOW>",
  "executive_summary": "<2-3 sentence professional summary of the overall finding with key evidence>",
  "primary_indicators": [
    "<most critical artifact — be specific about location and appearance>",
    "<second artifact>",
    "<third artifact>",
    "<fourth artifact>",
    "<fifth artifact>"
  ],
  "authenticity_signals": [
    "<evidence that supports authenticity — e.g., natural lens distortion present, sensor noise consistent>",
    "<second authenticity signal>",
    "<third authenticity signal>"
  ],
  "manipulation_signals": [
    "<evidence of manipulation — specific and located>",
    "<second manipulation signal>",
    "<third manipulation signal>",
    "<fourth manipulation signal>"
  ],
  "detailed_findings": {
    "facial_forensics": {
      "applicable": true | false,
      "score": <0-100, where 100 = definitely manipulated>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>", "<specific observation>"],
      "explanation": "<2-3 sentences with precise technical detail>"
    },
    "texture_analysis": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    },
    "lighting_forensics": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    },
    "background_analysis": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    },
    "color_chromatic": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    },
    "noise_compression": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    },
    "document_text": {
      "applicable": true | false,
      "score": <0-100>,
      "status": "SUSPICIOUS" | "MODERATE" | "CLEAN",
      "evidence": ["<specific observation>"],
      "explanation": "<2-3 sentences>"
    }
  },
  "provenance_assessment": "<1-2 sentences on likely origin — camera model type, generation method, editing software>",
  "recommendation": "<specific actionable advice for the analyst or decision-maker>",
  "analyst_notes": "<any additional observations, caveats, or edge cases the analyst should know>"
}"""


def list_available_models(api_key: str) -> tuple[list[str], str | None]:
    if not GEMINI_AVAILABLE:
        return [], "google-genai package not installed"
    try:
        client = genai.Client(api_key=api_key)
        results = []
        for m in client.models.list():
            raw_name = getattr(m, "name", "") or ""
            short = raw_name.replace("models/", "") if raw_name.startswith("models/") else raw_name
            methods = getattr(m, "supported_generation_methods", None) or []
            if methods and "generateContent" not in methods:
                continue
            if "gemini" not in short.lower():
                continue
            if any(x in short for x in ("embedding", "aqa", "retrieval", "text-")):
                continue
            if any(x in short for x in ("gemini-1.0", "gemini-pro-vision")):
                continue
            results.append(short)
        if not results:
            return [], "No eligible vision models found for this API key"

        def _sort_key(name: str):
            ver = 0.0
            match = re.search(r"(\d+\.\d+|\d+)", name)
            if match:
                ver = float(match.group())
            return (-ver, 0 if "flash" in name else 1, name)

        results.sort(key=_sort_key)
        return results, None
    except Exception as e:
        return [], str(e)


class GeminiAnalyzer:

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai not installed. Run: pip install google-genai")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def analyze(self, img: np.ndarray) -> dict:
        try:
            pil_img = Image.fromarray(img)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[ANALYSIS_PROMPT, pil_img],
                config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=2048),
            )
            raw = response.text.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                return self._error(f"No JSON in response: {raw[:300]}")
            return _parse_rich_response(json_match.group(), f"AI Engine ({self.model_name})")
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                retry = re.search(r"retryDelay.*?(\d+)s", msg)
                wait = int(retry.group(1)) if retry else 4578
                return {**self._error(msg), "quota_exhausted": True, "retry_after_mins": wait // 60}
            return self._error(msg)

    @staticmethod
    def _error(msg: str) -> dict:
        return {"success": False, "error": msg, "verdict": "UNCERTAIN", "confidence": 0,
                "source": "AI Engine (error)"}


def _parse_rich_response(raw_json: str, source: str) -> dict:
    data = json.loads(raw_json)
    verdict = str(data.get("verdict", "UNCERTAIN")).upper()
    if verdict not in ("FAKE", "REAL", "UNCERTAIN"):
        verdict = "UNCERTAIN"
    confidence = max(0, min(100, int(data.get("confidence", 50))))

    # Normalize detailed_findings scores to 0-1
    raw_findings = data.get("detailed_findings", {})
    findings = {}
    for key, val in raw_findings.items():
        if isinstance(val, dict):
            score_raw = val.get("score", 0)
            findings[key] = {
                "applicable": val.get("applicable", True),
                "score": max(0.0, min(1.0, score_raw / 100)),
                "status": val.get("status", "CLEAN"),
                "evidence": val.get("evidence", []),
                "explanation": val.get("explanation", ""),
            }

    return {
        "success": True,
        "verdict": verdict,
        "confidence": confidence,
        "manipulation_type": data.get("manipulation_type", "Unknown"),
        "risk_level": data.get("risk_level", "MEDIUM"),
        "executive_summary": data.get("executive_summary", ""),
        "primary_indicators": data.get("primary_indicators", []),
        "authenticity_signals": data.get("authenticity_signals", []),
        "manipulation_signals": data.get("manipulation_signals", []),
        "detailed_findings": findings,
        "provenance_assessment": data.get("provenance_assessment", ""),
        "recommendation": data.get("recommendation", ""),
        "analyst_notes": data.get("analyst_notes", ""),
        "source": source,
        # keep legacy fields for backward compat
        "explanation": data.get("executive_summary", ""),
        "dimension_scores": {k: v["score"] for k, v in findings.items() if v.get("applicable")},
    }
