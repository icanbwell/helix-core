import dataclasses
from typing import Optional, List

from dataclasses import field

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_resource_wrapper import (
    PatientAccessResourceWrapper,
)


@dataclasses.dataclass
class PatientAccessResourceFixerResult:
    resource: Optional[PatientAccessResourceWrapper]
    errors: List[PatientAccessError] = field(default_factory=list)
