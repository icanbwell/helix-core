import dataclasses

from fhir.resources.R4B.resource import Resource


@dataclasses.dataclass
class PatientAccessResourceWrapper:
    resource: Resource
    valid: bool = False
    fixed: bool = False
