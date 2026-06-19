"""Grading tools for the agent tool registry ('grading' category).

These give the controller authority over the academic ledger: grade work with
the Professor, record scores (auto-seeding remediation on weak performance,
mirroring Professor.audit_packet), and read GPA / degree eligibility. Mutating
tools are marked requires_review=True so they pass through the agent's draft
queue when run in REVIEW mode.
"""
from __future__ import annotations

from llm.tool_registry import register


def _grade_resp_to_dict(resp) -> dict:
    grade = getattr(resp, "parsed_json", None)
    warnings = getattr(resp, "warnings", []) or []
    if isinstance(grade, dict) and grade:
        return {"grade": grade, "warnings": warnings}
    return {"raw": (getattr(resp, "raw_text", "") or str(resp))[:2000], "warnings": warnings}


@register(
    name="grade_essay",
    description=(
        "Grade a student essay with the Professor. Returns a structured grade "
        "(score, letter, strengths, improvements, feedback). Does NOT record it — "
        "call record_grade to persist."
    ),
    parameters={
        "type": "object",
        "properties": {
            "essay_text": {"type": "string"},
            "rubric": {"type": "string", "description": "optional grading rubric"},
        },
        "required": ["essay_text"],
    },
    category="grading",
)
def grade_essay(essay_text: str, rubric: str = "") -> dict:
    try:
        from llm.professor import Professor
        resp = Professor(session_id="agent_grading").grade_essay(essay_text, rubric)
        return _grade_resp_to_dict(resp)
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="grade_code",
    description=(
        "Review a student code submission with the Professor. Returns a structured "
        "grade (score, correctness, style, improvements, feedback). Does NOT record it."
    ),
    parameters={
        "type": "object",
        "properties": {
            "code_text": {"type": "string"},
            "task_description": {"type": "string"},
        },
        "required": ["code_text"],
    },
    category="grading",
)
def grade_code(code_text: str, task_description: str = "") -> dict:
    try:
        from llm.professor import Professor
        resp = Professor(session_id="agent_grading").grade_code(code_text, task_description)
        return _grade_resp_to_dict(resp)
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="record_grade",
    description=(
        "Record a score for an assignment and (when score < 90) seed remediation "
        "items from the listed weaknesses, so the student's backlog reflects what "
        "to re-teach. Use after grade_essay/grade_code."
    ),
    parameters={
        "type": "object",
        "properties": {
            "assignment_id": {"type": "string"},
            "score": {"type": "number"},
            "feedback": {"type": "string"},
            "course_id": {"type": "string", "description": "for remediation linkage"},
            "weaknesses": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["assignment_id", "score"],
    },
    category="grading",
    requires_review=True,
)
def record_grade(assignment_id: str, score: float, feedback: str = "",
                 course_id: str = "", weaknesses: list | None = None) -> dict:
    try:
        from core.database import submit_assignment, add_remediation_item
        submit_assignment(assignment_id, score, feedback)
        seeded = 0
        if score is not None and score < 90 and weaknesses:
            for weakness in list(weaknesses)[:5]:
                add_remediation_item(
                    source_type="assignment",
                    source_id=str(assignment_id),
                    course_id=str(course_id),
                    weakness=str(weakness),
                    severity="high" if score < 80 else "medium",
                    suggested_title=f"Remediation: {str(weakness)[:40]}",
                    data={"assignment_id": assignment_id, "score": score},
                )
                seeded += 1
        return {"recorded": True, "assignment_id": assignment_id,
                "score": score, "remediation_seeded": seeded}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="compute_gpa",
    description="Compute the student's current GPA and the number of graded assignments.",
    parameters={"type": "object", "properties": {}, "required": []},
    category="grading",
)
def compute_gpa() -> dict:
    try:
        from core.database import compute_gpa as _gpa
        gpa, count = _gpa()
        return {"gpa": round(gpa, 3), "graded_count": count}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="get_eligible_degrees",
    description="List degree programs the student currently qualifies for (by GPA + credits).",
    parameters={"type": "object", "properties": {}, "required": []},
    category="grading",
)
def get_eligible_degrees() -> dict:
    try:
        from core.database import eligible_degrees
        return {"eligible_degrees": eligible_degrees()}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="flag_prove_it",
    description=(
        "Flag an assignment for a 'prove-it' oral/practical re-check (anti-cheat / "
        "mastery verification). Returns the flag record."
    ),
    parameters={
        "type": "object",
        "properties": {"assignment_id": {"type": "string"}},
        "required": ["assignment_id"],
    },
    category="grading",
    requires_review=True,
)
def flag_prove_it(assignment_id: str) -> dict:
    try:
        from core.database import flag_prove_it as _flag
        result = _flag(assignment_id)
        return {"flagged": result if result is not None else None,
                "assignment_id": assignment_id}
    except Exception as exc:
        return {"error": str(exc)}
