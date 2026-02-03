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
    display_name="MTGA",
    github_repo="BiFangKNT/mtga",
    error_log_filename="mtga_error.log",
    ca_common_name="MTGA_CA",
    api_key_visible_chars=4,
)
