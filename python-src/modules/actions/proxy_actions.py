from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from modules.runtime.operation_result import OperationResult
from modules.runtime.result_messages import describe_result
from modules.runtime.thread_manager import ThreadManager


@dataclass(frozen=True)
class ProxyTaskDependencies:
    ensure_global_config_ready: Callable[[], bool]
    build_proxy_config: Callable[[], dict[str, Any] | None]
    get_current_config: Callable[[], dict[str, Any]]
    restart_proxy: Callable[..., OperationResult]
    stop_proxy_and_restore: Callable[..., OperationResult]
    has_existing_ca_cert: Callable[..., bool]
    generate_certificates: Callable[..., bool]
    install_ca_cert: Callable[..., bool]
    modify_hosts_file: Callable[..., OperationResult]
    ca_common_name: str


class ProxyTaskRunner:
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        thread_manager: ThreadManager,
        deps: ProxyTaskDependencies,
    ) -> None:
        self._log = log_func
        self._thread_manager = thread_manager
        self._deps = deps
        self.proxy_start_task_id = None
        self.proxy_stop_task_id = None

    def start_proxy(self) -> str | None:
        if not self._deps.ensure_global_config_ready():
            return None

        def task() -> None:
            config = self._deps.build_proxy_config()
            if not config:
                return
            self._deps.restart_proxy(config)

        wait_targets = [self.proxy_stop_task_id] if self.proxy_stop_task_id else None
        self.proxy_start_task_id = self._thread_manager.run(
            "proxy_start",
            task,
            wait_for=wait_targets,
        )
        return self.proxy_start_task_id

    def stop_proxy(self) -> str | None:
        def task() -> None:
            self._deps.stop_proxy_and_restore(show_idle_message=True)

        wait_targets = [self.proxy_start_task_id] if self.proxy_start_task_id else None
        self.proxy_stop_task_id = self._thread_manager.run(
            "proxy_stop",
            task,
            wait_for=wait_targets,
        )
        return self.proxy_stop_task_id

    def start_all(self) -> str | None:
        if not self._deps.ensure_global_config_ready():
            return None

        def task() -> None:
            self._thread_manager.wait(self.proxy_start_task_id)
            self._thread_manager.wait(self.proxy_stop_task_id)

            current_config = self._deps.get_current_config()
            if not current_config:
                self._log("❌ 错误: 没有可用的配置组")
                return

            self._log("=== 开始一键启动全部服务 ===")

            self._log("步骤 1/4: 生成证书")
            has_existing_ca = self._deps.has_existing_ca_cert(
                self._deps.ca_common_name,
                log_func=self._log,
            )
            if has_existing_ca:
                self._log(
                    f"检测到系统已存在 CA 证书 ({self._deps.ca_common_name})，跳过证书生成和安装"
                )
                self._log("ℹ️ 如有需要，请手动执行生成和安装")
                self._log("步骤 2/4: 安装CA证书（已跳过）")
            else:
                if not self._deps.generate_certificates(
                    log_func=self._log,
                    ca_common_name=self._deps.ca_common_name,
                ):
                    self._log("❌ 生成证书失败，无法继续")
                    return

                self._log("步骤 2/4: 安装CA证书")
                if not self._deps.install_ca_cert(log_func=self._log):
                    self._log("❌ 安装CA证书失败，无法继续")
                    return

            self._log("步骤 3/4: 修改hosts文件")
            modify_result = self._deps.modify_hosts_file(log_func=self._log)
            if not modify_result.ok:
                message = describe_result(modify_result, "修改hosts文件失败，无法继续")
                self._log(f"❌ {message}")
                return

            self._log("步骤 4/4: 启动代理服务器")
            config = self._deps.build_proxy_config()
            if not config:
                return
            restart_result = self._deps.restart_proxy(
                config,
                success_message="✅ 全部服务启动成功",
                hosts_modified=modify_result.ok,
            )
            if restart_result.ok:
                return
            self._log("❌ 全部服务启动失败：代理服务器未能启动")

        return self._thread_manager.run("start_all", task)
