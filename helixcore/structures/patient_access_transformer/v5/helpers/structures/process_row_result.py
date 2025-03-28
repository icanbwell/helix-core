import dataclasses
import sys
import traceback
from dataclasses import field
from datetime import datetime
from typing import List, Dict, Optional, Any

from dataclasses_json import DataClassJsonMixin, config

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.demographics_mismatch_entry import (
    DemographicsMismatchEntry,
)
from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row import (
    PatientAccessRow,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.raw_resource_info import (
    RawResourceInfo,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.resource_received_info import (
    ResourceReceivedInfo,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.resources_by_type_map import (
    ResourcesByTypeMap,
)
from helixcore.structures.token_service_receiver.v3.connection_entry import (
    ConnectionEntry,
)
from helixcore.utilities.fhir_helpers.fhir_merge_response_item import (
    FhirMergeResponseItem,
)


def encode_fhir_merge_response_item(
    items: List[FhirMergeResponseItem],
) -> List[Dict[str, str]]:
    return [item.to_dict() for item in items]


def decode_fhir_merge_response_item(
    items: List[Dict[str, str]],
) -> List[FhirMergeResponseItem]:
    return [FhirMergeResponseItem.from_dict(item) for item in items]


def encode_resources_by_type_map(
    items: ResourcesByTypeMap,
) -> Dict[str, List[Dict[str, Any]]]:
    return {key: [item.to_dict() for item in value] for key, value in items.map.items()}


def decode_resources_by_type_map(
    items: Dict[str, List[Dict[str, Any]]],
) -> ResourcesByTypeMap:
    result = ResourcesByTypeMap()
    for key, value in items.items():
        result.map[key] = [RawResourceInfo.from_dict(item) for item in value]
    return result


@dataclasses.dataclass
class ProcessRowResult(DataClassJsonMixin):
    connection_entry: ConnectionEntry
    errors: List[PatientAccessError]
    match_errors: List[DemographicsMismatchEntry] | None
    results: List[FhirMergeResponseItem] = field(
        metadata=config(
            encoder=encode_fhir_merge_response_item,
            decoder=decode_fhir_merge_response_item,
        )
    )
    resources_by_type: Dict[str, List[ResourceReceivedInfo]]
    time_to_get_resources_from_source: Optional[float]
    time_send_resources_to_fhir: Optional[float]
    time_to_match_person: Optional[float]
    matched: Optional[bool]
    start_time: datetime
    end_time: datetime
    raw_resources_by_resource_type: ResourcesByTypeMap = field(
        metadata=config(
            encoder=encode_resources_by_type_map,
            decoder=decode_resources_by_type_map,
        )
    )
    partition_start_time: Optional[datetime]
    chunk_start_time: Optional[datetime]
    partition_index: int
    chunk_index: int

    def remove_resources(self) -> None:
        self.results.clear()
        self.raw_resources_by_resource_type.clear()
        self.resources_by_type.clear()
        if self.match_errors is not None:
            self.match_errors.clear()
        self.errors.clear()

    @staticmethod
    def from_error(
        *,
        e: Exception,
        patient_access_row: PatientAccessRow,
        step: str,
        row_context: PatientAccessRowContext,
        partition_index: int,
        chunk_index: int,
        partition_start_time: datetime,
        chunk_start_time: datetime,
        start_time: datetime,
        end_time: datetime,
    ) -> "ProcessRowResult":
        error_text = ""
        if isinstance(e, AssertionError):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_list = traceback.extract_tb(exc_traceback)
            # Get the last frame (where the assertion occurred)
            last_frame = tb_list[-1]
            error_text = f"Assertion Failed at {last_frame.filename}:{last_frame.lineno} {last_frame.line}"

        return ProcessRowResult(
            connection_entry=patient_access_row,
            errors=[
                PatientAccessError.construct(
                    row_context=row_context,
                    request_id=None,
                    resource_id=patient_access_row.patient_id,
                    resource_type=patient_access_row.resourceType,
                    url=patient_access_row.url,
                    error_text=error_text,
                    status_code=400,
                    step=step,
                    resource_json=None,
                    severity="error",
                    exception=e,
                )
            ],
            match_errors=None,
            results=[],
            resources_by_type={},
            time_to_get_resources_from_source=None,
            time_send_resources_to_fhir=None,
            time_to_match_person=None,
            matched=None,
            start_time=start_time,
            end_time=end_time,
            raw_resources_by_resource_type=ResourcesByTypeMap(),
            partition_index=partition_index,
            chunk_index=chunk_index,
            partition_start_time=partition_start_time,
            chunk_start_time=chunk_start_time,
        )
