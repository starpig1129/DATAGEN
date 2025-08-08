from __future__ import annotations

import inspect
import uuid
from typing import Any, Dict, List, Optional, Tuple, Type

from pydantic import BaseModel, Field

# Capability model describing LLM tool/JSON capabilities.
class LLMCapabilities(BaseModel):
    family: str = Field(..., description="Model family: openai|anthropic|google|ollama|other")
    native_tools: bool = Field(False, description="Supports native tool/function calling")
    force_tool: bool = Field(False, description="Supports native forced tool_choice")
    json_mode: bool = Field(False, description="Supports response_format/json mode")
    notes: str = Field("", description="Any additional notes or detection hints")


def detect_capabilities(llm: Any, overrides: Optional[Dict[str, Any]] = None) -> LLMCapabilities:
    """Detect model capabilities with best-effort heuristics and optional overrides.
    Overrides example:
      {
        "family": "openai",
        "native_tools": True,
        "force_tool": True,
        "json_mode": True
      }
    """
    # Heuristics by class/module/name to avoid tight coupling.
    name = repr(llm)
    module = getattr(llm, "__module__", "") or ""
    clsname = getattr(llm, "__class__", type("X", (), {})).__name__

    family = "other"
    native_tools = False
    force_tool = False
    json_mode = False
    notes: List[str] = []

    s = f"{module}.{clsname}:{name}".lower()

    # OpenAI (langchain OpenAI/ChatOpenAI or openai client wrappers)
    if "openai" in s or "gpt" in s or "gpt-" in s:
        family = "openai"
        native_tools = True
        force_tool = True
        json_mode = True
        notes.append("Detected OpenAI family with native tools, forced tool_choice and JSON mode")

    # Anthropic
    if "anthropic" in s or "claude" in s:
        family = "anthropic"
        native_tools = True  # beta tool use available
        force_tool = False  # As of API 2024-09, tool_choice is not supported
        json_mode = True   # supports response_format: { "type": "json_object" }
        notes.append("Detected Anthropic; native tools, JSON mode, no forced tool_choice")

    # Google (Vertex/PaLM/Gemini)
    if "google" in s or "vertex" in s or "palm" in s or "gemini" in s:
        family = "google"
        native_tools = True  # function calling equivalents exist
        force_tool = False  # tool_choice not generally available
        json_mode = True   # supports response_format: { "type": "json_object" }
        notes.append("Detected Google; native tools, JSON mode, no forced tool_choice")

    # Ollama local
    if "ollama" in s:
        family = "ollama"
        native_tools = False
        force_tool = False
        json_mode = False
        notes.append("Detected Ollama; rely on prompt routing and strict JSON prompting")

    # Apply overrides last
    overrides = overrides or {}
    family = overrides.get("family", family)
    native_tools = bool(overrides.get("native_tools", native_tools))
    force_tool = bool(overrides.get("force_tool", force_tool))
    json_mode = bool(overrides.get("json_mode", json_mode))

    return LLMCapabilities(
        family=family,
        native_tools=native_tools,
        force_tool=force_tool,
        json_mode=json_mode,
        notes="; ".join(notes),
    )


# Standardized tool schema (OpenAI function schema superset)
class ToolParam(BaseModel):
    name: str
    description: str = ""
    required: bool = False
    schema: Dict[str, Any] = Field(default_factory=dict)


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)  # JSONSchema object for parameters
    required: List[str] = Field(default_factory=list)


def build_tool_schema(pydantic_model: Type[BaseModel], name: Optional[str] = None, description: Optional[str] = None) -> ToolSpec:
    """Build a standardized function schema from a pydantic model type.
    Output compatible with OpenAI function schema (name/description/parameters/required).
    """
    if not (inspect.isclass(pydantic_model) and issubclass(pydantic_model, BaseModel)):
        raise TypeError("pydantic_model must be a subclass of pydantic.BaseModel")

    model_name = name or pydantic_model.__name__
    model_desc = description or (getattr(pydantic_model, "__doc__", "") or "").strip()

    # Pydantic v2 JSON schema
    schema = pydantic_model.model_json_schema()
    # Extract properties and required
    props = schema.get("properties", {}) or {}
    required = list(schema.get("required", []) or [])

    # Assemble OpenAI-like parameters object
    parameters = {
        "type": "object",
        "properties": props,
        "additionalProperties": False,
    }
    if required:
        parameters["required"] = required

    return ToolSpec(
        name=model_name,
        description=model_desc,
        parameters=parameters,  # Already JSONSchema
        required=required,
    )


def _to_openai_tools(tool_defs: List[ToolSpec]) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for t in tool_defs:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
        )
    return tools


def bind_or_route(
    llm: Any,
    tool_defs: List[ToolSpec],
    capabilities: Optional[LLMCabilities] = None,  # type: ignore[name-defined]
    force: bool = False,
) -> Tuple[Any, Dict[str, Any]]:
    """Return either a tool-bound LLM or a router-plan setup depending on capabilities.
    For OpenAI with force_tool=True: return llm.bind_tools(..., tool_choice='required' or a specific)
    Otherwise: return llm unchanged and provide a routing plan descriptor consumed by caller.
    """
    # Typo fix for forward ref
    caps = capabilities or detect_capabilities(llm)
    meta: Dict[str, Any] = {
        "trace_id": str(uuid.uuid4()),
        "mode": "route",
        "family": caps.family,
    }

    # OpenAI path (native forced tools)
    if caps.family == "openai" and caps.native_tools:
        try:
            # LangChain's .bind_tools exists on many chat models
            if hasattr(llm, "bind_tools"):
                tools = _to_openai_tools(tool_defs)
                tool_choice = "required" if force or caps.force_tool else "auto"
                bound = llm.bind_tools(tools=tools, tool_choice=tool_choice)
                meta["mode"] = "bind"
                meta["tool_choice"] = tool_choice
                meta["tools_count"] = len(tools)
                return bound, meta
        except Exception as e:
            meta["bind_error"] = str(e)

    # Fallback: routing mode (two-stage)
    plan = {
        "mode": "route",
        "tools_index": {i: t.name for i, t in enumerate(tool_defs)},
        "tools_schema": [t.model_dump() for t in tool_defs],
        "force": force,
    }
    meta.update(plan)
    return llm, meta


# Planning schema for stage 1 routing decision
class RouteSchema(BaseModel):
    """Router decision: which next action to take.
    next: tool name or "FINISH"
    input: JSON that will be passed to the tool (if tool chosen)
    explanation: optional model-side reason (kept in JSON to avoid out-of-band text)
    """

    next: str = Field(..., description="Tool name to call or FINISH")
    input: Dict[str, Any] = Field(default_factory=dict, description="Arguments JSON for the chosen tool")
    explanation: Optional[str] = Field(default=None, description="Reasoning in JSON string")


def route_then_execute(
    decision: RouteSchema,
    name_to_callable: Dict[str, Any],
) -> Tuple[str, Any]:
    """Execute the tool decision. Returns (status, result).
    status:
      - "FINISH": decision to finish
      - "OK": tool executed successfully
      - "ERROR": tool execution failed
    """
    nxt = (decision.next or "").strip()
    if nxt.upper() == "FINISH":
        return "FINISH", None

    if nxt not in name_to_callable:
        return "ERROR", {"error": f"Unknown tool: {nxt}"}

    tool_fn = name_to_callable[nxt]
    try:
        # Expect tool_fn to accept kwargs matching decision.input
        result = tool_fn(**(decision.input or {}))
        return "OK", result
    except Exception as e:
        return "ERROR", {"error": str(e)}