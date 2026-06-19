"""Proactive controller policy for The God Factory University.

A thin, read-only policy layer that turns the AI controller from reactive
(waits for a button) to proactive (acts on student state). It reads already-
exposed student signals and returns a ranked list of next-action proposals,
each carrying the natural-language task and the agent tool categories needed to
carry it out. The UI renders these as one-click "Run this" launchers.

No new engine, no writes — pure policy over core.database reads.
"""
from __future__ import annotations


def _safe(fn, default):
    try:
        return fn()
    except Exception:
        return default


def propose_next_action(max_items: int = 4) -> list[dict]:
    """Return ranked next-action proposals based on current student state.

    Each proposal: {label, reason, task_text, categories, priority}.
    Lower priority number = more urgent. Best-effort; never raises.
    """
    from core.database import (
        get_student_world_state,
        get_academic_progress_summary,
        list_remediation_backlog,
        get_active_quests,
    )

    world = _safe(get_student_world_state, {})
    academic = _safe(get_academic_progress_summary, {})
    backlog = _safe(lambda: list_remediation_backlog(limit=10), [])
    quests = _safe(get_active_quests, [])

    proposals: list[dict] = []

    # 1) Open remediation backlog → re-teach the weaknesses (most urgent).
    weaknesses = [b.get("weakness", "") for b in (backlog or []) if b.get("weakness")]
    if weaknesses:
        proposals.append({
            "label": f"Close {len(weaknesses)} weak area(s)",
            "reason": "Open remediation: " + "; ".join(weaknesses[:2]),
            "task_text": (
                "Review the student's open remediation backlog. For each weakness, "
                "create a short remedial lecture (or a targeted quiz) that closes the "
                "gap, then mark the item addressed. Weaknesses: " + "; ".join(weaknesses[:5])
            ),
            "categories": ["utility", "course", "grading"],
            "priority": 1,
        })

    # 2) Idle for a while → prepare a re-engagement refresher.
    idle = world.get("idle_days")
    if isinstance(idle, (int, float)) and idle >= 2:
        proposals.append({
            "label": "Resume studying",
            "reason": f"Idle for ~{idle:.0f} days.",
            "task_text": (
                "The student has been idle. Pick the most relevant in-progress course "
                "and prepare a short refresher quiz on its key concepts to re-engage them."
            ),
            "categories": ["utility", "course"],
            "priority": 2,
        })

    # 3) Unfinished weekly quest → help advance it.
    open_quests = [q for q in (quests or []) if not q.get("completed")]
    if open_quests:
        q = open_quests[0]
        proposals.append({
            "label": f"Finish quest: {q.get('title', 'weekly quest')}",
            "reason": f"{q.get('progress', 0)}/{q.get('target', 1)} complete.",
            "task_text": (
                f"Help the student make progress on the weekly quest "
                f"'{q.get('title', '')}'. Suggest a concrete next step and, if the "
                f"student completes it, advance the quest."
            ),
            "categories": ["utility", "progression"],
            "priority": 3,
        })

    # 4) No completed courses yet → onboard with a starter course.
    if academic.get("completed_courses", 0) == 0:
        proposals.append({
            "label": "Build a starter course",
            "reason": "No completed courses yet.",
            "task_text": (
                "Recommend a beginner-friendly starter course for a brand-new student, "
                "create its outline and first module, and explain how to begin."
            ),
            "categories": ["utility", "course"],
            "priority": 4,
        })

    proposals.sort(key=lambda p: p["priority"])
    return proposals[:max_items]
