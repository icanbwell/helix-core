from contextlib import contextmanager, asynccontextmanager
from typing import Optional, Dict, Any, Iterator, AsyncIterator, override, ClassVar

from helixcore.utilities.telemetry.metrics.telemetry_counter import (
    TelemetryCounter,
)
from helixcore.utilities.telemetry.metrics.telemetry_histogram_counter import (
    TelemetryHistogram,
)
from helixcore.utilities.telemetry.metrics.telemetry_up_down_counter import (
    TelemetryUpDownCounter,
)

from helixcore.utilities.telemetry.null_telemetry_span_wrapper import (
    NullTelemetrySpanWrapper,
)
from helixcore.utilities.telemetry.telemetry import Telemetry
from helixcore.utilities.telemetry.telemetry_parent import (
    TelemetryParent,
)
from helixcore.utilities.telemetry.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)
from opentelemetry.metrics import NoOpCounter, NoOpUpDownCounter, NoOpHistogram


class NullTelemetry(Telemetry):
    """
    This is a null telemetry implementation that does nothing


    """

    telemetry_provider: ClassVar[str] = "NullTelemetry"

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
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryCounter:
        """
        Get a counter metric

        :param name: Name of the counter
        :param unit: Unit of the counter
        :param description: Description
        :param attributes: Optional attributes
        :return: The Counter metric
        """
        return TelemetryCounter(
            counter=NoOpCounter(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=None,
        )

    @override
    def get_up_down_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryUpDownCounter:
        """
        Get an up_down_counter metric

        :param name: Name of the up_down_counter
        :param unit: Unit of the up_down_counter
        :param description: Description
        :param attributes: Optional attributes
        :return: The Counter metric
        """
        return TelemetryUpDownCounter(
            counter=NoOpUpDownCounter(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=None,
        )

    @override
    def get_histogram(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryHistogram:
        """
        Get a histograms metric

        :param name: Name of the histograms
        :param unit: Unit of the histograms
        :param description: Description
        :param attributes: Optional attributes
        :return: The Counter metric
        """
        return TelemetryHistogram(
            histogram=NoOpHistogram(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=None,
        )

    async def shutdown_async(self) -> None:
        pass
