from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional, override

from helixcore.utilities.telemetry.telemetry_span_creator import (
    TelemetrySpanCreator,
)
from helixcore.utilities.metrics.base_metrics import (
    BaseMetric,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_async import (
    BaseMetricsWriterAsync,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)
from helixcore.utilities.mysql.my_sql_writer.v2.my_sql_writer import (
    MySqlWriter,
)


class MetricsWriter(BaseMetricsWriterAsync):
    def __init__(
        self,
        *,
        parameters: BaseMetricsWriterParameters,
        logger: Optional[Logger],
        telemetry_span_creator: TelemetrySpanCreator,
    ) -> None:
        """
        This class writes metrics to the database

        :param logger: logger to use
        :param parameters: parameters for the metrics writer"""
        super().__init__(
            parameters=parameters,
            logger=logger,
            telemetry_span_creator=telemetry_span_creator,
        )
        self.my_sql_writer: Optional[MySqlWriter] = None

    @override
    async def __aenter__(self) -> "MetricsWriter":
        self.my_sql_writer = MySqlWriter(schema_name=self.schema_name, max_batch_size=0)
        await self.my_sql_writer.open_async()
        return self

    @override
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self.my_sql_writer is not None:
            await self.my_sql_writer.close_async()

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

    @override
    async def create_table_if_not_exists_async(self, *, metric: BaseMetric) -> None:
        """
        Creates the table if it does not exist

        :param metric: metric to create the table for

        :return: None
        """
        async with self.telemetry_span_creator.create_telemetry_span(
            name="create_table_if_not_exists_async",
            attributes={"metric": metric.get_name()},
        ):
            assert metric, "metric should not be None"

            assert (
                self.my_sql_writer
            ), "my_sql_writer should not be None.  Use this class as a context manager"

            table_name: Optional[str] = self._get_table_for_metric(metric=metric)
            if not table_name:
                return

            create_ddl: str = metric.get_create_ddl(
                db_schema_name=self.schema_name, db_table_name=table_name
            )
            assert create_ddl, "create_ddl should not be None"

            if not self.has_database_been_created:
                await self.my_sql_writer.create_database_async(logger=self.logger)
                self.has_database_been_created = True

            await self.my_sql_writer.run_query_async(
                query=create_ddl, logger=self.logger
            )
            self.tables_created_for_metric[metric.get_name()] = True

    @override
    async def write_single_metric_to_table_async(
        self, *, metric: BaseMetric
    ) -> Optional[int]:
        """
        Writes a single metric to the database

        :param metric: metric to write
        :return: number of rows affected
        """
        return await self.write_metrics_to_table_async(metrics=[metric])

    @override
    async def write_metrics_to_table_async(
        self, *, metrics: Sequence[BaseMetric]
    ) -> Optional[int]:
        """
        Writes the data to the table

        :param metrics: list of metrics to write
        :return: number of rows affected
        """
        assert metrics is not None, "metrics should not be None"

        assert (
            self.my_sql_writer
        ), "my_sql_writer should not be None.  Use this class as a context manager"

        if not any(metrics):
            return 0  # nothing to do

        first_metric: BaseMetric = next(iter(metrics))
        assert first_metric, "first_metric should not be None"

        async with self.telemetry_span_creator.create_telemetry_span(
            name="write_metrics_to_table_async",
            attributes={
                "metric": first_metric.get_name(),
                "number_of_metrics": len(metrics),
            },
        ):

            columns: List[str] = first_metric.columns

            assert columns, "columns should not be None"
            table_name: Optional[str] = self._get_table_for_metric(metric=first_metric)
            if not table_name:
                return 0

            assert len(columns) > 0, "columns should not be empty"
            if not self._has_table_been_created_for_metric(metric=first_metric):
                await self.create_table_if_not_exists_async(metric=first_metric)

            data: List[Dict[str, Any]] = [metric.to_dict() for metric in metrics]

            rows_affected: Optional[int] = (
                await self.my_sql_writer.write_to_table_async(
                    table_name=table_name,
                    columns=columns,
                    data=data,
                    logger=self.logger,
                    create_table_ddl=first_metric.get_create_ddl(
                        db_schema_name=self.schema_name, db_table_name=table_name
                    ),
                )
            )

            return rows_affected

    @override
    async def read_metrics_from_table_async(
        self, metric: BaseMetric
    ) -> List[Dict[str, Any]]:
        """
        Reads the data from the table

        :param metric:
        :return: data read from the table
        """
        async with self.telemetry_span_creator.create_telemetry_span(
            name="read_metrics_from_table_async",
            attributes={"metric": metric.get_name()},
        ):
            assert (
                self.my_sql_writer
            ), "my_sql_writer should not be None.  Use this class as a context manager"

            table_name = self._get_table_for_metric(metric=metric)
            if not table_name:
                return []

            return await self.my_sql_writer.read_from_table_async(
                table_name=table_name, columns=metric.columns
            )
