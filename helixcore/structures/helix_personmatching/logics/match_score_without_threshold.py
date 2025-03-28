import json
from dataclasses import dataclass
from typing import List, Optional, OrderedDict, Any

from helix_personmatching.logics.rule_score import RuleScore
from helix_personmatching.logics.scoring_input import ScoringInput
from helix_personmatching.utils.json_serializer import EnhancedJSONEncoder
from helix_personmatching.utils.score_diagnostics_generator import (
    ScoreDiagnosticsGenerator,
)


@dataclass
class MatchScoreWithoutThreshold:
    id_source: Optional[str]
    id_target: Optional[str]
    source: ScoringInput
    target: ScoringInput
    rule_scores: List[RuleScore]
    total_score: float
    total_score_unscaled: float
    average_score: float
    average_boost: Optional[float]
    diagnostics: List[OrderedDict[str, Any]] | None

    def __post_init__(self) -> None:
        self.diagnostics = self._generate_diagnostics()

    def to_json(
        self, include_diagnostics: bool = False, include_rule_scores: bool = False
    ) -> str:
        dict_ = self.__dict__
        if not include_diagnostics or not include_rule_scores:
            dict_ = self.__dict__.copy()

        if not include_diagnostics:
            # don't include diagnostics in the json by default
            dict_.pop("diagnostics")
        if not include_rule_scores:
            # don't include rule scores in the json by default
            dict_.pop("rule_scores")
        return json.dumps(dict_, cls=EnhancedJSONEncoder)

    def _generate_diagnostics(self) -> List[OrderedDict[str, Any]]:
        return ScoreDiagnosticsGenerator.generate_diagnostics(self.rule_scores)

    def get_diagnostics_as_csv(self) -> Optional[str]:
        return ScoreDiagnosticsGenerator.convert_to_csv(self.diagnostics)

    def get_diagnostics_as_json(self) -> Optional[str]:
        return json.dumps(self.diagnostics, cls=EnhancedJSONEncoder)
