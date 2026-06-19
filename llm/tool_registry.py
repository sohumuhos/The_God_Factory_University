"""Agent tool registry primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    """A callable tool the agent can invoke."""

    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]
    category: str = "general"
    requires_review: bool = False

    def to_schema(self) -> dict:
        """Return the tool as a JSON-schema dict for LLM consumption."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


_TOOLS: dict[str, Tool] = {}


def register(name: str, description: str, parameters: dict,
             category: str = "general", requires_review: bool = False):
    """Decorator to register a function as an agent tool."""

    def decorator(fn: Callable) -> Callable:
        _TOOLS[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            handler=fn,
            category=category,
            requires_review=requires_review,
        )
        return fn

    return decorator


def get_tool(name: str) -> Tool | None:
    return _TOOLS.get(name)


def list_tools(category: str | None = None) -> list[Tool]:
    tools = list(_TOOLS.values())
    if category:
        tools = [tool for tool in tools if tool.category == category]
    return tools


def get_schemas(category: str | None = None) -> list[dict]:
    """Return JSON schemas for all tools (or a category)."""
    return [tool.to_schema() for tool in list_tools(category)]


def call_tool(name: str, args: dict) -> dict:
    """Execute a tool by name. Returns {'ok': bool, 'result': ...}.

    If the handler itself returns a dict carrying a truthy ``error`` key, the
    call is reported as a failure (``ok=False``) with that error surfaced at the
    top level. Without this, the agent loop's consecutive-error circuit breaker
    (which inspects the outer dict's ``error``) never trips on tool-internal
    failures — only on raised exceptions.
    """
    tool = get_tool(name)
    if not tool:
        return {"ok": False, "error": f"Unknown tool: {name}"}
    try:
        result = tool.handler(**args)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    if isinstance(result, dict) and result.get("error"):
        return {"ok": False, "error": str(result["error"]), "result": result}
    return {"ok": True, "result": result}
