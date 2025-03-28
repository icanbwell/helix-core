from dataclasses import dataclass
from typing import Optional
from dataclasses_json import DataClassJsonMixin


@dataclass
class RawResourceInfo(DataClassJsonMixin):
    url: Optional[str]
    resource_type: str
    resource: str
