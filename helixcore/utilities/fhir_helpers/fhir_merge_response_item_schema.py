from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameStringType,
    DataFrameBooleanType,
)


class FhirMergeResponseItemSchema:
    updated = "updated"
    created = "created"
    deleted = "deleted"
    issue = "issue"
    id_ = "id"
    uuid = "uuid"
    resourceType = "resourceType"
    sourceAssigningAuthority = "sourceAssigningAuthority"
    resource_version = "resource_version"
    message = "message"
    error = "error"
    token = "token"
    resource_json = "resource_json"

    @staticmethod
    def get_schema() -> DataFrameStructType:
        """
        Returns the schema of FhirMergeResponse

        Should match to
        https://github.com/icanbwell/helix.fhir.client.sdk/blob/main/helix_fhir_client_sdk/responses/fhir_merge_response.py
        """
        response_schema = DataFrameStructType(
            [
                DataFrameStructField(
                    FhirMergeResponseItemSchema.created,
                    DataFrameBooleanType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.updated,
                    DataFrameBooleanType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.deleted,
                    DataFrameBooleanType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.id_,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.uuid,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.resourceType,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.sourceAssigningAuthority,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.resource_version,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.message,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.issue,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.error,
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    FhirMergeResponseItemSchema.token,
                    DataFrameStringType(),
                    nullable=True,
                ),
            ]
        )
        return response_schema
