from collections import OrderedDict
from typing import List, Any, Dict, Optional

from helixcore.structures.helix_personmatching.logics.rule_score import RuleScore


class ScoreDiagnosticsGenerator:
    @staticmethod
    def generate_diagnostics(
        rule_scores: List[RuleScore],
    ) -> List[OrderedDict[str, Any]]:
        """
        Generates diagnostics for the given rule scores.


        :param rule_scores: the rule scores
        :return: the diagnostics
        """
        score_out_list: List[Dict[str, Any]] = []
        score_out_unique_keys: List[str] = [
            "rule_name",
            "description",
            "score",
            "boost",
        ]

        sorted_rule_scores = sorted(
            rule_scores, key=lambda x: x.rule_score, reverse=True
        )
        for rule_score in sorted_rule_scores:
            score_out: Dict[str, Any] = {
                "rule_name": rule_score.rule_name,
                "description": rule_score.rule_description,
                "score": rule_score.rule_score,
                "boost": rule_score.rule_boost,
            }
            for attribute_score in rule_score.attribute_scores:
                score_out[f"{attribute_score.attribute.name}_source"] = (
                    attribute_score.source
                )
                score_out[f"{attribute_score.attribute.name}_target"] = (
                    attribute_score.target
                )
                score_out[f"{attribute_score.attribute.name}_score"] = (
                    attribute_score.score
                )
            score_out_list.append(score_out)
            for key in score_out.keys():
                if key not in score_out_unique_keys:
                    score_out_unique_keys.append(key)

        # now create the list of OrderedDicts
        scores_list: List[OrderedDict[str, Any]] = []
        for score_out in score_out_list:
            score_ordered_dict: OrderedDict[str, Any] = OrderedDict()
            for unique_key in score_out_unique_keys:
                if unique_key in score_out:
                    score_ordered_dict[unique_key] = score_out[unique_key]
                else:
                    score_ordered_dict[unique_key] = None
            scores_list.append(score_ordered_dict)

        return scores_list

    @staticmethod
    def convert_to_csv(scores: List[OrderedDict[str, Any]] | None) -> Optional[str]:
        if scores is None or len(scores) == 0:
            return None

        header: str = ",".join(scores[0].keys())
        rows: List[str] = [
            ",".join(
                [
                    ScoreDiagnosticsGenerator.format_value(value)
                    for value in score.values()
                ]
            )
            for score in scores
        ]
        rows_text = "\n".join(rows)
        return f"{header}\n{rows_text}"

    @staticmethod
    def format_value(value: Optional[Any]) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:.3f}"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, int):
            return str(value)
        if isinstance(value, str) and "," in value:
            return f'"{value}"'
        return f"{value}"
