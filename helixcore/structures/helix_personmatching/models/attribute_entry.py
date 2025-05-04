from dataclasses import dataclass
from typing import Optional


@dataclass
class AttributeEntry:
    name: str
    exact_only: Optional[bool] = None
    nick_name_match: Optional[bool] = None
