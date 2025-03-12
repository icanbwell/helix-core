from abc import ABC, abstractmethod
from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional

from helixcore.utilities.telemetry.telemetry_span_creator import (
    TelemetrySpanCreator,
)
from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)


class BaseMetricsWriterAsync(ABC):
    def __init__(
        self,
        *,
        parameters: BaseMetricsWriterParameters,
        logger: Optional[Logger],
        telemetry_span_creator: TelemetrySpanCreator,
    ) -> None:
        assert parameters is not None, "parameters should not be None"
        assert isinstance(
            parameters, BaseMetricsWriterParameters
        ), "parameters should be an instance of BaseMetricsWriterParameters"
        assert (
            telemetry_span_creator is not None
        ), "telemetry_span_creator should not be None"

        self.logger: Optional[Logger] = logger

        self.schema_name: str = parameters.schema_name
        self.metric_table_map: Dict[str, Optional[str]] = parameters.metric_table_map
        self.tables_created_for_metric: Dict[str, bool] = {}
        self.has_database_been_created: bool = False
        self.buffer_length: Optional[int] = parameters.buffer_length
        self.max_batch_size: Optional[int] = parameters.max_batch_size
        self.telemetry_span_creator: TelemetrySpanCreator = telemetry_span_creator

    @abstractmethod
    async def __aenter__(self) -> "BaseMetricsWriterAsync":
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass

    @abstractmethod
    async def create_table_if_not_exists_async(self, *, metric: BaseMetric) -> None:
        pass

    @abstractmethod
    async def write_single_metric_to_table_async(
        self, *, metric: BaseMetric
    ) -> Optional[int]:
        pass

    @abstractmethod
    async def write_metrics_to_table_async(
        self, *, metrics: Sequence[BaseMetric]
    ) -> Optional[int]:
        pass

    @abstractmethod
    async def read_metrics_from_table_async(
        self, metric: BaseMetric
    ) -> List[Dict[str, Any]]:
        pass
