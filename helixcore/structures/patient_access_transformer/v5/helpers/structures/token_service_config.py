import dataclasses


@dataclasses.dataclass
class TokenServiceConfig:
    token_service_url: str
    identity_provider_url: str
    client_id: str
    client_secret: str
