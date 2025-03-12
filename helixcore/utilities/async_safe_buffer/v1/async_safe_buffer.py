import asyncio
from asyncio import Lock
from collections import deque
from typing import Dict, List, Tuple


class AsyncSafeBuffer[TKey, TValue]:
    def __init__(self) -> None:
        self._lock: Lock = asyncio.Lock()
        self._buffer: Dict[TKey, deque[TValue]] = {}
        self._total_items: int = 0

    async def add(self, metric_type: TKey, item: TValue) -> None:
        """Add an item to the buffer."""
        async with self._lock:
            if metric_type not in self._buffer:
                self._buffer[metric_type] = deque()
            self._buffer[metric_type].append(item)
            self._total_items += 1

    async def add_list(self, items: List[Tuple[TKey, TValue]]) -> None:
        """Add a list of items to the buffer."""
        async with self._lock:
            metric_type: TKey
            item: TValue
            for metric_type, item in items:
                if metric_type not in self._buffer:
                    self._buffer[metric_type] = deque()
                self._buffer[metric_type].append(item)
                self._total_items += 1

    async def get_all(self) -> Dict[TKey, List[TValue]]:
        """Get all items from the buffer."""
        async with self._lock:
            result = {k: list(v) for k, v in self._buffer.items()}
            self._buffer.clear()
            self._total_items = 0
            return result

    async def get_up_to(self, count: int) -> Dict[TKey, List[TValue]]:
        """
        Get up to 'count' items from the buffer.
        Returns a tuple of (items_dict, items_retrieved)
        """
        async with self._lock:
            result: Dict[TKey, List[TValue]] = {}
            items_retrieved = 0

            if self._total_items == 0:
                return result

            # Copy items up to count, maintaining proportion across types
            remaining_count = count
            while remaining_count > 0 and self._total_items > 0:
                # Get one item from each non-empty buffer type
                for metric_type in list(self._buffer.keys()):
                    if not self._buffer[metric_type]:
                        del self._buffer[metric_type]
                        continue

                    if metric_type not in result:
                        result[metric_type] = []

                    item = self._buffer[metric_type].popleft()
                    result[metric_type].append(item)
                    items_retrieved += 1
                    self._total_items -= 1
                    remaining_count -= 1

                    if remaining_count <= 0:
                        break

            return result

    async def clear(self) -> None:
        """Clear the buffer."""
        async with self._lock:
            self._buffer.clear()
            self._total_items = 0

    async def total_items(self) -> int:
        """Get the total number of items in the buffer."""
        async with self._lock:
            return self._total_items

    async def total_items_by_type(self, metric_type: TKey) -> int:
        """Get the total number of items in the buffer for specified type."""
        async with self._lock:
            return len(self._buffer.get(metric_type, []))

    async def items_by_type(self) -> Dict[TKey, int]:
        """Get the count of items for each type."""
        async with self._lock:
            return {k: len(v) for k, v in self._buffer.items()}
