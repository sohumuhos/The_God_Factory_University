"""
Video Production Wizard — configure and render lecture videos.

Covers: quality profiles, VFX settings, AI backgrounds, TTS voice selection,
binaural beats, single/batch rendering, and export options.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from core.wizard_engine import (
    WizardDef, WizardStep, register_wizard, log_wizard_error,
)

ROOT = Path(__file__).resolve().parent.parent.parent
WIZARD_ID = "video_production"


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def _execute_voice_config(data: dict, key: str) -> tuple[bool, str]:
    voice = data.get("tts_voice", "en-US-AriaNeural")
    rate = data.get("tts_rate", "+0%")
    pitch = data.get("tts_pitch", "+0Hz")

    try:
        from core.database import save_setting
        save_setting("tts_voice", voice)
        save_setting("tts_rate", rate)
        save_setting("tts_pitch", pitch)
        data["voice_configured"] = True
        return True, f"Voice: {voice} | Rate: {rate} | Pitch: {pitch}"
    except Exception as exc:
        return False, str(exc)


def _execute_binaural_config(data: dict, key: str) -> tuple[bool, str]:
    preset = data.get("binaural_preset", "none")
    try:
        from core.database import save_setting
        save_setting("binaural_preset", preset)
        data["binaural_configured"] = True
        presets = {
            "none": "None", "gamma": "Gamma 40Hz (Peak Focus)",
            "beta": "Beta 18Hz (Active Thinking)",
            "alpha": "Alpha 10Hz (Relaxed Focus)",
            "theta": "Theta 6Hz (Deep Meditation)",
        }
        return True, f"Binaural: {presets.get(preset, preset)}"
    except Exception as exc:
        return False, str(exc)


def _execute_quality_profile(data: dict, key: str) -> tuple[bool, str]:
    profile = data.get("quality_profile", "balanced")
    fps = data.get("video_fps", 15)
    resolution = data.get("video_resolution", "1280x720")

    # Apply profile presets
    profiles = {
        "draft": {"fps": 10, "resolution": "960x540"},
        "balanced": {"fps": 15, "resolution": "1280x720"},
        "high": {"fps": 24, "resolution": "1280x720"},
        "final": {"fps": 24, "resolution": "1920x1080"},
        "custom": {"fps": fps, "resolution": resolution},
    }

    settings = profiles.get(profile, profiles["balanced"])
    data["video_fps"] = settings["fps"]
    data["video_resolution"] = settings["resolution"]

    try:
        from core.database import save_setting
        save_setting("video_profile", profile)
        save_setting("video_fps", str(settings["fps"]))
        save_setting("video_resolution", settings["resolution"])
        return True, f"Profile: {profile} | FPS: {settings['fps']} | Res: {settings['resolution']}"
    except Exception as exc:
        return False, str(exc)


def _execute_vfx_config(data: dict, key: str) -> tuple[bool, str]:
    vfx = {
        "ai_backgrounds": data.get("vfx_ai_backgrounds", True),
        "transitions": data.get("vfx_transitions", True),
        "ken_burns": data.get("vfx_ken_burns", True),
        "color_grade": data.get("vfx_color_grading", True),
        "text_overlay": data.get("vfx_text_overlays", True),
        "ambient_particles": data.get("vfx_particles", True),
        "watermark": data.get("vfx_watermark", False),
    }
    data["vfx_config"] = vfx

    try:
        from core.database import save_setting
        save_setting("vfx_config", json.dumps(vfx))
        enabled = [k for k, v in vfx.items() if v]
        return True, f"{len(enabled)} VFX enabled: {', '.join(enabled)}"
    except Exception as exc:
        return False, str(exc)


def _execute_image_provider(data: dict, key: str) -> tuple[bool, str]:
    provider = data.get("image_provider", "pollinations")
    try:
        from core.database import save_setting
        save_setting("image_provider", provider)
        data["image_provider_set"] = True
        return True, f"AI background provider: {provider}"
    except Exception as exc:
        return False, str(exc)


def _execute_select_courses(data: dict, key: str) -> tuple[bool, str]:
    course_ids = data.get("render_course_ids", [])
    render_all = data.get("render_all_courses", False)

    if render_all:
        try:
            from core.database import get_all_courses
            courses = get_all_courses()
            course_ids = [c["id"] for c in courses]
            data["render_course_ids"] = course_ids
        except Exception as exc:
            return False, f"Failed to load courses: {exc}"

    if not course_ids:
        return False, "No courses selected for rendering"

    data["render_course_ids"] = course_ids
    return True, f"{len(course_ids)} course(s) selected for rendering"


def _execute_enrich_before_render(data: dict, key: str) -> tuple[bool, str]:
    if not data.get("enrich_before_render", False):
        return True, "Skipping pre-render enrichment"

    course_ids = data.get("render_course_ids", [])
    enriched = 0
    try:
        from llm.tools_enrichment import enrich_course_narration
        for cid in course_ids:
            try:
                result = enrich_course_narration(cid)
                enriched += result.get("lectures_enriched", 0)
            except Exception as exc:
                log_wizard_error("Video Production", "Pre-render Enrich", str(exc))
            rate = data.get("rate_limit", 2.0)
            if rate > 0:
                time.sleep(rate)
    except Exception as exc:
        return False, f"Enrichment failed: {exc}"

    return True, f"{enriched} lectures enriched before render"


def _execute_batch_render(data: dict, key: str) -> tuple[bool, str]:
    course_ids = data.get("render_course_ids", [])
    if not course_ids:
        return False, "No courses to render"

    fps = data.get("video_fps", 15)
    res = data.get("video_resolution", "1280x720")
    parts = res.split("x")
    w, h = (int(parts[0]), int(parts[1])) if len(parts) == 2 else (1280, 720)

    export_dir = ROOT / "exports"
    export_dir.mkdir(exist_ok=True)

    rendered = 0
    errors = 0
    try:
        from core.database import get_modules, get_lectures
        from media.video.encoder import render_lecture

        for cid in course_ids:
            for mod in get_modules(cid):
                for lec in get_lectures(mod["id"]):
                    try:
                        lec_data = json.loads(lec.get("data") or "{}")
                        lec_data.setdefault("lecture_id", lec["id"])
                        lec_data.setdefault("title", lec["title"])
                        lec_data.setdefault("course_id", cid)
                        lec_data.setdefault("module_id", mod["id"])
                        render_lecture(lec_data, export_dir,
                                       fps=fps, width=w, height=h)
                        rendered += 1
                    except Exception as exc:
                        errors += 1
                        log_wizard_error("Video Production", "Render",
                                         f"{lec.get('title', 'unknown')}: {exc}")
    except Exception as exc:
        return False, f"Render pipeline failed: {exc}"

    data["rendered_count"] = rendered
    data["render_errors"] = errors
    msg = f"{rendered} lectures rendered"
    if errors:
        msg += f" ({errors} errors — see errors/ folder)"
    return rendered > 0 or errors == 0, msg


def _execute_summary(data: dict, key: str) -> tuple[bool, str]:
    rendered = data.get("rendered_count", 0)
    errors = data.get("render_errors", 0)
    export_dir = ROOT / "exports"

    # List recent renders
    mp4s = sorted(export_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime,
                  reverse=True) if export_dir.exists() else []
    recent = mp4s[:10]
    data["recent_renders"] = [
        {"name": p.name, "size_mb": round(p.stat().st_size / (1024 * 1024), 1)}
        for p in recent
    ]

    total_size = sum(p.stat().st_size for p in mp4s) / (1024 * 1024)
    return True, f"{len(mp4s)} total videos ({total_size:.1f} MB) | Latest render: {rendered} lectures"


# ---------------------------------------------------------------------------
# Wizard definition
# ---------------------------------------------------------------------------

def _build() -> WizardDef:
    return WizardDef(
        wizard_id=WIZARD_ID,
        title="Video Production",
        subtitle="Configure audio, video, VFX and render lecture videos",
        description=(
            "Complete video production wizard: choose TTS voice and binaural "
            "beats, set quality profiles (Draft → Final), configure all visual "
            "effects, select AI background provider, optionally enrich "
            "narrations, then batch render all selected courses to MP4."
        ),
        icon="[VID]",
        category="content",
        min_mode="student",
        steps=[
            WizardStep(
                key="voice",
                title="TTS Voice Configuration",
                description="Choose the neural voice for narration",
                execute=_execute_voice_config,
                group="Audio",
                fields=[
                    {"key": "tts_voice", "label": "Voice",
                     "type": "select", "default": "en-US-AriaNeural",
                     "options": [
                         "en-US-AriaNeural", "en-US-JennyNeural",
                         "en-US-AmberNeural", "en-US-EmmaNeural",
                         "en-US-GuyNeural", "en-US-BrianNeural",
                         "en-US-DavisNeural", "en-US-AndrewNeural",
                         "en-GB-SoniaNeural", "en-GB-RyanNeural",
                         "en-AU-NatashaNeural", "en-AU-WilliamNeural",
                         "en-CA-ClaraNeural",
                     ]},
                    {"key": "tts_rate", "label": "Speaking Rate",
                     "type": "select", "default": "+0%",
                     "options": ["-50%", "-25%", "+0%", "+25%", "+50%"]},
                    {"key": "tts_pitch", "label": "Pitch",
                     "type": "select", "default": "+0Hz",
                     "options": ["-50Hz", "-25Hz", "+0Hz", "+25Hz", "+50Hz"]},
                ],
            ),
            WizardStep(
                key="binaural",
                title="Binaural Beats",
                description="Choose background binaural beat frequency",
                execute=_execute_binaural_config,
                group="Audio",
                fields=[
                    {"key": "binaural_preset", "label": "Preset",
                     "type": "radio", "default": "none",
                     "options": ["none", "gamma", "beta", "alpha", "theta"]},
                ],
            ),
            WizardStep(
                key="quality",
                title="Quality Profile",
                description="Set video resolution, FPS, and quality level",
                execute=_execute_quality_profile,
                group="Video",
                fields=[
                    {"key": "quality_profile", "label": "Profile",
                     "type": "radio", "default": "balanced",
                     "options": ["draft", "balanced", "high", "final", "custom"]},
                    {"key": "video_fps", "label": "FPS (custom only)",
                     "type": "select", "default": 15,
                     "options": [10, 15, 24, 30]},
                    {"key": "video_resolution", "label": "Resolution (custom only)",
                     "type": "select", "default": "1280x720",
                     "options": ["960x540", "1280x720", "1920x1080"]},
                ],
            ),
            WizardStep(
                key="vfx",
                title="Visual Effects",
                description="Toggle individual VFX for video production",
                execute=_execute_vfx_config,
                group="Video",
                fields=[
                    {"key": "vfx_ai_backgrounds", "label": "AI-generated backgrounds",
                     "type": "toggle", "default": True},
                    {"key": "vfx_transitions", "label": "Scene transitions",
                     "type": "toggle", "default": True},
                    {"key": "vfx_ken_burns", "label": "Ken Burns pan/zoom",
                     "type": "toggle", "default": True},
                    {"key": "vfx_color_grading", "label": "Cinematic color grading",
                     "type": "toggle", "default": True},
                    {"key": "vfx_text_overlays", "label": "Title/term overlays",
                     "type": "toggle", "default": True},
                    {"key": "vfx_particles", "label": "Ambient particles",
                     "type": "toggle", "default": True},
                    {"key": "vfx_watermark", "label": "Watermark",
                     "type": "toggle", "default": False},
                ],
            ),
            WizardStep(
                key="image_provider",
                title="AI Background Provider",
                description="Select which image service generates backgrounds",
                execute=_execute_image_provider,
                group="Video",
                fields=[
                    {"key": "image_provider", "label": "Provider",
                     "type": "select", "default": "pollinations",
                     "options": ["pollinations", "huggingface", "github",
                                 "deepai", "prodia", "getimg", "stability",
                                 "leonardo", "limewire", "comfyui"]},
                ],
            ),
            WizardStep(
                key="select_courses",
                title="Select Courses to Render",
                description="Choose which courses to render",
                execute=_execute_select_courses,
                group="Render",
                fields=[
                    {"key": "render_all_courses", "label": "Render all courses",
                     "type": "toggle", "default": False},
                    {"key": "render_course_ids", "label": "Specific courses",
                     "type": "multiselect", "default": [],
                     "description": "Select individual courses"},
                ],
            ),
            WizardStep(
                key="pre_enrich",
                title="Pre-Render Enrichment",
                description="Optionally enrich narrations before rendering",
                execute=_execute_enrich_before_render,
                group="Render",
                optional=True,
                fields=[
                    {"key": "enrich_before_render", "label": "Enrich before render",
                     "type": "toggle", "default": False},
                    {"key": "rate_limit", "label": "Rate limit (seconds)",
                     "type": "slider", "default": 2.0, "min": 0.0, "max": 30.0},
                ],
            ),
            WizardStep(
                key="render",
                title="Batch Render",
                description="Render all selected lectures to MP4 video",
                execute=_execute_batch_render,
                group="Render",
            ),
            WizardStep(
                key="summary",
                title="Render Summary",
                description="View render results and output files",
                execute=_execute_summary,
                group="Results",
            ),
        ],
    )


def register():
    register_wizard(_build())
