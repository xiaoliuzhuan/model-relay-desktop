from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from modules.cert.cert_utils import normalize_fingerprint
from modules.runtime.resource_manager import ResourceManager


def _to_unix_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _format_utc_iso(unix_ts: int) -> str:
    return datetime.fromtimestamp(unix_ts, tz=UTC).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def build_ca_info(fingerprint_sha1: str, not_after_unix: int) -> dict[str, object]:
    normalized = normalize_fingerprint(fingerprint_sha1)
    return {
        "fingerprint_sha1": normalized,
        "not_after_unix": int(not_after_unix),
        "not_after_utc": _format_utc_iso(int(not_after_unix)),
    }


def load_ca_info(resource_manager: ResourceManager, log_func=print) -> dict[str, object] | None:
    path = resource_manager.get_ca_info_file()
    if not os.path.exists(path):
        log_func(f"未找到 CA 元数据文件: {path}")
        return None

    try:
        with open(path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception as exc:  # noqa: BLE001
        log_func(f"读取 CA 元数据失败: {exc}")
        return None
    if not isinstance(payload, dict):
        log_func("CA 元数据格式无效：不是对象")
        return None

    fingerprint = normalize_fingerprint(payload.get("fingerprint_sha1"))
    not_after_unix = _to_unix_int(payload.get("not_after_unix"))

    if not fingerprint or not_after_unix is None:
        log_func("CA 元数据缺少指纹或到期时间")
        return None

    return build_ca_info(fingerprint, not_after_unix)


def save_ca_info(
    resource_manager: ResourceManager,
    *,
    fingerprint_sha1: str,
    not_after_unix: int,
    log_func=print,
) -> bool:
    normalized = normalize_fingerprint(fingerprint_sha1)
    if not normalized:
        log_func("CA 元数据写入失败: 指纹为空")
        return False

    unix_value = _to_unix_int(not_after_unix)
    if unix_value is None:
        log_func("CA 元数据写入失败: 到期时间为空")
        return False

    path = resource_manager.get_ca_info_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = build_ca_info(normalized, unix_value)

    try:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
    except Exception as exc:  # noqa: BLE001
        log_func(f"写入 CA 元数据失败: {exc}")
        return False

    log_func(f"已写入 CA 元数据: {path}")
    return True


__all__ = ["build_ca_info", "load_ca_info", "save_ca_info"]
