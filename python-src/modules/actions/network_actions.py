from __future__ import annotations

from collections.abc import Callable

from modules.network.network_environment import check_network_environment
from modules.runtime.thread_manager import ThreadManager


def run_network_environment_check(
    *,
    log_func: Callable[[str], None],
    thread_manager: ThreadManager,
) -> None:
    def task() -> None:
        log_func("开始检查网络环境...")
        report = check_network_environment(
            log_func=log_func,
            emit_logs=True,
        )
        if report.explicit_proxy_detected:
            log_func("⚠️ 检测到显式代理配置，hosts 导流可能被绕过。\n" + "⚠️" * 21)
            return
        log_func("✅ 未检测到系统/环境变量层面的显式代理配置。")
        log_func(
            "ℹ️ 若仍无法连接，请检查 Trae 的代理设置，"
            "或是否启用了 TUN/VPN/安全软件网络防护。"
        )

    thread_manager.run("network_env_check", task)
