from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.runtime.error_codes import ErrorCode


def _empty_details() -> dict[str, Any]:
    return {}


@dataclass(frozen=True)
class OperationResult:
    ok: bool
    message: str | None = None
    code: ErrorCode | None = None
    details: dict[str, Any] = field(default_factory=_empty_details)

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.ok

    @classmethod
    def success(
        cls,
        message: str | None = None,
        *,
        code: ErrorCode | None = None,
        **details: Any,
    ) -> OperationResult:
        return cls(True, message, code, dict(details))

    @classmethod
    def failure(
        cls,
        message: str | None = None,
        *,
        code: ErrorCode | None = None,
        **details: Any,
    ) -> OperationResult:
        return cls(False, message, code, dict(details))


__all__ = ["OperationResult"]
