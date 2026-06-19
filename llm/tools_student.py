"""Student-state read tools for the agent tool registry.

These are read-only "grounding" tools: they let the controller see who the
student is — progress, mastery, weakness backlog, and prior conversation —
before it decides what to do. Every wrapped function is already exported as a
plain callable from ``core.database``; the handlers are thin and side-effect
free, so they are registered in the existing ``utility`` category (no agent
config change needed) and never require review.
"""
from __future__ import annotations

from llm.tool_registry import register


@register(
    name="get_student_state",
    description=(
        "Get the student's world state: study hours, days enrolled, active days, "
        "and how long they have been idle. Use this to decide whether to nudge, "
        "review, or advance the student."
    ),
    parameters={"type": "object", "properties": {}, "required": []},
    category="utility",
)
def get_student_state() -> dict:
    from core.database import get_student_world_state
    try:
        return get_student_world_state()
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


@register(
    name="get_academic_progress",
    description=(
        "Get the student's academic progress summary: verified credits, activity "
        "credits, completed courses, and verified assessments. Use before grading, "
        "enrolling in a program, or recommending next steps."
    ),
    parameters={"type": "object", "properties": {}, "required": []},
    category="utility",
)
def get_academic_progress() -> dict:
    from core.database import get_academic_progress_summary
    try:
        return get_academic_progress_summary()
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


@register(
    name="get_competency_profile",
    description=(
        "Get the student's competency profile for a specific course: mastery per "
        "topic / Bloom's level. Use to find weak spots before re-teaching or testing."
    ),
    parameters={
        "type": "object",
        "properties": {"course_id": {"type": "string"}},
        "required": ["course_id"],
    },
    category="utility",
)
def get_competency_profile(course_id: str) -> dict:
    from core.database import get_competency_profile as _get
    try:
        return _get(course_id)
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


@register(
    name="get_remediation_backlog",
    description=(
        "List the student's open remediation items (concepts they failed or scored "
        "low on). Each item names a weakness to address. Use to drive re-teaching."
    ),
    parameters={
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "open | resolved (default open)"},
            "limit": {"type": "integer", "description": "max items (default 20)"},
        },
        "required": [],
    },
    category="utility",
)
def get_remediation_backlog(status: str = "open", limit: int = 20) -> dict:
    from core.database import list_remediation_backlog
    try:
        items = list_remediation_backlog(status, limit)
        return {"count": len(items), "items": items}
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


@register(
    name="search_chat_history",
    description=(
        "Search prior Professor conversation for messages containing a keyword. "
        "Use to recall what the student previously asked or was told."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "session_id": {"type": "string", "description": "chat session (default 'default')"},
            "limit": {"type": "integer", "description": "messages to scan (default 200)"},
        },
        "required": ["query"],
    },
    category="utility",
)
def search_chat_history(query: str, session_id: str = "default", limit: int = 200) -> dict:
    from core.database import get_chat
    try:
        rows = get_chat(session_id, limit=limit)
        q = (query or "").lower()
        matches = [
            {"role": r["role"], "content": (r["content"] or "")[:500]}
            for r in rows
            if q in (r["content"] or "").lower()
        ]
        return {"query": query, "count": len(matches), "matches": matches}
    except Exception as exc:  # pragma: no cover - defensive
        return {"error": str(exc)}


# ─── Agent grounding helper ───────────────────────────────────────────────────

def build_student_state_block() -> str:
    """Compact student-state summary injected into the agent's system prompt.

    Mirrors ``ProfessorBaseMixin._student_context_block`` so the autonomous agent
    is grounded in the same context the chat Professor sees, before it calls any
    read tool. Best-effort: returns an empty string on any failure.
    """
    try:
        from core.database import (
            get_student_world_state,
            get_academic_progress_summary,
            list_remediation_backlog,
        )
        world = get_student_world_state()
        academic = get_academic_progress_summary()
        backlog = list_remediation_backlog(limit=5)
    except Exception:
        return ""

    lines = [
        "Current student state (for grounding — use read tools for detail):",
        f"- Verified credits: {academic.get('official_credits', 0):.2f}",
        f"- Completed courses: {academic.get('completed_courses', 0)}",
        f"- Verified assessments: {academic.get('verified_assessments', 0)}",
        f"- Study hours: {world.get('study_hours', 0.0):.1f}",
        f"- Active days: {world.get('active_days', 0)}",
    ]
    idle_days = world.get("idle_days")
    if idle_days is not None:
        lines.append(f"- Idle for ~{idle_days:.2f} days")
    weaknesses = [item.get("weakness", "") for item in (backlog or []) if item.get("weakness")]
    if weaknesses:
        lines.append("- Weakness backlog: " + "; ".join(weaknesses[:5]))
    return "\n".join(lines)
