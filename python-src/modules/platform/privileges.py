from __future__ import annotations

import ctypes
import os
import sys
from ctypes import wintypes
from typing import Any, cast

from .system import is_posix, is_windows

_CTYPES = cast(Any, ctypes)


def is_windows_admin() -> bool:
    if not is_windows():
        return False
    try:
        return bool(_CTYPES.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def is_windows_elevated() -> bool:
    if not is_windows():
        return False

    try:
        kernel32 = _CTYPES.WinDLL("kernel32", use_last_error=True)
        advapi32 = _CTYPES.WinDLL("advapi32", use_last_error=True)
    except Exception:
        return False

    TOKEN_QUERY = 0x0008
    TokenElevation = 20

    token = wintypes.HANDLE()
    try:
        if not advapi32.OpenProcessToken(
            kernel32.GetCurrentProcess(),
            TOKEN_QUERY,
            ctypes.byref(token),
        ):
            return False

        elevation = wintypes.DWORD()
        returned_size = wintypes.DWORD()
        if not advapi32.GetTokenInformation(
            token,
            TokenElevation,
            ctypes.byref(elevation),
            ctypes.sizeof(elevation),
            ctypes.byref(returned_size),
        ):
            return False
        return bool(elevation.value)
    except Exception:
        return False
    finally:
        try:
            if token:
                kernel32.CloseHandle(token)
        except Exception:
            pass


def is_admin() -> bool:
    """Return True when the current process is elevated/admin on this platform."""
    if is_windows():
        return is_windows_admin()
    if is_posix():
        get_euid = getattr(os, "geteuid", None)
        if get_euid is None:
            return False
        try:
            return get_euid() == 0
        except Exception:
            return False
    return False


def check_is_admin() -> bool:
    return is_admin()


def run_as_admin() -> None:
    """Request admin privileges and relaunch the script when possible."""
    if check_is_admin():
        return
    if is_windows():
        try:
            _CTYPES.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception:
            print("无法获取 Windows 提权接口。")
            sys.exit(1)
        sys.exit(0)
    if is_posix():
        print("此程序需要管理员权限才能运行。")
        print("请使用以下命令重新运行：")
        print(f"sudo {sys.executable} {' '.join(sys.argv)}")
        sys.exit(1)
    print("不支持的操作系统")
    sys.exit(1)


__all__ = [
    "check_is_admin",
    "is_admin",
    "is_windows_admin",
    "is_windows_elevated",
    "run_as_admin",
]
