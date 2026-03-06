from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, cast

import requests

from modules.proxy.proxy_config import (
    ANTHROPIC_MESSAGES_PROTOCOL,
    DEFAULT_ANTHROPIC_VERSION,
    DEFAULT_PROTOCOL,
    normalize_middle_route,
    normalize_protocol,
)

HTTP_OK = 200
CONTENT_PREVIEW_LEN = 50


class ThreadRunner(Protocol):
    def run(  # noqa: PLR0913
        self,
        name: str,
        target: Callable[..., None],
        *,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        wait_for: list[str] | None = None,
        allow_parallel: bool = False,
        daemon: bool = True,
    ) -> str: ...


def _extract_model_items(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    payload_dict = cast(dict[str, Any], payload)

    data = payload_dict.get("data")
    if isinstance(data, list):
        items: list[dict[str, Any]] = []
        data_list = cast(list[object], data)
        for item in data_list:
            if isinstance(item, dict):
                items.append(cast(dict[str, Any], item))
        return items

    result = payload_dict.get("result")
    if isinstance(result, dict):
        result_dict = cast(dict[str, Any], result)
        result_data = result_dict.get("data")
        if isinstance(result_data, list):
            items: list[dict[str, Any]] = []
            result_data_list = cast(list[object], result_data)
            for item in result_data_list:
                if isinstance(item, dict):
                    items.append(cast(dict[str, Any], item))
            return items

    alt = payload_dict.get("models")
    if isinstance(alt, list):
        items: list[dict[str, Any]] = []
        alt_list = cast(list[object], alt)
        for item in alt_list:
            if isinstance(item, dict):
                items.append(cast(dict[str, Any], item))
        return items

    return []


def _collect_model_ids(model_items: list[dict[str, Any]]) -> set[str]:
    model_ids: set[str] = set()
    for item in model_items:
        model_id = item.get("id")
        if isinstance(model_id, str):
            model_ids.add(model_id)
    return model_ids


def _build_middle_route_path(middle_route: str, suffix: str) -> str:
    normalized = normalize_middle_route(middle_route)
    if normalized == "/":
        return f"/{suffix.lstrip('/')}"
    return f"{normalized.rstrip('/')}/{suffix.lstrip('/')}"


def _resolve_protocol(config_group: dict[str, Any]) -> str:
    protocol_obj = config_group.get("protocol")
    protocol = protocol_obj if isinstance(protocol_obj, str) else DEFAULT_PROTOCOL
    return normalize_protocol(protocol)


def _resolve_anthropic_version(config_group: dict[str, Any]) -> str:
    version_obj = config_group.get("anthropic_version")
    if isinstance(version_obj, str) and version_obj.strip():
        return version_obj.strip()
    return DEFAULT_ANTHROPIC_VERSION


def _build_upstream_headers(
    config_group: dict[str, Any],
    *,
    protocol: str,
) -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    api_key_obj = config_group.get("api_key")
    api_key = api_key_obj if isinstance(api_key_obj, str) else ""
    api_key = api_key.strip()

    if protocol == ANTHROPIC_MESSAGES_PROTOCOL:
        if api_key:
            headers["x-api-key"] = api_key
        headers["anthropic-version"] = _resolve_anthropic_version(config_group)
        return headers

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _log_model_list(
    payload: Any,
    model_id: str,
    log_func: Callable[[str], None],
) -> None:
    model_ids = _parse_model_ids(payload, log_func)
    if not model_ids:
        return
    if model_id in model_ids:
        log_func(f"✅ 发现模型: {model_id}")
    else:
        log_func(f"❌ 未找到模型: {model_id}")


def _log_response_error(
    response: requests.Response,
    log_func: Callable[[str], None],
) -> None:
    log_func(f"❌ 模型列表获取失败: HTTP {response.status_code}")
    try:
        error_info = response.text[:200]
        log_func(f"   错误信息: {error_info}")
    except Exception:
        log_func("   (无法获取错误详情)")


def _parse_response_json(
    response: requests.Response,
    log_func: Callable[[str], None],
) -> Any | None:
    try:
        return response.json()
    except Exception:
        log_func("   (响应成功，但无法解析详细信息)")
        return None


def _parse_model_ids(
    payload: Any,
    log_func: Callable[[str], None],
) -> list[str]:
    if isinstance(payload, dict):
        payload_dict = cast(dict[str, Any], payload)
        if payload_dict.get("object"):
            log_func(f"   对象类型: {payload_dict['object']}")

    model_items = _extract_model_items(payload)
    if not model_items:
        log_func("❌ 响应中未发现模型列表")
        return []

    model_ids = sorted(_collect_model_ids(model_items))
    log_func(f"   模型数量: {len(model_ids)}")
    return model_ids


def _fetch_model_payload(
    config_group: dict[str, Any],
    log_func: Callable[[str], None],
    *,
    model_id: str | None = None,
) -> Any | None:
    api_url = config_group.get("api_url", "").rstrip("/")
    if not api_url:
        log_func("检查失败: API URL为空")
        return None

    route_path = _build_middle_route_path(
        config_group.get("middle_route", ""),
        "models",
    )
    test_url = f"{api_url}{route_path}"
    protocol = _resolve_protocol(config_group)
    headers = _build_upstream_headers(config_group, protocol=protocol)

    log_func(f"正在获取模型列表: {test_url}")

    suffix = f": {model_id}" if model_id else ""
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        log_func(f"❌ 模型列表获取超时{suffix}")
        return None
    except requests.exceptions.RequestException as exc:
        log_func(f"❌ 模型列表获取网络错误{suffix}: {str(exc)}")
        return None
    except Exception as exc:
        log_func(f"❌ 模型列表获取意外错误{suffix}: {str(exc)}")
        return None

    if response.status_code != HTTP_OK:
        _log_response_error(response, log_func)
        return None

    log_func("✅ 模型列表获取成功")
    return _parse_response_json(response, log_func)


def _run_model_connection_test(
    config_group: dict[str, Any],
    log_func: Callable[[str], None],
) -> None:
    model_id = config_group.get("model_id", "")
    if not config_group.get("api_url") or not model_id:
        log_func("检查失败: API URL或模型ID为空")
        return

    payload = _fetch_model_payload(config_group, log_func, model_id=model_id)
    if payload is None:
        return
    _log_model_list(payload, model_id, log_func)


def _extract_chat_preview(response_json: dict[str, Any], *, protocol: str) -> tuple[str, int | str]:
    if protocol == ANTHROPIC_MESSAGES_PROTOCOL:
        content_obj = response_json.get("content")
        content = ""
        if isinstance(content_obj, list):
            for raw_item in cast(list[object], content_obj):
                if not isinstance(raw_item, dict):
                    continue
                item = cast(dict[str, Any], raw_item)
                if item.get("type") == "text":
                    text_obj = item.get("text")
                    if isinstance(text_obj, str):
                        content += text_obj
        usage_obj = response_json.get("usage")
        total_tokens: int | str = "未知"
        if isinstance(usage_obj, dict):
            usage = cast(dict[str, Any], usage_obj)
            in_tokens = usage.get("input_tokens")
            out_tokens = usage.get("output_tokens")
            if isinstance(in_tokens, int) and isinstance(out_tokens, int):
                total_tokens = in_tokens + out_tokens
        return content, total_tokens

    content = (
        response_json.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    usage_obj = response_json.get("usage")
    total_tokens: int | str = "未知"
    if isinstance(usage_obj, dict):
        usage = cast(dict[str, Any], usage_obj)
        tokens_obj = usage.get("total_tokens")
        if isinstance(tokens_obj, int):
            total_tokens = tokens_obj
    return content, total_tokens


def fetch_model_list(
    config_group: dict[str, Any],
    *,
    log_func: Callable[[str], None] = print,
) -> tuple[list[str], bool]:
    payload = _fetch_model_payload(config_group, log_func)
    if payload is None:
        return [], False
    model_ids = _parse_model_ids(payload, log_func)
    if not model_ids:
        return [], False
    return model_ids, True


def test_model_in_list(
    config_group: dict[str, Any],
    *,
    log_func: Callable[[str], None] = print,
    thread_manager: ThreadRunner,
) -> None:
    """测试模型是否在列表中（GET /v1/models）。"""
    thread_manager.run(
        "test_model_in_list",
        lambda: _run_model_connection_test(config_group, log_func),
    )


def test_chat_completion(
    config_group: dict[str, Any],
    *,
    log_func: Callable[[str], None] = print,
    thread_manager: ThreadRunner,
) -> None:
    """测试模型连接。OpenAI 使用 chat/completions，Claude 使用 messages。"""

    def run_test():
        model_id = "未知模型"
        try:
            api_url = config_group.get("api_url", "").rstrip("/")
            model_id = config_group.get("model_id", "")
            protocol = _resolve_protocol(config_group)

            if not api_url or not model_id:
                log_func("测活失败: API URL或模型ID为空")
                return

            if protocol == ANTHROPIC_MESSAGES_PROTOCOL:
                route_path = _build_middle_route_path(
                    config_group.get("middle_route", ""),
                    "messages",
                )
                test_data = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": "1"}]}],
                    "max_tokens": 1,
                    "temperature": 0,
                }
            else:
                route_path = _build_middle_route_path(
                    config_group.get("middle_route", ""),
                    "chat/completions",
                )
                test_data = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": "1"}],
                    "max_tokens": 1,
                    "temperature": 0,
                }

            test_url = f"{api_url}{route_path}"
            headers = _build_upstream_headers(config_group, protocol=protocol)

            log_func(f"正在测活模型: {model_id} (会消耗少量tokens)")

            response = requests.post(test_url, json=test_data, headers=headers, timeout=30)

            if response.status_code == HTTP_OK:
                log_func(f"✅ 模型测活成功: {model_id}")
                try:
                    completion_info_obj = response.json()
                    if isinstance(completion_info_obj, dict):
                        completion_info = cast(dict[str, Any], completion_info_obj)
                        content, total_tokens = _extract_chat_preview(
                            completion_info,
                            protocol=protocol,
                        )
                        preview = content[:CONTENT_PREVIEW_LEN]
                        suffix = "..." if len(content) > CONTENT_PREVIEW_LEN else ""
                        if preview:
                            log_func(f"   响应内容: {preview}{suffix}")
                        log_func(f"   消耗tokens: {total_tokens}")
                except Exception:
                    log_func("   (响应成功，但无法解析详细信息)")
            else:
                log_func(f"❌ 模型测活失败: HTTP {response.status_code}")
                try:
                    error_info = response.text[:200]
                    log_func(f"   错误信息: {error_info}")
                except Exception:
                    log_func("   (无法获取错误详情)")

        except requests.exceptions.Timeout:
            log_func(f"❌ 模型测活超时: {model_id}")
        except requests.exceptions.RequestException as exc:
            log_func(f"❌ 模型测活网络错误: {str(exc)}")
        except Exception as exc:
            log_func(f"❌ 模型测活意外错误: {str(exc)}")

    thread_manager.run("test_chat_completion", run_test)
