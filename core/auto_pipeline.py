"""One-click auto pipeline engine for The God Factory University.

Orchestrates multi-step workflows (course creation, enrichment,
decomposition, jargon generation, flashcard creation, quiz generation,
and batch rendering) via a single function call with progress callbacks.
"""

from __future__ import annotations

import json
import time
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

EXPORT_DIR = Path("exports")

# ---------------------------------------------------------------------------
# Pipeline configuration
# ---------------------------------------------------------------------------

PRESET_FULL_BUILD = "full_build"
PRESET_DEEP_ENRICH = "deep_enrich"
PRESET_STUDY_PREP = "study_prep"
PRESET_FULL_RENDER = "full_render"
PRESET_CUSTOM = "custom"

PRESET_LABELS = {
    PRESET_FULL_BUILD: "Full Course Build",
    PRESET_DEEP_ENRICH: "Deep Enrichment Cycle",
    PRESET_STUDY_PREP: "Study Prep Package",
    PRESET_FULL_RENDER: "Full Render Pipeline",
    PRESET_CUSTOM: "Custom Pipeline",
}


@dataclass
class PipelineConfig:
    preset: str = PRESET_FULL_BUILD
    # Course creation
    topic: str = ""
    difficulty: str = "undergraduate"
    pacing: str = "standard"
    lectures_per_module: int = 3
    # Target courses (empty = create new, otherwise enrich/render existing)
    course_ids: list[str] = field(default_factory=list)
    # Steps toggles (for custom pipeline)
    do_generate: bool = True
    do_enrich: bool = True
    do_decompose: bool = True
    do_jargon: bool = True
    do_flashcards: bool = True
    do_quiz: bool = True
    do_render: bool = True
    # Rendering
    fps: int = 15
    resolution: str = "1280x720"
    # Rate limiting
    rate_limit: float = 2.0


@dataclass
class PipelineStatus:
    running: bool = False
    current_step: str = ""
    step_number: int = 0
    total_steps: int = 0
    log: list[str] = field(default_factory=list)
    error: str = ""
    created_course_ids: list[str] = field(default_factory=list)
    finished: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_resolution(res: str) -> tuple[int, int]:
    parts = res.split("x")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    return 1280, 720


def _log(status: PipelineStatus, msg: str, callback=None):
    status.log.append(msg)
    if callback:
        callback(status)


def _sleep(config: PipelineConfig):
    if config.rate_limit > 0:
        time.sleep(config.rate_limit)


# ---------------------------------------------------------------------------
# Step implementations
# ---------------------------------------------------------------------------

def _step_generate(config: PipelineConfig, status: PipelineStatus,
                   stop: Callable[[], bool], cb=None):
    """Generate a new course from topic via Professor AI."""
    _log(status, f"[GENERATE] Creating course: {config.topic}", cb)
    from llm.professor import Professor
    prof = Professor(session_id="auto_pipeline")
    resp = prof.chunked_curriculum(
        config.topic,
        level=config.difficulty,
        lectures_per_module=config.lectures_per_module,
    )
    if stop():
        return
    course_json = resp.parsed_json if resp.parsed_json else None
    if not course_json:
        _log(status, "[GENERATE] WARN: No structured JSON returned, trying raw parse", cb)
        try:
            course_json = json.loads(resp.raw_text)
        except Exception:
            status.error = "Course generation returned no valid JSON"
            _log(status, f"[GENERATE] ERROR: {status.error}", cb)
            return

    from core.database import bulk_import_json
    ids = bulk_import_json(course_json)
    if ids:
        status.created_course_ids.extend(ids)
        config.course_ids.extend(ids)
        _log(status, f"[GENERATE] OK — imported {len(ids)} course(s): {ids}", cb)
    else:
        _log(status, "[GENERATE] WARN: Import returned no IDs", cb)
    _sleep(config)


def _step_enrich(config: PipelineConfig, status: PipelineStatus,
                 stop: Callable[[], bool], cb=None):
    """Enrich narrations for all target courses."""
    from llm.tools_enrichment import enrich_course_narration
    for cid in config.course_ids:
        if stop():
            return
        _log(status, f"[ENRICH] Enriching course {cid}", cb)
        try:
            result = enrich_course_narration(cid)
            n = result.get("lectures_enriched", 0)
            _log(status, f"[ENRICH] OK — {n} lectures enriched in {cid}", cb)
        except Exception as exc:
            _log(status, f"[ENRICH] ERROR on {cid}: {exc}", cb)
        _sleep(config)


def _step_decompose(config: PipelineConfig, status: PipelineStatus,
                    stop: Callable[[], bool], cb=None):
    """Decompose target courses into sub-courses."""
    from llm.professor import Professor
    prof = Professor(session_id="auto_pipeline")
    new_ids: list[str] = []
    for cid in list(config.course_ids):
        if stop():
            return
        _log(status, f"[DECOMPOSE] Decomposing course {cid} (pacing={config.pacing})", cb)
        try:
            resp = prof.decompose_course(cid, pacing=config.pacing)
            pj = resp.parsed_json or {}
            sub_ids = pj.get("sub_course_ids", [])
            new_ids.extend(sub_ids)
            _log(status, f"[DECOMPOSE] OK — {len(sub_ids)} sub-courses from {cid}", cb)
        except Exception as exc:
            _log(status, f"[DECOMPOSE] ERROR on {cid}: {exc}", cb)
        _sleep(config)
    if new_ids:
        config.course_ids.extend(new_ids)
        status.created_course_ids.extend(new_ids)


def _step_jargon(config: PipelineConfig, status: PipelineStatus,
                 stop: Callable[[], bool], cb=None):
    """Generate jargon sub-courses."""
    from llm.professor import Professor
    prof = Professor(session_id="auto_pipeline")
    for cid in list(config.course_ids):
        if stop():
            return
        _log(status, f"[JARGON] Generating jargon course for {cid}", cb)
        try:
            resp = prof.generate_jargon_course(cid)
            pj = resp.parsed_json or {}
            jid = pj.get("jargon_course_id", "")
            if jid:
                config.course_ids.append(jid)
                status.created_course_ids.append(jid)
            _log(status, f"[JARGON] OK — jargon course {jid} from {cid}", cb)
        except Exception as exc:
            _log(status, f"[JARGON] ERROR on {cid}: {exc}", cb)
        _sleep(config)


def _step_flashcards(config: PipelineConfig, status: PipelineStatus,
                     stop: Callable[[], bool], cb=None):
    """Generate flashcards from all lectures in target courses."""
    from core.database import get_modules, get_lectures
    from core.university import generate_flashcards_from_lecture
    total = 0
    for cid in config.course_ids:
        if stop():
            return
        for mod in get_modules(cid):
            for lec in get_lectures(mod["id"]):
                if stop():
                    return
                try:
                    ids = generate_flashcards_from_lecture(lec["id"])
                    total += len(ids)
                except Exception:
                    pass
    _log(status, f"[FLASHCARDS] OK — {total} flashcards created", cb)


def _step_quiz(config: PipelineConfig, status: PipelineStatus,
               stop: Callable[[], bool], cb=None):
    """Generate quizzes for all lectures in target courses."""
    from core.database import get_modules, get_lectures
    from llm.tools_course import generate_quiz_for_lecture
    total = 0
    for cid in config.course_ids:
        if stop():
            return
        for mod in get_modules(cid):
            for lec in get_lectures(mod["id"]):
                if stop():
                    return
                _log(status, f"[QUIZ] Generating quiz for {lec['title'][:40]}", cb)
                try:
                    generate_quiz_for_lecture(lec["id"], num_questions=5)
                    total += 1
                except Exception as exc:
                    _log(status, f"[QUIZ] ERROR: {exc}", cb)
                _sleep(config)
    _log(status, f"[QUIZ] OK — {total} quizzes generated", cb)


def _step_render(config: PipelineConfig, status: PipelineStatus,
                 stop: Callable[[], bool], cb=None):
    """Batch render all lectures in target courses."""
    from core.database import get_modules, get_lectures
    from media.video.encoder import render_lecture
    EXPORT_DIR.mkdir(exist_ok=True)
    w, h = _parse_resolution(config.resolution)
    rendered = 0
    errors = 0
    for cid in config.course_ids:
        if stop():
            return
        for mod in get_modules(cid):
            for lec in get_lectures(mod["id"]):
                if stop():
                    return
                _log(status, f"[RENDER] Rendering {lec['title'][:50]}", cb)
                try:
                    lec_data = json.loads(lec.get("data") or "{}")
                    lec_data.setdefault("lecture_id", lec["id"])
                    lec_data.setdefault("title", lec["title"])
                    lec_data.setdefault("course_id", cid)
                    lec_data.setdefault("module_id", mod["id"])
                    render_lecture(lec_data, EXPORT_DIR,
                                  fps=config.fps, width=w, height=h)
                    rendered += 1
                    _log(status, f"[RENDER] OK — {lec['title'][:50]}", cb)
                except Exception as exc:
                    errors += 1
                    _log(status, f"[RENDER] ERROR: {exc}", cb)
    _log(status, f"[RENDER] Done — {rendered} rendered, {errors} errors", cb)


# ---------------------------------------------------------------------------
# Preset → step list mapping
# ---------------------------------------------------------------------------

def _steps_for_preset(config: PipelineConfig):
    """Return list of (label, func) tuples for the chosen preset."""
    if config.preset == PRESET_FULL_BUILD:
        steps = []
        steps.append(("Generate Course", _step_generate))
        steps.append(("Enrich Narrations", _step_enrich))
        steps.append(("Generate Jargon Course", _step_jargon))
        steps.append(("Render All Lectures", _step_render))
        return steps

    if config.preset == PRESET_DEEP_ENRICH:
        return [
            ("Enrich Narrations", _step_enrich),
            ("Decompose Courses", _step_decompose),
            ("Generate Jargon Courses", _step_jargon),
            ("Enrich Sub-courses", _step_enrich),
            ("Render All Lectures", _step_render),
        ]

    if config.preset == PRESET_STUDY_PREP:
        return [
            ("Generate Flashcards", _step_flashcards),
            ("Generate Quizzes", _step_quiz),
        ]

    if config.preset == PRESET_FULL_RENDER:
        steps = []
        steps.append(("Enrich Narrations", _step_enrich))
        steps.append(("Render All Lectures", _step_render))
        return steps

    # Custom: user picks steps
    steps = []
    if config.do_generate and config.topic:
        steps.append(("Generate Course", _step_generate))
    if config.do_enrich:
        steps.append(("Enrich Narrations", _step_enrich))
    if config.do_decompose:
        steps.append(("Decompose Courses", _step_decompose))
    if config.do_jargon:
        steps.append(("Generate Jargon Courses", _step_jargon))
    if config.do_flashcards:
        steps.append(("Generate Flashcards", _step_flashcards))
    if config.do_quiz:
        steps.append(("Generate Quizzes", _step_quiz))
    if config.do_render:
        steps.append(("Render All Lectures", _step_render))
    return steps


# ---------------------------------------------------------------------------
# Main pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(config: PipelineConfig,
                 stop_flag: Callable[[], bool] | None = None,
                 progress_callback: Callable[[PipelineStatus], None] | None = None
                 ) -> PipelineStatus:
    """Execute the pipeline synchronously.  Returns final status."""
    if stop_flag is None:
        stop_flag = lambda: False

    status = PipelineStatus(running=True)
    steps = _steps_for_preset(config)
    status.total_steps = len(steps)

    _log(status, f"Pipeline started: {PRESET_LABELS.get(config.preset, config.preset)} "
         f"({len(steps)} steps)", progress_callback)

    for i, (label, func) in enumerate(steps, 1):
        if stop_flag():
            _log(status, "Pipeline stopped by user", progress_callback)
            break
        status.step_number = i
        status.current_step = label
        _log(status, f"--- Step {i}/{len(steps)}: {label} ---", progress_callback)
        if progress_callback:
            progress_callback(status)
        try:
            func(config, status, stop_flag, progress_callback)
        except Exception as exc:
            status.error = str(exc)
            _log(status, f"FATAL: {exc}", progress_callback)
            break
        if status.error:
            break

    status.running = False
    status.finished = True
    _log(status, f"Pipeline finished. Courses: {status.created_course_ids}", progress_callback)
    if progress_callback:
        progress_callback(status)
    return status


def run_pipeline_async(config: PipelineConfig,
                       stop_flag: Callable[[], bool] | None = None,
                       progress_callback: Callable[[PipelineStatus], None] | None = None
                       ) -> tuple[PipelineStatus, threading.Thread]:
    """Launch the pipeline in a background thread.  Returns (status, thread)."""
    status_box: list[PipelineStatus] = [PipelineStatus()]

    def _worker():
        status_box[0] = run_pipeline(config, stop_flag, progress_callback)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return status_box[0], t
