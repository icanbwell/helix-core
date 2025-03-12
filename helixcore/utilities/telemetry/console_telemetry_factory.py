from typing import Optional, override

from helixcore.utilities.telemetry.base_telemetry_factory import (
    BaseTelemetryFactory,
)
from helixcore.utilities.telemetry.console_telemetry import (
    ConsoleTelemetry,
)
from helixcore.utilities.telemetry.null_telemetry import NullTelemetry
from helixcore.utilities.telemetry.telemetry import (
    Telemetry,
)
from helixcore.utilities.telemetry.telemetry_provider import (
    TelemetryProvider,
)


class ConsoleTelemetryFactory(BaseTelemetryFactory):
    @override
    def create(self, *, log_level: Optional[str | int]) -> Telemetry:
        """
        Create a telemetry instance

        :return: telemetry instance
        """
        if not self.telemetry_context:
            return NullTelemetry(telemetry_context=self.telemetry_context)

        match self.telemetry_context.provider:
            case TelemetryProvider.CONSOLE:
                return ConsoleTelemetry(
                    telemetry_context=self.telemetry_context, log_level=log_level
                )
            case TelemetryProvider.NULL:
                return NullTelemetry(telemetry_context=self.telemetry_context)
            case _:
                raise ValueError(
                    f"Invalid telemetry provider: {self.telemetry_context.provider}"
                )
