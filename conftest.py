import os
from typing import Generator, Any

import boto3
import pytest
from _pytest.fixtures import FixtureFunctionMarker
from botocore.client import BaseClient
from moto import mock_aws

from helixcore.register import register


@pytest.fixture(scope="function")
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_REGION"] = "us-east-1"


@pytest.fixture(scope="function")
def ssm_mock(
    aws_credentials: FixtureFunctionMarker,
) -> Generator[BaseClient, None, None]:
    with mock_aws():
        yield boto3.client("ssm", region_name="us-east-1")


@pytest.fixture(scope="function")
def s3_mock(
    aws_credentials: FixtureFunctionMarker,
) -> Generator[BaseClient, None, None]:
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture(scope="session", autouse=True)
def run_before_each_test() -> Generator[None, Any, None]:
    # This code will run before every test
    # print("Setting up something before each test")
    # You can do setup operations here
    # For example, initializing databases, clearing caches, etc.
    register()

    # Optional: You can yield if you want to do tear down after the test
    yield

    # Optional teardown code here
    print("Cleaning up after each test")
