"""Orchestration tools for the agent tool registry ('pipeline' category).

These let the controller run whole multi-step pipelines (generate -> enrich ->
decompose -> jargon -> render) and the 24/7 continuous enrichment loop with a
single tool call, reusing the existing engines in core/auto_pipeline.py and
core/continuous_engine.py — no parallel orchestration layer.

All write tools are requires_review=True. This category is deliberately NOT in
the agent's default tool_categories (it can render the whole catalog); enable it
explicitly on the Agent page, or via a Professor-dispatched job, when intended.
"""
from __future__ import annotations

from llm.tool_registry import register


@register(
    name="list_presets",
    description="List the available auto-pipeline presets (id -> label).",
    parameters={"type": "object", "properties": {}, "required": []},
    category="pipeline",
)
def list_presets() -> dict:
    try:
        from core.auto_pipeline import PRESET_LABELS
        return {"presets": dict(PRESET_LABELS)}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="run_pipeline",
    description=(
        "Run an auto-pipeline synchronously. preset='full_build' generates a new "
        "course from 'topic' (then enriches/renders); other presets operate on "
        "'course_ids'. Returns created course ids and a log tail. Heavy: may take "
        "minutes when rendering."
    ),
    parameters={
        "type": "object",
        "properties": {
            "preset": {"type": "string", "description": "full_build | deep_enrich | study_prep | full_render | custom"},
            "topic": {"type": "string", "description": "required for full_build"},
            "course_ids": {"type": "array", "items": {"type": "string"}},
            "difficulty": {"type": "string", "description": "default 'undergraduate'"},
            "lectures_per_module": {"type": "integer", "description": "default 3"},
        },
        "required": ["preset"],
    },
    category="pipeline",
    requires_review=True,
)
def run_pipeline(preset: str = "full_build", topic: str = "", course_ids: list | None = None,
                 difficulty: str = "undergraduate", lectures_per_module: int = 3) -> dict:
    from core.auto_pipeline import PipelineConfig, run_pipeline as _run, PRESET_LABELS
    if preset not in PRESET_LABELS:
        return {"error": f"Unknown preset '{preset}'. Valid: {list(PRESET_LABELS)}"}
    course_ids = list(course_ids or [])
    if preset == "full_build" and not topic:
        return {"error": "preset 'full_build' requires a 'topic' to generate the course."}
    if preset not in ("full_build",) and not course_ids and not topic:
        return {"error": f"preset '{preset}' requires 'course_ids' (existing courses) or a 'topic'."}
    cfg = PipelineConfig(
        preset=preset, topic=topic, course_ids=course_ids,
        difficulty=difficulty, lectures_per_module=int(lectures_per_module),
    )
    try:
        status = _run(cfg, stop_flag=lambda: False)
    except Exception as exc:
        return {"error": str(exc)}
    out = {
        "preset": preset,
        "created_course_ids": status.created_course_ids,
        "steps_completed": status.step_number,
        "total_steps": status.total_steps,
        "log_tail": status.log[-10:],
        "finished": status.finished,
    }
    if status.error:
        out["error"] = status.error  # surfaces as a tool failure to the agent loop
    return out


@register(
    name="start_continuous",
    description=(
        "Run the continuous enrichment loop for a bounded number of cycles over "
        "EXPLICIT target courses (enrich -> periodic decompose/jargon/level-advance). "
        "Requires target_course_ids to avoid touching the whole catalog."
    ),
    parameters={
        "type": "object",
        "properties": {
            "target_course_ids": {"type": "array", "items": {"type": "string"}},
            "cycles": {"type": "integer", "description": "number of full cycles (default 1)"},
            "jargon_per_cycle": {"type": "integer", "description": "default 1"},
            "auto_render": {"type": "boolean", "description": "render after each cycle (default false)"},
        },
        "required": ["target_course_ids"],
    },
    category="pipeline",
    requires_review=True,
)
def start_continuous(target_course_ids: list | None = None, cycles: int = 1,
                     jargon_per_cycle: int = 1, auto_render: bool = False) -> dict:
    targets = list(target_course_ids or [])
    if not targets:
        return {"error": "start_continuous requires explicit 'target_course_ids' "
                         "(empty would enrich the entire catalog)."}
    from core.continuous_engine import run_continuous, ContinuousConfig
    cfg = ContinuousConfig(
        target_course_ids=targets,
        jargon_per_cycle=int(jargon_per_cycle),
        auto_render=bool(auto_render),
    )
    max_cycles = max(1, int(cycles))
    state = {"stop": False}

    def _stop() -> bool:
        return state["stop"]

    def _on_progress(p) -> None:
        # Stop once we've started past the requested number of full cycles. The
        # extra (N+1)th cycle breaks immediately on the first inner stop check.
        if getattr(p, "cycle", 0) > max_cycles:
            state["stop"] = True

    try:
        progress = run_continuous(cfg, _stop, _on_progress)
    except Exception as exc:
        return {"error": str(exc)}
    return {
        "cycles_requested": max_cycles,
        "enrichments": getattr(progress, "total_enrichments", 0),
        "decompositions": getattr(progress, "total_decompositions", 0),
        "jargon_courses": getattr(progress, "total_jargon", 0),
        "level_advances": getattr(progress, "level_advances", 0),
        "errors": list(getattr(progress, "errors", []))[:5],
    }
