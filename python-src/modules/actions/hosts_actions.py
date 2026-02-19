from __future__ import annotations

from collections.abc import Callable

from modules.runtime.operation_result import OperationResult
from modules.runtime.result_messages import describe_result
from modules.runtime.thread_manager import ThreadManager

type ModifyHostsFileFn = Callable[..., OperationResult]
type OpenHostsFileFn = Callable[..., OperationResult]


class HostsTaskRunner:
    def __init__(
        self,
        *,
        log_func: Callable[[str], None],
        thread_manager: ThreadManager,
        modify_hosts_file: ModifyHostsFileFn,
        open_hosts_file: OpenHostsFileFn,
    ) -> None:
        self._log = log_func
        self._thread_manager = thread_manager
        self._modify_hosts_file = modify_hosts_file
        self._open_hosts_file = open_hosts_file
        self._hosts_task_id: str | None = None

    def modify_hosts(self, action: str = "add", *, block: bool = False) -> str | None:
        def task() -> None:
            action_names = {"add": "修改", "remove": "移除", "backup": "备份", "restore": "还原"}
            action_name = action_names.get(action, action)
            self._log(f"开始{action_name} hosts文件...")
            ip_tuple: tuple[str, str] = ("127.0.0.1", "::1")
            result = self._modify_hosts_file(action=action, ip=ip_tuple, log_func=self._log)
            if result.ok:
                self._log(f"✅ hosts文件{action_name}完成")
            else:
                message = describe_result(result, f"hosts文件{action_name}失败")
                self._log(f"❌ {message}")

        if block:
            self._thread_manager.wait(self._hosts_task_id)
            self._hosts_task_id = None
            task()
            return None

        wait_targets = [self._hosts_task_id] if self._hosts_task_id else None
        self._hosts_task_id = self._thread_manager.run(
            "hosts_manage",
            task,
            wait_for=wait_targets,
        )
        return self._hosts_task_id

    def open_hosts(self) -> None:
        def task() -> None:
            self._log("正在打开hosts文件...")
            result = self._open_hosts_file(log_func=self._log)
            if result.ok:
                self._log("✅ hosts文件已打开")
            else:
                message = describe_result(result, "打开hosts文件失败")
                self._log(f"❌ {message}")

        self._thread_manager.run("hosts_open", task)
