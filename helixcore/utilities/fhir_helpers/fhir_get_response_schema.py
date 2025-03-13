from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameIntegerType,
    DataFrameArrayType,
    DataFrameStringType,
)


class FhirGetResponseSchema:
    """
    This class provides names for columns in FhirGetResponse

    Should match to
    https://github.com/icanbwell/helix.fhir.client.sdk/blob/main/helix_fhir_client_sdk/responses/fhir_get_response.py
    """

    partition_index = "partition_index"
    sent = "sent"
    received = "received"
    responses = "responses"
    first = "first"
    last = "last"
    error_text = "error_text"
    url = "url"
    status_code = "status_code"
    request_id = "request_id"
    access_token = "access_token"
    extra_context_to_return = "extra_context_to_return"

    @staticmethod
    def get_schema() -> DataFrameStructType:
        """
        Returns the schema of FhirGetResponse

        Should match to
        https://github.com/icanbwell/helix.fhir.client.sdk/blob/main/helix_fhir_client_sdk/responses/fhir_get_response.py
        """
        response_schema = DataFrameStructType(
            [
                DataFrameStructField(
                    FhirGetResponseSchema.partition_index,
                    DataFrameIntegerType(),
                    nullable=False,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.sent, DataFrameIntegerType(), nullable=False
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.received,
                    DataFrameIntegerType(),
                    nullable=False,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.responses,
                    DataFrameArrayType(DataFrameStringType()),
                    nullable=False,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.first, DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.last, DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.error_text,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.url, DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.status_code,
                    DataFrameIntegerType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.request_id,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.access_token,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirGetResponseSchema.extra_context_to_return,
                    DataFrameStringType(),
                    nullable=True,
                ),
            ]
        )
        return response_schema
