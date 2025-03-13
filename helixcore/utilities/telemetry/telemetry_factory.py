from typing import Any, Dict, Optional, Callable, Type

from helixcore.utilities.telemetry.telemetry import (
    Telemetry,
)
from helixcore.utilities.telemetry.telemetry_context import (
    TelemetryContext,
)
from helixcore.utilities.telemetry.telemetry_span_creator import (
    TelemetrySpanCreator,
)


class TelemetryFactory:

    _registry: Dict[str, type[Telemetry]] = {}

    def __init__(self, *, telemetry_context: TelemetryContext) -> None:
        """
        Telemetry factory used to create telemetry instances based on the telemetry context


        :param telemetry_context: telemetry context
        """
        self.telemetry_context = telemetry_context

    @classmethod
    def register_telemetry(
        cls, name: Optional[str] = None
    ) -> Callable[[Type[Telemetry]], Type[Telemetry]]:
        """
        Decorator to register Telemetry subclasses in the factory registry.

        Args:
            name (Optional[str], optional): Custom registration name.
                Defaults to the class name if not provided.

        Returns:
            Callable: A decorator function for registering Telemetry classes
        """

        def decorator(telemetry_class: Type[Telemetry]) -> Type[Telemetry]:
            # Use provided name or fallback to class name
            registration_name = name or telemetry_class.__name__

            # Validate that the class is a Telemetry subclass
            if not issubclass(telemetry_class, Telemetry):
                raise TypeError(
                    f"{telemetry_class.__name__} must be a subclass of Telemetry"
                )

            # Register the class in the factory's registry
            cls._registry[registration_name] = telemetry_class

            return telemetry_class

        return decorator

    def create(self, *, name: str, log_level: Optional[str | int]) -> Telemetry:
        """
        Create a telemetry instance

        :return: telemetry instance
        """
        assert (
            name in self._registry
        ), f"Telemetry {name} not found in registry.  Did you register a class for it?"
        return self._registry[name](
            telemetry_context=self.telemetry_context, log_level=log_level
        )

    def create_telemetry_span_creator(
        self, *, name: str, log_level: Optional[str | int]
    ) -> TelemetrySpanCreator:
        """
        Create a telemetry span creator

        :return: telemetry span creator
        """
        return TelemetrySpanCreator(
            telemetry=self.create(name=name, log_level=log_level),
            telemetry_context=self.telemetry_context,
        )

    def __getstate__(self) -> Dict[str, Any]:
        assert "TelemetryFactory should not be pickled (serialized) as it is not serializable"
        # Exclude certain properties from being pickled otherwise they cause errors in pickling
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in ["_telemetry_factory", "_telemetry"]
        }
