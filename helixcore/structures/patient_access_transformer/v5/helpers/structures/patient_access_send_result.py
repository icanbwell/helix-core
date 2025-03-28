import dataclasses
from typing import List, Optional

from helixcore.utilities.fhir_helpers.fhir_merge_response_item import (
    FhirMergeResponseItem,
)

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.patient_access_transformer.v5.helpers.metrics.demographics_mismatch_entry import (
    DemographicsMismatchEntry,
)


@dataclasses.dataclass
class PatientAccessSendResult:
    """
    This class stores result of sending Patient Access data to b.well FHIR server

    """

    patient_id: Optional[str]
    results: List[FhirMergeResponseItem]
    errors: List[PatientAccessError]
    match_errors: List[DemographicsMismatchEntry] | None
    time_send_resources_to_fhir: Optional[float]
    time_to_match_person: Optional[float]
    request_id: Optional[str]
    slug: str
    url: str
    matched: Optional[bool]
    client_person_to_patient_link_created: Optional[bool]

    def get_results(self) -> List[FhirMergeResponseItem]:
        """
        Returns the results

        :return: the results
        """
        return self.results

    def get_errors(self) -> List[PatientAccessError]:
        """
        Returns the errors

        :return: the errors
        """
        return self.errors
