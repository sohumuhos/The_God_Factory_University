"""Assessment authoring tools for the agent tool registry ('assessment' category).

These finally give the prototype Placement and Test-Prep engines a question bank:
the controller authors multiple-choice questions with the LLM and scores the
results, seeding remediation when the student places low. The placement/test_prep
engine functions take a tx_func, so these tools pass core.database.tx directly.

OPERATOR-GATED: not in the agent's default tool_categories (it generates content
and calls the LLM). All tools are requires_review.
"""
from __future__ import annotations

import json
import re

from llm.tool_registry import register


def _author_mcq(cfg, subject: str, difficulty: int):
    """Author one MCQ via the LLM. Returns (question, choices, correct) or None."""
    from llm.providers import simple_complete
    prompt = (
        f"Write ONE multiple-choice question assessing knowledge of '{subject}' at "
        f"difficulty {difficulty} (1=easy .. 5=hard). Exactly 4 distinct choices, one "
        f"correct. Output ONLY JSON: "
        '{"question":"...","choices":["..","..","..",".."],'
        '"correct_answer":"<exact text of the correct choice>"}'
    )
    raw = simple_complete(cfg, prompt) or ""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except Exception:
        return None
    q = obj.get("question")
    choices = obj.get("choices")
    correct = obj.get("correct_answer")
    if not (q and isinstance(choices, list) and len(choices) >= 2 and correct in choices):
        return None
    return q, choices, correct


@register(
    name="create_placement_test",
    description=(
        "Author a placement test for a subject: creates the test and fills it with "
        "LLM-generated multiple-choice questions at adaptive difficulty. The student "
        "then answers it on the Placement page; call score_placement to finalize."
    ),
    parameters={
        "type": "object",
        "properties": {
            "subject_id": {"type": "string"},
            "num_questions": {"type": "integer", "description": "default 5 (max 12)"},
        },
        "required": ["subject_id"],
    },
    category="assessment",
    requires_review=True,
)
def create_placement_test(subject_id: str, num_questions: int = 5) -> dict:
    from core.database import tx
    from core import placement
    from llm.providers import cfg_from_settings
    n = max(1, min(int(num_questions), 12))
    try:
        test_id = placement.start_test(subject_id, tx)
    except Exception as exc:
        return {"error": f"start_test failed: {exc}"}
    cfg = cfg_from_settings()
    added = 0
    for i in range(n):
        try:
            diff = placement.get_adaptive_difficulty(test_id, tx)
        except Exception:
            diff = 3
        authored = _author_mcq(cfg, subject_id, diff)
        if not authored:
            continue
        q, choices, correct = authored
        try:
            placement.add_question(test_id, q, choices, correct, int(diff), i, tx)
            added += 1
        except Exception:
            continue
    if added == 0:
        return {"error": "No questions authored (LLM unavailable or invalid output).",
                "test_id": test_id}
    return {"test_id": test_id, "subject_id": subject_id, "questions_added": added}


@register(
    name="score_placement",
    description=(
        "Finalize a placement test the student has answered: computes score and "
        "recommended level, and seeds a remediation item when the score is low."
    ),
    parameters={"type": "object", "properties": {"test_id": {"type": "string"}}, "required": ["test_id"]},
    category="assessment",
    requires_review=True,
)
def score_placement(test_id: str) -> dict:
    from core.database import tx, add_remediation_item
    from core import placement
    try:
        result = placement.finish_test(test_id, tx)
    except Exception as exc:
        return {"error": str(exc)}
    score = result.get("score_pct", 0)
    seeded = False
    if isinstance(score, (int, float)) and result.get("total", 0) > 0 and score < 60:
        try:
            add_remediation_item(
                source_type="placement", source_id=str(test_id), course_id="",
                weakness=f"Low placement score ({score:.0f}%); level {result.get('recommended_level','')}",
                severity="high" if score < 40 else "medium",
                suggested_title="Foundational remediation from placement",
            )
            seeded = True
        except Exception:
            pass
    return {"result": result, "remediation_seeded": seeded}


@register(
    name="create_test_prep_session",
    description=(
        "Author a standardized-test prep session for a named test + section, filling "
        "it with LLM-generated questions. The student answers on the Test Prep page; "
        "call score_test_prep to finalize."
    ),
    parameters={
        "type": "object",
        "properties": {
            "test_name": {"type": "string", "description": "e.g. SAT, GRE"},
            "section": {"type": "string", "description": "e.g. Math, Verbal"},
            "num_questions": {"type": "integer", "description": "default 5 (max 12)"},
        },
        "required": ["test_name", "section"],
    },
    category="assessment",
    requires_review=True,
)
def create_test_prep_session(test_name: str, section: str, num_questions: int = 5) -> dict:
    from core.database import tx
    from core import test_prep
    from llm.providers import cfg_from_settings
    n = max(1, min(int(num_questions), 12))
    try:
        session_id = test_prep.start_session(test_name, section, tx)
    except Exception as exc:
        return {"error": f"start_session failed: {exc}"}
    cfg = cfg_from_settings()
    added = 0
    for i in range(n):
        authored = _author_mcq(cfg, f"{test_name} {section}", 3)
        if not authored:
            continue
        q, choices, correct = authored
        try:
            test_prep.add_question(session_id, test_name, section, q, choices, correct, 3, i, tx)
            added += 1
        except Exception:
            continue
    if added == 0:
        return {"error": "No questions authored (LLM unavailable or invalid output).",
                "session_id": session_id}
    return {"session_id": session_id, "test_name": test_name, "section": section,
            "questions_added": added}


@register(
    name="score_test_prep",
    description=(
        "Finalize a test-prep session the student has answered: computes score and "
        "percentile, and seeds remediation when the score is low."
    ),
    parameters={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
    category="assessment",
    requires_review=True,
)
def score_test_prep(session_id: str) -> dict:
    from core.database import tx, add_remediation_item
    from core import test_prep
    try:
        result = test_prep.finish_session(session_id, tx)
    except Exception as exc:
        return {"error": str(exc)}
    score = result.get("score_pct", 0)
    seeded = False
    if isinstance(score, (int, float)) and result.get("total", 0) > 0 and score < 60:
        try:
            add_remediation_item(
                source_type="test_prep", source_id=str(session_id), course_id="",
                weakness=f"Low test-prep score ({score:.0f}%); percentile {result.get('percentile','')}",
                severity="high" if score < 40 else "medium",
                suggested_title="Test-prep remediation",
            )
            seeded = True
        except Exception:
            pass
    return {"result": result, "remediation_seeded": seeded}
