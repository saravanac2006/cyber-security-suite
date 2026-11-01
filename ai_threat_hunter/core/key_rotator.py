"""
AI key rotation pool for Threat Hunter — Claude keys preferred (text analysis).
Add more keys to the lists to increase uptime.
"""
import json
import os

_CLAUDE_KEYS: list[str] = [
    # Add your Claude API keys here, or use the sidebar "Backup AI Key" input
]

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "keys_config.json")
_EXHAUSTED: set[str] = set()


def _load_saved() -> list[str]:
    try:
        with open(_CONFIG_PATH) as f:
            data = json.load(f)
            return data.get("claude", [])
    except Exception:
        return []


def save_user_key(key: str):
    try:
        try:
            with open(_CONFIG_PATH) as f:
                data = json.load(f)
        except Exception:
            data = {}
        pool = data.setdefault("claude", [])
        if key not in pool:
            pool.append(key)
        with open(_CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def mark_exhausted(key: str):
    _EXHAUSTED.add(key)


def next_key(user_key: str = "") -> str | None:
    seen: set[str] = set()
    candidates: list[str] = []
    for k in _CLAUDE_KEYS + _load_saved():
        k = k.strip()
        if k and k not in seen:
            seen.add(k)
            candidates.append(k)
    if user_key.strip() and user_key.strip() not in seen:
        candidates.append(user_key.strip())
    for k in candidates:
        if k not in _EXHAUSTED:
            return k
    return None


def pool_ready(user_key: str = "") -> bool:
    return next_key(user_key) is not None
