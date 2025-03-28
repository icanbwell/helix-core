from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, cast

from dataclasses_json import DataClassJsonMixin
from fhir.resources.R4B.bundle import Bundle

from helixcore.utilities.metrics.base_metrics import BaseMetric
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.resource_received_info import (
    ResourceReceivedInfo,
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
    DataFrameIntegerType,
)


@dataclass
class PatientAccessResourceMetric(DataClassJsonMixin, BaseMetric):
    row_context: PatientAccessRowContext
    resource_type: str
    resources_received: List[ResourceReceivedInfo]
    slug: Optional[str] = field(init=False)
    patient_id: Optional[str] = field(init=False)
    client_person_id: Optional[str] = field(init=False)
    master_person_id: Optional[str] = field(init=False)
    run_id: str = field(init=False)
    run_date_time: Optional[datetime] = field(init=False)
    pipeline_category: Optional[str] = field(init=False)
    new_tokens_only: Optional[bool] = field(init=False)
    connection_type: Optional[str] = field(init=False)
    pipeline_version: Optional[str] = field(init=False)
    fhir_version: Optional[str] = field(init=False)
    scope: Optional[str] = field(init=False)
    source_system_type: Optional[str] = field(init=False)
    status: Optional[str] = field(init=False)
    resource_count: int = field(init=False)
    resource_json: Optional[str] = field(init=False)
    resource_ids: Optional[str] = field(init=False)
    url: Optional[str] = field(init=False)

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    def __post_init__(self) -> None:
        assert self.row_context, "row_context should not be None"
        self.slug = self.row_context.connection_entry.service_slug
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
        self.scope = MySqlTextHelper.truncate(
            self.row_context.connection_entry.scope,
            maximum_length=MYSQL_MEDIUMTEXT_MAX_CHARACTERS,
        )
        self.source_system_type = self.row_context.connection_entry.source_system_type
        self.status = self.row_context.connection_entry.status
        self.resource_count = len(self.resources_received)
        bundle = (
            Bundle.construct(
                type="transaction",
                entry=[r.get_resource() for r in self.resources_received],
            )
            if self.row_context.run_context.enable_json_in_resource_metrics
            else None
        )
        self.resource_json = MySqlTextHelper.truncate(
            cast(str, bundle.json()) if bundle is not None else None,
            maximum_length=MYSQL_LONGTEXT_MAX_CHARACTERS,
        )
        resource_ids: List[str] = [
            r.resource_id for r in self.resources_received if r.resource_id is not None
        ]
        self.resource_ids = MySqlTextHelper.truncate(",".join(resource_ids))
        resource_urls: List[str] = [
            r.resource_url for r in self.resources_received if r.resource_url
        ]
        self.url = MySqlTextHelper.truncate(
            ",".join(list(set(resource_urls))),
            maximum_length=MYSQL_TEXT_MAX_CHARACTERS - 2,
        )  # remove duplicates

    @property
    def spark_schema(self) -> DataFrameStructType:
        return self.get_schema()

    def get_create_ddl(self, db_schema_name: str, db_table_name: str) -> str:
        return self.get_create_statement_ddl(
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
                DataFrameStructField("scope", DataFrameStringType(), nullable=True),
                DataFrameStructField("slug", DataFrameStringType(), nullable=True),
                DataFrameStructField("url", DataFrameStringType(), nullable=True),
                DataFrameStructField(
                    "resource_type", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "resource_count", DataFrameIntegerType(), nullable=True
                ),
                DataFrameStructField(
                    "resource_ids", DataFrameStringType(), nullable=True
                ),
                DataFrameStructField(
                    "resource_json", DataFrameStringType(), nullable=True
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
    connection_type VARCHAR(255) NULL COMMENT 'Type of connection: proa, hapi, hie',
    fhir_version VARCHAR(255) NULL COMMENT 'FHIR version: r4, dstu2',
    pipeline_category VARCHAR(255) NULL COMMENT 'Category of pipeline: Provider, Insurance',
    pipeline_version VARCHAR(255) NULL COMMENT 'Version of helix.pipelines release',
    new_tokens_only BOOLEAN NULL COMMENT 'Whether we only want to use new tokens',
    master_person_id VARCHAR(255) NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
    client_person_id VARCHAR(255) NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
    patient_id VARCHAR(255) NULL COMMENT 'Patient id in the source system',
    source_system_type VARCHAR(255) NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
    scope MEDIUMTEXT NULL COMMENT 'Scope of the token',
    slug VARCHAR(255) NULL COMMENT 'Slug in b.well that identifies the source system',
    url TEXT NULL COMMENT 'url of the source system',
    resource_type VARCHAR(255) NULL COMMENT 'Type of resource: Patient, Observation, etc.',
    resource_count INT NULL COMMENT 'Number of resources retrieved',
    resource_ids TEXT NULL COMMENT 'resource ids retrieved',
    resource_json LONGTEXT NULL COMMENT 'JSON of resources retrieved',
    PRIMARY KEY (ID)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci;
"""  # noqa: E501
        return ddl_statement
