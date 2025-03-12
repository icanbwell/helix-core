import csv
import os


# Define constants
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

DYNAMODB_DDL_TABLE_NAME = os.environ.get(
    "DYNAMODB_DDL_TABLE_NAME", "ingestion-table-ddl"
)
DYNAMODB_COLUMN_MAP_TABLE_NAME = os.environ.get(
    "DYNAMODB_COLUMN_MAP_TABLE_NAME", "ingestion-table-conversions"
)
DYNAMODB_LOGGING_TABLE_NAME = os.environ.get(
    "DYNAMODB_LOGGING_TABLE_NAME", "ingestion-verification"
)
DYNAMODB_FILE_METADATA_TABLE_NAME = os.environ.get(
    "DYNAMODB_FILE_METADATA_TABLE_NAME", "ingestion-client-file-metadata"
)
DYNAMODB_CONFIG_TABLE_NAME = os.environ.get(
    "DYNAMODB_CONFIG_TABLE_NAME", "ingestion-config"
)

SNS_ARN_DATABELT_DEVS = "arn:aws:sns:us-east-1:400686897767:Bwell_databelt_dev"
SNS_ARN_INGESTION_VERIFICATION = (
    "arn:aws:sns:us-east-1:400686897767:Bwell_Data_ingestion_file_verification"
)


# Global, single installation of the bwell dialect
class DatabeltCSVDialect(csv.Dialect):
    quoting = csv.QUOTE_ALL
    delimiter = "|"

    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"


csv.register_dialect("databelt", DatabeltCSVDialect)
