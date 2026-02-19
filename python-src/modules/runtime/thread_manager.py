"""统一的后台线程管理器，用于跟踪和调度 GUI 中的所有异步任务。"""

from __future__ import annotations

import itertools
import logging
import threading
import time
import traceback
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

TaskFn = Callable[..., None]
Snapshot = dict[str, float | str | None]


@dataclass
class TaskRecord:
    """表示一个受管线程任务的运行状态。"""

    task_id: str
    name: str
    status: str = "pending"
    thread: threading.Thread | None = None
    started_at: float | None = None
    finished_at: float | None = None
    error: str | None = None
    done_event: threading.Event = field(default_factory=threading.Event)

    def snapshot(self) -> Snapshot:
        """返回只读快照，便于 UI 查询。"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }


class ThreadManager:
    """集中管理后台线程，避免重复创建和状态混乱。"""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._tasks_by_name: dict[str, list[str]] = {}
        self._name_locks: dict[str, threading.Lock] = {}
        self._lock = threading.Lock()
        self._counter = itertools.count(1)
        self._logger = logger or logging.getLogger(__name__)

    def _get_name_lock(self, name: str) -> threading.Lock:
        with self._lock:
            lock = self._name_locks.get(name)
            if lock is None:
                lock = threading.Lock()
                self._name_locks[name] = lock
            return lock

    def run(  # noqa: PLR0913
        self,
        name: str,
        target: TaskFn,
        *,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        wait_for: Iterable[str] | None = None,
        allow_parallel: bool = False,
        daemon: bool = True,
    ) -> str:
        """启动一个后台任务并返回 task_id。"""

        args = args or ()
        kwargs = kwargs or {}
        dependencies = [dep for dep in (wait_for or []) if dep]
        task_id = f"{name}-{next(self._counter)}"
        record = TaskRecord(task_id=task_id, name=name)

        def runner() -> None:
            try:
                for dep_id in dependencies:
                    self.wait(dep_id)
                lock = None if allow_parallel else self._get_name_lock(name)
                if lock:
                    with lock:
                        self._execute(record, target, args, kwargs)
                else:
                    self._execute(record, target, args, kwargs)
            finally:
                record.done_event.set()

        thread = threading.Thread(target=runner, daemon=daemon, name=f"mtga-{task_id}")
        record.thread = thread

        with self._lock:
            self._tasks[task_id] = record
            self._tasks_by_name.setdefault(name, []).append(task_id)

        thread.start()
        return task_id

    def _execute(
        self,
        record: TaskRecord,
        target: TaskFn,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        record.status = "running"
        record.started_at = time.time()
        try:
            target(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            record.status = "failed"
            record.error = str(exc)
            self._logger.error("后台任务 %s 失败: %s", record.task_id, exc)
            self._logger.debug("线程堆栈:\n%s", traceback.format_exc())
        else:
            record.status = "finished"
        finally:
            record.finished_at = time.time()

    def wait(self, task_id: str | None, timeout: float | None = None) -> bool:
        """等待指定任务完成，若任务不存在则视为已完成。"""
        if not task_id:
            return True
        record = self._tasks.get(task_id)
        if not record:
            return True
        return record.done_event.wait(timeout=timeout)

    def get_status(
        self,
        *,
        task_id: str | None = None,
        name: str | None = None,
    ) -> Snapshot | None:
        """查询任务状态，可以通过 task_id 或名称获取最新一次运行信息。"""
        record = None
        with self._lock:
            if task_id:
                record = self._tasks.get(task_id)
            elif name:
                ids = self._tasks_by_name.get(name, [])
                if ids:
                    record = self._tasks.get(ids[-1])
        return record.snapshot() if record else None

    def is_running(self, name: str) -> bool:
        """判断某个逻辑任务是否仍在运行。"""
        with self._lock:
            ids = self._tasks_by_name.get(name, [])
            for task_id in reversed(ids):
                record = self._tasks.get(task_id)
                if record and record.thread and record.thread.is_alive():
                    return True
        return False

    def get_active_tasks(self) -> list[Snapshot]:
        """返回所有仍在运行的任务快照，便于诊断。"""
        snapshots: list[Snapshot] = []
        with self._lock:
            for record in self._tasks.values():
                if record.thread and record.thread.is_alive():
                    snapshots.append(record.snapshot())
        return snapshots


__all__ = ["ThreadManager", "TaskRecord"]
