"""
文件可操作性检查（跨平台，Windows 优先）

用于在实际写入前尽量用“可断言的状态码”判断目标文件是否能被当前进程写入。
"""

from __future__ import annotations

import ctypes
import os
import stat
import tempfile
from collections.abc import Callable
from ctypes import wintypes
from dataclasses import dataclass
from enum import Enum
from typing import Any, cast

from modules.platform.privileges import is_windows_admin, is_windows_elevated
from modules.platform.system import is_windows

_CTYPES = cast(Any, ctypes)
type LogFunc = Callable[[str], None]


class FileOperabilityStatus(Enum):
    OK = "ok"
    FILE_NOT_FOUND = "file_not_found"
    ACCESS_DENIED = "access_denied"
    ACCESS_DENIED_ELEVATED = "access_denied_elevated"
    SHARING_VIOLATION = "sharing_violation"
    APPEND_ONLY = "append_only"
    DIR_CREATE_DENIED = "dir_create_denied"
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class FileOperabilityReport:
    status: FileOperabilityStatus
    is_admin: bool | None = None
    is_elevated: bool | None = None
    os_access_w_ok: bool | None = None
    attrs: int | None = None
    attr_flags: tuple[str, ...] = ()
    write_probe_winerror: int | None = None
    append_probe_winerror: int | None = None
    dir_create_probe_winerror: int | None = None

    @property
    def ok(self) -> bool:
        return self.status is FileOperabilityStatus.OK


def _get_windows_file_attributes(
    file_path: str, log_func: LogFunc
) -> tuple[int | None, tuple[str, ...]]:
    """读取 Windows 文件属性位并返回 (attrs, flags)。"""
    attrs = None
    attr_names: list[str] = []
    try:
        attrs = getattr(os.stat(file_path), "st_file_attributes", 0)
        flag_map = {
            getattr(stat, "FILE_ATTRIBUTE_READONLY", 0): "READONLY",
            getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 0): "HIDDEN",
            getattr(stat, "FILE_ATTRIBUTE_SYSTEM", 0): "SYSTEM",
            getattr(stat, "FILE_ATTRIBUTE_ARCHIVE", 0): "ARCHIVE",
            getattr(stat, "FILE_ATTRIBUTE_NOT_CONTENT_INDEXED", 0): "NOT_CONTENT_INDEXED",
        }
        for flag, name in flag_map.items():
            if attrs & flag:
                attr_names.append(name)
    except OSError as e:
        log_func(f"⚠️ 读取文件属性失败: {e}")
    return attrs, tuple(attr_names)


def _windows_probe_open(file_path: str, desired_access: int):
    """用 CreateFileW 探测句柄是否能打开（不写入、不截断）。"""
    try:
        kernel32 = _CTYPES.WinDLL("kernel32", use_last_error=True)
    except Exception:
        return False, None
    last_error = getattr(_CTYPES, "get_last_error", None)

    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    FILE_SHARE_DELETE = 0x00000004
    OPEN_EXISTING = 3
    FILE_ATTRIBUTE_NORMAL = 0x00000080

    INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

    kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel32.CreateFileW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    handle = kernel32.CreateFileW(
        str(file_path),
        wintypes.DWORD(desired_access),
        wintypes.DWORD(FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE),
        None,
        wintypes.DWORD(OPEN_EXISTING),
        wintypes.DWORD(FILE_ATTRIBUTE_NORMAL),
        None,
    )
    if handle == INVALID_HANDLE_VALUE:
        return False, last_error() if last_error else None
    kernel32.CloseHandle(handle)
    return True, None


def check_file_operability(file_path: str, *, log_func: LogFunc = print) -> FileOperabilityReport:
    """
    检查指定文件在当前环境下是否“可操作”（尽量以可断言的状态码返回）。

    主要用于 hosts 文件写入前的预检查：
    - 收集 is_admin / is_elevated / os.access(W_OK) / attrs 等上下文
    - 用 WinAPI 探测能否以写入/追加权限打开句柄（非破坏性）
    - 尝试在同目录创建临时文件（判断目录是否可写）
    """
    if not os.path.exists(file_path):
        log_func(f"⚠️ 文件不存在: {file_path}")
        return FileOperabilityReport(status=FileOperabilityStatus.FILE_NOT_FOUND)

    if not is_windows():
        try:
            with open(file_path, "r+b"):
                pass
            return FileOperabilityReport(status=FileOperabilityStatus.OK)
        except PermissionError:
            return FileOperabilityReport(status=FileOperabilityStatus.ACCESS_DENIED)
        except OSError:
            return FileOperabilityReport(status=FileOperabilityStatus.UNKNOWN_ERROR)

    WINERROR_ACCESS_DENIED = 5
    WINERROR_SHARING_VIOLATION = 32
    WINERROR_LOCK_VIOLATION = 33

    is_admin = is_windows_admin()
    elevated = is_windows_elevated()
    writable = os.access(file_path, os.W_OK)
    attrs, attr_flags = _get_windows_file_attributes(file_path, log_func)
    flags_text = ",".join(attr_flags) if attr_flags else "none"
    log_func(
        f"ℹ️ 写入前检查: is_admin={is_admin}, is_elevated={elevated}, "
        f"os.access(W_OK)={writable}, attrs={attrs}, flags={flags_text}"
    )

    GENERIC_WRITE = 0x40000000
    FILE_APPEND_DATA = 0x00000004

    write_ok, write_err = _windows_probe_open(file_path, GENERIC_WRITE)
    append_ok, append_err = _windows_probe_open(file_path, FILE_APPEND_DATA)

    dir_err = None
    dir_ok = True
    try:
        parent = os.path.dirname(os.path.abspath(file_path)) or "."
        with tempfile.NamedTemporaryFile(prefix="mtga_probe_", dir=parent, delete=True) as fp:
            fp.write(b"x")
            fp.flush()
    except (PermissionError, OSError) as e:
        dir_ok = False
        dir_err = getattr(e, "winerror", None)

    if write_ok:
        status = FileOperabilityStatus.OK
    elif write_err in (WINERROR_SHARING_VIOLATION, WINERROR_LOCK_VIOLATION):
        status = FileOperabilityStatus.SHARING_VIOLATION
    elif write_err == WINERROR_ACCESS_DENIED and append_ok:
        status = FileOperabilityStatus.APPEND_ONLY
    elif write_err == WINERROR_ACCESS_DENIED and not dir_ok:
        status = FileOperabilityStatus.DIR_CREATE_DENIED
    elif write_err == WINERROR_ACCESS_DENIED and elevated:
        status = FileOperabilityStatus.ACCESS_DENIED_ELEVATED
    elif write_err == WINERROR_ACCESS_DENIED:
        status = FileOperabilityStatus.ACCESS_DENIED
    else:
        status = FileOperabilityStatus.UNKNOWN_ERROR

    return FileOperabilityReport(
        status=status,
        is_admin=is_admin,
        is_elevated=elevated,
        os_access_w_ok=writable,
        attrs=attrs,
        attr_flags=attr_flags,
        write_probe_winerror=write_err,
        append_probe_winerror=append_err,
        dir_create_probe_winerror=dir_err,
    )


def ensure_windows_file_writable(file_path: str, *, log_func: LogFunc = print) -> None:
    """
    尝试清理 Windows 文件的只读属性，避免因只读属性导致写入失败。
    """
    if os.name != "nt":
        return
    try:
        os.chmod(file_path, stat.S_IWRITE)
    except PermissionError as e:
        log_func(f"⚠️ 无法移除文件只读属性: {e}")
    except OSError as e:
        log_func(f"⚠️ 调整文件权限时出错: {e}")
