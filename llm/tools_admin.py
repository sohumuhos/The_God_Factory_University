"""Admin tools for the agent tool registry ('admin' category).

Give the controller authority over settings and program enrollment. This
category is OPERATOR-GATED: it is NOT in the agent's default tool_categories and
the Agent page leaves its checkbox unchecked by default. Setting writes are
VALIDATED against core/settings_registry (unknown keys rejected; select/radio
options and number min/max enforced) so the agent can never write garbage, and
secret (password) values are redacted on read. All writes are requires_review.
"""
from __future__ import annotations

from llm.tool_registry import register


def _validate_setting(defn, value):
    """Return (ok, normalized_value_or_error_message)."""
    widget = defn.widget
    val = str(value)
    if widget in ("select", "radio") and defn.options:
        if val not in defn.options:
            return False, f"must be one of {list(defn.options)}"
        return True, val
    if widget == "toggle":
        if val.lower() in ("1", "true", "on", "yes"):
            return True, "1"
        if val.lower() in ("0", "false", "off", "no"):
            return True, "0"
        return False, "must be '0' or '1'"
    if widget in ("number", "slider"):
        try:
            num = float(val)
        except ValueError:
            return False, "must be numeric"
        if defn.min_val is not None and num < float(defn.min_val):
            return False, f"must be >= {defn.min_val}"
        if defn.max_val is not None and num > float(defn.max_val):
            return False, f"must be <= {defn.max_val}"
        return True, str(int(num)) if num.is_integer() else str(num)
    return True, val  # text / password / json


def _display_value(defn, val: str) -> str:
    if defn and defn.widget == "password":
        return "<set>" if val else "<empty>"
    return val


@register(
    name="get_setting",
    description="Read a setting value by key. Secret (password) values are redacted.",
    parameters={"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]},
    category="admin",
)
def get_setting(key: str) -> dict:
    try:
        from core.settings_registry import get_def
        from core.database import get_setting as _get
        defn = get_def(key)
        return {"key": key, "value": _display_value(defn, _get(key, ""))}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="set_setting",
    description=(
        "Set a setting value, validated against the settings registry (unknown keys "
        "rejected; select/radio options and number ranges enforced). Use list_settings "
        "to discover valid keys and allowed values."
    ),
    parameters={
        "type": "object",
        "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
        "required": ["key", "value"],
    },
    category="admin",
    requires_review=True,
)
def set_setting(key: str, value) -> dict:
    try:
        from core.settings_registry import get_def
        from core.database import set_setting as _set
        defn = get_def(key)
        if defn is None:
            return {"error": f"Unknown setting '{key}'. Use list_settings for valid keys."}
        ok, norm = _validate_setting(defn, value)
        if not ok:
            return {"error": f"Invalid value for '{key}': {norm}"}
        _set(key, norm)
        return {"set": key, "value": _display_value(defn, norm)}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="list_settings",
    description="List settings (optionally filtered by category) with current values, widgets, and allowed options.",
    parameters={
        "type": "object",
        "properties": {"category": {"type": "string", "description": "optional category filter"}},
        "required": [],
    },
    category="admin",
)
def list_settings(category: str = "") -> dict:
    try:
        from core.settings_registry import SETTINGS, settings_for_category, CATEGORIES
        from core.database import get_setting as _get
        defs = settings_for_category(category) if category else SETTINGS
        out = []
        for d in defs:
            val = _get(d.key, str(d.default))
            out.append({
                "key": d.key, "label": d.label, "category": d.category,
                "widget": d.widget, "options": list(d.options) if d.options else [],
                "value": _display_value(d, val),
            })
        return {"count": len(out), "categories": CATEGORIES, "settings": out}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="list_programs",
    description="List all degree programs the student could enroll in.",
    parameters={"type": "object", "properties": {}, "required": []},
    category="admin",
)
def list_programs() -> dict:
    try:
        from core.database import get_all_programs
        programs = get_all_programs()
        return {"count": len(programs), "programs": programs}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="enroll_program",
    description="Enroll the student in a degree program by id.",
    parameters={"type": "object", "properties": {"program_id": {"type": "string"}}, "required": ["program_id"]},
    category="admin",
    requires_review=True,
)
def enroll_program(program_id: str) -> dict:
    try:
        from core.database import enroll_program as _enroll
        result = _enroll(program_id)
        return {"enrolled": program_id, "enrollment": result}
    except Exception as exc:
        return {"error": str(exc)}


@register(
    name="get_enrollments",
    description="List the student's current program enrollments.",
    parameters={"type": "object", "properties": {}, "required": []},
    category="admin",
)
def get_enrollments() -> dict:
    try:
        from core.database import get_enrollments as _get
        rows = _get()
        return {"count": len(rows), "enrollments": rows}
    except Exception as exc:
        return {"error": str(exc)}
