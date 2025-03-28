import dataclasses

from helixcore.utilities.fhir_helpers.fhir_merge_response_item import (
    FhirMergeResponseItem,
)

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_send_request import (
    PatientAccessSendRequest,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_send_result import (
    PatientAccessSendResult,
)


@dataclasses.dataclass
class PatientAccessSendResultPromise(PatientAccessSendResult):
    request: PatientAccessSendRequest
    resolved: bool

    def resolve(self, result: PatientAccessSendResult) -> None:
        """
        Replaces my values with the passed in values

        """
        self.results.extend(result.results)
        self.errors.extend(result.errors)
        self.resolved = True

    def add_merge_item(self, merge_item: FhirMergeResponseItem) -> None:
        """
        Adds a merge item to the results

        """
        self.results.append(merge_item)

    def add_error(self, error: PatientAccessError) -> None:
        """
        Adds an error to the results

        """
        self.errors.append(error)
