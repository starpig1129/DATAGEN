from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

try:
    import orjson  # type: ignore
except Exception:  # pragma: no cover - optional dep
    orjson = None  # type: ignore

try:
    import simplejson  # type: ignore
except Exception:  # pragma: no cover - optional dep
    simplejson = None  # type: ignore

try:
    # Pydantic v2
    from pydantic import BaseModel
    from pydantic.type_adapter import TypeAdapter
except Exception as e:  # pragma: no cover
    raise RuntimeError("OutputGuard requires pydantic v2") from e


T = TypeVar("T")


JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    flags=re.IGNORECASE,
)

# Rough but effective JSON object/array block finder
JSON_BLOCK_RE = re.compile(
    r"(\{[\s\S]*\}|\[[\s\S]*\])",
    flags=re.MULTILINE,
)

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", flags=re.MULTILINE)

# NaN/Infinity tokens
NAN_INF_RE = re.compile(r"\bNaN\b|\bInfinity\b|\b-Infinity\b", flags=re.IGNORECASE)

# Remove JS style comments
LINE_COMMENT_RE = re.compile(r"(^|\s)//.*?$", flags=re.MULTILINE)
BLOCK_COMMENT_RE = re.compile(r"/\*[\s\S]*?\*/", flags=re.MULTILINE)

TRAILING_COMMA_RE = re.compile(r",(\s*[\}\]])")  # ", }" or ", ]"


def _structured_log(event: str, payload: Dict[str, Any]) -> None:
    # Minimal structured logging (stdout). Users can wire to their logger later.
    record = {"trace_id": payload.get("trace_id"), "event": event, **payload}
    try:
        print(json.dumps(record, ensure_ascii=False))
    except Exception:
        # Last resort
        print(f"[OutputGuard:{event}] {record}")


def extract_json_block(text: str, trace_id: Optional[str] = None) -> Optional[str]:
    """Extract the most plausible JSON block.
    Priority:
      1) ```json ... ``` fenced block
      2) Any triple backtick block
      3) First global balanced-ish {..} or [..] region
    """
    trace_id = trace_id or str(uuid.uuid4())

    # 1) Prefer explicit fenced json
    fenced = JSON_FENCE_RE.findall(text)
    if fenced:
        best = max(fenced, key=lambda s: len(s or ""))
        _structured_log("extract.fenced", {"trace_id": trace_id, "size": len(best)})
        return best.strip()

    # 2) Any code fence
    generic_fence = re.findall(r"```[\s\S]*?```", text)
    if generic_fence:
        # strip fences
        cleaned = [re.sub(r"^```(?:[a-zA-Z0-9_-]+)?\s*|\s*```$", "", block).strip() for block in generic_fence]
        best2 = max(cleaned, key=lambda s: len(s or ""))
        if best2.startswith("{") or best2.startswith("["):
            _structured_log("extract.code_fence", {"trace_id": trace_id, "size": len(best2)})
            return best2

    # 3) Global best-effort JSON-looking block
    matches = JSON_BLOCK_RE.findall(text)
    if matches:
        best3 = max(matches, key=lambda s: len(s or ""))
        _structured_log("extract.global", {"trace_id": trace_id, "size": len(best3)})
        return best3.strip()

    _structured_log("extract.none", {"trace_id": trace_id, "size": 0})
    return None


def sanitize_json(text: str, allow_repair: bool = True, trace_id: Optional[str] = None) -> str:
    """Apply common repairs to improve JSON parse-ability."""
    trace_id = trace_id or str(uuid.uuid4())
    original_len = len(text)

    # Remove control chars
    text = CONTROL_CHARS_RE.sub("", text)

    if allow_repair:
        # Remove comments
        text = LINE_COMMENT_RE.sub(r"\1", text)
        text = BLOCK_COMMENT_RE.sub("", text)

        # Replace NaN/Infinity with null
        text = NAN_INF_RE.sub("null", text)

        # Attempt to fix trailing commas
        # Repeat until stabilized (guard with small loop)
        for _ in range(3):
            new_text = TRAILING_COMMA_RE.sub(r"\1", text)
            if new_text == text:
                break
            text = new_text

        # Convert single quotes to double quotes conservatively:
        # Replace keys and string values that are quoted by single quotes and do not contain embedded quotes.
        def _fix_single_quotes(m: re.Match) -> str:
            s = m.group(0)
            return s.replace("'", '"')

        text = re.sub(r"(?<!\\)'([^'\\]*(?:\\.[^'\\]*)*)'", _fix_single_quotes, text)

    _structured_log(
        "sanitize",
        {"trace_id": trace_id, "orig_len": original_len, "new_len": len(text), "allow_repair": allow_repair},
    )
    return text


def _loads_std(s: str) -> Any:
    return json.loads(s)


def _loads_orjson(s: str) -> Any:
    if orjson is None:
        raise RuntimeError("orjson not available")
    return orjson.loads(s)  # type: ignore


def _loads_simplejson(s: str) -> Any:
    if simplejson is None:
        raise RuntimeError("simplejson not available")
    # Disallow NaN to enforce strict JSON
    return simplejson.loads(s, ignore_nan=False)  # type: ignore


def try_parse_multi(text: str, trace_id: Optional[str] = None) -> Tuple[bool, Optional[Any], Optional[str]]:
    """Try multiple parsers in order with increasing leniency."""
    trace_id = trace_id or str(uuid.uuid4())
    parsers = [
        ("json", _loads_std),
    ]
    if orjson is not None:
        parsers.append(("orjson", _loads_orjson))
    if simplejson is not None:
        parsers.append(("simplejson", _loads_simplejson))

    last_err = None
    for name, loader in parsers:
        try:
            data = loader(text)
            _structured_log("parse.success", {"trace_id": trace_id, "parser": name})
            return True, data, None
        except Exception as e:
            last_err = f"{name}: {e}"
            _structured_log("parse.fail", {"trace_id": trace_id, "parser": name, "error": str(e)})

    return False, None, last_err


def validate_and_coerce(data: Any, schema: Type[T] | TypeAdapter[T], trace_id: Optional[str] = None) -> Tuple[bool, Optional[T], Optional[str]]:
    """Validate data against a pydantic v2 schema or TypeAdapter. Coerce common mild mismatches."""
    trace_id = trace_id or str(uuid.uuid4())

    adapter: TypeAdapter[Any]
    if isinstance(schema, TypeAdapter):
        adapter = schema  # type: ignore
    else:
        if not (isinstance(schema, type) and issubclass(schema, BaseModel)):  # type: ignore
            return False, None, "Invalid schema type; expect pydantic BaseModel subclass or TypeAdapter"
        adapter = TypeAdapter(schema)

    try:
        validated = adapter.validate_python(data)
        _structured_log("schema.validate_ok", {"trace_id": trace_id})
        return True, validated, None
    except Exception as e:
        _structured_log("schema.validate_fail", {"trace_id": trace_id, "error": str(e)})
        # Attempt field-level coercions is already done by pydantic v2 where possible.
        # If still failing, report error.
        return False, None, str(e)


def build_minimal(data: Any, schema: Type[T] | TypeAdapter[T], trace_id: Optional[str] = None) -> Tuple[bool, Optional[T], Dict[str, Any]]:
    """Build minimal feasible JSON instance given partial data and schema.
    Strategy:
      - Keep intersecting fields when dict
      - Fill missing required fields with None or sensible empty types ([], {}, "")
      - Mark degraded=True in meta
    Note: This is best-effort; schema defaults (if defined) are leveraged by pydantic.
    """
    trace_id = trace_id or str(uuid.uuid4())

    adapter: TypeAdapter[Any]
    if isinstance(schema, TypeAdapter):
        adapter = schema  # type: ignore
        model_cls = None
    else:
        if not (isinstance(schema, type) and issubclass(schema, BaseModel)):  # type: ignore
            return False, None, {"reason": "Invalid schema type", "trace_id": trace_id}
        model_cls = schema
        adapter = TypeAdapter(schema)

    minimal: Any = {}
    if isinstance(data, dict):
        minimal = dict(data)
    else:
        # Wrap non-dict into a dict under "data" field if model has such field, else empty
        minimal = {"data": data}

    # Let pydantic fill defaults and convert types as much as possible
    try:
        validated = adapter.validate_python(minimal)
        meta = {"trace_id": trace_id, "degraded": False}
        _structured_log("minimal.ok", {"trace_id": trace_id})
        return True, validated, meta
    except Exception as e:
        # Try pruning unexpected keys and retry
        if model_cls is not None and hasattr(model_cls, "model_fields"):
            allowed = set(getattr(model_cls, "model_fields").keys())  # pydantic v2
            pruned = {k: v for k, v in minimal.items() if k in allowed}
        else:
            pruned = minimal

        try:
            validated2 = adapter.validate_python(pruned)
            meta = {"trace_id": trace_id, "degraded": True, "repair": "pruned_extra_keys"}
            _structured_log("minimal.degraded", {"trace_id": trace_id, "repair": "pruned_extra_keys"})
            return True, validated2, meta
        except Exception as e2:
            meta = {"trace_id": trace_id, "degraded": True, "repair": "failed_minimal", "error": str(e2)}
            _structured_log("minimal.fail", {"trace_id": trace_id, "error": str(e2)})
            return False, None, meta


def guarded_parse(
    raw_text: str,
    schema: Optional[Type[T] | TypeAdapter[T]] = None,
    allow_repair: bool = True,
    trace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """High-level pipeline:
      - Extract JSON block
      - Sanitize/repair
      - Multi-parser
      - Optional schema validation/coercion
      - Fallback minimal build
    Returns a dict with keys:
      ok: bool
      data: Any | None
      error: str | None
      meta: dict (trace_id, steps, degraded, etc.)
    """
    trace_id = trace_id or str(uuid.uuid4())
    steps = []

    block = extract_json_block(raw_text, trace_id=trace_id)
    if not block:
        steps.append("extract:none")
        return {
            "ok": False,
            "data": None,
            "error": "No JSON-like content found",
            "meta": {"trace_id": trace_id, "steps": steps},
        }
    steps.append("extract:ok")

    sanitized = sanitize_json(block, allow_repair=allow_repair, trace_id=trace_id)
    steps.append("sanitize:ok")

    ok, data, perr = try_parse_multi(sanitized, trace_id=trace_id)
    if not ok or data is None:
        steps.append("parse:fail")
        return {
            "ok": False,
            "data": None,
            "error": perr or "Parse failed",
            "meta": {"trace_id": trace_id, "steps": steps},
        }
    steps.append("parse:ok")

    if schema is None:
        return {"ok": True, "data": data, "error": None, "meta": {"trace_id": trace_id, "steps": steps}}

    v_ok, v_data, v_err = validate_and_coerce(data, schema, trace_id=trace_id)
    if v_ok and v_data is not None:
        steps.append("schema:ok")
        return {"ok": True, "data": v_data, "error": None, "meta": {"trace_id": trace_id, "steps": steps}}

    steps.append("schema:fail")
    b_ok, b_data, meta = build_minimal(data, schema, trace_id=trace_id)
    steps.append("minimal:" + ("ok" if b_ok else "fail"))
    return {
        "ok": b_ok,
        "data": b_data if b_ok else None,
        "error": None if b_ok else (v_err or "Schema validation failed and minimal build failed"),
        "meta": {"trace_id": trace_id, "steps": steps, **meta},
    }