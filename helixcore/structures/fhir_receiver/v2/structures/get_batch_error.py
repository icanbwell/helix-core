import dataclasses
from typing import Optional

from dataclasses_json import DataClassJsonMixin


@dataclasses.dataclass
class GetBatchError(DataClassJsonMixin):
    url: str
    status_code: int
    error_text: str
    request_id: Optional[str]
