from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from modules.runtime.log_bus import push_log
from modules.runtime.operation_result import OperationResult
from modules.runtime.result_messages import describe_result


def collect_logs() -> tuple[list[str], Any]:
    logs: list[str] = []

    def _log(message: Any) -> None:
        if message is None:
            return
        text = str(message)
        logs.append(text)
        push_log(text)

    return logs, _log


def _coerce_detail(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: _coerce_detail(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_coerce_detail(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_coerce_detail(item) for item in value)
    return value


def build_result_payload(
    result: OperationResult,
    _logs: list[str],
    default_message: str,
) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "message": describe_result(result, default_message),
        "code": str(result.code) if result.code else None,
        "details": _coerce_detail(result.details),
    }
