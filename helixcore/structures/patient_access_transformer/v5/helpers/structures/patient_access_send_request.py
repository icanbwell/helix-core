import dataclasses
from logging import Logger
from typing import Optional

from fhir.resources.R4B.resource import Resource

from helixcore.structures.patient_access_transformer.common.helpers.structures.fhir_server_config import (
    FhirServerConfig,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)


@dataclasses.dataclass
class PatientAccessSendRequest:
    """
    This class holds the parameters for sending data to the FHIR server

    :param row_context: the run context
    :param destination: the destination FHIR server
    :param destination_auth_access_token: the destination auth access token
    :param log_level: the log level
    :param resource: the resource to send
    :param resource_type: the resource type
    :param retry_count: the retry count
    :param token: the token
    :param logger: the logger
    :param patient_id: the patient id
    :param slug: the slug
    :param client_person_id: the client person id
    :param master_person_id: the master person id
    """

    id_: Optional[str]
    row_context: PatientAccessRowContext
    destination: Optional[FhirServerConfig]
    destination_auth_access_token: Optional[str]
    log_level: Optional[str]
    resource: Resource
    resource_type: str
    retry_count: Optional[int]
    token: Optional[str]
    logger: Logger
    patient_id: str
    slug: str
    client_person_id: str
    master_person_id: Optional[str]
