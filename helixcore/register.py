from helixcore.utilities.telemetry.telemetry_factory import TelemetryFactory
from helixcore.utilities.telemetry.null_telemetry import NullTelemetry
from helixcore.utilities.telemetry.console_telemetry import ConsoleTelemetry


def register() -> None:
    """
    Register the telemetry classes with the telemetry factory
    """

    TelemetryFactory.register_telemetry_class(
        name="null", telemetry_class=NullTelemetry
    )
    TelemetryFactory.register_telemetry_class(
        name="class", telemetry_class=ConsoleTelemetry
    )
