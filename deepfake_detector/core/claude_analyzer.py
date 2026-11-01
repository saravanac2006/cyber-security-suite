"""
Claude Vision deepfake analyzer — uses the Anthropic Messages API.
"""
import base64
import json
import re
import io
import numpy as np
from PIL import Image
from core.gemini_analyzer import ANALYSIS_PROMPT, _parse_rich_response

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


def list_claude_models(api_key: str) -> tuple[list[str], str | None]:
    if not CLAUDE_AVAILABLE:
        return [], "anthropic package not installed"
    try:
        client = anthropic.Anthropic(api_key=api_key)
        all_models = client.models.list()
        vision_models = []
        for m in all_models.data:
            mid = m.id
            if ("claude-3" in mid or "claude-sonnet" in mid or
                    "claude-opus" in mid or "claude-haiku" in mid):
                if "instant" not in mid:
                    vision_models.append(mid)
        vision_models.sort(reverse=True)
        if not vision_models:
            return [], "No vision-capable Claude models found"
        return vision_models, None
    except Exception as e:
        return [], str(e)


class ClaudeAnalyzer:

    def __init__(self, api_key: str, model_name: str = "claude-haiku-4-5-20251001"):
        if not CLAUDE_AVAILABLE:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = model_name

    def analyze(self, img: np.ndarray) -> dict:
        try:
            pil_img = Image.fromarray(img).convert("RGB")
            if max(pil_img.size) > 1024:
                pil_img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            pil_img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
                        },
                        {"type": "text", "text": ANALYSIS_PROMPT},
                    ],
                }],
            )
            raw = response.content[0].text.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                return self._error(f"No JSON in response: {raw[:200]}")
            return _parse_rich_response(json_match.group(), f"AI Engine ({self.model_name})")

        except json.JSONDecodeError as e:
            return self._error(f"JSON parse error: {e}")
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate_limit" in msg.lower() or "overloaded" in msg.lower():
                return {**self._error(msg), "quota_exhausted": True, "retry_after_mins": 1}
            return self._error(msg)

    @staticmethod
    def _error(msg: str) -> dict:
        return {"success": False, "error": msg, "verdict": "UNCERTAIN", "confidence": 0,
                "source": "AI Engine (error)"}
