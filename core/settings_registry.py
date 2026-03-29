"""Centralized settings registry for The God Factory University.

Provides a single source of truth for all setting keys, their default
values, types, and which category they belong to. Other pages import
these helpers to stay consistent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ── Setting definition ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SettingDef:
    key: str
    label: str
    category: str
    default: Any
    description: str = ""
    widget: str = "text"        # text | password | toggle | select | slider | number | radio | json
    options: tuple = ()         # For select/radio widgets
    min_val: Any = None
    max_val: Any = None
    step: Any = None

# ── Categories ────────────────────────────────────────────────────────────────

CAT_GENERAL      = "General"
CAT_LLM          = "LLM & AI"
CAT_VOICE        = "Voice & Audio"
CAT_VIDEO        = "Video & Rendering"
CAT_IMAGE        = "Image Generation"
CAT_LEARNING     = "Course & Learning"
CAT_ADVANCED     = "Advanced"

# ── Registry ──────────────────────────────────────────────────────────────────

SETTINGS: list[SettingDef] = [
    # General
    SettingDef("student_name", "Student Name", CAT_GENERAL, "Scholar", "Your display name throughout the university."),
    SettingDef("ui_mode", "UI Mode", CAT_GENERAL, "student", "Controls which pages are visible.", widget="select", options=("student", "builder", "operator")),
    SettingDef("deadlines_enabled", "Deadline System", CAT_GENERAL, "0", "Show countdown timers on assignments.", widget="toggle"),
    SettingDef("quests_enabled", "Weekly Quests", CAT_GENERAL, "1", "Enable weekly learning quest challenges.", widget="toggle"),

    # LLM & AI
    SettingDef("llm_provider", "LLM Provider", CAT_LLM, "ollama", "AI provider for text generation.", widget="select",
               options=("ollama", "lm_studio", "openai", "github_models", "anthropic", "groq", "mistral", "together_ai", "huggingface")),
    SettingDef("llm_model", "LLM Model", CAT_LLM, "", "Model name to use with the selected provider."),
    SettingDef("llm_api_key", "LLM API Key", CAT_LLM, "", "API key for the selected LLM provider.", widget="password"),
    SettingDef("llm_base_url", "LLM Base URL", CAT_LLM, "", "Custom endpoint URL (for local or self-hosted)."),

    # Voice & Audio
    SettingDef("tts_voice", "TTS Voice", CAT_VOICE, "en-US-AriaNeural", "Microsoft Neural TTS voice for narration.", widget="select"),
    SettingDef("tts_engine", "TTS Engine", CAT_VOICE, "edge_tts", "Text-to-speech engine.", widget="select",
               options=("edge_tts", "pyttsx3", "gtts", "coqui", "elevenlabs", "bark", "silero")),
    SettingDef("elevenlabs_api_key", "ElevenLabs API Key", CAT_VOICE, "", "API key for ElevenLabs voices.", widget="password"),

    # Video & Rendering
    SettingDef("video_profile", "Quality Profile", CAT_VIDEO, "Balanced", "Video quality preset.", widget="select",
               options=("Draft (Fast)", "Balanced", "High Quality", "Final (Slow)", "Custom")),
    SettingDef("video_fps", "FPS", CAT_VIDEO, "15", "Frames per second.", widget="select", options=("10", "15", "24", "30")),
    SettingDef("video_resolution", "Resolution", CAT_VIDEO, "960x540", "Output resolution.", widget="select",
               options=("960x540", "1280x720", "1920x1080")),
    SettingDef("render_provider", "Render Engine", CAT_VIDEO, "local", "Video rendering backend.", widget="select",
               options=("local", "comfyui", "free_cloud_mix", "custom_api")),
    SettingDef("render_api_key", "Custom Render API Key", CAT_VIDEO, "", "API key for custom render backend.", widget="password"),
    SettingDef("vfx_config", "VFX Configuration", CAT_VIDEO, "{}", "Visual effects JSON config.", widget="json"),

    # Image Generation
    SettingDef("pollinations_api_key", "Pollinations API Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("hf_api_token", "HuggingFace API Token", CAT_IMAGE, "", "", widget="password"),
    SettingDef("leonardo_api_key", "Leonardo API Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("github_token", "GitHub Models Token", CAT_IMAGE, "", "", widget="password"),
    SettingDef("limewire_api_key", "LimeWire API Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("stability_api_key", "Stability AI Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("getimg_api_key", "GetImg.ai API Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("deepai_api_key", "DeepAI API Key", CAT_IMAGE, "", "", widget="password"),
    SettingDef("prodia_api_key", "Prodia API Key", CAT_IMAGE, "", "", widget="password"),

    # Course & Learning
    SettingDef("token_target", "Daily Token Target", CAT_LEARNING, "50000", "Target tokens to study per day.", widget="number", min_val=1000, max_val=500000, step=5000),
    SettingDef("student_preferences", "Learning Preferences", CAT_LEARNING, "", "Free-text description of how you like to learn."),

    # Advanced
    SettingDef("share_generated_media", "Media Sharing", CAT_ADVANCED, "private", "How generated media is shared.", widget="radio",
               options=("private", "course_shared", "global")),
]

# ── Lookup helpers ────────────────────────────────────────────────────────────

_BY_KEY: dict[str, SettingDef] = {s.key: s for s in SETTINGS}
_BY_CATEGORY: dict[str, list[SettingDef]] = {}
for _s in SETTINGS:
    _BY_CATEGORY.setdefault(_s.category, []).append(_s)

CATEGORIES = [CAT_GENERAL, CAT_LLM, CAT_VOICE, CAT_VIDEO, CAT_IMAGE, CAT_LEARNING, CAT_ADVANCED]


def get_def(key: str) -> SettingDef | None:
    """Get the definition for a setting key."""
    return _BY_KEY.get(key)


def get_default(key: str) -> Any:
    """Get the default value for a setting key."""
    defn = _BY_KEY.get(key)
    return defn.default if defn else ""


def settings_for_category(category: str) -> list[SettingDef]:
    """Get all settings in a category."""
    return _BY_CATEGORY.get(category, [])
