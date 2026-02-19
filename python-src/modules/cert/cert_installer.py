"""
证书安装模块
处理 CA 证书的系统安装和信任设置
"""

from __future__ import annotations

import os
from collections.abc import Callable

from modules.cert.ca_store import install_ca_cert_file
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager

type LogFunc = Callable[[str], None]


def install_ca_cert_result(log_func: LogFunc = print) -> OperationResult:
    """根据操作系统安装 CA 证书，返回结果对象。"""
    log_func("开始安装 CA 证书...")

    resource_manager = ResourceManager()
    possible_cert_files = [
        resource_manager.get_ca_cert_file(),
        os.path.join(resource_manager.ca_path, "rootCA.crt"),
        os.path.join(resource_manager.ca_path, "ca.cer"),
        os.path.join(resource_manager.ca_path, "rootCA.cer"),
    ]

    ca_cert_file = None
    for cert_file in possible_cert_files:
        if os.path.exists(cert_file):
            ca_cert_file = cert_file
            log_func(f"找到 CA 证书文件: {ca_cert_file}")
            break

    if ca_cert_file is None:
        log_func(f"错误: 未找到 CA 证书文件，已检查以下路径: {', '.join(possible_cert_files)}")
        return OperationResult.failure("未找到 CA 证书文件")

    try:
        return install_ca_cert_file(ca_cert_file, log_func=log_func)
    except Exception as exc:  # noqa: BLE001
        log_func(f"安装 CA 证书失败: {exc}")
        return OperationResult.failure("安装 CA 证书失败")


def install_ca_cert(log_func: LogFunc = print) -> bool:
    """根据操作系统安装 CA 证书，返回是否成功。"""
    return install_ca_cert_result(log_func=log_func).ok


__all__ = ["install_ca_cert", "install_ca_cert_result"]
