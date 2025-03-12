from abc import abstractmethod
from typing import Any, Dict, Optional

from helixcore.utilities.telemetry.telemetry import (
    Telemetry,
)
from helixcore.utilities.telemetry.telemetry_context import (
    TelemetryContext,
)
from helixcore.utilities.telemetry.telemetry_span_creator import (
    TelemetrySpanCreator,
)


class BaseTelemetryFactory:
    def __init__(self, *, telemetry_context: TelemetryContext) -> None:
        """
        Telemetry factory used to create telemetry instances based on the telemetry context


        :param telemetry_context: telemetry context
        """
        self.telemetry_context = telemetry_context

    @abstractmethod
    def create(self, *, log_level: Optional[str | int]) -> Telemetry:
        """
        Create a telemetry instance

        :return: telemetry instance
        """
        ...

    def create_telemetry_span_creator(
        self, *, log_level: Optional[str | int]
    ) -> TelemetrySpanCreator:
        """
        Create a telemetry span creator

        :return: telemetry span creator
        """
        return TelemetrySpanCreator(
            telemetry=self.create(log_level=log_level),
            telemetry_context=self.telemetry_context,
        )

    def __getstate__(self) -> Dict[str, Any]:
        # Exclude certain properties from being pickled otherwise they cause errors in pickling
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in ["_telemetry_factory", "_telemetry"]
        }
