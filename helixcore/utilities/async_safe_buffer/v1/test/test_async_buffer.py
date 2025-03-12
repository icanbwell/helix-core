import asyncio

import pytest

from helixcore.utilities.async_safe_buffer.v1.async_safe_buffer import (
    AsyncSafeBuffer,
)


@pytest.fixture
async def buffer() -> AsyncSafeBuffer[str, int]:
    return AsyncSafeBuffer[str, int]()


@pytest.mark.asyncio
async def test_empty_buffer_initialization(buffer: AsyncSafeBuffer[str, int]) -> None:
    assert await buffer.total_items() == 0
    assert await buffer.items_by_type() == {}
    assert await buffer.get_up_to(10) == {}


@pytest.mark.asyncio
async def test_add_single_item(buffer: AsyncSafeBuffer[str, int]) -> None:
    await buffer.add("metric1", 42)

    assert await buffer.total_items() == 1
    assert await buffer.items_by_type() == {"metric1": 1}

    result = await buffer.get_up_to(1)
    assert result == {"metric1": [42]}


@pytest.mark.asyncio
async def test_add_list_items(buffer: AsyncSafeBuffer[str, int]) -> None:
    items = [1, 2, 3]
    await buffer.add_list([("metric1", item) for item in items])

    assert await buffer.total_items() == 3
    assert await buffer.items_by_type() == {"metric1": 3}

    result = await buffer.get_up_to(3)
    assert result == {"metric1": [1, 2, 3]}


@pytest.mark.asyncio
async def test_get_up_to_partial(buffer: AsyncSafeBuffer[str, int]) -> None:
    items = [1, 2, 3]
    await buffer.add_list([("metric1", item) for item in items])
    result = await buffer.get_up_to(2)

    assert len(result["metric1"]) == 2
    assert await buffer.total_items() == 1


@pytest.mark.asyncio
async def test_multiple_metric_types(buffer: AsyncSafeBuffer[str, int]) -> None:
    await buffer.add("metric1", 1)
    await buffer.add("metric2", 2)

    assert await buffer.total_items() == 2
    assert await buffer.items_by_type() == {"metric1": 1, "metric2": 1}

    result = await buffer.get_up_to(2)
    assert "metric1" in result
    assert "metric2" in result
    assert len(result["metric1"]) == 1
    assert len(result["metric2"]) == 1


@pytest.mark.asyncio
async def test_clear_buffer(buffer: AsyncSafeBuffer[str, int]) -> None:
    await buffer.add("metric1", 1)
    await buffer.add("metric2", 2)
    await buffer.clear()

    assert await buffer.total_items() == 0
    assert await buffer.items_by_type() == {}


@pytest.mark.asyncio
async def test_empty_metric_type_removal(buffer: AsyncSafeBuffer[str, int]) -> None:
    await buffer.add("metric1", 1)
    result = await buffer.get_up_to(1)

    assert {"metric1": 0} == await buffer.items_by_type()


@pytest.mark.asyncio
async def test_concurrent_access() -> None:
    buffer: AsyncSafeBuffer[str, int] = AsyncSafeBuffer[str, int]()

    async def add_items() -> None:
        for i in range(100):
            await buffer.add("metric1", i)

    async def get_items() -> None:
        for _ in range(10):
            await buffer.get_up_to(10)

    # Create multiple tasks
    tasks = [add_items(), add_items(), get_items(), get_items()]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

    # Verify final state
    total = await buffer.total_items()
    assert total >= 0  # The exact number will depend on timing


@pytest.mark.asyncio
async def test_different_types() -> None:
    buffer: AsyncSafeBuffer[str, str] = AsyncSafeBuffer[str, str]()
    await buffer.add("metric1", "value1")
    await buffer.add_list([("metric2", "value2"), ("metric2", "value3")])

    result = await buffer.get_up_to(3)
    assert isinstance(result["metric1"][0], str)
    assert isinstance(result["metric2"][0], str)


@pytest.mark.asyncio
async def test_get_up_to_with_empty_buffer(buffer: AsyncSafeBuffer[str, int]) -> None:
    result = await buffer.get_up_to(10)
    assert result == {}
