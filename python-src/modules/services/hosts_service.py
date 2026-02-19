from __future__ import annotations

from collections.abc import Callable, Iterable

from modules.hosts.hosts_manager import (
    backup_hosts_file,
    modify_hosts_file,
    open_hosts_file,
    remove_hosts_entry,
    restore_hosts_file,
)
from modules.runtime.operation_result import OperationResult

type LogFunc = Callable[[str], None]


def backup_hosts_file_result(*, log_func: LogFunc = print) -> OperationResult:
    if backup_hosts_file(log_func=log_func):
        return OperationResult.success()
    return OperationResult.failure("hosts 文件备份失败")


def restore_hosts_file_result(*, log_func: LogFunc = print) -> OperationResult:
    if restore_hosts_file(log_func=log_func):
        return OperationResult.success()
    return OperationResult.failure("hosts 文件还原失败")


def remove_hosts_entry_result(
    *, domain: str, log_func: LogFunc = print, ip: str | Iterable[object] | object | None = None
) -> OperationResult:
    if remove_hosts_entry(domain, log_func=log_func, ip=ip):
        return OperationResult.success()
    return OperationResult.failure("hosts 条目删除失败")


def modify_hosts_file_result(
    *,
    domain: str = "api.openai.com",
    action: str = "add",
    ip: str | Iterable[object] | object | None = None,
    log_func: LogFunc = print,
) -> OperationResult:
    if modify_hosts_file(domain=domain, action=action, ip=ip, log_func=log_func):
        return OperationResult.success()
    return OperationResult.failure("hosts 文件修改失败")


def open_hosts_file_result(*, log_func: LogFunc = print) -> OperationResult:
    if open_hosts_file(log_func=log_func):
        return OperationResult.success()
    return OperationResult.failure("打开 hosts 文件失败")

__all__ = [
    "backup_hosts_file",
    "backup_hosts_file_result",
    "modify_hosts_file",
    "modify_hosts_file_result",
    "open_hosts_file",
    "open_hosts_file_result",
    "remove_hosts_entry",
    "remove_hosts_entry_result",
    "restore_hosts_file",
    "restore_hosts_file_result",
]
