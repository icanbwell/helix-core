import dataclasses
from typing import Optional

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.token_service_receiver.v3.connection_entry import (
    ConnectionEntry,
)


@dataclasses.dataclass
class PatientAccessRow(DataClassJsonMixin, ConnectionEntry):
    resourceType: Optional[str] = None
    client_source_url: Optional[str] = None

    def __post_init__(self) -> None:
        if self.url is None:
            self.url = self.client_source_url
        if self.client_source_url is None:
            self.client_source_url = self.url
        if self.patient_id is not None and self.id is None:
            self.id = self.patient_id
        if self.patient_id is None and self.id is not None:
            self.patient_id = self.id

    @classmethod
    def from_connection_entry(
        cls, connection_entry: ConnectionEntry
    ) -> "PatientAccessRow":
        return PatientAccessRow.from_dict(connection_entry.to_dict())
