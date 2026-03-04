from __future__ import annotations

import contextlib
import json
import logging
import threading
import time
import uuid
from collections.abc import Callable, Generator
from typing import Any, cast

import requests
from flask import Flask, Response, jsonify, request

from modules.proxy.proxy_auth import ProxyAuth
from modules.proxy.proxy_config import DEFAULT_MIDDLE_ROUTE, ProxyConfig, build_proxy_config
from modules.proxy.proxy_transport import ProxyTransport
from modules.runtime.error_codes import ErrorCode
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager

HTTP_BAD_REQUEST = 400


class ProxyApp:
    """代理服务的领域逻辑：配置解析 + Flask 路由 + 上游转发。"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        log_func: Callable[[str], None] = print,
        *,
        resource_manager: ResourceManager,
    ) -> None:
        self.config: dict[str, Any] = config or {}
        self.log_func = log_func
        self.resource_manager = resource_manager
        self._config_lock = threading.RLock()
        self._retired_transports: dict[int, ProxyTransport] = {}
        self._transport_ref_counts: dict[int, int] = {}
        self._root_logger_default_level = logging.getLogger().level
        self._app_logger_default_level = logging.WARNING
        self.app: Flask | None = None
        self.valid = True
        self.proxy_config: ProxyConfig | None = None
        self.auth: ProxyAuth | None = None
        self.transport: ProxyTransport | None = None
        self.http_client: requests.Session | None = None
        self.target_api_base_url = ""
        self.middle_route = ""
        self.inbound_route = DEFAULT_MIDDLE_ROUTE
        self.custom_model_id = ""
        self.target_model_id = ""
        self.stream_mode: str | None = None
        self.debug_mode = False
        self.disable_ssl_strict_mode = False

        proxy_config = build_proxy_config(
            self.config,
            resource_manager=self.resource_manager,
            log_func=self.log_func,
        )
        if not proxy_config:
            self.valid = False
            return

        self.proxy_config = proxy_config
        self.target_api_base_url = proxy_config.target_api_base_url
        self.middle_route = proxy_config.middle_route
        self.custom_model_id = proxy_config.custom_model_id
        self.target_model_id = proxy_config.target_model_id
        self.stream_mode = proxy_config.stream_mode  # None, 'true', 'false'
        self.debug_mode = proxy_config.debug_mode
        self.disable_ssl_strict_mode = proxy_config.disable_ssl_strict_mode
        self.auth = ProxyAuth(proxy_config.mtga_auth_key)
        self.transport = ProxyTransport(
            resource_manager=self.resource_manager,
            disable_ssl_strict_mode=self.disable_ssl_strict_mode,
            log_func=self.log_func,
        )
        self.http_client = self.transport.session

        self._create_app()

    def close(self) -> None:
        transports_to_close: list[ProxyTransport] = []
        with self._config_lock:
            if self.transport:
                transports_to_close.append(self.transport)
            transports_to_close.extend(self._retired_transports.values())
            self._retired_transports = {}
            self._transport_ref_counts = {}
            self.transport = None
            self.http_client = None
            self.auth = None
        for transport in transports_to_close:
            with contextlib.suppress(Exception):
                transport.close()

    def _snapshot_runtime_state(self) -> dict[str, Any]:
        with self._config_lock:
            return {
                "inbound_route": self.inbound_route,
                "target_api_base_url": self.target_api_base_url,
                "middle_route": self.middle_route,
                "custom_model_id": self.custom_model_id,
                "target_model_id": self.target_model_id,
                "stream_mode": self.stream_mode,
                "debug_mode": self.debug_mode,
                "auth": self.auth,
                "transport": self.transport,
                "http_client": self.http_client,
                "proxy_config": self.proxy_config,
            }

    def _snapshot_chat_runtime_state(self) -> dict[str, Any]:
        with self._config_lock:
            transport = self.transport
            if transport is not None:
                key = id(transport)
                self._transport_ref_counts[key] = (
                    self._transport_ref_counts.get(key, 0) + 1
                )
            return {
                "inbound_route": self.inbound_route,
                "target_api_base_url": self.target_api_base_url,
                "middle_route": self.middle_route,
                "custom_model_id": self.custom_model_id,
                "target_model_id": self.target_model_id,
                "stream_mode": self.stream_mode,
                "debug_mode": self.debug_mode,
                "auth": self.auth,
                "transport": transport,
                "http_client": self.http_client,
                "proxy_config": self.proxy_config,
            }

    def _release_transport_ref(self, transport: ProxyTransport | None) -> None:
        if transport is None:
            return
        close_target: ProxyTransport | None = None
        with self._config_lock:
            key = id(transport)
            current = self._transport_ref_counts.get(key, 0)
            if current <= 1:
                self._transport_ref_counts.pop(key, None)
                retired = self._retired_transports.pop(key, None)
                if retired is not None:
                    close_target = retired
            else:
                self._transport_ref_counts[key] = current - 1
        if close_target is not None:
            with contextlib.suppress(Exception):
                close_target.close()

    def _retire_transport(self, transport: ProxyTransport | None) -> None:
        if transport is None:
            return
        close_target: ProxyTransport | None = None
        with self._config_lock:
            key = id(transport)
            if self._transport_ref_counts.get(key, 0) > 0:
                self._retired_transports[key] = transport
                return
            close_target = transport
        with contextlib.suppress(Exception):
            close_target.close()

    def _apply_debug_logging(self, debug_mode: bool) -> None:
        app = self.app
        if not app:
            return
        root_logger = logging.getLogger()
        if debug_mode:
            root_logger.setLevel(logging.INFO)
            app.logger.setLevel(logging.INFO)
            return
        root_logger.setLevel(self._root_logger_default_level)
        app.logger.setLevel(self._app_logger_default_level)

    def apply_runtime_config(self, raw_config: dict[str, Any] | None) -> OperationResult:
        new_proxy_config = build_proxy_config(
            raw_config,
            resource_manager=self.resource_manager,
            log_func=lambda _message: None,
        )
        if not new_proxy_config:
            return OperationResult.failure(
                "config_invalid",
                code=ErrorCode.CONFIG_INVALID,
            )

        new_auth = ProxyAuth(new_proxy_config.mtga_auth_key)
        new_transport = ProxyTransport(
            resource_manager=self.resource_manager,
            disable_ssl_strict_mode=new_proxy_config.disable_ssl_strict_mode,
            log_func=self.log_func,
        )
        old_transport: ProxyTransport | None = None
        with self._config_lock:
            old_transport = self.transport
            self.proxy_config = new_proxy_config
            self.target_api_base_url = new_proxy_config.target_api_base_url
            self.middle_route = new_proxy_config.middle_route
            self.custom_model_id = new_proxy_config.custom_model_id
            self.target_model_id = new_proxy_config.target_model_id
            self.stream_mode = new_proxy_config.stream_mode
            self.debug_mode = new_proxy_config.debug_mode
            self.disable_ssl_strict_mode = new_proxy_config.disable_ssl_strict_mode
            self.auth = new_auth
            self.transport = new_transport
            self.http_client = new_transport.session

        self._apply_debug_logging(self.debug_mode)

        self._retire_transport(old_transport)
        return OperationResult.success("config_applied", apply_status="applied")

    @staticmethod
    def _new_request_id() -> str:
        return uuid.uuid4().hex[:6]

    @staticmethod
    def _timestamp_ms() -> str:
        now = time.time()
        base = time.strftime("%H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)
        return f"{base}.{ms:03d}"

    def _log_request(self, request_id: str, message: str) -> None:
        self.log_func(f"{self._timestamp_ms()} [{request_id}] {message}")

    def _get_mapped_model_id(self) -> str:
        return self.custom_model_id

    def _build_route(self, base_route: str, suffix: str) -> str:
        middle_route = base_route or ""
        if not middle_route.startswith("/"):
            middle_route = f"/{middle_route}"
        if middle_route == "/":
            return f"/{suffix.lstrip('/')}"
        return f"{middle_route.rstrip('/')}/{suffix.lstrip('/')}"

    @staticmethod
    def _extract_text_from_message_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            content_list = cast(list[object], content)
            for raw_item in content_list:
                if not isinstance(raw_item, dict):
                    continue
                item = cast(dict[str, Any], raw_item)
                text_value = item.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
            return "".join(chunks)
        return ""

    def _build_responses_payload_from_chat(  # noqa: PLR0912
        self, request_data: dict[str, Any]
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}

        passthrough_keys = (
            "model",
            "temperature",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
            "tools",
            "tool_choice",
            "parallel_tool_calls",
            "metadata",
            "user",
            "reasoning",
        )
        for key in passthrough_keys:
            value = request_data.get(key)
            if value is not None:
                payload[key] = value

        max_tokens = request_data.get("max_tokens")
        if max_tokens is not None:
            payload["max_output_tokens"] = max_tokens
        max_completion_tokens = request_data.get("max_completion_tokens")
        if max_completion_tokens is not None:
            payload["max_output_tokens"] = max_completion_tokens

        reasoning_effort_obj = request_data.get("reasoning_effort")
        if isinstance(reasoning_effort_obj, str) and reasoning_effort_obj.strip():
            reasoning_obj = payload.get("reasoning")
            if isinstance(reasoning_obj, dict):
                reasoning = cast(dict[str, Any], reasoning_obj)
                reasoning.setdefault("effort", reasoning_effort_obj.strip())
            else:
                payload["reasoning"] = {"effort": reasoning_effort_obj.strip()}

        stream_obj = request_data.get("stream")
        if isinstance(stream_obj, bool):
            payload["stream"] = stream_obj

        messages_obj = request_data.get("messages")
        input_messages: list[dict[str, str]] = []
        if isinstance(messages_obj, list):
            messages_list = cast(list[object], messages_obj)
            for raw_message in messages_list:
                if not isinstance(raw_message, dict):
                    continue
                message = cast(dict[str, Any], raw_message)
                role_obj = message.get("role")
                role = role_obj if isinstance(role_obj, str) else "user"
                if role not in {"system", "developer", "user", "assistant"}:
                    role = "user"

                content_text = self._extract_text_from_message_content(message.get("content"))
                if content_text:
                    input_messages.append({"role": role, "content": content_text})

        if input_messages:
            payload["input"] = input_messages

        response_format_obj = request_data.get("response_format")
        if isinstance(response_format_obj, dict):
            response_format = cast(dict[str, Any], response_format_obj)
            response_format_type = response_format.get("type")
            if response_format_type == "json_object":
                payload["text"] = {"format": {"type": "json_object"}}
            elif response_format_type == "json_schema":
                json_schema_obj = response_format.get("json_schema")
                if isinstance(json_schema_obj, dict):
                    json_schema = cast(dict[str, Any], json_schema_obj)
                    payload["text"] = {
                        "format": {
                            "type": "json_schema",
                            "name": json_schema.get("name") or "schema",
                            "schema": json_schema.get("schema") or {},
                            "strict": bool(json_schema.get("strict", False)),
                        }
                    }

        return payload

    @staticmethod
    def _extract_text_from_responses_output(  # noqa: PLR0912
        response_json: dict[str, Any]
    ) -> str:
        output_text_obj = response_json.get("output_text")
        if isinstance(output_text_obj, str) and output_text_obj:
            return output_text_obj
        if isinstance(output_text_obj, list):
            output_text_list = cast(list[object], output_text_obj)
            text_chunks = [item for item in output_text_list if isinstance(item, str)]
            if text_chunks:
                return "".join(text_chunks)

        output_obj = response_json.get("output")
        if not isinstance(output_obj, list):
            return ""

        output_list = cast(list[object], output_obj)
        chunks: list[str] = []
        for raw_output_item in output_list:
            if not isinstance(raw_output_item, dict):
                continue
            output_item = cast(dict[str, Any], raw_output_item)

            # 兼容 output 层直接携带文本
            direct_text_obj = output_item.get("text") or output_item.get("output_text")
            if isinstance(direct_text_obj, str):
                chunks.append(direct_text_obj)

            content_obj = output_item.get("content")
            if isinstance(content_obj, str):
                chunks.append(content_obj)
                continue
            if not isinstance(content_obj, list):
                continue

            content_list = cast(list[object], content_obj)
            for raw_content in content_list:
                if not isinstance(raw_content, dict):
                    continue
                content_item = cast(dict[str, Any], raw_content)
                text_obj = content_item.get("text") or content_item.get("output_text")
                if isinstance(text_obj, str):
                    chunks.append(text_obj)
                    continue
                if isinstance(text_obj, dict):
                    text_dict = cast(dict[str, Any], text_obj)
                    text_value = text_dict.get("value")
                    if isinstance(text_value, str):
                        chunks.append(text_value)

            summary_obj = output_item.get("summary")
            if isinstance(summary_obj, list):
                summary_list = cast(list[object], summary_obj)
                for raw_summary in summary_list:
                    if not isinstance(raw_summary, dict):
                        continue
                    summary_item = cast(dict[str, Any], raw_summary)
                    summary_text_obj = summary_item.get("text")
                    if isinstance(summary_text_obj, str):
                        chunks.append(summary_text_obj)

        return "".join(chunks)

    def _convert_responses_to_chat_completion(
        self,
        response_json: dict[str, Any],
        *,
        model_name: str,
    ) -> dict[str, Any]:
        content = self._extract_text_from_responses_output(response_json)

        created_obj = response_json.get("created_at")
        created = int(created_obj) if isinstance(created_obj, (int, float)) else int(time.time())

        usage_obj = response_json.get("usage")
        usage = None
        if isinstance(usage_obj, dict):
            usage_dict = cast(dict[str, Any], usage_obj)
            input_tokens_obj = usage_dict.get("input_tokens")
            output_tokens_obj = usage_dict.get("output_tokens")
            total_tokens_obj = usage_dict.get("total_tokens")

            prompt_tokens = int(input_tokens_obj) if isinstance(input_tokens_obj, int) else 0
            completion_tokens = int(output_tokens_obj) if isinstance(output_tokens_obj, int) else 0
            total_tokens = (
                int(total_tokens_obj)
                if isinstance(total_tokens_obj, int)
                else prompt_tokens + completion_tokens
            )
            usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }

        chat_completion = {
            "id": response_json.get("id") or self._new_request_id(),
            "object": "chat.completion",
            "created": created,
            "model": response_json.get("model") or model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
        }
        if usage is not None:
            chat_completion["usage"] = usage
        return chat_completion

    @staticmethod
    def _should_fallback_to_responses(response: requests.Response) -> bool:
        if response.status_code != HTTP_BAD_REQUEST:
            return False
        response_text = response.text.lower()
        return (
            "unsupported legacy protocol" in response_text
            and "/v1/chat/completions" in response_text
            and "/v1/responses" in response_text
        )

    @staticmethod
    def _simulate_stream_from_chat_response(
        response_json: dict[str, Any],
        *,
        log: Callable[[str], None],
    ) -> Generator[str]:
        choices_obj = response_json.get("choices")
        if not isinstance(choices_obj, list) or not choices_obj:
            log("响应中没有找到 choices 字段")
            yield f"data: {json.dumps({'error': 'No choices in response'})}\n\n"
            return
        choices = cast(list[object], choices_obj)

        first_choice_obj = choices[0]
        if not isinstance(first_choice_obj, dict):
            log("响应 choices[0] 不是对象")
            yield f"data: {json.dumps({'error': 'Invalid first choice in response'})}\n\n"
            return
        first_choice = cast(dict[str, Any], first_choice_obj)

        message_obj = first_choice.get("message")
        message = cast(dict[str, Any], message_obj) if isinstance(message_obj, dict) else {}
        content_obj = message.get("content")
        content = content_obj if isinstance(content_obj, str) else ""

        if not content:
            log("响应中没有找到内容")
            yield f"data: {json.dumps({'error': 'No content in response'})}\n\n"
            return

        model_obj = response_json.get("model")
        model = model_obj if isinstance(model_obj, str) else ""
        id_obj = response_json.get("id")
        id_value = id_obj if isinstance(id_obj, str) else ""
        created_obj = response_json.get("created")
        created = int(created_obj) if isinstance(created_obj, int) else int(time.time())

        chunk_size = 10
        total_chars = len(content)

        for index in range(0, total_chars, chunk_size):
            chunk = content[index : index + chunk_size]

            chunk_data = {
                "id": id_value,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None
                        if index + chunk_size < total_chars
                        else first_choice.get("finish_reason", "stop"),
                    }
                ],
            }

            yield f"data: {json.dumps(chunk_data)}\n\n"
            time.sleep(0.01)

        yield "data: [DONE]\n\n"

    @staticmethod
    def _build_chat_chunk_bytes(  # noqa: PLR0913
        *,
        request_id: str,
        model_name: str,
        created: int,
        include_role: bool,
        content: str | None = None,
        reasoning_content: str | None = None,
        finish_reason: str | None = None,
    ) -> bytes:
        delta: dict[str, Any] = {}
        if include_role:
            delta["role"] = "assistant"
        if content:
            delta["content"] = content
        if reasoning_content:
            delta["reasoning_content"] = reasoning_content

        chunk_obj = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": delta,
                    "logprobs": None,
                    "finish_reason": finish_reason,
                }
            ],
        }
        chunk_json = json.dumps(chunk_obj, ensure_ascii=False)
        return f"data: {chunk_json}\n\n".encode()

    def _create_app(self) -> None:
        self.app = Flask(__name__)
        self._app_logger_default_level = self.app.logger.level
        self._apply_debug_logging(self.debug_mode)

        models_route = self._build_route(self.inbound_route, "models")
        chat_route = self._build_route(self.inbound_route, "chat/completions")

        self.app.add_url_rule(models_route, "get_models", self._get_models, methods=["GET"])
        self.app.add_url_rule(
            chat_route,
            "chat_completions",
            self._chat_completions,
            methods=["POST"],
        )

    def _get_models(self) -> tuple[Response, int] | Response:
        snapshot = self._snapshot_runtime_state()
        inbound_route = str(snapshot["inbound_route"])
        auth = snapshot["auth"]
        mapped_model_id = str(snapshot["custom_model_id"])
        self.log_func(f"收到模型列表请求 {self._build_route(inbound_route, 'models')}")
        if not auth:
            self.log_func("代理鉴权未就绪")
            return jsonify(
                {"error": {"message": "Proxy not ready", "type": "server_error"}}
            ), 500

        auth_header = request.headers.get("Authorization")
        if not auth.verify(auth_header):
            self.log_func("模型列表请求鉴权失败")
            return jsonify(
                {"error": {"message": "Invalid authentication", "type": "authentication_error"}}
            ), 401

        model_data = {
            "object": "list",
            "data": [
                {
                    "id": mapped_model_id,
                    "object": "model",
                    "owned_by": "openai",
                    "created": int(time.time()),
                    "permission": [
                        {
                            "id": f"modelperm-{mapped_model_id}",
                            "object": "model_permission",
                            "created": int(time.time()),
                            "allow_create_engine": False,
                            "allow_sampling": True,
                            "allow_logprobs": True,
                            "allow_search_indices": False,
                            "allow_view": True,
                            "allow_fine_tuning": False,
                            "organization": "*",
                            "group": None,
                            "is_blocking": False,
                        }
                    ],
                }
            ],
        }

        self.log_func(f"返回映射模型: {mapped_model_id}")
        return jsonify(model_data)

    def _chat_completions(self) -> tuple[Response, int] | Response:  # noqa: PLR0911, PLR0912, PLR0915
        request_id = self._new_request_id()

        def log(message: str) -> None:
            self._log_request(request_id, message)

        snapshot = self._snapshot_chat_runtime_state()
        inbound_route = str(snapshot["inbound_route"])
        target_model_id = str(snapshot["target_model_id"])
        target_api_base_url = str(snapshot["target_api_base_url"])
        middle_route = str(snapshot["middle_route"])
        stream_mode = snapshot["stream_mode"]
        debug_mode = bool(snapshot["debug_mode"])
        auth = snapshot["auth"]
        transport = snapshot["transport"]
        http_client = snapshot["http_client"]
        proxy_config = snapshot["proxy_config"]
        transport_released = False

        def release_transport() -> None:
            nonlocal transport_released
            if transport_released:
                return
            transport_released = True
            self._release_transport_ref(transport)

        log(f"收到聊天补全请求 {self._build_route(inbound_route, 'chat/completions')}")

        if not (auth and transport and http_client):
            log("代理服务未就绪")
            release_transport()
            return jsonify({"error": "Proxy not ready"}), 500

        if debug_mode:
            headers_str = "\\n".join(f"{k}: {v}" for k, v in request.headers.items())
            log_message = (
                f"--- 请求头 (调试模式) ---\\n{headers_str}\\n"
                "--------------------------------------"
            )
            try:
                body_str = request.get_data(as_text=True)
                log_message += (
                    f"--- 请求体 (调试模式) ---\\n{body_str}\\n"
                    "--------------------------------------"
                )
            except Exception as body_exc:
                error_msg = f"读取请求体数据时出错: {body_exc}\\n"
                log(error_msg)
                log_message += error_msg
            log(log_message)

        request_data_obj = request.get_json(silent=True)

        if not isinstance(request_data_obj, dict):
            log("解析 JSON 失败或请求不是 JSON 格式")
            log(f"Content-Type: {request.headers.get('Content-Type')}")
            release_transport()
            return jsonify(
                {
                    "error": "Invalid JSON or Content-Type",
                    "message": (
                        "The request body must be valid JSON and the Content-Type header "
                        "must be 'application/json'."
                    ),
                }
            ), 400
        request_data = cast(dict[str, Any], request_data_obj)

        client_requested_stream = request_data.get("stream", False)
        log(f"客户端请求的流模式: {client_requested_stream}")

        if "model" in request_data:
            original_model = request_data["model"]
            log(f"替换模型名: {original_model} -> {target_model_id}")
            request_data["model"] = target_model_id
        else:
            log(f"请求中没有 model 字段，添加 model: {target_model_id}")
            request_data["model"] = target_model_id

        if stream_mode is not None:
            stream_value = stream_mode == "true"
            if "stream" in request_data:
                original_stream_value = request_data["stream"]
                log(f"强制修改流模式: {original_stream_value} -> {stream_value}")
                request_data["stream"] = stream_value
            else:
                log(f"请求中没有 stream 参数，设置为 {stream_value}")
                request_data["stream"] = stream_value

        auth_header = request.headers.get("Authorization")
        if not auth.verify(auth_header):
            log("聊天补全请求MTGA鉴权失败")
            release_transport()
            return jsonify(
                {"error": {"message": "Invalid authentication", "type": "authentication_error"}}
            ), 401

        target_api_key = ""
        if isinstance(proxy_config, ProxyConfig):
            target_api_key = proxy_config.api_key
        forward_headers = auth.build_forward_headers(
            auth_header,
            target_api_key,
            log_func=log,
        )

        try:
            target_url = (
                f"{target_api_base_url.rstrip('/')}"
                f"{self._build_route(middle_route, 'chat/completions')}"
            )
            log(f"转发请求到: {target_url}")

            is_stream = request_data.get("stream", False)
            log(f"流模式: {is_stream}")

            response_from_target = http_client.post(
                target_url,
                json=request_data,
                headers=forward_headers,
                stream=is_stream,
                timeout=300,
            )
            if self._should_fallback_to_responses(response_from_target):
                log("上游仅支持 /v1/responses，自动切换协议")
                with contextlib.suppress(Exception):
                    response_from_target.close()

                responses_url = (
                    f"{target_api_base_url.rstrip('/')}"
                    f"{self._build_route(middle_route, 'responses')}"
                )
                responses_payload = self._build_responses_payload_from_chat(request_data)
                if not responses_payload.get("input"):
                    log("无法从 chat/completions 请求构建 responses input 字段")
                    release_transport()
                    return jsonify({"error": "Invalid chat request for responses fallback"}), 400
                log(f"转发请求到: {responses_url}")
                reasoning_obj = responses_payload.get("reasoning")
                reasoning_effort_log = "-"
                if isinstance(reasoning_obj, dict):
                    reasoning_dict = cast(dict[str, Any], reasoning_obj)
                    effort_obj = reasoning_dict.get("effort")
                    if isinstance(effort_obj, str) and effort_obj:
                        reasoning_effort_log = effort_obj
                log(
                    "responses 参数: "
                    f"stream={responses_payload.get('stream', False)}, "
                    f"reasoning_effort={reasoning_effort_log}"
                )

                responses_response = http_client.post(
                    responses_url,
                    json=responses_payload,
                    headers=forward_headers,
                    stream=is_stream,
                    timeout=300,
                )
                responses_response.raise_for_status()

                if is_stream:
                    upstream_content_type = responses_response.headers.get("content-type", "")
                    if "text/event-stream" in upstream_content_type.lower():
                        log("Responses 返回流式响应，实时转换为 chat.completion.chunk")

                        def generate_responses_stream() -> Generator[bytes]:  # noqa: PLR0912, PLR0915
                            request_id_for_stream = self._new_request_id()
                            created = int(time.time())
                            role_sent = False
                            done_sent = False
                            event_index = 0
                            try:
                                for upstream_chunk_index, raw_event in transport.extract_sse_events(
                                    responses_response, log=log
                                ):
                                    event_index += 1
                                    event_text = raw_event.decode("utf-8", errors="replace")
                                    data_lines = [
                                        line[len("data:") :].lstrip()
                                        for line in event_text.splitlines()
                                        if line.startswith("data:")
                                    ]
                                    if not data_lines:
                                        continue
                                    data_str = "\n".join(data_lines).strip()
                                    if not data_str:
                                        continue

                                    if debug_mode:
                                        log(
                                            "RESP<< "
                                            f"evt#{event_index} "
                                            f"src_chunk#{upstream_chunk_index} "
                                            f"| {data_str}"
                                        )

                                    if data_str == "[DONE]":
                                        done_sent = True
                                        yield b"data: [DONE]\n\n"
                                        break

                                    try:
                                        payload_obj = json.loads(data_str)
                                    except Exception:  # noqa: BLE001
                                        continue
                                    if not isinstance(payload_obj, dict):
                                        continue
                                    payload = cast(dict[str, Any], payload_obj)

                                    event_type_obj = payload.get("type")
                                    event_type = (
                                        event_type_obj if isinstance(event_type_obj, str) else ""
                                    )

                                    if event_type == "response.output_text.delta":
                                        delta_obj = payload.get("delta")
                                        delta = delta_obj if isinstance(delta_obj, str) else ""
                                        if delta:
                                            yield self._build_chat_chunk_bytes(
                                                request_id=request_id_for_stream,
                                                model_name=target_model_id,
                                                created=created,
                                                include_role=not role_sent,
                                                content=delta,
                                            )
                                            role_sent = True
                                        continue

                                    if event_type in {
                                        "response.reasoning.delta",
                                        "response.reasoning_summary.delta",
                                        "response.reasoning_summary_text.delta",
                                    }:
                                        reasoning_obj = payload.get("delta") or payload.get("text")
                                        reasoning = (
                                            reasoning_obj if isinstance(reasoning_obj, str) else ""
                                        )
                                        if reasoning:
                                            yield self._build_chat_chunk_bytes(
                                                request_id=request_id_for_stream,
                                                model_name=target_model_id,
                                                created=created,
                                                include_role=not role_sent,
                                                reasoning_content=reasoning,
                                            )
                                            role_sent = True
                                        continue

                                    if event_type == "response.completed":
                                        yield self._build_chat_chunk_bytes(
                                            request_id=request_id_for_stream,
                                            model_name=target_model_id,
                                            created=created,
                                            include_role=not role_sent,
                                            finish_reason="stop",
                                        )
                                        role_sent = True
                                        continue

                                if not done_sent:
                                    with contextlib.suppress(Exception):
                                        yield b"data: [DONE]\n\n"
                            finally:
                                release_transport()
                                with contextlib.suppress(Exception):
                                    responses_response.close()

                        return Response(
                            generate_responses_stream(),
                            content_type="text/event-stream",
                        )

                    log(
                        "Responses 流模式未返回 SSE，回退为非流式适配"
                        f" (content-type={upstream_content_type})"
                    )

                responses_json_obj = responses_response.json()
                if not isinstance(responses_json_obj, dict):
                    log("Responses 上游响应不是 JSON 对象")
                    release_transport()
                    return jsonify({"error": "Invalid response from target API"}), 502
                responses_json = cast(dict[str, Any], responses_json_obj)
                chat_response_json = self._convert_responses_to_chat_completion(
                    responses_json,
                    model_name=target_model_id,
                )
                content_obj = (
                    chat_response_json.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                if not isinstance(content_obj, str) or not content_obj.strip():
                    response_keys = ",".join(sorted(responses_json.keys()))
                    log(f"Responses 转换后内容为空，原始响应 keys: {response_keys}")

                if is_stream or (client_requested_stream and stream_mode == "false"):
                    log("将 Responses 非流式响应转换为流式格式返回给客户端")
                    release_transport()
                    return Response(
                        self._simulate_stream_from_chat_response(chat_response_json, log=log),
                        content_type="text/event-stream",
                    )

                release_transport()
                return jsonify(chat_response_json), responses_response.status_code

            response_from_target.raise_for_status()
            if debug_mode:
                log(f"上游响应状态码: {response_from_target.status_code}")
                log(f"上游 Content-Type: {response_from_target.headers.get('content-type')}")

            if is_stream:
                log("返回流式响应")

                log_file = None
                log_file_stack = None
                log_path = None
                if debug_mode:
                    try:
                        log_path = transport.prepare_sse_log_path()
                        log_file_stack = contextlib.ExitStack()
                        log_file = log_file_stack.enter_context(open(log_path, "wb"))  # noqa: SIM115
                        log(f"SSE 原始数据将记录到: {log_path}")
                    except Exception as log_exc:  # noqa: BLE001
                        log(f"SSE 日志文件创建失败: {log_exc}")

                def generate_stream() -> Generator[bytes]:  # noqa: PLR0915, PLR0912
                    nonlocal log_file, log_file_stack
                    event_index = 0
                    done_sent = False
                    finish_reason_seen = None
                    try:
                        for upstream_chunk_index, raw_event in transport.extract_sse_events(
                            response_from_target, log_file=log_file, log=log
                        ):
                            event_index += 1
                            event_text = raw_event.decode("utf-8", errors="replace")
                            data_lines = [
                                line[len("data:") :].lstrip()
                                for line in event_text.splitlines()
                                if line.startswith("data:")
                            ]
                            if not data_lines:
                                log(f"evt#{event_index} 跳过无 data 行的事件: {event_text!r}")
                                continue
                            data_str = "\n".join(data_lines)

                            if debug_mode:
                                log(
                                    f"UP<< evt#{event_index} src_chunk#{upstream_chunk_index} "
                                    f"bytes={len(raw_event)} | {data_str.strip()}"
                                )

                            if data_str.strip() == "[DONE]":
                                done_sent = True
                                done_bytes = b"data: [DONE]\n\n"
                                try:
                                    yield done_bytes
                                except GeneratorExit:
                                    log(
                                        f"DOWN 连接提前中断，已读取上游 evt#{event_index} (DONE)"
                                    )
                                    raise
                                except Exception as downstream_exc:  # noqa: BLE001
                                    log(f"DOWN 写入异常 (DONE)，停止向下游发送: {downstream_exc}")
                                    break
                                log("已转发 [DONE]")
                                break

                            normalized_bytes, finish_reason = transport.normalize_openai_event(
                                data_str,
                                event_index,
                                model_name=target_model_id,
                                log=log,
                            )
                            if finish_reason:
                                finish_reason_seen = finish_reason
                            try:
                                yield normalized_bytes
                            except GeneratorExit:
                                log(
                                    f"DOWN 连接提前中断，已读取上游 evt#{event_index} "
                                    f"finish={finish_reason_seen}"
                                )
                                raise
                            except Exception as downstream_exc:  # noqa: BLE001
                                log(f"DOWN 写入异常，停止向下游发送: {downstream_exc}")
                                break
                        if not done_sent:
                            tail_bytes = b"data: [DONE]\n\n"
                            with contextlib.suppress(Exception):
                                yield tail_bytes
                            if debug_mode:
                                extra = (
                                    f"，finish_reason={finish_reason_seen}"
                                    if finish_reason_seen
                                    else ""
                                )
                                log(f"未收到上游 [DONE]，已补发终止事件{extra}")
                    finally:
                        release_transport()
                        if log_file_stack:
                            with contextlib.suppress(Exception):
                                log_file_stack.close()
                        if log_path:
                            log(f"SSE 记录完成: {log_path}")
                        with contextlib.suppress(Exception):
                            response_from_target.close()
                        if debug_mode:
                            log(f"UP 流结束，累计 {event_index} 个事件")

                downstream_content_type = response_from_target.headers.get(
                    "content-type", "text/event-stream"
                )
                if debug_mode:
                    log(f"下游响应 Content-Type: {downstream_content_type}")

                return Response(
                    generate_stream(),
                    content_type=downstream_content_type,
                )

            response_json_obj = response_from_target.json()
            if not isinstance(response_json_obj, dict):
                log("上游响应不是 JSON 对象")
                release_transport()
                return jsonify({"error": "Invalid response from target API"}), 502
            response_json = cast(dict[str, Any], response_json_obj)

            if client_requested_stream and stream_mode == "false":
                log("将非流式响应转换为流式格式返回给客户端")
                release_transport()
                return Response(
                    self._simulate_stream_from_chat_response(response_json, log=log),
                    content_type="text/event-stream",
                )

            if debug_mode:
                response_str = json.dumps(response_json, indent=2, ensure_ascii=False)
                log(
                    f"--- 完整响应体 (调试模式) ---\\n{response_str}\\n"
                    "--------------------------------------"
                )
            else:
                log("返回非流式 JSON 响应")
            release_transport()
            return jsonify(response_json), response_from_target.status_code

        except requests.exceptions.HTTPError as e:
            error_msg = f"目标 API HTTP 错误: {e.response.status_code} - {e.response.text}"
            log(error_msg)
            release_transport()
            return jsonify(
                {"error": f"Target API error: {e.response.status_code}", "details": e.response.text}
            ), e.response.status_code
        except requests.exceptions.RequestException as e:
            error_msg = f"连接目标 API 时出错: {e}"
            log(error_msg)
            release_transport()
            return jsonify({"error": f"Error contacting target API: {str(e)}"}), 503
        except Exception as e:
            error_msg = f"发生意外错误: {e}"
            log(error_msg)
            release_transport()
            return jsonify({"error": "An internal server error occurred"}), 500


__all__ = ["ProxyApp"]
