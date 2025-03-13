from logging import Logger
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

import pytest
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin

from helixcore.utilities.data_frame_struct.data_frame_struct_type import (
    DataFrameStructType,
)
from helixcore.utilities.telemetry.telemetry_context import (
    TelemetryContext,
)

from helixcore.utilities.async_safe_buffer.v1.async_safe_buffer import (
    AsyncSafeBuffer,
)
from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)
from helixcore.utilities.metrics.writer.v2.metrics_writer_parallel import (
    MetricsWriterParallel,
)
from helixcore.utilities.mysql.my_sql_writer.v2.my_sql_writer import (
    MySqlWriter,
)
from helixcore.utilities.telemetry.telemetry_factory import TelemetryFactory


@dataclass
class MockMetricA(DataClassJsonMixin, BaseMetric):
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    col1: int
    col2: str

    @property
    def spark_schema(self) -> DataFrameStructType:
        return DataFrameStructType()

    def get_create_ddl(self, db_schema_name: str, db_table_name: str) -> str:
        return f"CREATE TABLE {db_schema_name}.{db_table_name} (col1 INT, col2 VARCHAR(255))"

    @property
    def columns(self) -> List[str]:
        return ["col1", "col2"]


@dataclass
class MockMetricB(DataClassJsonMixin, BaseMetric):
    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    col3: int
    col4: str

    @property
    def spark_schema(self) -> DataFrameStructType:
        return DataFrameStructType()

    def get_create_ddl(self, db_schema_name: str, db_table_name: str) -> str:
        return f"CREATE TABLE {db_schema_name}.{db_table_name} (col3 INT, col4 VARCHAR(255))"

    @property
    def columns(self) -> List[str]:
        return ["col3", "col4"]


@pytest.fixture
def mock_logger() -> Logger:
    return Mock(spec=Logger)


@pytest.fixture
def metric_table_map() -> Dict[str, Optional[str]]:
    return {MockMetricA.__name__: "test_table"}


# Add a new fixture for multiple metric types
@pytest.fixture
def multi_metric_table_map() -> Dict[str, Optional[str]]:
    return {MockMetricA.__name__: "table_a", MockMetricB.__name__: "table_b"}


@pytest.fixture
async def metrics_writer(
    mock_logger: Logger, metric_table_map: Dict[str, Optional[str]]
) -> MetricsWriterParallel:
    writer = MetricsWriterParallel(
        parameters=BaseMetricsWriterParameters(
            schema_name="test_schema",
            metric_table_map=metric_table_map,
            buffer_length=2,
            max_batch_size=None,
        ),
        logger=mock_logger,
        telemetry_span_creator=TelemetryFactory(
            telemetry_context=TelemetryContext.get_null_context()
        ).create_telemetry_span_creator(name="console", log_level="INFO"),
    )
    return writer


@pytest.mark.asyncio
async def test_metrics_writer_initialization(
    metrics_writer: MetricsWriterParallel,
) -> None:
    assert metrics_writer.schema_name == "test_schema"
    assert metrics_writer.buffer_length == 2
    assert metrics_writer.my_sql_writer is None
    assert isinstance(metrics_writer.metrics_buffer, AsyncSafeBuffer)


@pytest.mark.asyncio
async def test_context_manager() -> None:
    mock_logger = Mock(spec=Logger)
    metric_table_map: Dict[str, Optional[str]] = {MockMetricA.__name__: "test_table"}

    async with MetricsWriterParallel(
        parameters=BaseMetricsWriterParameters(
            schema_name="test_schema",
            metric_table_map=metric_table_map,
            buffer_length=None,
            max_batch_size=None,
        ),
        logger=mock_logger,
        telemetry_span_creator=TelemetryFactory(
            telemetry_context=TelemetryContext.get_null_context()
        ).create_telemetry_span_creator(name="console", log_level="INFO"),
    ) as writer:
        assert isinstance(writer.my_sql_writer, MySqlWriter)
        assert writer.my_sql_writer.schema_name == "test_schema"


@pytest.mark.asyncio
async def test_get_table_for_metric(metrics_writer: MetricsWriterParallel) -> None:
    metric = MockMetricA(col1=1, col2="test")
    table_name = metrics_writer._get_table_for_metric(metric=metric)
    assert table_name == "test_table"


@pytest.mark.asyncio
async def test_create_table_if_not_exists_async(
    metrics_writer: MetricsWriterParallel,
) -> None:
    metric = MockMetricA(col1=1, col2="test")

    # Mock MySqlWriter
    metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)

    await metrics_writer.create_table_if_not_exists_async(metric=metric)

    metrics_writer.my_sql_writer.create_database_async.assert_called_once()
    metrics_writer.my_sql_writer.run_query_async.assert_called_once()
    assert metrics_writer.tables_created_for_metric[metric.get_name()] is True


@pytest.mark.asyncio
async def test_write_single_metric_to_table_async(
    metrics_writer: MetricsWriterParallel,
) -> None:
    metric = MockMetricA(col1=1, col2="test")

    with patch.object(metrics_writer, "write_metrics_to_table_async") as mock_write:
        mock_write.return_value = 1
        result = await metrics_writer.write_single_metric_to_table_async(metric=metric)

        assert result == 1
        mock_write.assert_called_once_with(metrics=[metric])


@pytest.mark.asyncio
async def test_add_metrics_to_buffer(metrics_writer: MetricsWriterParallel) -> None:
    metric = MockMetricA(col1=1, col2="test")
    await metrics_writer.add_metrics_to_buffer_async(metrics=[metric])

    assert (
        await metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=metric.get_name()
        )
        == 1
    )
    assert await metrics_writer.metrics_buffer.get_all() == {
        metric.get_name(): [metric]
    }


@pytest.mark.asyncio
async def test_write_metrics_to_table_async_with_buffer(
    metrics_writer: MetricsWriterParallel,
) -> None:
    metric = MockMetricA(col1=1, col2="test")
    metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)

    # Add metrics below buffer length
    result = await metrics_writer.write_metrics_to_table_async(metrics=[metric])
    write_to_table_async_calls = (
        metrics_writer.my_sql_writer.write_to_table_async.call_args_list
    )
    # Assert buffer length is expected (1) and no write calls made
    assert result is None
    assert (
        await metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=metric.get_name()
        )
        == 1
    )
    assert len(write_to_table_async_calls) == 0

    # Add more metrics to exceed buffer length
    await metrics_writer.write_metrics_to_table_async(metrics=[metric, metric])
    await metrics_writer.flush_async()
    # Assert buffer is now empty
    assert (
        await metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=metric.get_name()
        )
        == 0
    )
    # Assert one write call made
    assert len(write_to_table_async_calls) == 1
    # Assert correct table name in write call
    assert (
        write_to_table_async_calls[0].kwargs["table_name"]
        == metrics_writer.metric_table_map["MockMetricA"]
    )
    # Assert correct column names in write call
    assert write_to_table_async_calls[0].kwargs["columns"] == [
        "col1",
        "col2",
    ]
    # Assert correct data written in write call (3 instances of "metric")
    assert write_to_table_async_calls[0].kwargs["data"] == [
        metric.to_dict() for _ in range(0, 3)
    ]


@pytest.mark.asyncio
async def test_read_metrics_from_table_async(
    metrics_writer: MetricsWriterParallel,
) -> None:
    metric = MockMetricA(col1=1, col2="test")
    expected_data = [{"col1": 1, "col2": "test"}]

    metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)
    metrics_writer.my_sql_writer.read_from_table_async.return_value = expected_data

    result = await metrics_writer.read_metrics_from_table_async(metric)

    assert result == expected_data
    metrics_writer.my_sql_writer.read_from_table_async.assert_called_once_with(
        table_name="test_table", columns=metric.columns
    )


@pytest.mark.asyncio
async def test_flush_async(metrics_writer: MetricsWriterParallel) -> None:
    # Mock metric and writer, and add to buffer
    metric = MockMetricA(col1=1, col2="test")
    metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)
    await metrics_writer.add_metrics_to_buffer_async(metrics=[metric])

    # Assert buffer length is expected (1)
    assert (
        await metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=metric.get_name()
        )
        == 1
    )

    # Flush buffer and retrieve mocked writing details
    await metrics_writer.flush_async()
    write_to_table_async_calls = (
        metrics_writer.my_sql_writer.write_to_table_async.call_args_list
    )

    # Assert buffer is now empty
    assert (
        await metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=metric.get_name()
        )
        == 0
    )
    # Assert one write call made
    assert len(write_to_table_async_calls) == 1
    # Assert correct table name in write call
    assert (
        write_to_table_async_calls[0].kwargs["table_name"]
        == metrics_writer.metric_table_map["MockMetricA"]
    )
    # Assert correct column names in write call
    assert write_to_table_async_calls[0].kwargs["columns"] == [
        "col1",
        "col2",
    ]
    # Assert correct data written in write call (3 instances of "metric")
    assert write_to_table_async_calls[0].kwargs["data"] == [metric.to_dict()]


@pytest.fixture
async def multi_metrics_writer(
    mock_logger: Logger, multi_metric_table_map: Dict[str, Optional[str]]
) -> MetricsWriterParallel:
    writer = MetricsWriterParallel(
        parameters=BaseMetricsWriterParameters(
            schema_name="test_schema",
            metric_table_map=multi_metric_table_map,
            buffer_length=3,
            max_batch_size=None,
        ),
        logger=mock_logger,
        telemetry_span_creator=TelemetryFactory(
            telemetry_context=TelemetryContext.get_null_context()
        ).create_telemetry_span_creator(name="console", log_level="INFO"),
    )
    return writer


@pytest.mark.asyncio
async def test_multiple_metric_types_writing(
    multi_metrics_writer: MetricsWriterParallel,
) -> None:
    """Test writing multiple types of metrics"""
    # Create instances of both metric types
    metric_a1 = MockMetricA(col1=1, col2="test")
    metric_a2 = MockMetricA(col1=2, col2="test2")
    metric_b1 = MockMetricB(col3=3, col4="third")
    metric_b2 = MockMetricB(col3=4, col4="fourth")

    # Mock MySqlWriter
    multi_metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)
    multi_metrics_writer.my_sql_writer.write_to_table_async.return_value = 2

    multi_metrics_writer.buffer_length = 4

    # Add metrics to buffer
    await multi_metrics_writer.write_metrics_to_table_async(
        metrics=[metric_a1, metric_a2]
    )
    await multi_metrics_writer.write_metrics_to_table_async(
        metrics=[metric_b1, metric_b2]
    )

    # Verify buffer contents
    assert await multi_metrics_writer.metrics_buffer.total_items() == 4
    assert (
        await multi_metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=MockMetricA.get_name()
        )
        == 2
    ), f"Buffer: {multi_metrics_writer.metrics_buffer}"
    assert (
        await multi_metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=MockMetricB.get_name()
        )
        == 2
    ), f"Buffer: {multi_metrics_writer.metrics_buffer}"

    # Add one more metric to trigger write (buffer_length=5)
    additional_metric = MockMetricA(col1=3, col2="test3")
    await multi_metrics_writer.write_metrics_to_table_async(metrics=[additional_metric])
    await multi_metrics_writer.flush_async()

    # Verify that write_to_table_async was called for both metric types
    calls = multi_metrics_writer.my_sql_writer.write_to_table_async.call_args_list
    assert len(calls) == 2  # Should be called once for each metric type

    # Verify calls for MetricA
    metric_a_call = [call for call in calls if call.kwargs["table_name"] == "table_a"][
        0
    ]
    assert metric_a_call.kwargs["columns"] == ["col1", "col2"]
    assert len(metric_a_call.kwargs["data"]) == 3  # Should have 3 MetricA entries

    # Verify calls for MetricB
    metric_b_call = [call for call in calls if call.kwargs["table_name"] == "table_b"][
        0
    ]
    assert metric_b_call.kwargs["columns"] == ["col3", "col4"]
    assert len(metric_b_call.kwargs["data"]) == 2  # Should have 2 MetricB entries


@pytest.mark.asyncio
async def test_multiple_metric_types_table_creation(
    multi_metrics_writer: MetricsWriterParallel,
) -> None:
    """Test table creation for multiple metric types"""
    metric_a = MockMetricA(col1=1, col2="test")
    metric_b = MockMetricB(col3=3, col4="third")

    multi_metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)

    # Create tables for both metric types
    await multi_metrics_writer.create_table_if_not_exists_async(metric=metric_a)
    await multi_metrics_writer.create_table_if_not_exists_async(metric=metric_b)

    # Verify that create_database_async was called only once
    assert multi_metrics_writer.my_sql_writer.create_database_async.call_count == 1

    # Verify that run_query_async was called twice (once for each table)
    assert multi_metrics_writer.my_sql_writer.run_query_async.call_count == 2

    # Verify that tables were marked as created
    assert (
        multi_metrics_writer.tables_created_for_metric[MockMetricA.get_name()] is True
    )
    assert (
        multi_metrics_writer.tables_created_for_metric[MockMetricB.get_name()] is True
    )


@pytest.mark.asyncio
async def test_multiple_metric_types_flush(
    multi_metrics_writer: MetricsWriterParallel,
) -> None:
    """Test flushing buffer with multiple metric types"""
    metric_a = MockMetricA(col1=1, col2="test")
    metric_b = MockMetricB(col3=3, col4="third")

    multi_metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)
    multi_metrics_writer.my_sql_writer.write_to_table_async.return_value = 1

    # Add metrics to buffer
    await multi_metrics_writer.write_metrics_to_table_async(metrics=[metric_a])
    await multi_metrics_writer.write_metrics_to_table_async(metrics=[metric_b])

    # Verify buffer contents before flush
    assert (
        await multi_metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=MockMetricA.get_name()
        )
        == 1
    )
    assert (
        await multi_metrics_writer.get_count_of_metrics_by_type_in_buffer_async(
            metric_type=MockMetricB.get_name()
        )
        == 1
    )

    # Flush the buffer
    await multi_metrics_writer.flush_async()

    # Verify that write_to_table_async was called for both metric types
    calls = multi_metrics_writer.my_sql_writer.write_to_table_async.call_args_list
    assert len(calls) == 2

    # Verify buffer is empty after flush
    assert await multi_metrics_writer.get_count_of_metrics_in_buffer_async() == 0


@pytest.mark.asyncio
async def test_multiple_metric_types_read(
    multi_metrics_writer: MetricsWriterParallel,
) -> None:
    """Test reading different types of metrics"""
    metric_a = MockMetricA(col1=1, col2="test")
    metric_b = MockMetricB(col3=3, col4="third")

    multi_metrics_writer.my_sql_writer = AsyncMock(spec=MySqlWriter)

    # Set up different return values for different metrics
    metric_a_data = [{"col1": 1, "col2": "test"}]
    metric_b_data = [{"col3": 1, "col4": "test2"}]

    # noinspection PyUnusedLocal
    async def mock_read_from_table_async(
        table_name: str, columns: List[str]
    ) -> List[Dict[str, Any]]:
        if table_name == "table_a":
            return metric_a_data
        elif table_name == "table_b":
            return metric_b_data
        return []

    multi_metrics_writer.my_sql_writer.read_from_table_async.side_effect = (
        mock_read_from_table_async
    )

    # Read both types of metrics
    result_a = await multi_metrics_writer.read_metrics_from_table_async(metric_a)
    result_b = await multi_metrics_writer.read_metrics_from_table_async(metric_b)

    # Verify results
    assert result_a == metric_a_data

    assert result_b == metric_b_data
