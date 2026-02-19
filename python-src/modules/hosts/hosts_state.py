from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from modules.hosts.file_operability import FileOperabilityReport

ALLOW_UNSAFE_HOSTS_FLAG = "--allow-unsafe-hosts"
type LogFunc = Callable[[str], None]


@dataclass
class HostsModifyBlockState:
    blocked: bool = False
    reason: str | None = None
    report: FileOperabilityReport | None = None


_HOSTS_MODIFY_BLOCK_STATE = HostsModifyBlockState()


def configure_hosts_modify_block(
    blocked: bool,
    *,
    reason: str | None = None,
    report: FileOperabilityReport | None = None,
) -> None:
    """配置 hosts 自动修改的阻断开关（主要由 GUI 启动预检设置）。"""
    state = _HOSTS_MODIFY_BLOCK_STATE
    state.blocked = bool(blocked)
    state.reason = reason
    state.report = report


def is_hosts_modify_blocked() -> bool:
    return _HOSTS_MODIFY_BLOCK_STATE.blocked


def get_hosts_modify_block_report() -> FileOperabilityReport | None:
    return _HOSTS_MODIFY_BLOCK_STATE.report


def get_hosts_modify_block_state() -> HostsModifyBlockState:
    return _HOSTS_MODIFY_BLOCK_STATE


def should_block_hosts_action(action: str) -> bool:
    return action in {"remove", "restore"}


def guard_hosts_modify(action: str, log_func: LogFunc = print) -> bool:
    """如需阻断则输出提示并返回 False；允许则返回 True。"""
    state = _HOSTS_MODIFY_BLOCK_STATE
    if not state.blocked:
        return True
    if not should_block_hosts_action(action):
        return True
    report = state.report
    reason = state.reason or (report.status.value if report else "unknown")
    allow_flag = ALLOW_UNSAFE_HOSTS_FLAG
    log_func(f"⚠️ 当前环境 hosts 写入受限（reason={reason}）。")
    log_func("⚠️ 自动删除/还原需要原子性覆写，本环境下已禁用，请手动管理 hosts。")
    log_func("⚠️ 你可以点击「打开hosts文件」手动修改后重试。")
    log_func(f"⚠️ 如确需继续尝试自动修改，可使用启动参数 {allow_flag} 覆盖此检查（风险自负）。")
    return False


__all__ = [
    "ALLOW_UNSAFE_HOSTS_FLAG",
    "HostsModifyBlockState",
    "configure_hosts_modify_block",
    "get_hosts_modify_block_report",
    "get_hosts_modify_block_state",
    "guard_hosts_modify",
    "is_hosts_modify_blocked",
    "should_block_hosts_action",
]
