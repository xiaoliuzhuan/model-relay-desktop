from __future__ import annotations

from collections.abc import Callable

from modules.cert.cert_checker import check_existing_ca_cert, has_existing_ca_cert
from modules.cert.cert_cleaner import clear_ca_cert, clear_ca_cert_result
from modules.cert.cert_generator import generate_certificates, generate_server_cert
from modules.cert.cert_installer import install_ca_cert, install_ca_cert_result
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager

type LogFunc = Callable[[str], None]


def generate_certificates_result(
    *,
    log_func: LogFunc,
    ca_common_name: str,
    domain: str = "api.openai.com",
) -> OperationResult:
    if generate_certificates(log_func=log_func, ca_common_name=ca_common_name, domain=domain):
        return OperationResult.success()
    return OperationResult.failure("生成证书失败")


def generate_server_cert_result(*, log_func: LogFunc, domain: str) -> OperationResult:
    resource_manager = ResourceManager()
    if generate_server_cert(resource_manager, domain=domain, log_func=log_func):
        return OperationResult.success()
    return OperationResult.failure("生成服务器证书失败")


def has_existing_ca_cert_result(
    *,
    log_func: LogFunc,
    ca_common_name: str,
) -> OperationResult:
    return check_existing_ca_cert(ca_common_name, log_func=log_func)

__all__ = [
    "check_existing_ca_cert",
    "clear_ca_cert",
    "clear_ca_cert_result",
    "generate_certificates",
    "generate_certificates_result",
    "generate_server_cert_result",
    "has_existing_ca_cert",
    "has_existing_ca_cert_result",
    "install_ca_cert",
    "install_ca_cert_result",
]
