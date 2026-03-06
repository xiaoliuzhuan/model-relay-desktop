from __future__ import annotations

from collections.abc import Callable
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel
from pytauri import Commands

from modules.actions import model_tests
from modules.runtime.operation_result import OperationResult
from modules.runtime.resource_manager import ResourceManager
from modules.services.config_service import ConfigStore

from .common import build_result_payload, collect_logs


class InlineThreadManager:
    def run(  # noqa: PLR0913
        self,
        name: str,
        target: Callable[..., None],
        *,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
        wait_for: list[str] | None = None,
        allow_parallel: bool = False,
        daemon: bool = True,
    ) -> str:
        _ = (wait_for, allow_parallel, daemon)
        target(*(args or ()), **(kwargs or {}))
        return f"{name}-inline"

    def wait(self, _task_id: str | None, _timeout: float | None = None) -> bool:
        return True


class ConfigGroupTestPayload(BaseModel):
    index: int
    mode: Literal["chat", "models"] = "chat"


class ConfigGroupModelListPayload(BaseModel):
    api_url: str = ""
    model_id: str = ""
    api_key: str = ""
    middle_route: str = ""
    protocol: str = "openai"
    anthropic_version: str = ""


@lru_cache(maxsize=1)
def _get_resource_manager() -> ResourceManager:
    return ResourceManager()


@lru_cache(maxsize=1)
def _get_config_store() -> ConfigStore:
    resource_manager = _get_resource_manager()
    return ConfigStore(resource_manager.get_user_config_file())


def register_model_test_commands(commands: Commands) -> None:
    @commands.command()
    async def config_group_test(body: ConfigGroupTestPayload) -> dict[str, Any]:
        logs, log_func = collect_logs()
        config_store = _get_config_store()
        config_groups, _ = config_store.load_config_groups()
        if not config_groups:
            result = OperationResult.failure("没有可用的配置组")
            return build_result_payload(result, logs, "配置组测活失败")
        if body.index < 0 or body.index >= len(config_groups):
            result = OperationResult.failure("配置组索引无效")
            return build_result_payload(result, logs, "配置组测活失败")
        group_obj: object = config_groups[body.index]
        if not isinstance(group_obj, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            result = OperationResult.failure("配置组格式无效")
            return build_result_payload(result, logs, "配置组测活失败")
        config_group = {str(key): value for key, value in group_obj.items()}

        thread_manager = InlineThreadManager()
        if body.mode == "models":
            model_tests.test_model_in_list(
                config_group,
                log_func=log_func,
                thread_manager=thread_manager,
            )
        else:
            model_tests.test_chat_completion(
                config_group,
                log_func=log_func,
                thread_manager=thread_manager,
            )
        result = OperationResult.success()
        return build_result_payload(result, logs, "配置组测活完成")

    @commands.command()
    async def config_group_models(body: ConfigGroupModelListPayload) -> dict[str, Any]:
        logs, log_func = collect_logs()
        group = {
            "api_url": body.api_url,
            "model_id": body.model_id,
            "api_key": body.api_key,
            "middle_route": body.middle_route,
            "protocol": body.protocol,
            "anthropic_version": body.anthropic_version,
        }
        model_ids, ok = model_tests.fetch_model_list(group, log_func=log_func)
        if not ok:
            result = OperationResult.failure("模型列表获取失败", models=model_ids)
            return build_result_payload(result, logs, "模型列表获取失败")
        result = OperationResult.success(models=model_ids)
        return build_result_payload(result, logs, "模型列表获取完成")

    _ = (config_group_test, config_group_models)
