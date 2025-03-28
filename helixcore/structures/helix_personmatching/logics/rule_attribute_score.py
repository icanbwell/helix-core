from dataclasses import dataclass
from typing import Optional

from helix_personmatching.models.attribute_entry import AttributeEntry
from helix_personmatching.models.string_match_type import StringMatchType


@dataclass
class RuleAttributeScore:
    attribute: AttributeEntry
    score: float
    present: bool
    source: Optional[str]
    target: Optional[str]
    string_match_type: Optional[StringMatchType] = None
