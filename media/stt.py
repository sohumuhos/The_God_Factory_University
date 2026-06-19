"""Speech-to-text for Office Hours voice chat.

Transcribes recorded audio using an OpenAI-compatible Whisper endpoint. Defaults
to Groq's free Whisper (whisper-large-v3) — the same free engine the FreeFlow
dictation app relies on — reusing the already-installed `openai` client and the
provider key configured in Settings. Falls back to the OpenAI Whisper API when
the provider is OpenAI. No heavy local model, works on Python 3.14.
"""
from __future__ import annotations

import io


def _stt_config() -> tuple[str | None, str | None, str | None]:
    """Return (api_key, base_url, model) for transcription, or (None, None, None)."""
    from core.database import get_setting
    provider = (get_setting("llm_provider", "") or "").lower()
    key = get_setting("llm_api_key", "") or ""
    if provider == "groq" and key:
        return key, "https://api.groq.com/openai/v1", "whisper-large-v3"
    if provider == "openai" and key:
        return key, None, "whisper-1"
    # Explicit override settings, if a user added them
    groq_key = get_setting("groq_api_key", "") or ""
    if groq_key:
        return groq_key, "https://api.groq.com/openai/v1", "whisper-large-v3"
    return None, None, None


def transcribe(audio_bytes: bytes, filename: str = "audio.wav") -> dict:
    """Transcribe audio bytes. Returns {'text': ...} or {'error': ...}."""
    if not audio_bytes:
        return {"error": "No audio captured."}
    key, base_url, model = _stt_config()
    if not key:
        return {"error": (
            "Voice transcription needs a Groq or OpenAI API key. Set the LLM Provider "
            "to Groq (free tier) or OpenAI in Settings — Groq is free and fast."
        )}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key, base_url=base_url) if base_url else OpenAI(api_key=key)
        buf = io.BytesIO(audio_bytes)
        buf.name = filename
        resp = client.audio.transcriptions.create(model=model, file=buf)
        return {"text": (getattr(resp, "text", "") or "").strip()}
    except Exception as exc:
        return {"error": f"Transcription failed: {exc}"}
