from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from modules.hosts.file_operability import FileOperabilityReport
from modules.network.network_environment import NetworkEnvironmentReport
from modules.services import startup_checks


@dataclass(frozen=True)
class StartupContext:
    hosts_preflight_report: FileOperabilityReport | None
    network_env_report: NetworkEnvironmentReport | None

    def emit_logs(
        self,
        *,
        log: Callable[[str], None],
        check_environment: Callable[[], tuple[bool, str]],
        is_packaged: Callable[[], bool],
    ) -> startup_checks.StartupReport:
        return startup_checks.emit_startup_logs(
            log=log,
            check_environment=check_environment,
            is_packaged=is_packaged,
            hosts_preflight_report=self.hosts_preflight_report,
            network_env_report=self.network_env_report,
        )


def build_startup_context() -> StartupContext:
    return StartupContext(
        hosts_preflight_report=startup_checks.run_hosts_preflight(),
        network_env_report=startup_checks.run_network_environment_preflight(),
    )
