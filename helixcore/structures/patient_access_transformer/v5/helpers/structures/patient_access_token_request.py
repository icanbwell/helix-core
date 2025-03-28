import dataclasses
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.patient_access_transformer.v5.helpers.structures.token_service_authentication import (
    TokenServiceAuthentication,
)


@dataclasses.dataclass
class PatientAccessTokenRequest(DataClassJsonMixin):
    """
    This class stores the input parameters to PatientAccessTokenReceiver

    """

    max_tokens_per_batch: int
    """ The maximum number of tokens to request in a single batch """

    limit_tokens_per_api_call: int
    """ The maximum number of tokens to request in a single API call """

    token_service_authentication: TokenServiceAuthentication
    """ The authentication for the token service """

    new_tokens_only: Optional[bool]
    """ Whether to only request new tokens """

    get_all_tokens: Optional[bool] = None
    """ Whether to get all tokens """

    token_statuses: Optional[List[str]] = None
    """ The statuses of the tokens to request """

    check_expiry_date: Optional[bool] = True
    """ Whether to check the expiry date of the token """

    token_category: Optional[str] = None
    """ The category of the token """
