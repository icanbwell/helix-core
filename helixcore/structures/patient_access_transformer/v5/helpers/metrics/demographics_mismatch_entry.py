from dataclasses import dataclass
from datetime import datetime
from typing import Optional, override

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.helix_personmatching.logics.scoring_input import ScoringInput
from helixcore.utilities.metrics.base_metrics import (
    BaseMetric,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_match_result import (
    PatientAccessMatchResult,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.person_match_result_or_error import (
    PersonMatchResultOrError,
)
from helixcore.utilities.mysql.my_sql_text_helper.my_sql_text_helper import (
    MySqlTextHelper,
    MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
)
from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameStringType,
    DataFrameTimestampType,
    DataFrameBooleanType,
)


@dataclass
class DemographicsMismatchEntry(DataClassJsonMixin, BaseMetric):
    row_context: PatientAccessRowContext
    master_person_id: Optional[str]
    slug: Optional[str]
    patient_id: Optional[str]
    client_person_id: Optional[str]
    match_result: Optional[PatientAccessMatchResult]
    run_id: Optional[str] = None
    run_date_time: Optional[datetime] = None
    connection_type: Optional[str] = None
    fhir_version: Optional[str] = None
    pipeline_category: Optional[str] = None
    pipeline_version: Optional[str] = None
    new_tokens_only: Optional[bool] = None
    error: Optional[str] = None
    client_person_to_patient_match: Optional[str] = None
    client_person_to_patient_source: Optional[str] = None
    client_person_to_patient_target: Optional[str] = None
    client_person_to_patient_diagnostics: Optional[str] = None

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    def __post_init__(self) -> None:
        assert self.row_context, "row_context should not be None"
        self.run_id: Optional[str] = self.row_context.run_context.run_id
        self.run_date_time: Optional[datetime] = (
            self.row_context.run_context.run_date_time
        )
        self.connection_type: Optional[str] = (
            self.row_context.run_context.connection_type
        )
        self.fhir_version: Optional[str] = (
            self.row_context.connection_entry.fhir_version
        )
        self.pipeline_category: Optional[str] = (
            self.row_context.run_context.pipeline_category
        )
        self.pipeline_version: Optional[str] = (
            self.row_context.run_context.pipeline_version
        )
        self.new_tokens_only: Optional[bool] = (
            self.row_context.run_context.new_tokens_only
        )

        self.error: Optional[str] = MySqlTextHelper.truncate(
            text=self.match_result.get_error_text() if self.match_result else None,
            maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
        )
        client_person_to_patient_match_result: PersonMatchResultOrError | None = (
            self.match_result.client_person_to_patient_match_result
            if self.match_result is not None
            and self.match_result.client_person_to_patient_match_result is not None
            else None
        )
        client_person_to_patient_source: ScoringInput | None = (
            self.match_result.client_person_to_patient_match_result.source
            if self.match_result is not None
            and self.match_result.client_person_to_patient_match_result is not None
            else None
        )
        client_person_to_patient_target: ScoringInput | None = (
            self.match_result.client_person_to_patient_match_result.target
            if self.match_result is not None
            and self.match_result.client_person_to_patient_match_result is not None
            else None
        )

        self.client_person_to_patient_match: Optional[str] = MySqlTextHelper.truncate(
            (
                client_person_to_patient_match_result.to_json()
                if client_person_to_patient_match_result
                else None
            ),
            maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
        )

        # noinspection PyUnresolvedReferences
        self.client_person_to_patient_source: Optional[str] = MySqlTextHelper.truncate(
            client_person_to_patient_source.to_json()
            if client_person_to_patient_source
            else None
        )
        # noinspection PyUnresolvedReferences
        self.client_person_to_patient_target: Optional[str] = MySqlTextHelper.truncate(
            client_person_to_patient_target.to_json()
            if client_person_to_patient_target
            else None
        )

        self.client_person_to_patient_diagnostics: Optional[str] = (
            MySqlTextHelper.truncate(
                (
                    client_person_to_patient_match_result.first_match_result.get_diagnostics_as_csv()
                    if client_person_to_patient_match_result
                    and client_person_to_patient_match_result.first_match_result
                    is not None
                    else None
                ),
                maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
            )
        )

    @override
    @property
    def spark_schema(self) -> DataFrameStructType:
        return self.get_schema()

    def get_create_ddl(self, db_schema_name: str, db_table_name: str) -> str:
        return self.get_create_statement_ddl(
            db_schema_name=db_schema_name, db_table_name=db_table_name
        )

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
                DataFrameStructField("slug", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "patient_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "client_person_id", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField("error", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "client_person_to_patient_match",
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    "client_person_to_patient_source",
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    "client_person_to_patient_target",
                    DataFrameStringType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    "client_person_to_patient_diagnostics",
                    DataFrameStringType(),
                    nullable=True,
                ),
            ]
        )

    @staticmethod
    def get_create_statement_ddl(db_schema_name: str, db_table_name: str) -> str:
        """
        Gets the DDL statement to create the table


        :param db_schema_name: the schema name
        :param db_table_name: the table name
        :return: the DDL statement
        """
        assert db_schema_name is not None
        assert db_table_name is not None

        ddl_statement: str = f"""
-- {db_schema_name}.{db_table_name} definition
CREATE SCHEMA IF NOT EXISTS {db_schema_name};

CREATE TABLE IF NOT EXISTS {db_schema_name}.{db_table_name} (
    ID BIGINT NOT NULL  auto_increment COMMENT 'Primary key',
    run_id VARCHAR(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
    run_date_time DATETIME NOT NULL COMMENT 'When was this flow run',
    connection_type VARCHAR(255) NULL COMMENT 'Type of connection: proa, hapi, hie',
    fhir_version VARCHAR(255) NULL COMMENT 'FHIR version: r4, dstu2',
    pipeline_category VARCHAR(255) NULL COMMENT 'Category of pipeline: Provider, Insurance',
    pipeline_version VARCHAR(255) NULL COMMENT 'Version of helix.pipelines release',
    new_tokens_only BOOLEAN NULL COMMENT 'Whether we only want to use new tokens',
    master_person_id VARCHAR(255) NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
    slug VARCHAR(255) NULL COMMENT 'Slug in b.well that identifies the source system',
    patient_id VARCHAR(255) NULL COMMENT 'Patient id in the source system',
    client_person_id VARCHAR(255) NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
    error MEDIUMTEXT NULL COMMENT 'Error while matching',
    client_person_to_patient_match MEDIUMTEXT NULL COMMENT 'Match result of client person to patient',
    client_person_to_patient_source TEXT NULL COMMENT 'Source of client person to patient match',
    client_person_to_patient_target TEXT NULL COMMENT 'Target of client person to patient match',
    client_person_to_patient_diagnostics MEDIUMTEXT NULL COMMENT 'Diagnostics of client person to patient match',
    PRIMARY KEY (ID)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;
"""  # noqa: E501
        return ddl_statement
