"""24/7 Continuous Enrichment Engine for The God Factory University.

Runs an in-session loop that enriches course lectures, optionally
decomposes courses into sub-courses, generates jargon courses, and
advances education levels automatically.

All enrichment passes are versioned — prior narration is never lost.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core.database import (
    get_all_courses,
    get_course,
    get_lectures,
    get_modules,
    get_setting,
    save_setting,
    update_lecture_data,
    tx,
)
from core.content_log import log_generated_content, get_covered_topics, get_level_count
from core.logger import log_error

DB_PATH = Path(__file__).resolve().parent.parent / "university.db"

# ── Enrichment version tracking ──────────────────────────────────────────────

def _ensure_version_table() -> None:
    """Create the enrichment_versions table if it doesn't exist."""
    import sqlite3
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS enrichment_versions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id       TEXT NOT NULL,
                lecture_id      TEXT NOT NULL,
                version_num     INTEGER NOT NULL,
                narration_snapshot TEXT NOT NULL,
                created_at      REAL NOT NULL,
                parent_version  INTEGER,
                enrichment_type TEXT DEFAULT 'llm_enrich'
            )
        """)
        con.execute("""
            CREATE INDEX IF NOT EXISTS idx_ev_course
            ON enrichment_versions(course_id, lecture_id)
        """)
        con.commit()
    finally:
        con.close()


def _next_version(course_id: str, lecture_id: str) -> int:
    """Get the next version number for a lecture."""
    import sqlite3
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        row = con.execute(
            "SELECT MAX(version_num) FROM enrichment_versions WHERE course_id=? AND lecture_id=?",
            (course_id, lecture_id),
        ).fetchone()
        return (row[0] or 0) + 1
    finally:
        con.close()


def save_version(course_id: str, lecture_id: str,
                 narration_snapshot: str, enrichment_type: str = "llm_enrich") -> int:
    """Save a new enrichment version. Returns the version number."""
    import sqlite3
    ver = _next_version(course_id, lecture_id)
    parent = ver - 1 if ver > 1 else None
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    try:
        con.execute(
            "INSERT INTO enrichment_versions "
            "(course_id, lecture_id, version_num, narration_snapshot, created_at, parent_version, enrichment_type) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (course_id, lecture_id, ver, narration_snapshot, time.time(), parent, enrichment_type),
        )
        con.commit()
        return ver
    finally:
        con.close()


def get_versions(course_id: str, lecture_id: str) -> list[dict]:
    """Get all enrichment versions for a lecture, newest first."""
    import sqlite3
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            "SELECT * FROM enrichment_versions WHERE course_id=? AND lecture_id=? ORDER BY version_num DESC",
            (course_id, lecture_id),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


# ── Engine configuration ─────────────────────────────────────────────────────

@dataclass
class ContinuousConfig:
    """Settings for the continuous enrichment loop."""
    jargon_per_cycle: int = 1
    enrichments_before_decompose: int = 3
    decompositions_before_level_advance: int = 2
    auto_render: bool = False
    rate_limit_s: float = 2.0
    target_course_ids: list[str] = field(default_factory=list)


@dataclass
class CycleProgress:
    """Progress state reported each cycle."""
    cycle: int = 0
    total_enrichments: int = 0
    total_decompositions: int = 0
    total_jargon: int = 0
    level_advances: int = 0
    current_action: str = ""
    errors: list[str] = field(default_factory=list)
    running: bool = True


# ── Core engine ──────────────────────────────────────────────────────────────

def run_continuous(
    config: ContinuousConfig,
    stop_flag: Callable[[], bool],
    progress_callback: Callable[[CycleProgress], None] | None = None,
) -> CycleProgress:
    """Run the continuous enrichment loop until stop_flag() returns True.

    Each cycle:
      1. Enrich all lectures in target courses (versioned)
      2. Every N enrichments, decompose courses into sub-courses
      3. Every decompose cycle, generate jargon courses
      4. After M decompositions, advance to next education level
    """
    _ensure_version_table()
    from llm.providers import simple_complete, cfg_from_settings

    progress = CycleProgress()
    enrichment_count_this_level = 0
    decompose_count_this_level = 0

    courses = _resolve_courses(config.target_course_ids)
    if not courses:
        progress.current_action = "No courses to enrich"
        progress.running = False
        if progress_callback:
            progress_callback(progress)
        return progress

    while not stop_flag():
        progress.cycle += 1
        progress.current_action = f"Cycle {progress.cycle}: enriching lectures"
        if progress_callback:
            progress_callback(progress)

        # ── Step 1: Enrich all lectures ──────────────────────────────────
        cfg = cfg_from_settings()
        for course in courses:
            if stop_flag():
                break
            cid = str(course["id"])
            modules = get_modules(cid)
            for mod in modules:
                if stop_flag():
                    break
                for lec in get_lectures(mod["id"]):
                    if stop_flag():
                        break
                    try:
                        _enrich_lecture(cfg, course, lec, simple_complete)
                        progress.total_enrichments += 1
                    except Exception as e:
                        err = f"Enrich {lec.get('title','?')}: {e}"
                        progress.errors.append(err)
                        log_error(err, category="continuous", error_id="ENRICH_FAIL")
                    time.sleep(config.rate_limit_s)

        enrichment_count_this_level += 1

        # ── Step 2: Decompose check ─────────────────────────────────────
        if enrichment_count_this_level >= config.enrichments_before_decompose:
            enrichment_count_this_level = 0
            progress.current_action = f"Cycle {progress.cycle}: decomposing courses"
            if progress_callback:
                progress_callback(progress)

            for course in courses:
                if stop_flag():
                    break
                try:
                    _decompose_course(course)
                    progress.total_decompositions += 1
                    decompose_count_this_level += 1
                except Exception as e:
                    err = f"Decompose {course.get('title','?')}: {e}"
                    progress.errors.append(err)
                    log_error(err, category="continuous", error_id="DECOMPOSE_FAIL")
                time.sleep(config.rate_limit_s)

            # ── Step 2b: Jargon courses ──────────────────────────────────
            for _ in range(config.jargon_per_cycle):
                if stop_flag():
                    break
                for course in courses:
                    if stop_flag():
                        break
                    try:
                        _generate_jargon(course)
                        progress.total_jargon += 1
                    except Exception as e:
                        err = f"Jargon {course.get('title','?')}: {e}"
                        progress.errors.append(err)
                    time.sleep(config.rate_limit_s)

        # ── Step 3: Level advancement check ──────────────────────────────
        if decompose_count_this_level >= config.decompositions_before_level_advance:
            decompose_count_this_level = 0
            progress.current_action = f"Cycle {progress.cycle}: advancing level"
            if progress_callback:
                progress_callback(progress)
            for course in courses:
                if stop_flag():
                    break
                try:
                    _advance_level(course)
                    progress.level_advances += 1
                except Exception as e:
                    err = f"Level advance {course.get('title','?')}: {e}"
                    progress.errors.append(err)

        # ── Optional auto-render ─────────────────────────────────────────
        if config.auto_render and not stop_flag():
            progress.current_action = f"Cycle {progress.cycle}: rendering"
            if progress_callback:
                progress_callback(progress)
            try:
                _auto_render(courses)
            except Exception as e:
                progress.errors.append(f"Auto-render: {e}")

        # Refresh course list (decompose may have created new sub-courses)
        courses = _resolve_courses(config.target_course_ids)
        if progress_callback:
            progress_callback(progress)

    progress.running = False
    progress.current_action = "Stopped"
    if progress_callback:
        progress_callback(progress)
    return progress


# ── Internal helpers ─────────────────────────────────────────────────────────

def _resolve_courses(target_ids: list[str]) -> list[dict]:
    """Resolve target course IDs to course dicts. Empty = all courses."""
    if target_ids:
        return [c for cid in target_ids if (c := get_course(cid))]
    return get_all_courses()


def _enrich_lecture(cfg, course: dict, lec: dict, llm_call) -> None:
    """Enrich a single lecture's narration and save a version."""
    data = json.loads(lec.get("data") or "{}")
    cid = str(course["id"])
    lid = str(lec["id"])
    recipe = data.get("video_recipe", {})
    scenes = recipe.get("scene_blocks", [])
    if not scenes:
        return

    covered = get_covered_topics(cid, max_topics=100)
    covered_str = ", ".join(covered[-30:]) if covered else "none yet"

    for scene in scenes:
        narr = scene.get("narration_prompt", "")
        dur = scene.get("duration_s", 60)
        word_target = int(dur * 2.5)

        # Save current narration as a version before overwriting
        save_version(cid, lid, narr, enrichment_type="pre_enrich")

        prompt = (
            f"Rewrite this narration to be richer and more educational (~{word_target} words).\n"
            f"Course: {course.get('title','')}\nLecture: {lec.get('title','')}\n"
            f"Already covered topics (do NOT repeat): {covered_str}\n"
            f"Original: {narr}\n\n"
            f"ACTUALLY TEACH the subject. Give real examples, define terms, explain step by step. "
            f"Do NOT use markdown or formatting. Output ONLY plain narration text."
        )
        result = llm_call(cfg, prompt)
        if result and not result.startswith("[LLM ERROR]") and not result.startswith("[ERROR]") and len(result.split()) > 20:
            scene["narration_prompt"] = result.strip()
            save_version(cid, lid, result.strip(), enrichment_type="llm_enrich")

    data["video_recipe"]["scene_blocks"] = scenes
    update_lecture_data(lid, data)
    log_generated_content(cid, cid, "enrich", [lec.get("title", "")])


def _decompose_course(course: dict) -> None:
    """Trigger decomposition for a course via Professor workflows."""
    from llm.professor import Professor
    prof = Professor()
    prof.decompose_course(str(course["id"]))


def _generate_jargon(course: dict) -> None:
    """Generate a jargon sub-course for a course."""
    from llm.professor import Professor
    prof = Professor()
    prof.generate_jargon_course(str(course["id"]))


def _advance_level(course: dict) -> None:
    """Advance a course to the next education level (depth_level)."""
    cid = str(course["id"])
    current = course.get("depth_level") or 0
    with tx() as con:
        con.execute(
            "UPDATE courses SET depth_level = ? WHERE id = ?",
            (current + 1, cid),
        )
    log_generated_content(cid, cid, "level_advance", [f"level_{current}_to_{current + 1}"], level=current + 1)


def _auto_render(courses: list[dict]) -> None:
    """Render all lectures for the given courses."""
    from media.video.encoder import render_lecture
    output_dir = Path(__file__).resolve().parent.parent / "exports"
    for course in courses:
        cid = str(course["id"])
        for mod in get_modules(cid):
            for lec in get_lectures(mod["id"]):
                data = json.loads(lec.get("data") or "{}")
                data.setdefault("lecture_id", lec["id"])
                data.setdefault("title", lec["title"])
                data.setdefault("course_id", cid)
                try:
                    render_lecture(data, output_dir)
                except Exception:
                    pass
