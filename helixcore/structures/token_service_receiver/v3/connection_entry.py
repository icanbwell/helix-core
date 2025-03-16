import dataclasses
import json
from datetime import datetime
from dateutil import parser
from typing import Optional, Any, Dict

from helixcore.utilities.json_serializer.json_serializer import EnhancedJSONEncoder


@dataclasses.dataclass
class ConnectionEntry:
    """
    This class represents an entry from the Aperture Token Server


    """

    """ This is the id of the token entry in the Aperture Token Server """
    id: Optional[str]
    """ This is the master person id of the user who made this connection """
    bwell_fhir_person_id: Optional[str] = None
    """ This is the client person id of the user who made this connection """
    client_fhir_person_id: Optional[str] = None
    """ This is the name shown in the UI for this connection """
    display_name: Optional[str] = None
    """ This is the datetime when the connection was created """
    created_date: datetime | str | None = None
    """ This is the datetime when the connection expires """
    expiry: datetime | str | None = None
    """ This is the base url for the fhir server for this connection"""
    url: Optional[str] = None
    """ This is the version of fhir used by this connection"""
    fhir_version: Optional[str] = None
    """ This is the datetime when this connection was last updated e.g., token was refreshed """
    last_updated: datetime | str | None = None
    """ This is the member id of the user in the legacy platform"""
    member_id: Optional[str] = None
    """ This is the patient id of this record in the source system"""
    patient_id: Optional[str] = None
    """ This is the FHIR scope provided by the source system"""
    scope: Optional[str] = None
    """ This is the slug used in b.well to represent the source system"""
    service_slug: Optional[str] = None
    """ This is the source system id of the source system"""
    source_id_prefix: Optional[str] = None
    """ This is the current status of this connection"""
    status: Optional[str] = None
    """ This is the token to use to connect to this source system"""
    token: Optional[str] = None
    """ This is the payload provided by the source system.  Different EMRs provided different payloads"""
    token_payload: Optional[Dict[str, Any]] = None
    """ This is the type of source system we're talking to e.g., Epic, Cerner"""
    source_system_type: Optional[str] = None
    """ This is the type of ats connection"""
    category: Optional[str] = None
    """ This is the type of interoperability connection for ats"""
    interop_type: Optional[str] = None
    """ This is a string field with custom parameters entered in ConnectHub. """
    custom_api_parameters: Optional[str] = None
    """ This is a boolean field used to make fhir query. """
    fhir_search_supported: Optional[bool] = False

    """ This is the managing organization provided in a token"""
    managing_organization: Optional[str] = None

    """ This is a string field which represents cursor_id of the given entry. It can be used in pagination"""
    cursor_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.source_system_type = self._get_source_system_type()
        # check if dates are stored as string then convert them to datetime
        if isinstance(self.created_date, str):
            self.created_date = ConnectionEntry.parse_date(self.created_date)
        if isinstance(self.expiry, str):
            self.expiry = ConnectionEntry.parse_date(self.expiry)
        if isinstance(self.last_updated, str):
            self.last_updated = ConnectionEntry.parse_date(self.last_updated)

    @staticmethod
    def from_dict(token_result: Dict[str, Any]) -> "ConnectionEntry":
        my_dict = ConnectionEntry.parse_dict(token_result)
        return ConnectionEntry(**my_dict)

    @staticmethod
    def parse_dict(token_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses the input values from the passed in dictionary and returns a dictionary that can be used to
        instantiate the class


        :param token_result: dictionary to parse
        :return: dictionary that can be used to instantiate the class
        """
        my_dict: Dict[str, Any] = {
            "id": token_result.get("patient_id") or token_result.get("id"),
            "expiry": ConnectionEntry.parse_date(token_result.get("expiry")),
            "member_id": token_result.get("member_id"),
            "patient_id": token_result.get("patient_id") or token_result.get("id"),
            "display_name": token_result.get("display_name"),
            "token": token_result.get("token"),
            "service_slug": token_result.get("service_slug"),
            "url": (
                token_result.get("fhir_url")
                or token_result.get("url")
                or token_result.get("client_source_url")
            ),
            "last_updated": ConnectionEntry.parse_date(
                token_result.get("last_updated")
            ),
            "status": token_result.get("status"),
            "source_id_prefix": token_result.get("source_id_prefix"),
            "bwell_fhir_person_id": token_result.get("bwell_fhir_person_id"),
            "client_fhir_person_id": token_result.get("client_fhir_person_id"),
            "created_date": ConnectionEntry.parse_date(
                token_result.get("created_date")
            ),
            "fhir_version": token_result.get("fhir_version"),
            "token_payload": token_result.get("token_payload"),
            "scope": token_result.get("scope"),
            "category": token_result.get("category"),
            "interop_type": token_result.get("interop_type"),
            "custom_api_parameters": token_result.get("custom_api_parameters", None),
            "fhir_search_supported": token_result.get("fhir_search_supported", False),
            "managing_organization": token_result.get("managing_organization"),
            "cursor_id": token_result.get("cursor_id", None),
        }
        return my_dict

    @staticmethod
    def parse_date(date_str: Optional[str] | datetime) -> Optional[datetime]:
        if date_str is None:
            return None
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, float):
            return datetime.fromtimestamp(date_str)
        if isinstance(date_str, int):
            return datetime.fromtimestamp(date_str)
        assert isinstance(
            date_str, str
        ), f"Expected string but got {type(date_str)}: {date_str}"
        try:
            return parser.parse(date_str)
        except ValueError:
            return None

    def to_dict(self) -> Dict[str, Any]:
        dict_: Dict[str, Any] = self.__dict__
        return dict_

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), cls=EnhancedJSONEncoder)

    def _get_source_system_type(self) -> Optional[str]:
        """
        Tries to detect what type of source system we're talking to based on the token payload
        e.g., Epic, Cerner, Athena, etc.

        """
        if self.token_payload is None:
            return None
        # check if this is Epic
        if "epic.eci" in self.token_payload:
            return "Epic"
        # check if this is Cerner
        if "urn:cerner:authorization:claims:version:1" in self.token_payload:
            return "Cerner"
        # check if this is Athena
        if self.url and self.url.startswith("https://api.platform.athenahealth.com"):
            return "Athena"
        if self.url and self.url.startswith("https://fhir.nextgen.com"):
            return "NextGen"
        return None

    def get_expiry(self) -> Optional[datetime]:
        return self.parse_date(self.expiry)

    def get_last_updated(self) -> Optional[datetime]:
        return self.parse_date(self.last_updated)

    def get_created_date(self) -> Optional[datetime]:
        return self.parse_date(self.created_date)
