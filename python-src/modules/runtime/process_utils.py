"""
Helpers for running subprocesses safely in GUI/no-console environments.

Goals:
- Avoid inheriting invalid stdin handles (common when launched without a console).
- Optionally hide the console window on Windows.
"""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from typing import Any, cast

WINDOWS_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _get_creationflags(hide_window: bool) -> int:
    """Return platform-appropriate creationflags."""

    if os.name == "nt" and hide_window:
        return WINDOWS_NO_WINDOW
    return 0


def run_command(
    cmd: Sequence[str] | str, *, shell: bool = False, hide_window: bool = True
) -> tuple[int, str, str]:
    """Run a command with safe defaults; never inherit stdin.

    Returns (returncode, stdout, stderr). On exception, returns (-1, "", str(exc)).
    """

    popen_kwargs: dict[str, Any] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "stdin": subprocess.DEVNULL,
        "text": True,
        "shell": shell,
    }
    creationflags = _get_creationflags(hide_window)
    if creationflags:
        popen_kwargs["creationflags"] = creationflags

    try:
        process = subprocess.Popen(cmd, **popen_kwargs)
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as exc:  # noqa: BLE001
        return -1, "", str(exc)


def run_subprocess(  # noqa: PLR0913
    command: Sequence[str] | str,
    *,
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    shell: bool = False,
    hide_window: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[str]:
    """Wrapper over subprocess.run with safe stdin and optional window hiding."""

    run_kwargs: dict[str, Any] = {
        "capture_output": capture_output,
        "text": text,
        "shell": shell,
    }
    run_kwargs.update(kwargs)
    if "stdin" not in run_kwargs and run_kwargs.get("input") is None:
        run_kwargs["stdin"] = subprocess.DEVNULL

    creationflags = _get_creationflags(hide_window)
    if creationflags:
        run_kwargs["creationflags"] = creationflags

    return cast(
        subprocess.CompletedProcess[str],
        subprocess.run(command, check=check, **run_kwargs),
    )


__all__ = ["run_command", "run_subprocess"]
