from os import environ
from types import TracebackType
from typing import Optional, List, Dict, Any

from helixcore.event_loggers.event_logger import EventLogger
from helixcore.logger.log_level import LogLevel
from helixcore.logger.yarn_logger import get_logger


class MlFlowConfig:
    def __init__(
        self,
        mlflow_tracking_url: str,
        artifact_url: str,
        experiment_name: str,
        flow_run_name: str,
        parameters: Dict[str, Any],
    ):
        self.mlflow_tracking_url = mlflow_tracking_url
        self.artifact_url = artifact_url
        self.experiment_name = experiment_name
        self.flow_run_name = flow_run_name
        self.parameters = parameters

    def clone(self) -> "MlFlowConfig":
        return MlFlowConfig(
            mlflow_tracking_url=self.mlflow_tracking_url,
            artifact_url=self.artifact_url,
            experiment_name=self.experiment_name,
            flow_run_name=self.flow_run_name,
            parameters=self.parameters.copy(),
        )


class ProgressLogger:
    def __init__(
        self,
        event_loggers: Optional[List[EventLogger]] = None,
        mlflow_config: Optional[MlFlowConfig] = None,
    ) -> None:
        self.logger = get_logger(__name__)
        self.event_loggers: Optional[List[EventLogger]] = event_loggers
        self.mlflow_config: Optional[MlFlowConfig] = mlflow_config
        system_log_level_text: Optional[str] = environ.get("LOGLEVEL")
        self.system_log_level: Optional[LogLevel] = (
            LogLevel.from_str(system_log_level_text)
            if system_log_level_text is not None
            else None
        )

    def __enter__(self) -> "ProgressLogger":
        return self

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        pass

    def start_mlflow_run(self, run_name: str, is_nested: bool = True) -> None:
        pass

    # noinspection PyMethodMayBeStatic
    def end_mlflow_run(self, status: Any = None) -> None:
        pass

    def log_metric(
        self,
        name: str,
        time_diff_in_minutes: float,
        log_level: LogLevel = LogLevel.TRACE,
    ) -> None:
        pass

    def log_param(
        self, key: str, value: str, log_level: LogLevel = LogLevel.TRACE
    ) -> None:
        pass

    def log_params(
        self, params: Dict[str, Any], log_level: LogLevel = LogLevel.TRACE
    ) -> None:
        pass

    # noinspection PyUnusedLocal
    def log_artifact(
        self, key: str, contents: str, folder_path: Optional[str] = None
    ) -> None:
        pass

    def write_to_log(
        self, name: str, message: str = "", log_level: LogLevel = LogLevel.INFO
    ) -> bool:
        return True

    def log_exception(self, event_name: str, event_text: str, ex: Exception) -> None:
        self.log_artifact("_exception.txt", str(ex))
        if self.event_loggers:
            for event_logger in self.event_loggers:
                event_logger.log_exception(
                    event_name=event_name, event_text=event_text, ex=ex
                )

    def log_progress_event(
        self,
        event_name: str,
        current: int,
        total: int,
        event_format_string: str,
        backoff: bool = True,
        log_level: LogLevel = LogLevel.TRACE,
    ) -> None:
        self.logger.debug(event_format_string.format(event_name, current, total))
        if not self.system_log_level or self.system_log_level == LogLevel.INFO:
            if (
                log_level == LogLevel.INFO or log_level == LogLevel.ERROR
            ):  # log only INFO messages
                if self.event_loggers:
                    for event_logger in self.event_loggers:
                        event_logger.log_progress_event(
                            event_name=event_name,
                            current=current,
                            total=total,
                            event_format_string=event_format_string,
                            backoff=backoff,
                        )
        else:  # LOGLEVEL is lower than INFO
            if self.event_loggers:
                for event_logger in self.event_loggers:
                    event_logger.log_progress_event(
                        event_name=event_name,
                        current=current,
                        total=total,
                        event_format_string=event_format_string,
                        backoff=backoff,
                    )

    def log_event(
        self, event_name: str, event_text: str, log_level: LogLevel = LogLevel.TRACE
    ) -> None:
        self.write_to_log(name=event_name, message=event_text)
        if not self.system_log_level or self.system_log_level == LogLevel.INFO:
            if (
                log_level == LogLevel.INFO or log_level == LogLevel.ERROR
            ):  # log only INFO messages
                if self.event_loggers:
                    for event_logger in self.event_loggers:
                        event_logger.log_event(
                            event_name=event_name, event_text=event_text
                        )
        else:
            if self.event_loggers:
                for event_logger in self.event_loggers:
                    event_logger.log_event(event_name=event_name, event_text=event_text)
