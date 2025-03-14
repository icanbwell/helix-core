from helixcore.utilities.telemetry.open_telemetry import OpenTelemetry
from helixcore.utilities.telemetry.telemetry_factory import TelemetryFactory
from helixcore.utilities.telemetry.null_telemetry import NullTelemetry
from helixcore.utilities.telemetry.console_telemetry import ConsoleTelemetry


def register() -> None:
    """
    Register the telemetry classes with the telemetry factory
    """

    TelemetryFactory.register_telemetry_class(
        name=NullTelemetry.telemetry_provider, telemetry_class=NullTelemetry
    )
    TelemetryFactory.register_telemetry_class(
        name=ConsoleTelemetry.telemetry_provider, telemetry_class=ConsoleTelemetry
    )

    TelemetryFactory.register_telemetry_class(
        name=OpenTelemetry.telemetry_provider,
        telemetry_class=OpenTelemetry,
    )
