import uuid
from contextlib import asynccontextmanager, contextmanager
from logging import Logger
from typing import Optional, Dict, Any, AsyncGenerator, Generator


from helixcore.logger.yarn_logger import get_logger
from helixcore.utilities.telemetry.metrics.telemetry_counter import (
    TelemetryCounter,
)
from helixcore.utilities.telemetry.metrics.telemetry_histogram_counter import (
    TelemetryHistogram,
)
from helixcore.utilities.telemetry.metrics.telemetry_up_down_counter import (
    TelemetryUpDownCounter,
)
from helixcore.utilities.telemetry.telemetry_context import (
    TelemetryContext,
)

from helixcore.utilities.telemetry.console_telemetry_span_wrapper import (
    ConsoleTelemetrySpanWrapper,
)
from helixcore.utilities.telemetry.telemetry import (
    Telemetry,
)
from helixcore.utilities.telemetry.telemetry_parent import (
    TelemetryParent,
)
from helixcore.utilities.telemetry.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)


class TelemetrySpanCreator:
    def __init__(
        self,
        *,
        telemetry: Optional[Telemetry],
        telemetry_context: TelemetryContext,
        log_level: str = "DEBUG",
    ) -> None:
        """
        Create a telemetry span creator that can create a telemetry span if telemetry is available else return a null context

        :param telemetry: Optional telemetry object
        """

        # Unique instance identifier
        self._instance_id = str(uuid.uuid4())

        assert telemetry is not None
        assert telemetry_context is not None
        self.telemetry = telemetry
        self._current_telemetry_context = telemetry_context

        self._logger: Logger = get_logger(
            __name__,
            level=log_level,
        )
        # get_logger sets the log level to the environment variable LOGLEVEL if it exists
        self._logger.setLevel(log_level)

    def __getstate__(self) -> Dict[str, Any]:
        # Exclude certain properties from being pickled otherwise they cause errors in pickling
        return {k: v for k, v in self.__dict__.items() if k not in ["telemetry"]}

    @asynccontextmanager
    async def create_telemetry_span(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]],
        telemetry_parent: Optional[TelemetryParent] = None,
    ) -> AsyncGenerator[TelemetrySpanWrapper, None]:
        """
        Create a telemetry span if telemetry is available else return a null context

        :param name: name of the span
        :param attributes:  optional attributes to add to the span
        :param telemetry_parent: telemetry parent
        :return: AsyncContextManager[Any]
        """

        if self.telemetry is not None:
            span: TelemetrySpanWrapper
            async with self.telemetry.trace_async(
                name=name,
                attributes=attributes,
                telemetry_parent=telemetry_parent,
            ) as span:
                yield span
        else:
            yield ConsoleTelemetrySpanWrapper(
                name=name,
                attributes=attributes,
                telemetry_context=TelemetryContext.get_null_context(),
                telemetry_parent=telemetry_parent,
            )

    @contextmanager
    def create_telemetry_span_sync(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]],
        telemetry_parent: Optional[TelemetryParent] = None,
    ) -> Generator[TelemetrySpanWrapper, None, None]:
        """
        Create a telemetry span if telemetry is available else return a null context

        :param name: name of the span
        :param attributes:  optional attributes to add to the span
        :param telemetry_parent: telemetry parent
        :return: AsyncContextManager[Any]
        """
        if self.telemetry is not None:
            span: TelemetrySpanWrapper
            with self.telemetry.trace(
                name=name,
                attributes=attributes,
                telemetry_parent=telemetry_parent,
            ) as span:
                yield span
        else:
            yield ConsoleTelemetrySpanWrapper(
                name=name,
                attributes=attributes,
                telemetry_context=TelemetryContext.get_null_context(),
                telemetry_parent=telemetry_parent,
            )

    async def flush_async(self) -> None:
        """
        Flush the telemetry

        :return: None
        """
        if self.telemetry:
            await self.telemetry.flush_async()

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
        return self.telemetry.get_counter(
            name=name, unit=unit, description=description, attributes=attributes
        )

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
        return self.telemetry.get_up_down_counter(
            name=name, unit=unit, description=description, attributes=attributes
        )

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
        return self.telemetry.get_histogram(
            name=name, unit=unit, description=description, attributes=attributes
        )
