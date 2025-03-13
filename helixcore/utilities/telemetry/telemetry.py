from abc import abstractmethod, ABC
from contextlib import asynccontextmanager, contextmanager
from opentelemetry.metrics import Counter, UpDownCounter, Histogram

from typing import Optional, Dict, Any, AsyncIterator, Iterator, Union

from helixcore.utilities.telemetry.telemetry_context import TelemetryContext
from helixcore.utilities.telemetry.telemetry_parent import (
    TelemetryParent,
)
from helixcore.utilities.telemetry.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)

from helixcore.utilities.telemetry.console_telemetry_span_wrapper import (
    ConsoleTelemetrySpanWrapper,
)


class Telemetry(ABC):
    """
    Abstract class for telemetry

    """

    def __init__(
        self,
        *,
        telemetry_context: TelemetryContext,
        log_level: Optional[Union[int, str]],
    ) -> None:
        self._telemetry_context = telemetry_context
        self._log_level = log_level

    @abstractmethod
    @contextmanager
    def trace(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        telemetry_parent: Optional[TelemetryParent],
    ) -> Iterator[TelemetrySpanWrapper]:
        """
        Start a new span

        :param name:  name of the span
        :param attributes: optional attributes to add to the span
        :param telemetry_parent: parent span
        :return: A context manager to use in a `with` statement
        """
        # This is never called but is here for mypy to understand this is a generator
        # noinspection PyTypeChecker
        yield ConsoleTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_context=None,
            telemetry_parent=None,
        )

    @abstractmethod
    @asynccontextmanager
    async def trace_async(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        telemetry_parent: Optional[TelemetryParent],
    ) -> AsyncIterator[TelemetrySpanWrapper]:
        """
        Start a new span

        :param name:  name of the span
        :param attributes: optional attributes to add to the span
        :param telemetry_parent: telemetry parent
        :return: A context manager to use in a `with` statement
        """
        # This is never called but is here for mypy to understand this is a generator
        # noinspection PyTypeChecker
        yield ConsoleTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_context=None,
            telemetry_parent=telemetry_parent,
        )

    @abstractmethod
    def track_exception(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track and record exceptions

        :param exception: exception to track
        :param additional_info: Optional extra context for the exception
        :return: None
        """
        ...

    @abstractmethod
    async def track_exception_async(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Track and record exceptions

        :param exception: exception to track
        :param additional_info: Optional extra context for the exception
        :return: None
        """
        ...

    @abstractmethod
    async def flush_async(self) -> None: ...

    @abstractmethod
    def get_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
    ) -> Counter:
        """
        Get a counter metric

        :param name: Name of the counter
        :param unit: Unit of the counter
        :param description: Description
        :return: The Counter metric
        """
        ...

    @abstractmethod
    def get_up_down_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
    ) -> UpDownCounter:
        """
        Get a up_down_counter metric

        :param name: Name of the up_down_counter
        :param unit: Unit of the up_down_counter
        :param description: Description
        :return: The Counter metric
        """
        ...

    @abstractmethod
    def get_histograms(
        self,
        *,
        name: str,
        unit: str,
        description: str,
    ) -> Histogram:
        """
        Get a histograms metric

        :param name: Name of the histograms
        :param unit: Unit of the histograms
        :param description: Description
        :return: The Counter metric
        """
        ...
