from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AppMetadata:
    display_name: str
    github_repo: str
    error_log_filename: str
    ca_common_name: str
    api_key_visible_chars: int


DEFAULT_METADATA = AppMetadata(
    display_name="Model Relay Desktop",
    github_repo="xiaoliuzhuan/model-relay-desktop",
    error_log_filename="model_relay_desktop_error.log",
    ca_common_name="MODEL_RELAY_DESKTOP_CA",
    api_key_visible_chars=4,
)
