from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from modules.proxy.proxy_config import (
    ANTHROPIC_MESSAGES_PROTOCOL,
    DEFAULT_ANTHROPIC_VERSION,
)

type LogFunc = Callable[[str], None]


@dataclass(frozen=True)
class ProxyAuth:
    mtga_auth_key: str = ""

    @staticmethod
    def _extract_token(auth_header: str | None, x_api_key: str | None = None) -> str:
        if auth_header:
            return auth_header[7:] if auth_header.startswith("Bearer ") else auth_header
        return (x_api_key or "").strip()

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
