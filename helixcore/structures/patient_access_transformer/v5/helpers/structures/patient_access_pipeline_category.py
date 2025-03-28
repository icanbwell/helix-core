from typing import Optional


class PatientAccessPipelineCategory:
    PROVIDER = "Provider"
    INSURANCE = "Insurance"
    HUMANAPI = "Hapi"
    COMMONWELL = "Commonwell"

    @staticmethod
    def get_from_text(text: Optional[str]) -> Optional[str]:
        if text is None:
            return None

        if text.lower() == PatientAccessPipelineCategory.PROVIDER.lower():
            return PatientAccessPipelineCategory.PROVIDER

        if text.lower() == PatientAccessPipelineCategory.INSURANCE.lower():
            return PatientAccessPipelineCategory.INSURANCE

        if text.lower() == PatientAccessPipelineCategory.HUMANAPI.lower():
            return PatientAccessPipelineCategory.HUMANAPI

        if text.lower() == PatientAccessPipelineCategory.COMMONWELL.lower():
            return PatientAccessPipelineCategory.COMMONWELL

        raise ValueError(f"{text} is not a known pipeline category")

    @staticmethod
    def is_human_api(pipeline_category: Optional[str]) -> bool:
        assert pipeline_category
        return (
            PatientAccessPipelineCategory.get_from_text(pipeline_category)
            == PatientAccessPipelineCategory.HUMANAPI
        )
