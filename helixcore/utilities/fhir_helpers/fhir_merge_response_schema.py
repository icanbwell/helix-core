from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameStringType,
    DataFrameArrayType,
    DataFrameIntegerType,
)


class FhirMergeResponseSchema:
    """
    This class provides names for columns in FhirMergeResponse

    Should match to https://github.com/icanbwell/helix.fhir.client.sdk/blob/main/helix_fhir_client_sdk/responses/fhir_merge_response.py
    """

    request_id = "request_id"
    url = "url"
    responses = "responses"
    error = "error"
    access_token = "access_token"
    status = "status"
    data = "data"

    @staticmethod
    def get_schema() -> DataFrameStructType:
        """
        Returns the schema of FhirMergeResponse

        Should match to https://github.com/icanbwell/helix.fhir.client.sdk/blob/main/helix_fhir_client_sdk/responses/fhir_merge_response.py
        """
        response_schema = DataFrameStructType(
            [
                DataFrameStructField(
                    "request_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField("url", DataFrameStringType(), nullable=False),
                DataFrameStructField(
                    "responses",
                    DataFrameArrayType(DataFrameStringType()),
                    nullable=False,
                ),
                DataFrameStructField("error", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "access_token", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField("status", DataFrameIntegerType(), nullable=False),
                DataFrameStructField("data", DataFrameStringType(), nullable=False),
            ]
        )
        return response_schema
