import dataclasses
from typing import Optional, List

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.helix_personmatching.logics.match_score import MatchScore
from helixcore.structures.helix_personmatching.logics.rule_score import RuleScore
from helixcore.structures.helix_personmatching.logics.scoring_input import ScoringInput
from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)


@dataclasses.dataclass
class PersonMatchResultOrError(DataClassJsonMixin):
    matched: bool
    error: Optional[PatientAccessError] = None
    match_results: List[MatchScore] | None = None
    highest_score: Optional[RuleScore] = None

    @property
    def first_match_result(self) -> MatchScore | None:
        if self.match_results is None or len(self.match_results) == 0:
            return None
        return self.match_results[0]

    @property
    def source(self) -> ScoringInput | None:
        """
        Returns the source ScoringInput if there is a match result, otherwise None.
        All match results should have the same source, so this is just a convenience method.

        :return: the source ScoringInput if there is a match result, otherwise None
        """
        return self.first_match_result.source if self.first_match_result else None

    @property
    def target(self) -> ScoringInput | None:
        """
        Returns the target ScoringInput if there is a match result, otherwise None
        All match results should have the same target, so this is just a convenience method.

        :return: the target ScoringInput if there is a match result, otherwise None
        """
        return self.first_match_result.target if self.first_match_result else None
