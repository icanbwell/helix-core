from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict, override

from dataclasses_json import DataClassJsonMixin
from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.utilities.mysql.my_sql_text_helper.my_sql_text_helper import (
    MySqlTextHelper,
    MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
    MYSQL_TEXT_MAX_CHARACTERS,
)
from helixcore.utilities.data_frame_types.data_frame_types import (
    DataFrameStructType,
    DataFrameStructField,
    DataFrameStringType,
    DataFrameTimestampType,
    DataFrameBooleanType,
    DataFrameIntegerType,
    DataFrameFloatType,
)


@dataclass
class PatientAccessMetrics(DataClassJsonMixin, BaseMetric):
    partition_index: int
    chunk_index: int
    row_context: PatientAccessRowContext
    number_of_resources: int
    time_to_get_resources_from_source: Optional[float]
    time_send_resources_to_fhir: Optional[float]
    time_to_match_person: Optional[float]
    matched: Optional[bool]
    warning_count: int
    error_count: int
    start_time: datetime
    end_time: datetime
    slug: Optional[str] = None
    url: Optional[str] = None
    patient_id: Optional[str] = None
    client_person_id: Optional[str] = None
    master_person_id: Optional[str] = None
    run_id: str | None = None
    run_date_time: Optional[datetime] = None
    pipeline_category: Optional[str] = None
    new_tokens_only: Optional[bool] = None
    connection_type: Optional[str] = None
    pipeline_version: Optional[str] = None
    fhir_version: Optional[str] = None
    token: Optional[str] = None
    last_updated: Optional[datetime] = None
    created_date: Optional[datetime] = None
    expiry: Optional[datetime] = None
    scope: Optional[str] = None
    source_system_type: Optional[str] = None
    status: Optional[str] = None
    partition_start_time: Optional[datetime] = None
    chunk_start_time: Optional[datetime] = None

    def __getstate__(self) -> Dict[str, Any]:
        # Exclude certain properties from being pickled otherwise they cause errors in pickling
        return {k: v for k, v in self.__dict__.items() if k not in ["row_context"]}

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    def __post_init__(self) -> None:
        assert self.row_context, "row_context should not be None"
        self.slug = self.row_context.connection_entry.service_slug
        self.url = MySqlTextHelper.truncate(
            self.row_context.connection_entry.url,
            maximum_length=MYSQL_TEXT_MAX_CHARACTERS,
        )
        self.patient_id = self.row_context.connection_entry.patient_id
        self.client_person_id = self.row_context.connection_entry.client_fhir_person_id
        self.master_person_id = self.row_context.connection_entry.bwell_fhir_person_id
        self.run_id = self.row_context.run_context.run_id
        self.run_date_time = self.row_context.run_context.run_date_time
        self.pipeline_category = self.row_context.run_context.pipeline_category
        self.new_tokens_only = self.row_context.run_context.new_tokens_only
        self.connection_type = self.row_context.run_context.connection_type
        self.pipeline_version = self.row_context.run_context.pipeline_version
        self.fhir_version = self.row_context.connection_entry.fhir_version
        self.token = self.row_context.connection_entry.token
        self.last_updated = self.row_context.connection_entry.get_last_updated()
        self.created_date = self.row_context.connection_entry.get_created_date()
        self.expiry = self.row_context.connection_entry.get_expiry()
        self.scope = MySqlTextHelper.truncate(
            self.row_context.connection_entry.scope,
            maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
        )
        self.source_system_type = self.row_context.connection_entry.source_system_type
        self.status = self.row_context.connection_entry.status

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
    def get_schema() -> DataFrameStructType:
        schema = DataFrameStructType(
            [
                DataFrameStructField("run_id", DataFrameStringType(), nullable=False),
                DataFrameStructField(
                    "run_date_time", DataFrameTimestampType(), nullable=False
                ),
                DataFrameStructField(
                    "start_time", DataFrameTimestampType(), nullable=False
                ),
                DataFrameStructField(
                    "end_time", DataFrameTimestampType(), nullable=False
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
                DataFrameStructField("slug", DataFrameStringType(), nullable=True),
                DataFrameStructField("url", DataFrameStringType(), nullable=True),
                DataFrameStructField("status", DataFrameStringType(), nullable=True),
                DataFrameStructField("token", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "number_of_resources", DataFrameIntegerType(), nullable=False
                ),
                DataFrameStructField(
                    "error_count", DataFrameIntegerType(), nullable=True
                ),
                DataFrameStructField(
                    "warning_count", DataFrameIntegerType(), nullable=True
                ),
                DataFrameStructField(
                    "time_to_get_resources_from_source",
                    DataFrameFloatType(),
                    nullable=True,
                ),
                DataFrameStructField(
                    "time_send_resources_to_fhir", DataFrameFloatType(), nullable=True
                ),
                DataFrameStructField(
                    "time_to_match_person", DataFrameFloatType(), nullable=True
                ),
                DataFrameStructField("matched", DataFrameBooleanType(), nullable=True),
                DataFrameStructField(
                    "partition_index", DataFrameIntegerType(), nullable=False
                ),
                DataFrameStructField(
                    "chunk_index", DataFrameIntegerType(), nullable=False
                ),
                DataFrameStructField(
                    "partition_start_time", DataFrameTimestampType(), nullable=True
                ),
                DataFrameStructField(
                    "chunk_start_time", DataFrameTimestampType(), nullable=True
                ),
            ]
        )
        return schema

    @staticmethod
    def get_create_statement_ddl(db_schema_name: str, db_table_name: str) -> str:
        ddl_statement: str = f"""
-- {db_schema_name}.{db_table_name} definition
CREATE SCHEMA IF NOT EXISTS {db_schema_name};

CREATE TABLE IF NOT EXISTS {db_schema_name}.{db_table_name} (
    ID BIGINT NOT NULL  auto_increment COMMENT 'Primary key',
    run_id VARCHAR(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
    run_date_time DATETIME NOT NULL COMMENT 'When was this flow run',
    start_time DATETIME NOT NULL COMMENT 'When did we start downloading this patient record',
    end_time DATETIME NOT NULL COMMENT 'When did we finish downloading this patient record',
    connection_type VARCHAR(255) NULL COMMENT 'Type of connection: proa, hapi, hie',
    fhir_version VARCHAR(255) NULL COMMENT 'FHIR version: r4, dstu2',
    pipeline_category VARCHAR(255) NULL COMMENT 'Category of pipeline: Provider, Insurance',
    pipeline_version VARCHAR(255) NULL COMMENT 'Version of helix.pipelines release',
    new_tokens_only BOOLEAN NULL COMMENT 'Whether we only want to use new tokens',
    master_person_id VARCHAR(255) NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
    client_person_id VARCHAR(255) NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
    patient_id VARCHAR(255) NULL COMMENT 'Patient id in the source system',
    source_system_type VARCHAR(255) NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
    created_date DATETIME NULL COMMENT 'Date the token was created',
    last_updated DATETIME NULL COMMENT 'Date the token was last updated',
    expiry DATETIME NULL COMMENT 'Date the token expires',
    scope MEDIUMTEXT NULL COMMENT 'Scope of the token',
    slug VARCHAR(255) NULL COMMENT 'Slug in b.well that identifies the source system',
    status VARCHAR(255) NULL COMMENT 'Status of the token',
    token TEXT NULL COMMENT 'Token used to access the source system',
    url TEXT NULL COMMENT 'url of the source system',
    number_of_resources INT NOT NULL COMMENT 'Number of resources successfully retrieved from the source system for this patient record',
    error_count INT NOT NULL COMMENT 'Number of errors encountered while retrieving this patient record',
    warning_count INT NOT NULL COMMENT 'Number of warnings encountered while retrieving this patient record',
    time_to_get_resources_from_source FLOAT COMMENT 'Time in seconds to get resources from source system',
    time_send_resources_to_fhir FLOAT COMMENT 'Time in seconds to send resources to b.well FHIR',
    time_to_match_person FLOAT COMMENT 'Time in seconds to match person',
    matched BOOLEAN COMMENT 'Whether the person was matched',
    partition_index INT NULL COMMENT 'Partition index',
    chunk_index INT NULL COMMENT 'Chunk index',
    partition_start_time DATETIME NULL COMMENT 'When did we start processing this batch',
    chunk_start_time DATETIME NULL COMMENT 'When did we start processing this chunk',
    PRIMARY KEY (ID)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;
"""  # noqa: E501
        return ddl_statement
