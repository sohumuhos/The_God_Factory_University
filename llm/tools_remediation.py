"""Adaptive Re-Teach tools for the agent tool registry ('remediation' category).

Closes the detect -> act loop the app never closed: the system already DETECTS
weakness (audit/grading seed remediation_backlog) but never acted on it. These
tools let the controller mint a short remedial micro-lecture targeting a weakness
and mark the backlog item resolved. Remedial lectures live in a dedicated
auto-generated 'Remediation & Re-Teach' course, viewable/renderable like any other.

Writes are requires_review=True.
"""
from __future__ import annotations

import json
import re
import time

from llm.tool_registry import register

REMEDIATION_COURSE_ID = "REMEDIATION"
_REMEDIATION_MODULE_ID = f"{REMEDIATION_COURSE_ID}-M1"


def _ensure_container():
    """Ensure the remediation course + module exist; return (course_id, module_id)."""
    from core.database import get_course, upsert_course, get_modules, upsert_module
    if not get_course(REMEDIATION_COURSE_ID):
        upsert_course(
            REMEDIATION_COURSE_ID, "Remediation & Re-Teach",
            "Auto-generated remedial micro-lectures targeting your weak areas.",
            0, {"auto_generated": True}, source="remediation",
        )
    if not any(m["id"] == _REMEDIATION_MODULE_ID for m in get_modules(REMEDIATION_COURSE_ID)):
        upsert_module(_REMEDIATION_MODULE_ID, REMEDIATION_COURSE_ID, "Remedial Lectures", 0, {})
    return REMEDIATION_COURSE_ID, _REMEDIATION_MODULE_ID


def _next_order(module_id: str) -> int:
    from core.database import get_lectures
    try:
        return len(get_lectures(module_id))
    except Exception:
        return 0


def _author_micro_lecture(cfg, weakness: str):
    from llm.providers import simple_complete
    prompt = (
        f"A student is weak on: '{weakness}'. Write a SHORT remedial micro-lecture that "
        f"re-teaches just this concept from the ground up with one concrete example. "
        f"Output ONLY JSON: "
        '{"title":"...","learning_objectives":["..",".."],"core_terms":["..",".."],'
        '"narration":"150-250 word clear re-teaching script with an example"}'
    )
    raw = simple_complete(cfg, prompt) or ""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except Exception:
        return None
    if not obj.get("title") or not obj.get("narration"):
        return None
    return obj


@register(
    name="create_remedial_lecture",
    description=(
        "Mint a short remedial micro-lecture that re-teaches a specific weakness, "
        "stored in the auto-generated 'Remediation & Re-Teach' course. Optionally "
        "pass the remediation backlog item id to mark it resolved."
    ),
    parameters={
        "type": "object",
        "properties": {
            "weakness": {"type": "string", "description": "the concept to re-teach"},
            "course_id": {"type": "string", "description": "originating course (for linkage)"},
            "remediation_id": {"type": "integer", "description": "backlog item id to resolve"},
        },
        "required": ["weakness"],
    },
    category="remediation",
    requires_review=True,
)
def create_remedial_lecture(weakness: str, course_id: str = "", remediation_id: int = 0) -> dict:
    if not weakness or not str(weakness).strip():
        return {"error": "weakness is required"}
    from core.database import upsert_lecture, resolve_remediation_item
    from llm.providers import cfg_from_settings
    rcid, mid = _ensure_container()
    content = _author_micro_lecture(cfg_from_settings(), weakness)
    if not content:
        return {"error": "Could not author remedial lecture (LLM unavailable or invalid output)."}
    narration = content.get("narration", "")
    title = content.get("title", f"Remedial: {weakness[:40]}")
    lid = f"{mid}-R{int(time.time())}"
    lecture_data = {
        "title": title,
        "learning_objectives": content.get("learning_objectives", []),
        "core_terms": content.get("core_terms", []),
        "remedial_for": weakness,
        "source_course_id": course_id,
        "video_recipe": {"scene_blocks": [{
            "block_id": "A", "duration_s": 90,
            "narration_prompt": narration, "narration": narration,
            "visual_prompt": f"Clear educational diagram explaining {weakness}",
        }]},
    }
    try:
        upsert_lecture(lid, mid, rcid, title, 5, _next_order(mid), lecture_data)
    except Exception as exc:
        return {"error": f"Failed to save lecture: {exc}"}
    resolved = False
    if remediation_id:
        try:
            resolved = resolve_remediation_item(int(remediation_id))
        except Exception:
            resolved = False
    return {"lecture_id": lid, "course_id": rcid, "title": title,
            "remediation_resolved": resolved}


@register(
    name="resolve_remediation",
    description="Mark a remediation backlog item resolved (or another status) by its id.",
    parameters={
        "type": "object",
        "properties": {
            "remediation_id": {"type": "integer"},
            "status": {"type": "string", "description": "default 'resolved'"},
        },
        "required": ["remediation_id"],
    },
    category="remediation",
    requires_review=True,
)
def resolve_remediation(remediation_id: int, status: str = "resolved") -> dict:
    from core.database import resolve_remediation_item
    try:
        ok = resolve_remediation_item(int(remediation_id), status)
        return {"remediation_id": remediation_id, "status": status, "updated": ok}
    except Exception as exc:
        return {"error": str(exc)}
