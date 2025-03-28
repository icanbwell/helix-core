import dataclasses
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, AsyncGenerator

from dataclasses_json import DataClassJsonMixin
from helixtelemetry.telemetry.structures.telemetry_parent import (
    TelemetryParent,
)

from helixtelemetry.telemetry.spans.telemetry_span_creator import (
    TelemetrySpanCreator,
)
from helixtelemetry.telemetry.spans.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)

from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_run_context import (
    PatientAccessRunContext,
)
from helixcore.structures.token_service_receiver.v3.connection_entry import (
    ConnectionEntry,
)


@dataclasses.dataclass
class PatientAccessRowContext(DataClassJsonMixin):
    """
    This class stores the context data related to each row in a Patient Access pipeline run

    """

    run_context: PatientAccessRunContext
    """ The context of the entire run """

    connection_entry: ConnectionEntry
    """ The connection entry for the row """

    @asynccontextmanager
    async def create_telemetry_span_async(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]],
        telemetry_parent: Optional[TelemetryParent],
        start_time: int | None = None,
    ) -> AsyncGenerator[TelemetrySpanWrapper, None]:
        async with self.run_context.create_telemetry_span_async(
            name=name,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
            start_time=start_time,
        ) as span:
            yield span

    @property
    def telemetry_span_creator(self) -> TelemetrySpanCreator:
        return self.run_context.telemetry_span_creator
