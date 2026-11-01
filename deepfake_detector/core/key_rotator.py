"""
Key rotation pool — tries all built-in keys across providers in priority order.
Working user-provided keys are saved to keys_config.json and join the pool automatically.
"""
import json
import os
import streamlit as st

# ── Built-in key pool ─────────────────────────────────────────────────────────
_GROQ_KEYS: list[str] = [
    # Add your Groq API keys here (gsk_...), or use the sidebar "Backup Key" input
]

_CLAUDE_KEYS: list[str] = [
    # Add your Claude API keys here (sk-ant-... or apikey_...)
]

_GEMINI_KEYS: list[str] = [
    # Add your Gemini API keys here (AIza... or AQ....)
]

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "keys_config.json")


def _load_saved_keys() -> dict[str, list[str]]:
    try:
        with open(_CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"groq": [], "claude": [], "gemini": []}


def save_user_key(key: str, provider: str):
    """Persist a working user key to keys_config.json so it joins the pool."""
    try:
        data = _load_saved_keys()
        pool = data.setdefault(provider, [])
        if key not in pool:
            pool.append(key)
        with open(_CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def detect_provider(key: str) -> str | None:
    k = key.strip()
    if k.startswith("AIza") or k.startswith("AQ."):
        return "gemini"
    if k.startswith("gsk_"):
        return "groq"
    if k.startswith("sk-ant-") or k.startswith("sk-") or k.startswith("apikey_"):
        return "claude"
    return None


# keep old name for compatibility
_detect_provider = detect_provider


def build_candidate_list(user_key: str = "") -> list[tuple[str, str]]:
    """
    Return ordered (provider, key) list. Priority: Groq → Claude → Gemini.
    Saved user keys from keys_config.json are merged in.
    User's current backup key is appended last.
    """
    saved = _load_saved_keys()

    seen: set[str] = set()
    candidates: list[tuple[str, str]] = []

    def _add(provider: str, keys: list[str]):
        for k in keys:
            k = k.strip()
            if k and k not in seen:
                seen.add(k)
                candidates.append((provider, k))

    _add("groq", _GROQ_KEYS + saved.get("groq", []))
    _add("claude", _CLAUDE_KEYS + saved.get("claude", []))
    _add("gemini", _GEMINI_KEYS + saved.get("gemini", []))

    if user_key.strip() and user_key.strip() not in seen:
        provider = detect_provider(user_key)
        if provider:
            candidates.append((provider, user_key.strip()))

    return candidates


def mark_key(key: str, status: str):
    pool = st.session_state.setdefault("_key_status", {})
    pool[key] = status


def get_key_status(key: str) -> str:
    return st.session_state.get("_key_status", {}).get(key, "ok")


def next_available(user_key: str = "") -> tuple[str, str] | None:
    for provider, key in build_candidate_list(user_key):
        if get_key_status(key) == "ok":
            return provider, key
    return None


def pool_stats(user_key: str = "") -> dict:
    candidates = build_candidate_list(user_key)
    ok = sum(1 for p, k in candidates if get_key_status(k) == "ok")
    exhausted = sum(1 for p, k in candidates if get_key_status(k) == "exhausted")
    invalid = sum(1 for p, k in candidates if get_key_status(k) == "invalid")
    return {"total": len(candidates), "ok": ok, "exhausted": exhausted, "invalid": invalid}
