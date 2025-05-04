from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional, override

from helixtelemetry.telemetry.metrics.telemetry_counter import (
    TelemetryCounter,
)
from helixtelemetry.telemetry.structures.telemetry_parent import (
    TelemetryParent,
)
from helixtelemetry.telemetry.spans.telemetry_span_creator import (
    TelemetrySpanCreator,
)

from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.utilities.metrics.writer.base_metrics_writer_async import (
    BaseMetricsWriterAsync,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)
from helixcore.utilities.mysql.my_sql_writer.v2.my_sql_writer import MySqlWriter
from helixcore.utilities.telemetry.telemetry_attributes import TelemetryAttributes
from helixcore.utilities.telemetry.telemetry_metric_names import TelemetryMetricNames


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

    def _get_table_for_metric_name(self, *, metric_name: str) -> Optional[str]:
        """
        Gets the table for this metrics from the mapping

        :param metric_name: metric name to get the table for
        :return: table name
        """
        assert metric_name
        if metric_name in self.metric_table_map:
            return self.metric_table_map[metric_name]
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
    async def create_table_if_not_exists_async(
        self,
        *,
        metric_type: Type[BaseMetric],
        telemetry_parent: Optional[TelemetryParent],
    ) -> None:
        """
        Creates the table if it does not exist

        :param metric_type: metric type to create the table for
        :param telemetry_parent: telemetry parent

        :return: None
        """
        assert metric_type, "metric type should not be None"

        metric_name: str = metric_type.get_name()

        assert (
            self.my_sql_writer
        ), "my_sql_writer should not be None.  Use this class as a context manager"

        table_name: Optional[str] = self._get_table_for_metric_name(
            metric_name=metric_name
        )
        if not table_name:
            return

        async with self.telemetry_span_creator.create_telemetry_span_async(
            name=self.create_table_if_not_exists_async.__qualname__,
            attributes={TelemetryAttributes.METRIC_TYPE: metric_name},
            telemetry_parent=telemetry_parent,
        ):
            create_ddl: str = metric_type.get_create_ddl(
                db_schema_name=self.schema_name, db_table_name=table_name
            )
            assert create_ddl, "create_ddl should not be None"

            if not self.has_database_been_created:
                await self.my_sql_writer.create_database_async(logger=self.logger)
                self.has_database_been_created = True

            await self.my_sql_writer.run_query_async(
                query=create_ddl, logger=self.logger
            )
            self.tables_created_for_metric[metric_name] = True

    @override
    async def write_single_metric_to_table_async(
        self, *, metric: BaseMetric, telemetry_parent: Optional[TelemetryParent]
    ) -> Optional[int]:
        """
        Writes a single metric to the database

        :param metric: metric to write
        :param telemetry_parent: telemetry parent
        :return: number of rows affected
        """
        return await self.write_metrics_to_table_async(
            metrics=[metric], telemetry_parent=telemetry_parent
        )

    @override
    async def write_metrics_to_table_async(
        self,
        *,
        metrics: Sequence[BaseMetric],
        telemetry_parent: Optional[TelemetryParent],
    ) -> Optional[int]:
        """
        Writes the data to the table

        :param metrics: list of metrics to write
        :param telemetry_parent: telemetry parent
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

        metric_type = first_metric.get_name()
        async with self.telemetry_span_creator.create_telemetry_span_async(
            name=self.write_metrics_to_table_async.__qualname__,
            attributes={
                TelemetryAttributes.METRIC_TYPE: metric_type,
                TelemetryAttributes.METRIC_COUNT: len(metrics),
            },
            telemetry_parent=telemetry_parent,
        ):
            metrics_written_counter: TelemetryCounter = (
                self.telemetry_span_creator.get_telemetry_counter(
                    name=TelemetryMetricNames.PROA_METRIC_WRITTEN_COUNT,
                    unit="1",
                    description="Number of metrics written",
                    telemetry_parent=telemetry_parent,
                    attributes={
                        TelemetryAttributes.SOURCE: self.__class__.__qualname__
                    },
                )
            )
            columns: List[str] = first_metric.columns

            assert columns, "columns should not be None"
            table_name: Optional[str] = self._get_table_for_metric_name(
                metric_name=metric_type
            )
            if not table_name:
                return 0

            assert len(columns) > 0, "columns should not be empty"

            if self.parameters.create_metrics_table_if_not_exists:
                if not self._has_table_been_created_for_metric(metric=first_metric):
                    await self.create_table_if_not_exists_async(
                        metric_type=type(first_metric),
                        telemetry_parent=telemetry_parent,
                    )

            data: List[Dict[str, Any]] = [metric.to_dict() for metric in metrics]

            metrics_written_counter.add(
                amount=len(metrics),
                attributes={
                    TelemetryAttributes.METRIC_TYPE: metric_type,
                    TelemetryAttributes.METRIC_WRITER: self.__class__.__name__,
                },
            )

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
        self,
        *,
        metric: BaseMetric,
        telemetry_parent: Optional[TelemetryParent],
    ) -> List[Dict[str, Any]]:
        """
        Reads the data from the table

        :param metric:
        :param telemetry_parent: telemetry parent
        :return: data read from the table
        """
        async with self.telemetry_span_creator.create_telemetry_span_async(
            name=self.read_metrics_from_table_async.__qualname__,
            attributes={TelemetryAttributes.METRIC_TYPE: metric.get_name()},
            telemetry_parent=telemetry_parent,
        ):
            assert (
                self.my_sql_writer
            ), "my_sql_writer should not be None.  Use this class as a context manager"

            table_name = self._get_table_for_metric_name(metric_name=metric.get_name())
            if not table_name:
                return []

            return await self.my_sql_writer.read_from_table_async(
                table_name=table_name, columns=metric.columns
            )
