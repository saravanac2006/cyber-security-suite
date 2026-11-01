"""
Groq Vision deepfake analyzer — uses Llama 3.2 Vision (free tier, 30 req/min).
"""
import base64
import json
import re
import io
import numpy as np
from PIL import Image
from core.gemini_analyzer import ANALYSIS_PROMPT, _parse_rich_response

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def list_groq_models(api_key: str) -> tuple[list[str], str | None]:
    if not GROQ_AVAILABLE:
        return [], "groq package not installed"
    try:
        client = Groq(api_key=api_key)
        all_models = client.models.list()
        vision_models = []
        for m in all_models.data:
            mid = m.id
            if "vision" in mid or "llava" in mid:
                vision_models.append(mid)
        vision_models.sort(reverse=True)
        if not vision_models:
            vision_models = sorted(
                [m.id for m in all_models.data if "whisper" not in m.id], reverse=True
            )
        return vision_models, None
    except Exception as e:
        return [], str(e)


class GroqAnalyzer:

    def __init__(self, api_key: str, model_name: str = "llama-3.2-90b-vision-preview"):
        if not GROQ_AVAILABLE:
            raise ImportError("groq not installed. Run: pip install groq")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def analyze(self, img: np.ndarray) -> dict:
        try:
            pil_img = Image.fromarray(img).convert("RGB")
            if max(pil_img.size) > 1024:
                pil_img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            pil_img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": ANALYSIS_PROMPT},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                    ],
                }],
                temperature=0.1,
                max_tokens=2048,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                return self._error(f"No JSON in response: {raw[:200]}")
            return _parse_rich_response(json_match.group(), f"AI Engine ({self.model_name})")

        except json.JSONDecodeError as e:
            return self._error(f"JSON parse error: {e}")
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate_limit" in msg.lower():
                return {**self._error(msg), "quota_exhausted": True, "retry_after_mins": 1}
            return self._error(msg)

    @staticmethod
    def _error(msg: str) -> dict:
        return {"success": False, "error": msg, "verdict": "UNCERTAIN", "confidence": 0,
                "source": "AI Engine (error)"}
