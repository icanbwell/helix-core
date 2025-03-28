import dataclasses
from typing import List, Optional

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.person_match_result_or_error import (
    PersonMatchResultOrError,
)


@dataclasses.dataclass
class PatientAccessMatchResult(DataClassJsonMixin):
    message: str
    errors: List[PatientAccessError]
    time_to_match_person: Optional[float]
    matched: bool
    client_person_to_patient_match_result: PersonMatchResultOrError | None
    client_person_to_patient_link_created: bool

    def get_error_text(self) -> str:
        return f"{self.message} {','.join([e.error_text for e in self.errors if e.error_text is not None])}"
