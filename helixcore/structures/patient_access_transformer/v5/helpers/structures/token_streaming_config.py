import dataclasses

from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_token_request import (
    PatientAccessTokenRequest,
)


@dataclasses.dataclass
class TokenStreamingConfig:
    enable_token_streaming: bool
    """ Whether to enable token streaming """

    enable_automatic_partitions: bool
    """ Whether to automatically determine partitions based on number of executors and cores"""

    token_request: PatientAccessTokenRequest
    """ The token request parameters """
