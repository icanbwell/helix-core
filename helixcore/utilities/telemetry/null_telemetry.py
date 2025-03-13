from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Dict, Any, Iterator, AsyncIterator, override


from helixcore.utilities.telemetry.null_telemetry_span_wrapper import (
    NullTelemetrySpanWrapper,
)
from helixcore.utilities.telemetry.telemetry import Telemetry
from helixcore.utilities.telemetry.telemetry_factory import TelemetryFactory
from helixcore.utilities.telemetry.telemetry_parent import (
    TelemetryParent,
)
from helixcore.utilities.telemetry.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)
from opentelemetry.metrics import Counter, UpDownCounter, Histogram
from opentelemetry.metrics import NoOpCounter, NoOpUpDownCounter, NoOpHistogram


@TelemetryFactory.register_telemetry(name="null")
class NullTelemetry(Telemetry):
    @override
    def track_exception(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @override
    async def track_exception_async(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @override
    async def flush_async(self) -> None:
        pass

    @contextmanager
    @override
    def trace(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        telemetry_parent: Optional[TelemetryParent],
    ) -> Iterator[TelemetrySpanWrapper]:
        yield NullTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_context=self._telemetry_context,
            telemetry_parent=telemetry_parent,
        )

    @asynccontextmanager
    @override
    async def trace_async(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        telemetry_parent: Optional[TelemetryParent],
    ) -> AsyncIterator[TelemetrySpanWrapper]:
        yield NullTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_context=self._telemetry_context,
            telemetry_parent=telemetry_parent,
        )

    @override
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
        return NoOpCounter(
            name=name,
            unit=unit,
            description=description,
        )

    @override
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

        return NoOpUpDownCounter(
            name=name,
            unit=unit,
            description=description,
        )

    @override
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
        return NoOpHistogram(
            name=name,
            unit=unit,
            description=description,
        )
