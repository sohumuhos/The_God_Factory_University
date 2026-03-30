"""
Auto Pipeline — one-click automated workflows that bypass manual navigation.
Select a preset (Full Course Build, Deep Enrichment, Study Prep, Full Render,
or Custom) and the pipeline handles every step automatically.
"""

import json
import sys
import time
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.database import get_all_courses
from core.auto_pipeline import (
    PipelineConfig, PipelineStatus,
    PRESET_FULL_BUILD, PRESET_DEEP_ENRICH, PRESET_STUDY_PREP,
    PRESET_FULL_RENDER, PRESET_CUSTOM, PRESET_LABELS,
    run_pipeline,
)
from ui.theme import inject_theme, gf_header, section_divider, stat_card, help_button

inject_theme()
gf_header("Auto Pipeline", "One-click automated workflows — skip the navigation.")
help_button("auto-pipeline")

# ───────────────────────────────────────────────────────────────────────────────
# Session state init
# ───────────────────────────────────────────────────────────────────────────────
if "ap_status" not in st.session_state:
    st.session_state.ap_status = None
if "ap_stop" not in st.session_state:
    st.session_state.ap_stop = False
if "ap_running" not in st.session_state:
    st.session_state.ap_running = False

# ───────────────────────────────────────────────────────────────────────────────
# Preset selector
# ───────────────────────────────────────────────────────────────────────────────
section_divider("Choose Pipeline Preset")

preset = st.radio(
    "Pipeline preset",
    options=[PRESET_FULL_BUILD, PRESET_DEEP_ENRICH, PRESET_STUDY_PREP,
             PRESET_FULL_RENDER, PRESET_CUSTOM],
    format_func=lambda k: PRESET_LABELS[k],
    horizontal=True,
    label_visibility="collapsed",
)

DESCRIPTIONS = {
    PRESET_FULL_BUILD: (
        "**Generate → Enrich → Jargon → Render**  \n"
        "Enter a topic and the pipeline creates a complete course, "
        "enriches all narrations, generates a jargon sub-course, "
        "and renders every lecture to MP4."
    ),
    PRESET_DEEP_ENRICH: (
        "**Enrich → Decompose → Jargon → Enrich Sub-courses → Render**  \n"
        "Select existing courses. The pipeline enriches narrations, "
        "decomposes into sub-courses, generates jargon courses, "
        "enriches the new sub-courses, and renders everything."
    ),
    PRESET_STUDY_PREP: (
        "**Flashcards → Quizzes**  \n"
        "Select courses. Generates SM-2 flashcards from all lectures "
        "and creates quizzes for each lecture."
    ),
    PRESET_FULL_RENDER: (
        "**Enrich → Render**  \n"
        "Select courses. Enriches narrations if needed, then "
        "batch renders all lectures to MP4."
    ),
    PRESET_CUSTOM: (
        "**Pick your own steps**  \n"
        "Toggle individual pipeline stages on or off."
    ),
}
st.info(DESCRIPTIONS.get(preset, ""))

# ───────────────────────────────────────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────────────────────────────────────
section_divider("Pipeline Configuration")

config = PipelineConfig(preset=preset)

# ── Topic input (for presets that generate) ──
needs_topic = preset in (PRESET_FULL_BUILD, PRESET_CUSTOM)
if needs_topic:
    config.topic = st.text_input(
        "Course topic",
        placeholder="e.g. Introduction to Machine Learning",
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        config.difficulty = st.selectbox(
            "Difficulty", ["elementary", "high_school", "undergraduate",
                           "graduate", "doctoral"],
            index=2,
        )
    with c2:
        config.pacing = st.selectbox("Pacing", ["fast", "standard", "slow"], index=1)
    with c3:
        config.lectures_per_module = st.number_input(
            "Lectures per module", min_value=1, max_value=10, value=3,
        )

# ── Course selector (for presets that work on existing courses) ──
needs_courses = preset in (PRESET_DEEP_ENRICH, PRESET_STUDY_PREP,
                           PRESET_FULL_RENDER, PRESET_CUSTOM)
if needs_courses:
    courses = get_all_courses()
    if courses:
        options = {f"{c['id']} — {c['title']}": c["id"] for c in courses}
        selected = st.multiselect(
            "Target courses",
            options=list(options.keys()),
            default=list(options.keys())[:1] if len(options) == 1 else [],
        )
        config.course_ids = [options[s] for s in selected]
    else:
        st.warning("No courses in database. Use **Full Course Build** to create one first.")

# ── Custom step toggles ──
if preset == PRESET_CUSTOM:
    st.markdown("**Select steps to run:**")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        config.do_generate = st.checkbox("Generate Course", value=bool(config.topic))
        config.do_enrich = st.checkbox("Enrich Narrations", value=True)
    with c2:
        config.do_decompose = st.checkbox("Decompose", value=True)
        config.do_jargon = st.checkbox("Jargon Course", value=True)
    with c3:
        config.do_flashcards = st.checkbox("Flashcards", value=True)
        config.do_quiz = st.checkbox("Quizzes", value=True)
    with c4:
        config.do_render = st.checkbox("Render Video", value=True)

# ── Render settings ──
with st.expander("Render & Rate Settings", expanded=False):
    r1, r2, r3 = st.columns(3)
    with r1:
        config.fps = st.selectbox("FPS", [10, 15, 24, 30], index=1)
    with r2:
        config.resolution = st.selectbox(
            "Resolution", ["960x540", "1280x720", "1920x1080"], index=1,
        )
    with r3:
        config.rate_limit = st.slider("Rate limit (sec)", 0.0, 10.0, 2.0, 0.5)

# ───────────────────────────────────────────────────────────────────────────────
# Validation
# ───────────────────────────────────────────────────────────────────────────────
can_run = True
if needs_topic and not config.topic and preset == PRESET_FULL_BUILD:
    can_run = False
if needs_courses and not config.course_ids and preset != PRESET_FULL_BUILD:
    can_run = False

# ───────────────────────────────────────────────────────────────────────────────
# Launch / Stop
# ───────────────────────────────────────────────────────────────────────────────
section_divider("Run Pipeline")

col_run, col_stop = st.columns(2)

with col_run:
    run_clicked = st.button(
        f"▶  Launch Pipeline ({PRESET_LABELS[preset]})",
        disabled=(not can_run or st.session_state.ap_running),
        use_container_width=True,
        type="primary",
    )

with col_stop:
    stop_clicked = st.button(
        "■  Stop Pipeline",
        disabled=not st.session_state.ap_running,
        use_container_width=True,
    )

if stop_clicked:
    st.session_state.ap_stop = True
    st.toast("Stop signal sent — pipeline will halt after current step.")

if run_clicked and can_run:
    st.session_state.ap_stop = False
    st.session_state.ap_running = True

    progress_bar = st.progress(0, text="Starting pipeline...")
    log_area = st.empty()
    status_area = st.empty()

    def _progress_cb(status: PipelineStatus):
        if status.total_steps > 0:
            pct = status.step_number / status.total_steps
            progress_bar.progress(min(pct, 1.0), text=status.current_step)

    def _stop_check() -> bool:
        return st.session_state.ap_stop

    try:
        final_status = run_pipeline(config, stop_flag=_stop_check,
                                    progress_callback=_progress_cb)
        st.session_state.ap_status = final_status
    except Exception as exc:
        st.error(f"Pipeline failed: {exc}")
        final_status = PipelineStatus(error=str(exc), finished=True)
        st.session_state.ap_status = final_status
    finally:
        st.session_state.ap_running = False
        progress_bar.progress(1.0, text="Done")

# ───────────────────────────────────────────────────────────────────────────────
# Results display
# ───────────────────────────────────────────────────────────────────────────────
status: PipelineStatus | None = st.session_state.ap_status

if status and status.finished:
    section_divider("Pipeline Results")

    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Steps Completed", f"{status.step_number}/{status.total_steps}")
    with c2:
        stat_card("Courses Created", str(len(status.created_course_ids)))
    with c3:
        flag = "[OK]" if not status.error else "[ERR]"
        stat_card("Status", flag)

    if status.error:
        st.error(f"Pipeline error: {status.error}")

    if status.created_course_ids:
        st.markdown("**Created course IDs:** " + ", ".join(
            f"`{cid}`" for cid in status.created_course_ids))

    with st.expander("Full Pipeline Log", expanded=True):
        st.code("\n".join(status.log), language="log")

elif status and not status.finished:
    st.info("Pipeline is running...")
    if status.log:
        with st.expander("Live Log", expanded=True):
            st.code("\n".join(status.log[-20:]), language="log")
