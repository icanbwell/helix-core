from typing import Optional, List, Dict


class FhirServerConfig:
    def __init__(
        self,
        *,
        url: Optional[str] = None,
        validation_url: Optional[str] = None,
        auth_server_url: Optional[str] = None,
        auth_client_id: Optional[str] = None,
        auth_client_secret: Optional[str] = None,
        auth_login_token: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_scopes: Optional[List[str]] = None,
        accept_type: Optional[str] = None,
        content_type: Optional[str] = None,
        accept_encoding: Optional[str] = None,
        ignore_status_codes: Optional[List[int]] = None,
        retry_count: Optional[int] = None,
        exclude_status_codes_from_retry: Optional[List[int]] = None,
    ) -> None:
        """
        This class captures the information needed to connect to a FHIR server


        :param url:
        :param auth_server_url: server url to call to get the authentication token
        :param auth_scopes: list of scopes to request permission for e.g., system/AllergyIntolerance.read
        :param headers: Additional request headers to send
        :param accept_type: (Optional) Accept header to use
        :param content_type: (Optional) Content-Type header to use
        :param accept_encoding: (Optional) Accept-encoding header to use
        :param ignore_status_codes: (Optional) do not throw an exception for these HTTP status codes
        """
        self.url = url

        self.auth_server_url: Optional[str] = auth_server_url
        self.validation_url: Optional[str] = validation_url
        self.auth_client_id: Optional[str] = auth_client_id
        self.auth_client_secret: Optional[str] = auth_client_secret
        self.auth_login_token: Optional[str] = auth_login_token
        self.auth_scopes: Optional[List[str]] = auth_scopes
        self.accept_type: Optional[str] = accept_type
        self.content_type: Optional[str] = content_type
        self.accept_encoding: Optional[str] = accept_encoding
        self.ignore_status_codes: Optional[List[int]] = ignore_status_codes
        self.retry_count: Optional[int] = retry_count
        self.exclude_status_codes_from_retry: Optional[List[int]] = (
            exclude_status_codes_from_retry
        )
        self.headers: Optional[Dict[str, str]] = headers
