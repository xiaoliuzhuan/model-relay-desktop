from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import yaml

from modules.runtime.resource_manager import ResourceManager

PLACEHOLDER_API_URL = "YOUR_REVERSE_ENGINEERED_API_ENDPOINT_BASE_URL"
DEFAULT_MIDDLE_ROUTE = "/v1"
DEFAULT_PROTOCOL = "openai"
ANTHROPIC_MESSAGES_PROTOCOL = "anthropic_messages"
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
SUPPORTED_PROTOCOLS = {DEFAULT_PROTOCOL, ANTHROPIC_MESSAGES_PROTOCOL}
type LogFunc = Callable[[str], None]


@dataclass(frozen=True)
class ProxyConfig:
    target_api_base_url: str
    middle_route: str
    custom_model_id: str
    target_model_id: str
    protocol: str
    anthropic_version: str
    stream_mode: str | None
    debug_mode: bool
    disable_ssl_strict_mode: bool
    api_key: str
    mtga_auth_key: str


def load_global_config(
    *, resource_manager: ResourceManager, log_func: LogFunc = print
) -> dict[str, Any]:
    try:
        config_file = resource_manager.get_user_config_file()
        if os.path.exists(config_file):
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception as exc:
        log_func(f"加载全局配置失败: {exc}")
    return {}


def _resolve_custom_model_id(
    *, global_config: dict[str, Any], raw_config: dict[str, Any]
) -> str:
    global_mapped_model_id = (global_config.get("mapped_model_id") or "").strip()
    legacy_group_mapped_model_id = (raw_config.get("mapped_model_id") or "").strip()
    return global_mapped_model_id or legacy_group_mapped_model_id or "CUSTOM_MODEL_ID"


def _resolve_target_model_id(*, raw_config: dict[str, Any], custom_model_id: str) -> str:
    target_model_id = (raw_config.get("model_id") or "").strip()
    return target_model_id if target_model_id else custom_model_id


def normalize_middle_route(value: str | None) -> str:
    raw_value = (value or "").strip()
    if not raw_value:
        raw_value = DEFAULT_MIDDLE_ROUTE
    if not raw_value.startswith("/"):
        raw_value = f"/{raw_value}"
    if len(raw_value) > 1:
        raw_value = raw_value.rstrip("/")
        if not raw_value:
            raw_value = "/"
    return raw_value


def normalize_protocol(value: str | None) -> str:
    protocol = (value or "").strip().lower()
    if protocol in SUPPORTED_PROTOCOLS:
        return protocol
    return DEFAULT_PROTOCOL


def normalize_anthropic_version(value: str | None) -> str:
    version = (value or "").strip()
    return version or DEFAULT_ANTHROPIC_VERSION


def build_proxy_config(
    raw_config: dict[str, Any] | None,
    *,
    resource_manager: ResourceManager,
    log_func: LogFunc = print,
) -> ProxyConfig | None:
    raw_config = raw_config or {}
    global_config = load_global_config(resource_manager=resource_manager, log_func=log_func)

    target_api_base_url = raw_config.get("api_url", PLACEHOLDER_API_URL)
    if target_api_base_url == PLACEHOLDER_API_URL:
        log_func("错误: 请在配置中设置正确的 API URL")
        return None

    custom_model_id = _resolve_custom_model_id(
        global_config=global_config,
        raw_config=raw_config,
    )
    target_model_id = _resolve_target_model_id(
        raw_config=raw_config,
        custom_model_id=custom_model_id,
    )
    middle_route = normalize_middle_route(raw_config.get("middle_route"))
    protocol = normalize_protocol(raw_config.get("protocol"))
    anthropic_version = normalize_anthropic_version(raw_config.get("anthropic_version"))

    return ProxyConfig(
        target_api_base_url=target_api_base_url,
        middle_route=middle_route,
        custom_model_id=custom_model_id,
        target_model_id=target_model_id,
        protocol=protocol,
        anthropic_version=anthropic_version,
        stream_mode=raw_config.get("stream_mode"),
        debug_mode=bool(raw_config.get("debug_mode", False)),
        disable_ssl_strict_mode=bool(raw_config.get("disable_ssl_strict_mode", False)),
        api_key=(raw_config.get("api_key") or ""),
        mtga_auth_key=(global_config.get("mtga_auth_key") or ""),
    )


__all__ = [
    "DEFAULT_MIDDLE_ROUTE",
    "DEFAULT_PROTOCOL",
    "ANTHROPIC_MESSAGES_PROTOCOL",
    "DEFAULT_ANTHROPIC_VERSION",
    "ProxyConfig",
    "PLACEHOLDER_API_URL",
    "build_proxy_config",
    "load_global_config",
    "normalize_protocol",
    "normalize_anthropic_version",
    "normalize_middle_route",
]
