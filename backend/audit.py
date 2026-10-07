"""Append-only audit trail for agent runs (Problem 12).

Every chat run appends one models.AuditRecord to output/audit_trail.json with the
time, who was chatting, the question, each tool call (name + short args + short
result), and why the run stopped. The file is never erased between runs: each run
reads the existing list, appends, and writes it back under a file lock.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from pydantic_ai.messages import ModelRequest, ModelResponse, ToolCallPart, ToolReturnPart

from config import OUTPUT_DIR
from models import AuditRecord, AuditToolCall

try:  # cross-process lock so concurrent requests don't corrupt the file (macOS/Linux)
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None

AUDIT_PATH = OUTPUT_DIR / "audit_trail.json"


def _short(value: object, limit: int = 160) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + "…"


def tool_calls_from_messages(messages: list) -> list[AuditToolCall]:
    """Pull the tool calls (and their results) out of a run's messages, in order."""
    args_by_id: dict[str, dict] = {}
    order: list[str] = []
    results_by_id: dict[str, str] = {}
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart):
                args_by_id[part.tool_call_id] = {"tool": part.tool_name, "args": _short(part.args)}
                order.append(part.tool_call_id)
            elif isinstance(part, ToolReturnPart):
                results_by_id[part.tool_call_id] = _short(part.content)
    return [
        AuditToolCall(
            tool=args_by_id[cid]["tool"],
            args=args_by_id[cid]["args"],
            result_summary=results_by_id.get(cid, ""),
        )
        for cid in order
    ]


def record_run(question: str, user: str, tool_calls: list[AuditToolCall], stop_reason: str) -> None:
    """Append one run to output/audit_trail.json. Append-only: existing history is kept."""
    record = AuditRecord(
        time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        user=user,
        question=_short(question, 200),
        tool_calls=tool_calls,
        stop_reason=stop_reason,
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_PATH, "a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            handle.seek(0)
            raw = handle.read().strip()
            data = json.loads(raw) if raw else []
            data.append(record.model_dump())
            handle.seek(0)
            handle.truncate()
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        finally:
            if fcntl is not None:
                fcntl.flock(handle, fcntl.LOCK_UN)
