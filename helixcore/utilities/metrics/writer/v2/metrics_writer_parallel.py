import logging
from logging import Logger
from types import TracebackType
from typing import Any, Dict, List, Type, Sequence, Optional, Tuple, override

from helixtelemetry.telemetry.metrics.telemetry_counter import (
    TelemetryCounter,
)
from helixtelemetry.telemetry.structures.telemetry_parent import (
    TelemetryParent,
)
from helixtelemetry.telemetry.spans.telemetry_span_creator import (
    TelemetrySpanCreator,
)

from helixcore.utilities.async_safe_buffer.v1.async_safe_buffer import AsyncSafeBuffer
from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.utilities.metrics.writer.base_metrics_writer_async import (
    BaseMetricsWriterAsync,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)
from helixcore.utilities.mysql.my_sql_writer.v2.my_sql_writer import MySqlWriter


class MetricsWriterParallel(BaseMetricsWriterAsync):
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
        :param parameters: parameters for the metrics writer
        """
        super().__init__(
            logger=logger,
            parameters=parameters,
            telemetry_span_creator=telemetry_span_creator,
        )
        self.my_sql_writer: Optional[MySqlWriter] = None
        self.metrics_buffer: AsyncSafeBuffer[str, BaseMetric] = AsyncSafeBuffer()

    @override
    async def __aenter__(self) -> "MetricsWriterParallel":
        self.my_sql_writer = MySqlWriter(
            schema_name=self.schema_name, max_batch_size=self.max_batch_size
        )
        await self.my_sql_writer.open_async()
        return self

    @override
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.flush_async(telemetry_parent=None)
        if self.my_sql_writer is not None:
            await self.my_sql_writer.close_async()

    def _get_table_for_metric_name(self, *, metric_name: str) -> Optional[str]:
        """
        Gets the table for this metrics from the mapping

        :param metric_name: metric name
        :return: table name
        """
        return self.metric_table_map.get(metric_name)

    def _has_table_been_created_for_metric(self, *, metric: BaseMetric) -> bool:
        """
        Checks whether we have already created the table for this metric

        :param metric: metric to check
        :return: True if the table has been created for this metric
        """
        return self.tables_created_for_metric.get(metric.get_name()) or False

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
        assert metric_type, "metric_type should not be None"
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

    async def add_metrics_to_buffer_async(
        self, *, metrics: Sequence[BaseMetric]
    ) -> None:
        """
        Adds metrics to the buffer

        :param metrics: metrics to add to the buffer
        :return: None
        """

        if len(metrics) == 0:
            return

        metrics_with_types: List[Tuple[str, BaseMetric]] = [
            (metric.get_name(), metric) for metric in metrics
        ]
        await self.metrics_buffer.add_list(metrics_with_types)
        if self.logger and self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                f"Added {len(metrics)} metrics to buffer: {set([metric.get_name() for metric in metrics])}"
            )

    async def write_metrics_to_table_async(
        self,
        *,
        metrics: Sequence[BaseMetric],
        telemetry_parent: Optional[TelemetryParent],
    ) -> Optional[int]:
        """
        writes metrics to table if the buffer length is exceeded.  Otherwise, just adds to buffer and returns

        :param metrics:
        :return:
        """
        await self.add_metrics_to_buffer_async(metrics=metrics)

        if self.buffer_length is None:
            result: Optional[int] = await self._write_metrics_unbuffered_to_table_async(
                count=self.buffer_length,
                telemetry_parent=telemetry_parent,
            )
            return result
        else:
            return None

    async def get_count_of_metrics_in_buffer_async(self) -> int:
        """
        Gets the count of metrics in the buffer

        :return: count of metrics in the buffer
        """
        return await self.metrics_buffer.total_items()

    async def get_count_of_metrics_by_type_in_buffer_async(
        self, metric_type: str
    ) -> int:
        """
        Gets the count of metrics in the buffer

        :return: count of metrics in the buffer
        """
        return await self.metrics_buffer.total_items_by_type(metric_type)

    async def flush_async(
        self,
        *,
        telemetry_parent: Optional[TelemetryParent],
    ) -> None:
        count_of_metrics_in_buffer = await self.get_count_of_metrics_in_buffer_async()
        if count_of_metrics_in_buffer > 0:
            async with self.telemetry_span_creator.create_telemetry_span_async(
                name=self.flush_async.__qualname__,
                attributes={
                    TelemetryAttributes.METRIC_COUNT: count_of_metrics_in_buffer
                },
                telemetry_parent=telemetry_parent,
            ):
                if self.logger and self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        f"Flushing metrics buffer.  Count Before: {count_of_metrics_in_buffer}"
                    )
                await self._write_metrics_unbuffered_to_table_async(
                    count=None,
                    telemetry_parent=telemetry_parent,
                )  # write all metrics
                count_of_metrics_in_buffer = (
                    await self.get_count_of_metrics_in_buffer_async()
                )
                if self.logger and self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(
                        f"Flushed metrics buffer. Count After: {count_of_metrics_in_buffer}"
                    )
                assert (
                    count_of_metrics_in_buffer == 0
                ), f"Buffer should be empty after flushing.  Found {count_of_metrics_in_buffer} metrics"

        await self.telemetry_span_creator.flush_async()

    async def _write_metrics_unbuffered_to_table_async(
        self,
        *,
        count: Optional[int],
        telemetry_parent: Optional[TelemetryParent],
    ) -> Optional[int]:
        """
        Writes the data to the table

        :return: number of rows affected
        """
        async with self.telemetry_span_creator.create_telemetry_span_async(
            name=self._write_metrics_unbuffered_to_table_async.__qualname__,
            attributes={TelemetryAttributes.METRIC_COUNT: count or 0},
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
            assert (
                self.my_sql_writer
            ), "my_sql_writer should not be None.  Use this class as a context manager"

            metrics_extracted: Dict[str, List[BaseMetric]] = (
                await self.metrics_buffer.get_up_to(count=count)
                if count is not None
                else await self.metrics_buffer.get_all()
            )

            rows_affected: Optional[int] = None

            metric_type: str
            metrics: List[BaseMetric]
            for metric_type, metrics in metrics_extracted.items():
                if len(metrics) > 0:
                    first_metric: BaseMetric = metrics[0]
                    table_name: Optional[str] = self._get_table_for_metric_name(
                        metric_name=first_metric.get_name()
                    )
                    # if there is no table mapping for this metric, skip it
                    if not table_name:
                        continue

                    columns: List[str] = first_metric.columns

                    assert columns, "columns should not be None"
                    assert len(columns) > 0, "columns should not be empty"

                    if self.parameters.create_metrics_table_if_not_exists:
                        if not self._has_table_been_created_for_metric(
                            metric=first_metric
                        ):
                            await self.create_table_if_not_exists_async(
                                metric_type=type(first_metric),
                                telemetry_parent=telemetry_parent,
                            )

                    data: List[Dict[str, Any]] = [
                        metric.to_dict() for metric in metrics
                    ]

                    rows_affected_by_metric: Optional[int] = (
                        await self.my_sql_writer.write_to_table_async(
                            table_name=table_name,
                            columns=columns,
                            data=data,
                            logger=self.logger,
                            create_table_ddl=first_metric.get_create_ddl(
                                db_schema_name=self.schema_name,
                                db_table_name=table_name,
                            ),
                        )
                    )
                    if self.logger and self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(
                            f"Wrote {rows_affected} metric rows for {metric_type} to the database"
                        )
                    if rows_affected_by_metric is not None:
                        if rows_affected is not None:
                            rows_affected += rows_affected_by_metric
                        else:
                            rows_affected = rows_affected_by_metric

                    metrics_written_counter.add(
                        amount=len(metrics),
                        attributes={
                            TelemetryAttributes.METRIC_TYPE: metric_type,
                            TelemetryAttributes.METRIC_WRITER: self.__class__.__name__,
                        },
                    )

            return rows_affected

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
