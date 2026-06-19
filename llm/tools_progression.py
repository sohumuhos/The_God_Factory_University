"""Progression tools for the agent tool registry ('progression' category).

These give the controller authority over the gamification ledger: read and
advance weekly quests, award XP, and unlock achievements. Mutating tools are
requires_review=True so they pass through the agent's draft queue in REVIEW mode.
add_xp is intentionally a single safe call — it auto-checks XP achievements and
ticks the earn-XP quest internally.
"""
from __future__ import annotations

from llm.tool_registry import register


@register(
    name="get_active_quests",
    description="List the student's active weekly quests with progress/target and XP reward.",
    parameters={"type": "object", "properties": {}, "required": []},
    category="progression",
)
def get_active_quests() -> dict:
    try:
        from core.database import get_active_quests as _quests
        quests = _quests()
        compact = [
            {
                "id": q.get("id"),
                "title": q.get("title"),
                "progress": q.get("progress"),
                "target": q.get("target"),
                "xp_reward": q.get("xp_reward"),
                "completed": bool(q.get("completed")),
            }
            for q in quests
        ]
        return {"count": len(compact), "quests": compact}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="advance_quest",
    description=(
        "Advance a quest's progress by an increment. Match the quest by its id "
        "prefix (e.g. 'complete_3_lectures', 'earn_200_xp'). Completing a quest "
        "auto-awards its XP."
    ),
    parameters={
        "type": "object",
        "properties": {
            "quest_prefix": {"type": "string"},
            "increment": {"type": "integer", "description": "default 1"},
        },
        "required": ["quest_prefix"],
    },
    category="progression",
    requires_review=True,
)
def advance_quest(quest_prefix: str, increment: int = 1) -> dict:
    try:
        from core.database import update_quest_progress
        update_quest_progress(quest_prefix, increment)
        return {"advanced": quest_prefix, "increment": increment}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="award_xp",
    description=(
        "Award XP to the student with a description. Use to reward genuine learning "
        "milestones. Auto-applies streak bonus and checks XP achievements/quests."
    ),
    parameters={
        "type": "object",
        "properties": {
            "amount": {"type": "integer"},
            "description": {"type": "string"},
            "event_type": {"type": "string", "description": "default 'agent'"},
        },
        "required": ["amount", "description"],
    },
    category="progression",
    requires_review=True,
)
def award_xp(amount: int, description: str, event_type: str = "agent") -> dict:
    try:
        from core.database import add_xp
        total = add_xp(int(amount), description, event_type)
        return {"awarded": int(amount), "new_xp_total": total}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="unlock_achievement",
    description="Unlock an achievement by id. Returns whether it was newly unlocked.",
    parameters={
        "type": "object",
        "properties": {"achievement_id": {"type": "string"}},
        "required": ["achievement_id"],
    },
    category="progression",
    requires_review=True,
)
def unlock_achievement(achievement_id: str) -> dict:
    try:
        from core.database import unlock_achievement as _unlock
        newly = _unlock(achievement_id)
        return {"achievement_id": achievement_id, "newly_unlocked": bool(newly)}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="list_achievements",
    description="List all achievements with their unlocked status.",
    parameters={"type": "object", "properties": {}, "required": []},
    category="progression",
)
def list_achievements() -> dict:
    try:
        from core.database import get_achievements
        rows = get_achievements()
        compact = [
            {"id": a.get("id"), "title": a.get("title"),
             "unlocked": bool(a.get("unlocked_at"))}
            for a in rows
        ]
        unlocked = sum(1 for a in compact if a["unlocked"])
        return {"count": len(compact), "unlocked": unlocked, "achievements": compact}
    except Exception as exc:
        return {"error": str(exc)}
