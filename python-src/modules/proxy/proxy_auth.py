from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from modules.proxy.proxy_config import (
    ANTHROPIC_MESSAGES_PROTOCOL,
    DEFAULT_ANTHROPIC_VERSION,
)

type LogFunc = Callable[[str], None]

BEARER_PARTS_COUNT = 2


@dataclass(frozen=True)
class ProxyAuth:
    mtga_auth_key: str = ""

    @staticmethod
    def _normalize_token(value: str) -> str:
        token = value.strip()
        if len(token) >= BEARER_PARTS_COUNT and token[0] == token[-1] and token[0] in {'"', "'"}:
            token = token[1:-1].strip()
        return token

    @classmethod
    def _extract_token(cls, auth_header: str | None, x_api_key: str | None = None) -> str:
        auth_value = (auth_header or "").strip()
        if auth_value:
            parts = auth_value.split(None, 1)
            if len(parts) == BEARER_PARTS_COUNT and parts[0].lower() == "bearer":
                return cls._normalize_token(parts[1])
            return cls._normalize_token(auth_value)
        return cls._normalize_token(x_api_key or "")

    def verify(self, auth_header: str | None, x_api_key: str | None = None) -> bool:
        provided_key = self._extract_token(auth_header, x_api_key)
        if not provided_key:
            return False
        if not self.mtga_auth_key:
            return True
        return provided_key == self.mtga_auth_key

    def build_forward_headers(  # noqa: PLR0913
        self,
        auth_header: str | None,
        api_key: str,
        *,
        protocol: str,
        anthropic_version: str | None = None,
        request_headers: Mapping[str, str] | None = None,
        x_api_key: str | None = None,
        log_func: LogFunc = print,
    ) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        effective_api_key = (api_key or "").strip() or self._extract_token(auth_header, x_api_key)

        if protocol == ANTHROPIC_MESSAGES_PROTOCOL:
            if effective_api_key:
                headers["x-api-key"] = effective_api_key
                log_func("使用 Anthropic x-api-key 转发")
            version = (anthropic_version or "").strip() or DEFAULT_ANTHROPIC_VERSION
            headers["anthropic-version"] = version
            if request_headers is not None:
                anthropic_beta = request_headers.get("anthropic-beta")
                if anthropic_beta:
                    headers["anthropic-beta"] = anthropic_beta
            return headers

        if effective_api_key:
            headers["Authorization"] = f"Bearer {effective_api_key}"
            log_func("使用 OpenAI Authorization 转发")

        return headers


__all__ = ["ProxyAuth"]
