import json
from dataclasses import dataclass
from typing import Optional

from helixcore.utilities.json_serializer.json_serializer import EnhancedJSONEncoder


@dataclass
class ScoringInput:
    id_: Optional[str]
    name_given: Optional[str]
    name_middle: Optional[str]
    name_middle_initial: Optional[str]
    name_family: Optional[str]
    gender: Optional[str]
    birth_date: Optional[str]
    address_postal_code: Optional[str]
    address_postal_code_first_five: Optional[str]
    address_line_1: Optional[str]
    address_line_1_st_num: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    birth_date_year: Optional[str]
    birth_date_month: Optional[str]
    birth_date_day: Optional[str]
    phone_area: Optional[str]
    phone_local: Optional[str]
    phone_line: Optional[str]
    email_username: Optional[str]
    is_adult_today: Optional[bool]
    ssn: Optional[str]
    ssn_last4: Optional[str]
    meta_security_client_slug: Optional[str]

    def to_json(self) -> str:
        return json.dumps(self, cls=EnhancedJSONEncoder)
