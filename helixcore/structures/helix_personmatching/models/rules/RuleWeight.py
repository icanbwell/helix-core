import dataclasses
from typing import Optional


@dataclasses.dataclass
class RuleWeight:
    exact_match: float
    partial_match: float
    missing: float
    boost: Optional[float] = None

    @staticmethod
    def get_standard_weight() -> "RuleWeight":
        return RuleWeight(exact_match=0.95, partial_match=0.95, missing=0.75)
