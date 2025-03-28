class PatientAccessErrorCode:
    MAPPING_ERROR = "MAPPING_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    PERSON_MATCHING_ERROR = "PERSON_MATCHING_ERROR"
    ENRICHMENT_ERROR = "ENRICHMENT_ERROR"

    @staticmethod
    def get_message_for_error_code(error_code: str) -> str:
        if error_code == PatientAccessErrorCode.MAPPING_ERROR:
            return "Failure to map source data to FHIR"
        elif error_code == PatientAccessErrorCode.CONNECTION_ERROR:
            return "Failure connecting to source or internal server"
        elif error_code == PatientAccessErrorCode.PERSON_MATCHING_ERROR:
            return "Failure to match to a bWell person"
        elif error_code == PatientAccessErrorCode.ENRICHMENT_ERROR:
            return "Failure when running intelligence layer"
        else:
            return "Unknown application error"
