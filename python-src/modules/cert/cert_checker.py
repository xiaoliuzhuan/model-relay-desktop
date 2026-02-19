"""
证书存在性检查模块
提供跨平台检测，避免重复生成或安装。
"""
from __future__ import annotations

from collections.abc import Callable

from modules.cert.ca_store import check_ca_cert
from modules.runtime.operation_result import OperationResult

type LogFunc = Callable[[str], None]


def check_existing_ca_cert(ca_common_name: str, log_func: LogFunc = print) -> OperationResult:
    """返回检查结果，details 中包含 exists 标志。"""
    return check_ca_cert(ca_common_name, log_func=log_func)


def has_existing_ca_cert(ca_common_name: str, log_func: LogFunc = print) -> bool:
    """跨平台检查系统中是否已存在指定 Common Name 的 CA 证书。"""
    result = check_existing_ca_cert(ca_common_name, log_func=log_func)
    if not result.ok:
        return False
    return bool(result.details.get("exists"))


__all__ = ["check_existing_ca_cert", "has_existing_ca_cert"]
