from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional, List
from helix_fhir_client_sdk.fhir_client import FhirClient


class BasePatientAccessFhirClientCreator(ABC):
    """
    Abstract base class for creating a FhirClient instance
    """

    @abstractmethod
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
        Abstract method to create a FHIRClient
        """
