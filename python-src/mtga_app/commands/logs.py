from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pytauri import Commands

from modules.runtime.log_bus import pull_logs


class LogPullPayload(BaseModel):
    after_id: int | None = None
    timeout_ms: int = 0
    max_items: int = 200


def register_log_commands(commands: Commands) -> None:
    @commands.command()
    async def pull_logs_command(body: LogPullPayload) -> dict[str, Any]:
        result = pull_logs(
            after_id=body.after_id,
            timeout_ms=body.timeout_ms,
            max_items=body.max_items,
        )
        return result

    _ = pull_logs_command


__all__ = ["register_log_commands"]
