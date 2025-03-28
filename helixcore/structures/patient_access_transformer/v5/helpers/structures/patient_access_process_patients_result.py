import dataclasses
from typing import List, Dict

from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_send_result import (
    PatientAccessSendResult,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.resource_received_info import (
    ResourceReceivedInfo,
)


@dataclasses.dataclass
class PatientAccessProcessPatientsResult:
    """
    This class stores the result from process_patients() call

    """

    patient_results: List[PatientAccessSendResult]
    resources_by_type: Dict[str, List[ResourceReceivedInfo]]
