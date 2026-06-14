"""
Settings — consolidated configuration hub.
Voice, binaural, video, deadlines, student profile, and more.
Organized into GitHub-style collapsible sections.
LLM deep configuration lives in pages/11_LLM_Setup.py.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.database import get_setting, save_setting
from core.tts_config import (
    format_pitch,
    format_rate,
    get_tts_settings,
    save_binaural_setting,
    save_tts_settings,
)
from core.settings_registry import CATEGORIES, settings_for_category, get_default
from ui.theme import inject_theme, gf_header, section_divider, play_sfx, help_button

inject_theme()
gf_header("Settings", "Calibrate your knowledge apparatus.")
help_button("voice-settings")

# ═══════════════════════════════  GENERAL  ═══════════════════════════════════
with st.expander("General", expanded=True):
    # Student identity
    student_name = st.text_input("Student name", value=get_setting("student_name", get_default("student_name")))
    if st.button("Save Name"):
        save_setting("student_name", student_name)
        play_sfx("click")
        st.success("Name saved.")

    # Interface theme (Appearance)
    THEME_LABELS = {
        "classic": "Classic — Dark Terminal (sharp, neon)",
        "glass": "Frosted Obsidian — Liquid Glass (translucent, blurred)",
    }
    cur_theme = get_setting("ui_theme", "classic")
    if cur_theme not in THEME_LABELS:
        cur_theme = "classic"
    sel_theme = st.selectbox(
        "Interface theme", list(THEME_LABELS.keys()),
        index=list(THEME_LABELS.keys()).index(cur_theme),
        format_func=lambda k: THEME_LABELS[k],
        help="Frosted Obsidian applies an Apple-style liquid-glass look over the dark-academic palette. "
             "Applies across every page.",
    )
    if sel_theme != cur_theme:
        save_setting("ui_theme", sel_theme)
        play_sfx("click")
        st.rerun()

    # Deadline system
    deadlines_on_val = get_setting("deadlines_enabled", "0") == "1"
    deadlines_toggle = st.toggle("Enable Deadlines", value=deadlines_on_val,
                                  help="Show countdown timers on assignments.")
    if deadlines_toggle != deadlines_on_val:
        save_setting("deadlines_enabled", "1" if deadlines_toggle else "0")
        play_sfx("click")
        st.rerun()
    if deadlines_toggle:
        st.caption("Deadline mode is ACTIVE. Assignments show due dates and countdown timers.")

    # Weekly quests
    quests_on_val = get_setting("quests_enabled", "1") == "1"
    quests_toggle = st.toggle("Enable Weekly Quests", value=quests_on_val,
                               help="Enable weekly learning quest challenges.")
    if quests_toggle != quests_on_val:
        save_setting("quests_enabled", "1" if quests_toggle else "0")
        play_sfx("click")
        st.rerun()

# ═══════════════════════════════  LLM & AI  ══════════════════════════════════
with st.expander("LLM & AI"):
    cur_llm = get_setting("llm_provider", "ollama")
    cur_model = get_setting("llm_model", "")
    st.markdown(f"**Current:** `{cur_llm}` / `{cur_model or 'not set'}`")
    st.page_link("pages/11_LLM_Setup.py", label="Open LLM Setup Wizard")
    st.caption("Full LLM configuration (provider, model, API keys, benchmarking) is managed in the LLM Setup page.")

# ═══════════════════════════════  VOICE & AUDIO  ═════════════════════════════
with st.expander("Voice & Audio"):
    help_button("voice-settings")

    VOICES = {
        "Aria (US, Female, Natural)":          "en-US-AriaNeural",
        "Jenny (US, Female, Conversational)":  "en-US-JennyNeural",
        "Amber (US, Female, Warm)":            "en-US-AmberNeural",
        "Emma (US, Female, Professional)":     "en-US-EmmaNeural",
        "Guy (US, Male, Warm)":                "en-US-GuyNeural",
        "Brian (US, Male, Deep)":              "en-US-BrianNeural",
        "Davis (US, Male, Casual)":            "en-US-DavisNeural",
        "Andrew (US, Male, Friendly)":         "en-US-AndrewNeural",
        "Sonia (UK, Female, Crisp)":           "en-GB-SoniaNeural",
        "Ryan (UK, Male, Professional)":       "en-GB-RyanNeural",
        "Natasha (AU, Female, Warm)":          "en-AU-NatashaNeural",
        "William (AU, Male, Steady)":          "en-AU-WilliamNeural",
        "Clara (CA, Female, Friendly)":        "en-CA-ClaraNeural",
    }

    tts_settings = get_tts_settings()
    current_voice_id = tts_settings["voice_id"]
    current_voice_label = next((k for k, v in VOICES.items() if v == current_voice_id), list(VOICES.keys())[0])
    selected_voice_label = st.selectbox("TTS Voice (edge-tts — Microsoft Neural)", list(VOICES.keys()),
                                         index=list(VOICES.keys()).index(current_voice_label))
    selected_voice_id = VOICES[selected_voice_label]

    vc1, vc2 = st.columns(2)
    with vc1:
        voice_rate = st.slider("Speaking rate", -50, 50, int(tts_settings["rate"]), step=5,
                                help="+N = faster, -N = slower")
    with vc2:
        voice_pitch = st.slider("Pitch", -50, 50, int(tts_settings["pitch"]), step=5)

    vb1, vb2 = st.columns(2)
    with vb1:
        if st.button("Preview Voice"):
            try:
                import asyncio, tempfile, os, edge_tts
                preview_text = "Greetings, scholar. Your journey through the God Factory begins now."
                rate_str = format_rate(voice_rate)
                pitch_str = format_pitch(voice_pitch)
                comm = edge_tts.Communicate(preview_text, selected_voice_id, rate=rate_str, pitch=pitch_str)
                tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                asyncio.run(comm.save(tmp.name))
                with open(tmp.name, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                os.unlink(tmp.name)
                play_sfx("click")
            except Exception as e:
                st.error(f"Voice preview failed: {e}")
    with vb2:
        if st.button("Save Voice Settings"):
            save_tts_settings(selected_voice_id, voice_rate, voice_pitch)
            play_sfx("success")
            st.success("Voice settings saved.")

    # Binaural beats
    st.divider()
    help_button("binaural-beats")
    st.caption("Binaural beats are stereo tones that modulate cognitive states. "
               "40Hz gamma supports focus; alpha (10Hz) supports relaxed absorption.")

    BINAURAL_PRESETS = {
        "None":                     None,
        "Gamma 40Hz — Peak Focus":  ("gamma_40hz",  200, 40),
        "Beta 18Hz — Active Study": ("beta_18hz",   200, 18),
        "Alpha 10Hz — Relaxed":     ("alpha_10hz",  200, 10),
        "Theta 6Hz — Creative":     ("theta_6hz",   200,  6),
    }
    current_binaural = str(tts_settings["binaural"])
    current_preset = next((label for label, value in BINAURAL_PRESETS.items()
                           if value and value[0] == current_binaural), "None")
    selected_preset = st.radio("Binaural Preset", list(BINAURAL_PRESETS.keys()),
                                index=list(BINAURAL_PRESETS.keys()).index(current_preset))

    bb1, bb2 = st.columns(2)
    with bb1:
        if st.button("Preview Binaural (10s)"):
            preset_data = BINAURAL_PRESETS[selected_preset]
            if preset_data is None:
                st.info("No binaural beats selected.")
            else:
                try:
                    from media.audio_engine import generate_binaural_wav
                    wav_bytes = generate_binaural_wav(10, base_freq=preset_data[1], beat_freq=preset_data[2])
                    st.audio(wav_bytes, format="audio/wav")
                except Exception as e:
                    st.error(f"Preview failed: {e}")
    with bb2:
        if st.button("Save Binaural Setting"):
            preset_value = BINAURAL_PRESETS[selected_preset]
            save_binaural_setting(preset_value[0] if preset_value else "none")
            play_sfx("click")
            st.success("Binaural preset saved.")

# ═══════════════════════════  VIDEO & RENDERING  ═════════════════════════════
with st.expander("Video & Rendering"):
    help_button("video-settings")

    QUALITY_PROFILES = {
        "Draft (Fast)": {"fps": 10, "res": "960x540"},
        "Balanced": {"fps": 15, "res": "960x540"},
        "High Quality": {"fps": 24, "res": "1280x720"},
        "Final (Slow)": {"fps": 24, "res": "1920x1080"},
        "Custom": None,
    }
    current_profile = get_setting("video_profile", "Balanced")
    profile = st.selectbox("Quality Profile", list(QUALITY_PROFILES.keys()),
                            index=list(QUALITY_PROFILES.keys()).index(current_profile)
                            if current_profile in QUALITY_PROFILES else 1)

    if profile != "Custom" and QUALITY_PROFILES[profile]:
        p = QUALITY_PROFILES[profile]
        fps = p["fps"]
        resolution = p["res"]
        st.caption(f"Profile: {fps}fps @ {resolution}")
    else:
        fps = st.select_slider("FPS", options=[10, 15, 24, 30],
                                value=int(get_setting("video_fps", "15")))
        resolution = st.selectbox("Resolution", ["960x540", "1280x720", "1920x1080"],
                                   index=["960x540", "1280x720", "1920x1080"].index(
                                       get_setting("video_resolution", "960x540")))

    render_provider = st.selectbox(
        "Render Engine",
        ["local", "comfyui", "free_cloud_mix", "custom_api"],
        index=["local", "comfyui", "free_cloud_mix", "custom_api"].index(
            get_setting("render_provider", "local")
            if get_setting("render_provider", "local") in ("local", "comfyui", "free_cloud_mix", "custom_api")
            else "local"
        ),
        format_func=lambda x: {"local": "Local (PIL Renderer)", "comfyui": "ComfyUI (Local Diffusion)",
                                "free_cloud_mix": "Free Cloud Mix (Auto-cycle)", "custom_api": "Custom API"}.get(x, x),
    )

    if render_provider == "custom_api":
        render_api_key = st.text_input("Custom API Key", value=get_setting("render_api_key", ""), type="password")
        save_setting("render_api_key", render_api_key)
    elif render_provider == "comfyui":
        st.caption("ComfyUI must be installed locally. See Library → Media Sources.")
    elif render_provider == "free_cloud_mix":
        st.caption("Uses free cloud services. Configure keys in Library → Media Sources.")

    if st.button("Save Video Settings"):
        save_setting("video_profile", profile)
        save_setting("video_fps", str(fps))
        w, h = resolution.split("x")
        save_setting("video_width", w)
        save_setting("video_height", h)
        save_setting("video_resolution", resolution)
        save_setting("render_provider", render_provider)
        play_sfx("click")
        st.success("Video settings saved.")

# ═══════════════════════════  IMAGE GENERATION  ══════════════════════════════
with st.expander("Image Generation"):
    st.caption("API keys for AI image providers. Configure in Library → Media Sources for full setup.")
    st.page_link("pages/01_Library.py", label="Open Media Sources Setup")

    img_keys = [s for s in settings_for_category("Image Generation")]
    for sdef in img_keys:
        val = get_setting(sdef.key, sdef.default)
        new_val = st.text_input(sdef.label, value=val, type="password", key=f"img_{sdef.key}")
        if new_val != val:
            save_setting(sdef.key, new_val)

# ══════════════════════════  COURSE & LEARNING  ══════════════════════════════
with st.expander("Course & Learning"):
    token_target = st.number_input("Daily Token Target",
                                    min_value=1000, max_value=500000, step=5000,
                                    value=int(get_setting("token_target", "50000")),
                                    help="How many tokens of content to aim for each day.")
    if st.button("Save Learning Settings"):
        save_setting("token_target", str(token_target))
        play_sfx("click")
        st.success("Learning settings saved.")

    prefs = st.text_area("Learning Preferences",
                          value=get_setting("student_preferences", ""),
                          help="Describe how you prefer to learn (e.g. 'I like analogies and hands-on examples').")
    if st.button("Save Preferences"):
        save_setting("student_preferences", prefs)
        play_sfx("click")
        st.success("Preferences saved.")

# ══════════════════════════════  ADVANCED  ════════════════════════════════════
with st.expander("Advanced"):
    share_mode = get_setting("share_generated_media", "private")
    share_options = ["private", "course_shared", "global"]
    share_labels = {"private": "Private (only you)", "course_shared": "Course Shared", "global": "Global"}
    new_share = st.radio("Media Sharing Mode",
                          share_options,
                          index=share_options.index(share_mode) if share_mode in share_options else 0,
                          format_func=lambda x: share_labels.get(x, x),
                          help="How generated images and media are shared.")
    if new_share != share_mode:
        save_setting("share_generated_media", new_share)
        play_sfx("click")
        st.rerun()
