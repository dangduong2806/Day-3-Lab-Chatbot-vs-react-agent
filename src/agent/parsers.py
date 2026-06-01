"""Parse ReAct-style LLM output (Thought / Action / Final Answer)."""

import re
from typing import Any, Dict, Optional, Tuple

FINAL_ANSWER_RE = re.compile(
    r"Final Answer:\s*(.+)",
    re.IGNORECASE | re.DOTALL,
)
ACTION_RE = re.compile(
    r"Action:\s*(\w+)\s*\(([^)]*)\)",
    re.IGNORECASE,
)


def parse_final_answer(text: str) -> Optional[str]:
    match = FINAL_ANSWER_RE.search(text)
    if match:
        return match.group(1).strip()
    return None


def parse_action(text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    match = ACTION_RE.search(text)
    if not match:
        return None
    tool_name = match.group(1).strip()
    kwargs = parse_tool_kwargs(match.group(2))
    return tool_name, kwargs


def parse_tool_kwargs(args_str: str) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}
    args_str = args_str.strip()
    if not args_str:
        return kwargs

    pattern = re.compile(
        r"(\w+)\s*=\s*"
        r'(?:"([^"]*)"|\'([^\']*)\'|([^,\)]+))'
    )
    for m in pattern.finditer(args_str):
        key = m.group(1)
        raw = (m.group(2) or m.group(3) or m.group(4) or "").strip()
        kwargs[key] = _coerce_value(raw)
    return kwargs


def _coerce_value(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw.strip('"').strip("'")
