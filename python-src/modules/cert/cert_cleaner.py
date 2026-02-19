"""
证书清理模块
提供跨平台的 CA 证书删除能力，避免在 GUI 中直接嵌入平台脚本。
"""

from __future__ import annotations

from collections.abc import Callable

from modules.cert.ca_store import clear_ca_cert_store
from modules.runtime.operation_result import OperationResult

type LogFunc = Callable[[str], None]


def clear_ca_cert_result(ca_common_name: str, log_func: LogFunc = print) -> OperationResult:
    """返回清理结果。"""
    return clear_ca_cert_store(ca_common_name, log_func=log_func)


def clear_ca_cert(ca_common_name: str, log_func: LogFunc = print) -> bool:
    """根据平台清除系统信任存储中的 CA 证书。"""
    return clear_ca_cert_result(ca_common_name, log_func=log_func).ok


__all__ = ["clear_ca_cert", "clear_ca_cert_result"]
