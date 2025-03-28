import dataclasses
import datetime
from contextlib import asynccontextmanager
from typing import Optional, Any, Dict, AsyncGenerator, List

from dataclasses_json import DataClassJsonMixin
from helixtelemetry.telemetry.providers.telemetry import Telemetry
from spark_pipeline_framework.utilities.async_pandas_udf.v1.async_pandas_udf_parameters import (
    AsyncPandasUdfParameters,
)
from helixtelemetry.telemetry.metrics.telemetry_counter import (
    TelemetryCounter,
)
from helixtelemetry.telemetry.metrics.telemetry_histogram_counter import (
    TelemetryHistogram,
)
from helixtelemetry.telemetry.metrics.telemetry_up_down_counter import (
    TelemetryUpDownCounter,
)
from helixtelemetry.telemetry.spans.telemetry_span_wrapper import (
    TelemetrySpanWrapper,
)

from transformers.intelligence_layer.person_clinical_data_transformer.v2.processors.run_context.run_context import (
    PersonClinicalDataRunContext,
)
from helixtelemetry.telemetry.factory.telemetry_factory import (
    TelemetryFactory,
)
from helixtelemetry.telemetry.structures.telemetry_parent import (
    TelemetryParent,
)
from helixtelemetry.telemetry.spans.telemetry_span_creator import (
    TelemetrySpanCreator,
)

from helixcore.structures.patient_access_transformer.v5.helpers.structures.token_streaming_config import \
    TokenStreamingConfig
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import BaseMetricsWriterParameters


@dataclasses.dataclass
class PatientAccessRunContext(DataClassJsonMixin):
    """
    This class stores the context data related to each Patient Access pipeline run


    """

    connection_type: str
    """ The type of connection for the run """

    run_id: str
    """ The id of the run """

    flow_name: Optional[str]
    """ The name of the prefect flow run """

    page_size_for_person_clinical_data_pipeline: Optional[int]
    """ Page size for fetching data from FHIR in person clinical data pipeline """

    run_date_time: datetime.datetime
    """ The date and time of the run """

    pipeline_category: Optional[str]
    """ The category of the pipeline """

    new_tokens_only: Optional[bool]
    """ If true, only new tokens will be processed """

    pipeline_version: Optional[str]
    """ The version of the pipeline """

    intelligence_layer_run_context: Optional[PersonClinicalDataRunContext]
    """ used to store the run context for the intelligence layer.  If set to None, we won't run the intelligence layer """

    metrics_writer_parameters: Optional[BaseMetricsWriterParameters]
    """ The metrics writer parameters to use for writing metrics """

    pandas_udf_parameters: AsyncPandasUdfParameters
    """ The parameters for the async pandas udf to run in parallel """

    current_date_time: Optional[datetime.datetime]
    """ set this to override the times in the run.  Used for unit testing to get deterministic results """

    telemetry_parent: Optional[TelemetryParent]
    """ The telemetry parent for the run """

    log_level: Optional[str]
    """ The log level for the run """

    raise_exception_on_error: Optional[bool] = None
    """ If true, raise an exception on error. Otherwise, log the error and continue """

    write_metrics_to_fhir: Optional[bool] = True
    """ If true, write metrics to FHIR """

    produce_connection_data_events: bool = False
    """ If true, produce connection data events """

    max_concurrent_requests: Optional[int] = 1
    """ The maximum number of concurrent requests to make to FHIR servers """

    max_concurrent_tasks: Optional[int] = 1
    """ The maximum number of concurrent tasks to run """

    sort_resources: Optional[bool] = None
    """ If true, sort the resources before processing them """

    token_streaming_config: Optional[TokenStreamingConfig] = None
    """ The token streaming configuration """

    request_size: Optional[int] = 1
    """Number of query params in a FHIR request eg. ?id=1,2,3"""

    enable_json_in_resource_metrics: Optional[bool] = True
    """ If true, resource json will be updated to resource metric table"""

    patients: Optional[List[str]] = None
    master_persons: Optional[List[str]] = None
    client_persons: Optional[List[str]] = None

    def is_human_api_pipeline(self) -> bool:
        return self.connection_type == "humanapi"

    @asynccontextmanager
    async def create_telemetry_span_async(
        self,
        *,
        name: str,
        attributes: Optional[Dict[str, Any]],
        telemetry_parent: Optional[TelemetryParent],
        start_time: int | None = None,
    ) -> AsyncGenerator[TelemetrySpanWrapper, None]:
        async with self.telemetry_span_creator.create_telemetry_span_async(
            name=name,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
            start_time=start_time,
        ) as span:
            yield span

    def _create_telemetry(self) -> Telemetry:
        _telemetry_factory: TelemetryFactory = TelemetryFactory(
            telemetry_parent=self.telemetry_parent or TelemetryParent.get_null_parent()
        )
        _telemetry: Telemetry = _telemetry_factory.create(log_level=self.log_level)
        return _telemetry

    @property
    def telemetry_span_creator(self) -> TelemetrySpanCreator:
        _telemetry: Telemetry = self._create_telemetry()
        return TelemetrySpanCreator(telemetry=_telemetry)

    async def flush_telemetry_async(self) -> None:
        pass
        # if self._telemetry:
        #     await self._telemetry.flush_async()

    def __getstate__(self) -> Dict[str, Any]:
        # Exclude certain properties from being pickled otherwise they cause errors in pickling
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in ["_telemetry_factory", "_telemetry"]
        }

    def get_telemetry_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryCounter:
        _telemetry: Telemetry = self._create_telemetry()
        return _telemetry.get_counter(
            name=name,
            unit=unit,
            description=description,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    def get_telemetry_histogram(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryHistogram:
        _telemetry: Telemetry = self._create_telemetry()
        return _telemetry.get_histogram(
            name=name,
            unit=unit,
            description=description,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    def get_telemetry_up_down_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TelemetryUpDownCounter:
        _telemetry: Telemetry = self._create_telemetry()
        return _telemetry.get_up_down_counter(
            name=name,
            unit=unit,
            description=description,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )
