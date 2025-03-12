from abc import ABC, abstractmethod
from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional

from helixcore.utilities.metrics.base_metrics import BaseMetric


class BaseMetricsWriter(ABC):
    def __init__(
        self,
        *,
        schema_name: str,
        logger: Optional[Logger],
        metric_table_map: Dict[str, Optional[str]],
    ) -> None:
        self.schema_name: str = schema_name
        self.logger: Optional[Logger] = logger
        self.metric_table_map: Dict[str, Optional[str]] = metric_table_map
        self.tables_created_for_metric: Dict[str, bool] = {}
        self.has_database_been_created: bool = False

    @abstractmethod
    def __enter__(self) -> "BaseMetricsWriter":
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        pass

    @abstractmethod
    def create_table_if_not_exists(self, *, metric: BaseMetric) -> None:
        pass

    @abstractmethod
    def write_single_metric_to_table(self, *, metric: BaseMetric) -> Optional[int]:
        pass

    @abstractmethod
    def write_metrics_to_table(self, *, metrics: Sequence[BaseMetric]) -> Optional[int]:
        pass

    @abstractmethod
    def read_metrics_from_table(self, metric: BaseMetric) -> List[Dict[str, Any]]:
        pass
