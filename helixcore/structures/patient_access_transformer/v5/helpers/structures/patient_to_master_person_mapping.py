import dataclasses


@dataclasses.dataclass
class PatientToMasterPersonMapping:
    """
    This class stores the mapping from a source patient id and service slug to a master person id

    """

    source_patient_id: str
    service_slug: str
    master_person_id: str
    client_person_id: str
