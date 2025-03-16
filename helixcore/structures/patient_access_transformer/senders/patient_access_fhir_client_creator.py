from logging import Logger
from typing import Optional, List

from helix_fhir_client_sdk.fhir_client import FhirClient
from helixcore.utilities.fhir_helpers.get_fhir_client import (
    get_fhir_client,
)

from helixcore.structures.patient_access_transformer.common.helpers.senders.base_patient_access_fhir_client_creator import (
    BasePatientAccessFhirClientCreator,
)


class PatientAccessFhirClientCreator(BasePatientAccessFhirClientCreator):
    """
    This class creates a FhirClient instance


    """

    def __init__(self) -> None:
        pass

    # noinspection PyMethodMayBeStatic
    def create_fhir_client(
        self,
        *,
        logger: Logger,
        server_url: str,
        auth_server_url: Optional[str] = None,
        auth_client_id: Optional[str] = None,
        auth_client_secret: Optional[str] = None,
        auth_login_token: Optional[str] = None,
        auth_access_token: Optional[str] = None,
        auth_scopes: Optional[List[str]] = None,
        log_level: Optional[str] = None,
    ) -> FhirClient:
        """
        Create a FHIRClient


        """
        fhir_client: FhirClient = get_fhir_client(
            logger=logger,
            server_url=server_url,
            auth_server_url=auth_server_url,
            auth_client_id=auth_client_id,
            auth_client_secret=auth_client_secret,
            auth_login_token=auth_login_token,
            auth_access_token=auth_access_token,
            auth_scopes=auth_scopes,
            log_level=log_level,
        )
        return fhir_client
