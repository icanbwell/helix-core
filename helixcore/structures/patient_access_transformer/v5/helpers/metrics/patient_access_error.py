import traceback

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, ClassVar, Dict, override

from dataclasses_json import DataClassJsonMixin, config, LetterCase
from dataclasses_json.core import Json
from helix_fhir_client_sdk.utilities.fhir_scope_parser import FhirScopeParser

from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_issue_severity import (
    PatientAccessIssueSeverity,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.utilities.fhir.fhir_resource_helpers.v2.fhir_resource_helpers import (
    FhirResourceHelpers,
)
from helixcore.utilities.mysql.my_sql_text_helper.my_sql_text_helper import (
    MySqlTextHelper,
    MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
    MYSQL_LONGTEXT_MAX_CHARACTERS,
    MYSQL_TEXT_MAX_CHARACTERS,
)
from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameStringType,
    DataFrameTimestampType,
    DataFrameBooleanType,
)


@dataclass
class PatientAccessError(DataClassJsonMixin, BaseMetric):
    potential_clientside_error_codes: ClassVar[List[int]] = [403, 404]

    request_id: Optional[str]
    resource_id: Optional[str]
    resource_type: Optional[str] = field(metadata=config(letter_case=LetterCase.CAMEL))
    url: Optional[str]
    error_text: Optional[str]
    status_code: Optional[int]
    step: str
    resource_json: Optional[str]
    severity: str
    error_code: Optional[str]
    raw_resource_json: Optional[str]

    # These fields are set from row_context
    client_person_id: Optional[str]
    client_source_url: Optional[str]
    slug: Optional[str]
    master_person_id: Optional[str]
    connection_type: str
    fhir_version: Optional[str]
    run_id: str
    run_date_time: datetime
    pipeline_category: Optional[str]
    new_tokens_only: Optional[bool]
    pipeline_version: Optional[str]
    token: Optional[str]
    patient_id: Optional[str]
    last_updated: Optional[datetime]
    created_date: Optional[datetime]
    expiry: Optional[datetime]
    scope: Optional[str]
    source_system_type: Optional[str]

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @classmethod
    def construct(
        cls,
        *,
        row_context: PatientAccessRowContext,
        request_id: Optional[str],
        resource_id: Optional[str],
        resource_type: Optional[str],
        url: Optional[str],
        error_text: Optional[str],
        status_code: Optional[int],
        step: str,
        resource_json: Optional[str],
        severity: str,
        error_code: Optional[str] = None,
        raw_resource_json: Optional[str] = None,
        exception: Optional[Exception],
    ) -> "PatientAccessError":
        """
        Read values from the row context and set them as attributes

        :param row_context: row context
        :param request_id: request id
        :param resource_id: resource's id
        :param resource_type: resource type
        :param url: url
        :param error_text: error text
        :param status_code: status code
        :param step: step
        :param resource_json: resource json
        :param severity: severity
        :param error_code: error code
        :param raw_resource_json: raw resource json
        :param exception: exception
        :return:
        """
        assert row_context, "row_context must be provided"
        assert row_context.run_context, "run_context must be provided"
        # read values from the run context
        client_person_id: Optional[str] = (
            row_context.connection_entry.client_fhir_person_id
        )
        client_source_url: Optional[str] = row_context.connection_entry.url
        slug: Optional[str] = row_context.connection_entry.service_slug
        master_person_id: Optional[str] = (
            row_context.connection_entry.bwell_fhir_person_id
        )
        connection_type: str = row_context.run_context.connection_type
        fhir_version: Optional[str] = row_context.connection_entry.fhir_version
        run_id: str = row_context.run_context.run_id
        run_date_time: datetime = row_context.run_context.run_date_time
        pipeline_category: Optional[str] = row_context.run_context.pipeline_category
        new_tokens_only: Optional[bool] = row_context.run_context.new_tokens_only
        pipeline_version: Optional[str] = row_context.run_context.pipeline_version
        token: Optional[str] = row_context.connection_entry.token
        patient_id: Optional[str] = row_context.connection_entry.patient_id
        last_updated: Optional[datetime] = (
            row_context.connection_entry.get_last_updated()
        )
        created_date: Optional[datetime] = (
            row_context.connection_entry.get_created_date()
        )
        expiry: Optional[datetime] = row_context.connection_entry.get_expiry()
        scope: Optional[str] = MySqlTextHelper.truncate(
            row_context.connection_entry.scope,
            maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
        )
        source_system_type: Optional[str] = (
            row_context.connection_entry.source_system_type
        )

        url = MySqlTextHelper.truncate(url, maximum_length=MYSQL_TEXT_MAX_CHARACTERS)
        if exception is not None:
            error_text = (
                (error_text or "")
                + "\n"
                + "\n".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                )
            )
        error_text = MySqlTextHelper.truncate(
            error_text, maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS
        )
        resource_json = MySqlTextHelper.truncate(
            resource_json, maximum_length=MYSQL_LONGTEXT_MAX_CHARACTERS
        )
        raw_resource_json = MySqlTextHelper.truncate(
            raw_resource_json, maximum_length=MYSQL_LONGTEXT_MAX_CHARACTERS
        )

        return cls(
            request_id=request_id,
            resource_id=resource_id,
            resource_type=resource_type,
            url=url,
            error_text=error_text,
            status_code=status_code,
            step=step,
            resource_json=resource_json,
            severity=severity,
            error_code=error_code,
            raw_resource_json=raw_resource_json,
            client_person_id=client_person_id,
            client_source_url=client_source_url,
            slug=slug,
            master_person_id=master_person_id,
            connection_type=connection_type,
            fhir_version=fhir_version,
            run_id=run_id,
            run_date_time=run_date_time,
            pipeline_category=pipeline_category,
            new_tokens_only=new_tokens_only,
            pipeline_version=pipeline_version,
            token=token,
            patient_id=patient_id,
            last_updated=last_updated,
            created_date=created_date,
            expiry=expiry,
            scope=scope,
            source_system_type=source_system_type,
        )

    def to_dict(self, encode_json: bool = False) -> Dict[str, Json]:
        my_dict: Dict[str, Json] = super().to_dict(encode_json=encode_json)
        # remove the row context from serialization
        my_dict.pop("row_context", None)
        return my_dict

    # noinspection PyPep8Naming
    @property
    def resourceType(self) -> Optional[str]:
        return self.resource_type

    @property
    def spark_schema(self) -> DataFrameStructType:
        return self.get_schema()

    @classmethod
    @override
    def get_create_ddl(cls, db_schema_name: str, db_table_name: str) -> str:
        return cls.get_create_statement_ddl(
            db_schema_name=db_schema_name, db_table_name=db_table_name
        )

    @staticmethod
    def check_clientside_error_severity(
        row_context: PatientAccessRowContext,
        scope: Optional[str],
        status_code: int,
        resource_type: Optional[str],
        url: Optional[str],
        severity: str,
    ) -> str:
        scope_parser: FhirScopeParser = FhirScopeParser(
            scope.split(" ") if isinstance(scope, str) else None
        )
        if (
            status_code == 404
            and url is not None
            and (
                FhirResourceHelpers.sanitize_reference(
                    value=str(url), extract_relative_url=True
                )
                is not None
            )
        ):
            return PatientAccessIssueSeverity.WARNING
        elif (
            (status_code == 403)
            and (resource_type == "Encounter")
            and (row_context.connection_entry.custom_api_parameters == "epic")
            and scope_parser.scope_allows(resource_type="Encounter", interaction="read")
        ):
            return PatientAccessIssueSeverity.WARNING
        else:
            return severity

    @staticmethod
    def get_schema() -> DataFrameStructType:
        return DataFrameStructType(
            [
                DataFrameStructField("run_id", DataFrameStringType(), nullable=False),
                DataFrameStructField(
                    "run_date_time", DataFrameTimestampType(), nullable=False
                ),
                DataFrameStructField(
                    "connection_type", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "fhir_version", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "pipeline_category", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "pipeline_version", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "new_tokens_only", DataFrameBooleanType(), nullable=True
                ),
                DataFrameStructField(
                    "master_person_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "client_person_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "patient_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "client_source_url", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField("step", DataFrameStringType(), nullable=False),
                DataFrameStructField("severity", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "source_system_type", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "created_date", DataFrameTimestampType(), nullable=True
                ),
                DataFrameStructField(
                    "last_updated", DataFrameTimestampType(), nullable=True
                ),
                DataFrameStructField("expiry", DataFrameTimestampType(), nullable=True),
                DataFrameStructField("scope", DataFrameStringType(), nullable=True),
                DataFrameStructField("token", DataFrameStringType(), nullable=True),
                DataFrameStructField("slug", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "resourceType", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "request_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "resource_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField("url", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "status_code", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "error_text", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "raw_resource_json", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "resource_json", DataFrameStringType(), nullable=True
                ),
            ]
        )

    @staticmethod
    def get_create_statement_ddl(db_schema_name: str, db_table_name: str) -> str:
        ddl_statement = f"""
-- {db_schema_name}.{db_table_name} definition
CREATE SCHEMA IF NOT EXISTS {db_schema_name};

CREATE TABLE IF NOT EXISTS {db_schema_name}.{db_table_name} (
    ID BIGINT NOT NULL  auto_increment COMMENT 'Primary key',
    run_id VARCHAR(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
    run_date_time DATETIME NOT NULL COMMENT 'Flow run date time in Prefect that created this row',
    connection_type VARCHAR(255) NULL COMMENT 'Type of connection: proa, hapi, hie',
    fhir_version VARCHAR(255) NULL COMMENT 'FHIR version: r4, dstu2',
    pipeline_category VARCHAR(255) NULL COMMENT 'Category of pipeline: Provider, Insurance',
    pipeline_version VARCHAR(255) NULL COMMENT 'Version of helix.pipelines release',
    new_tokens_only BOOLEAN NULL COMMENT 'Whether we only want to use new tokens',
    master_person_id VARCHAR(255) NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
    client_person_id VARCHAR(255) NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
    patient_id VARCHAR(255) NULL COMMENT 'Patient id in the source system',
    client_source_url VARCHAR(255) NULL COMMENT 'Base url of the source system',
    step VARCHAR(255) NOT NULL COMMENT 'Step in the process where the error occurred',
    severity VARCHAR(255) NOT NULL COMMENT 'Severity of the error: fatal, error, warning, information',
    source_system_type VARCHAR(255) NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
    created_date DATETIME NULL COMMENT 'Date the token was created',
    last_updated DATETIME NULL COMMENT 'Date the token was last updated',
    expiry DATETIME NULL COMMENT 'Date the token expires',
    scope MEDIUMTEXT NULL COMMENT 'Scope of the token',
    token TEXT NULL COMMENT 'Token used to access the source system',
    slug VARCHAR(255) NULL COMMENT 'Slug in b.well that identifies the source system',
    resourceType VARCHAR(255) NULL COMMENT 'FHIR resourceType: Patient, Practitioner, Organization, Coverage, Observation',
    request_id VARCHAR(255) NULL COMMENT 'Request id from b.well FHIR server if the error was sending data to our FHIR server',
    resource_id VARCHAR(255) NULL COMMENT 'Resource id of the resource with the error',
    url TEXT NULL COMMENT 'Full url to retrieve this resource',
    status_code VARCHAR(64) NULL COMMENT 'HTTP status code returned by the FHIR server',
    error_text MEDIUMTEXT NULL COMMENT 'Error text returned by the FHIR server',
    raw_resource_json LONGTEXT NULL COMMENT 'JSON of the resource with the error',
    resource_json LONGTEXT NULL COMMENT 'JSON of the resource with the error',
    PRIMARY KEY (ID)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;
"""  # noqa: E501
        return ddl_statement
