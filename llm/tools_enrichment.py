"""Enrichment and progression tool definitions for the agent tool registry."""
from __future__ import annotations

from llm.tool_registry import register


@register(
    name="decompose_course",
    description="Decompose a course into deeper sub-courses. Creates child courses with more granular content.",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {"type": "string", "description": "ID of the course to decompose"},
        },
        "required": ["course_id"],
    },
    category="course",
)
def decompose_course(course_id: str) -> dict:
    from llm.professor import Professor
    prof = Professor()
    result = prof.decompose_course(course_id)
    if hasattr(result, "text"):
        return {"status": "ok", "result": result.text[:500]}
    return {"status": "ok", "result": str(result)[:500]}


@register(
    name="generate_jargon_course",
    description="Generate a jargon/terminology sub-course for a course. Extracts key terms and creates a focused vocabulary course.",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {"type": "string", "description": "ID of the parent course"},
        },
        "required": ["course_id"],
    },
    category="course",
)
def generate_jargon_course(course_id: str) -> dict:
    from llm.professor import Professor
    prof = Professor()
    result = prof.generate_jargon_course(course_id)
    if hasattr(result, "text"):
        return {"status": "ok", "result": result.text[:500]}
    return {"status": "ok", "result": str(result)[:500]}


@register(
    name="enrich_course_narration",
    description="Enrich all lecture narrations in a course using the LLM. Rewrites narration to be richer and more educational. Each enrichment is versioned.",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {"type": "string", "description": "ID of the course to enrich"},
        },
        "required": ["course_id"],
    },
    category="course",
)
def enrich_course_narration(course_id: str) -> dict:
    import json
    from core.database import get_course, get_modules, get_lectures, update_lecture_data
    from core.content_log import log_generated_content, get_covered_topics
    from core.continuous_engine import save_version
    from llm.providers import simple_complete, cfg_from_settings

    course = get_course(course_id)
    if not course:
        return {"status": "error", "message": f"Course {course_id} not found"}

    cfg = cfg_from_settings()
    enriched = 0
    covered = get_covered_topics(course_id, max_topics=100)
    covered_str = ", ".join(covered[-30:]) if covered else "none yet"

    for mod in get_modules(course_id):
        for lec in get_lectures(mod["id"]):
            data = json.loads(lec.get("data") or "{}")
            recipe = data.get("video_recipe", {})
            scenes = recipe.get("scene_blocks", [])
            if not scenes:
                continue
            for scene in scenes:
                narr = scene.get("narration_prompt", "")
                dur = scene.get("duration_s", 60)
                word_target = int(dur * 2.5)
                save_version(course_id, str(lec["id"]), narr, enrichment_type="pre_enrich")
                prompt = (
                    f"Rewrite this narration to be richer and more educational (~{word_target} words).\n"
                    f"Course: {course.get('title','')}\nLecture: {lec.get('title','')}\n"
                    f"Already covered: {covered_str}\n"
                    f"Original: {narr}\n\n"
                    f"ACTUALLY TEACH the subject. Give real examples, define terms, explain step by step. "
                    f"Do NOT use markdown. Output ONLY plain narration text."
                )
                result = simple_complete(cfg, prompt)
                if result and not result.startswith("[LLM ERROR]") and not result.startswith("[ERROR]") and len(result.split()) > 20:
                    scene["narration_prompt"] = result.strip()
                    save_version(course_id, str(lec["id"]), result.strip(), enrichment_type="llm_enrich")
            data["video_recipe"]["scene_blocks"] = scenes
            update_lecture_data(lec["id"], data)
            enriched += 1
            log_generated_content(course_id, course_id, "enrich", [lec.get("title", "")])

    return {"status": "ok", "lectures_enriched": enriched}


@register(
    name="advance_course_level",
    description="Advance a course to the next education depth level. Higher levels provide more sophisticated content.",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {"type": "string", "description": "ID of the course to advance"},
        },
        "required": ["course_id"],
    },
    category="course",
)
def advance_course_level(course_id: str) -> dict:
    from core.database import get_course, tx
    from core.content_log import log_generated_content

    course = get_course(course_id)
    if not course:
        return {"status": "error", "message": f"Course {course_id} not found"}

    current = course.get("depth_level") or 0
    new_level = current + 1
    with tx() as con:
        con.execute("UPDATE courses SET depth_level = ? WHERE id = ?", (new_level, course_id))
    log_generated_content(course_id, course_id, "level_advance",
                          [f"level_{current}_to_{new_level}"], level=new_level)
    return {"status": "ok", "course_id": course_id, "old_level": current, "new_level": new_level}


@register(
    name="batch_render_course",
    description="Render all lectures in a course as MP4 video files.",
    parameters={
        "type": "object",
        "properties": {
            "course_id": {"type": "string", "description": "ID of the course to render"},
        },
        "required": ["course_id"],
    },
    category="video",
)
def batch_render_course(course_id: str) -> dict:
    import json
    from pathlib import Path
    from core.database import get_course, get_modules, get_lectures
    from media.video.encoder import render_lecture

    course = get_course(course_id)
    if not course:
        return {"status": "error", "message": f"Course {course_id} not found"}

    output_dir = Path(__file__).resolve().parent.parent / "exports"
    rendered = 0
    errors = []
    for mod in get_modules(course_id):
        for lec in get_lectures(mod["id"]):
            data = json.loads(lec.get("data") or "{}")
            data.setdefault("lecture_id", lec["id"])
            data.setdefault("title", lec["title"])
            data.setdefault("course_id", course_id)
            try:
                render_lecture(data, output_dir)
                rendered += 1
            except Exception as e:
                errors.append(f"{lec['title']}: {e}")

    return {"status": "ok", "rendered": rendered, "errors": errors[:5]}
