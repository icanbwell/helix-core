import dataclasses
from datetime import datetime
from typing import Optional

from helixcore.structures.patient_access_transformer.v5.helpers.structures.token_service_config import (
    TokenServiceConfig,
)


@dataclasses.dataclass
class TokenServiceAuthentication:
    """This class encapsulates an authentication token for a token service"""

    config: TokenServiceConfig
    """ The configuration for the token service """

    access_token: Optional[str] = None
    """ The access token """

    login_token: Optional[str] = None
    """ The login token """

    refresh_token: Optional[str] = None
    """ The refresh token """

    access_token_expiry: Optional[str] = None
    """ The expiry date of the access token """

    access_token_last_refresh: Optional[datetime] = None
    """ The date and time of the last access token refresh """
