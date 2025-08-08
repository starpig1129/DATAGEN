from __future__ import annotations

from typing import Any, Dict, List, Optional

JSON_ONLY_INSTRUCTIONS = """\
You must output ONLY a single JSON block in a fenced code block. Do not include any text outside the JSON block.
If you need to explain, include an "explanation" field inside the JSON.

Output format:
```json
{ ...valid json... }
```

Hard constraints:
- The first non-whitespace character MUST be '{' or '['.
- Do NOT output markdown, headings, prose, or commentary outside the JSON block.
- The JSON must be strictly valid: no comments, no trailing commas, double quotes only.
- Use null or empty string/array instead of placeholders like "N/A" or "None".
- Avoid NaN/Infinity; use null instead.
- If you are unsure, return the best possible JSON with empty strings/arrays/nulls for missing fields.

Self-check before finalizing (conceptual):
- Ensure JSON.parse(...) would succeed without errors.
- Ensure the schema keys are correct and spelled exactly as specified.
"""

JSON_GOOD_EXAMPLE = """\
Good example:
```json
{"next":"FINISH","input":{},"explanation":""}
```
"""

JSON_BAD_EXAMPLE = """\
Bad example (DO NOT DO THIS):
```json
{
  // wrong: line comments not allowed
  "next": "FINISH",,
  "input": {}, // trailing comma not allowed
}
```
"""

def inject_schema_description(schema_json: Dict[str, Any]) -> str:
    """Render a human-readable schema description to include in the prompt."""
    from json import dumps
    return (
        "Here is the STRICT JSON Schema you MUST follow exactly (OpenAPI/JSONSchema style):\n"
        f"```json\n{dumps(schema_json, ensure_ascii=False, indent=2)}\n```\n"
        "All required fields MUST be present. Do not add extra keys not present in the schema.\n"
    )


def json_only_base_prompt(task_instruction: str, schema_json: Optional[Dict[str, Any]] = None, extra_notes: Optional[str] = None) -> str:
    """Build a robust JSON-only prompt block with schema and examples."""
    blocks: List[str] = []
    if task_instruction:
        blocks.append(task_instruction.strip())

    blocks.append(JSON_ONLY_INSTRUCTIONS.strip())

    if schema_json:
        blocks.append(inject_schema_description(schema_json))

    blocks.append(JSON_GOOD_EXAMPLE.strip())
    blocks.append(JSON_BAD_EXAMPLE.strip())

    if extra_notes:
        blocks.append(f"Additional notes:\n{extra_notes.strip()}")

    # Explicit reminder
    blocks.append("Remember: respond ONLY with a single fenced JSON block, nothing else.")

    return "\n\n".join(blocks)


def router_stage1_decision_prompt(tools_schema: List[Dict[str, Any]]) -> str:
    """Prompt for routing decision: choose a tool or FINISH. Returns JSON-only instructions."""
    instruction = (
        "You are a routing policy. Decide the next action strictly in JSON. "
        "If a tool is beneficial, choose it and provide arguments under 'input'. "
        "If no tool is needed, set next to 'FINISH' and input to {}."
    )
    from json import dumps
    schema = {
        "type": "object",
        "properties": {
            "next": {"type": "string", "description": "Tool name to call or FINISH"},
            "input": {"type": "object", "additionalProperties": True},
            "explanation": {"type": "string"}
        },
        "required": ["next", "input"],
        "additionalProperties": False
    }
    examples = "Available tools schema:\n```json\n" + dumps(tools_schema, ensure_ascii=False, indent=2) + "\n```"
    return json_only_base_prompt(instruction + "\n\n" + examples, schema_json=schema, extra_notes="Choose FINISH if tool use is unnecessary.")