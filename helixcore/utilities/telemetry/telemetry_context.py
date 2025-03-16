import dataclasses
from typing import Optional, List, Any, Dict, Union

from dataclasses_json import DataClassJsonMixin

from helixcore.utilities.telemetry.telemetry_tracers import (
    TelemetryTracer,
)


@dataclasses.dataclass
class TelemetryContext(DataClassJsonMixin):
    telemetry_provider: str
    """ Provider for the telemetry context.  There must be corresponding telemetry implementation class registered for the provider """

    service_name: str
    """ Service name for the telemetry context """

    service_namespace: str
    """ Service namespace for the telemetry context.  Included in traces and metrics """

    instance_name: str
    """ Instance name for the telemetry context.  Included in traces and metrics """

    environment: str
    """ Environment for the telemetry context """

    attributes: Optional[Dict[str, Any]]
    """ Additional attributes to include in telemetry """

    log_level: Optional[Union[int, str]]
    """ Log level for the telemetry context """

    trace_id: Optional[str] = None
    """ Trace ID for the telemetry context """

    span_id: Optional[str] = None
    """ Span ID for the telemetry context """

    trace_all_calls: Optional[List[TelemetryTracer]] = None
    """ Whether to Trace certain calls like aiohttp, pymysql, etc """

    tracer_endpoint: Optional[str] = None
    """ Tracer endpoint for the telemetry context """

    metrics_endpoint: Optional[str] = None
    """ Metrics endpoint for the telemetry context """

    @staticmethod
    def get_null_context() -> "TelemetryContext":
        """
        Get a null telemetry context

        :return: a null telemetry context
        """
        return TelemetryContext(
            telemetry_provider="NullTelemetry",
            trace_id=None,
            span_id=None,
            service_name="",
            environment="",
            attributes=None,
            log_level=None,
            instance_name="",
            service_namespace="",
        )

    def copy(self) -> "TelemetryContext":
        """
        Create a copy of the telemetry context

        :return: a copy of the telemetry context
        """
        return TelemetryContext(
            telemetry_provider=self.telemetry_provider,
            trace_id=self.trace_id,
            span_id=self.span_id,
            service_name=self.service_name,
            environment=self.environment,
            trace_all_calls=self.trace_all_calls,
            attributes=self.attributes,
            log_level=self.log_level,
            instance_name=self.instance_name,
            service_namespace=self.service_namespace,
        )

    def create_child_context(
        self, *, trace_id: Optional[str], span_id: Optional[str]
    ) -> "TelemetryContext":
        """
        Create a child telemetry context

        :param trace_id: trace ID for the child context
        :param span_id: span ID for the child context
        :return: a child telemetry context
        """
        telemetry_context = self.copy()
        telemetry_context.trace_id = trace_id
        telemetry_context.span_id = span_id
        return telemetry_context
