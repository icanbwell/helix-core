import dataclasses
from typing import List

from dataclasses import field

from helixcore.utilities.fhir.fhir_resource_helpers.v2.types import FhirResourceType

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)


@dataclasses.dataclass
class PatientAccessConverterResult:
    resources: List[FhirResourceType] = field(default_factory=list)
    errors: List[PatientAccessError] = field(default_factory=list)

    def merge(
        self, other: "PatientAccessConverterResult"
    ) -> "PatientAccessConverterResult":
        """
        Merge the resources and errors from another PatientAccessConverterResult into this one.
        """
        self.resources.extend(other.resources)
        self.errors.extend(other.errors)
        return self
