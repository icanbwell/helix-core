from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional

from helixcore.utilities.metrics.base_metrics import (
    BaseMetric,
)
from helixcore.utilities.metrics.writer.base_metrics_writer import (
    BaseMetricsWriter,
)
from helixcore.utilities.mysql.my_sql_writer.my_sql_writer import (
    MySqlWriter,
)


class MetricsWriter(BaseMetricsWriter):
    def __init__(
        self,
        *,
        schema_name: str,
        logger: Optional[Logger],
        metric_table_map: Dict[str, Optional[str]],
    ) -> None:
        """
        This class writes metrics to the database

        :param schema_name: name of the schema to write to
        :param logger: logger to use
        :param metric_table_map: mapping of metric to table name
        """
        super().__init__(
            schema_name=schema_name,
            logger=logger,
            metric_table_map=metric_table_map,
        )
        self.my_sql_writer: Optional[MySqlWriter] = None

    def __enter__(self) -> "MetricsWriter":
        self.my_sql_writer = MySqlWriter(schema_name=self.schema_name)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self.my_sql_writer is not None:
            self.my_sql_writer.close()

    def _get_table_for_metric(self, *, metric: BaseMetric) -> Optional[str]:
        """
        Gets the table for this metrics from the mapping

        :param metric: metric to get the table for
        :return: table name
        """
        if metric.get_name() in self.metric_table_map:
            return self.metric_table_map[metric.get_name()]
        return None

    def _has_table_been_created_for_metric(self, *, metric: BaseMetric) -> bool:
        """
        Checks whether we have already created the table for this metric

        :param metric: metric to check
        :return: True if the table has been created for this metric
        """
        if metric.get_name() in self.tables_created_for_metric:
            return self.tables_created_for_metric[metric.get_name()]
        return False

    def create_table_if_not_exists(self, *, metric: BaseMetric) -> None:
        """
        Creates the table if it does not exist

        :param metric: metric to create the table for
        :return: None
        """
        assert (
            self.my_sql_writer is not None
        ), "my_sql_writer should not be None.   Use this class as a context manager: `with MetricsWriter(...) as writer:`"
        assert metric, "metric should not be None"
        table_name: Optional[str] = self._get_table_for_metric(metric=metric)
        if not table_name:
            return

        create_ddl: str = metric.get_create_ddl(
            db_schema_name=self.schema_name, db_table_name=table_name
        )
        assert create_ddl, "create_ddl should not be None"

        if not self.has_database_been_created:
            self.my_sql_writer.create_database(logger=self.logger)
            self.has_database_been_created = True

        self.my_sql_writer.run_query(query=create_ddl, logger=self.logger)
        self.tables_created_for_metric[metric.get_name()] = True

    def write_single_metric_to_table(self, *, metric: BaseMetric) -> Optional[int]:
        """
        Writes a single metric to the database

        :param metric: metric to write
        :return: number of rows affected
        """
        assert (
            self.my_sql_writer is not None
        ), "my_sql_writer should not be None.   Use this class as a context manager: `with MetricsWriter(...) as writer:`"
        return self.write_metrics_to_table(metrics=[metric])

    def write_metrics_to_table(self, *, metrics: Sequence[BaseMetric]) -> Optional[int]:
        """
        Writes the data to the table

        :param metrics: list of metrics to write
        :return: number of rows affected
        """
        assert (
            self.my_sql_writer is not None
        ), "my_sql_writer should not be None.   Use this class as a context manager: `with MetricsWriter(...) as writer:`"
        assert metrics is not None, "metrics should not be None"
        if not any(metrics):
            return 0  # nothing to do

        first_metric: BaseMetric = next(iter(metrics))
        assert first_metric, "first_metric should not be None"

        columns: List[str] = first_metric.columns

        assert columns, "columns should not be None"
        table_name: Optional[str] = self._get_table_for_metric(metric=first_metric)
        if not table_name:
            return 0

        assert len(columns) > 0, "columns should not be empty"

        if not self._has_table_been_created_for_metric(metric=first_metric):
            self.create_table_if_not_exists(metric=first_metric)

        data: List[Dict[str, Any]] = [metric.to_dict() for metric in metrics]

        rows_affected: Optional[int] = self.my_sql_writer.write_to_table(
            table_name=table_name, columns=columns, data=data, logger=self.logger
        )

        return rows_affected

    def read_metrics_from_table(self, metric: BaseMetric) -> List[Dict[str, Any]]:
        assert (
            self.my_sql_writer is not None
        ), "my_sql_writer should not be None.   Use this class as a context manager: `with MetricsWriter(...) as writer:`"
        table_name = self._get_table_for_metric(metric=metric)
        if not table_name:
            return []

        return self.my_sql_writer.read_from_table(
            table_name=table_name, columns=metric.columns
        )

    async def create_table_if_not_exists_async(self, *, metric: BaseMetric) -> None:
        raise NotImplementedError(
            "use sync functions instead of async.  If you want async functions use v2 MetricsWriter"
        )

    async def write_single_metric_to_table_async(
        self, *, metric: BaseMetric
    ) -> Optional[int]:
        raise NotImplementedError(
            "use sync functions instead of async.  If you want async functions use v2 MetricsWriter"
        )

    async def write_metrics_to_table_async(
        self, *, metrics: Sequence[BaseMetric]
    ) -> Optional[int]:
        raise NotImplementedError(
            "use sync functions instead of async.  If you want async functions use v2 MetricsWriter"
        )

    async def read_metrics_from_table_async(
        self, metric: BaseMetric
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError(
            "use sync functions instead of async.  If you want async functions use v2 MetricsWriter"
        )
