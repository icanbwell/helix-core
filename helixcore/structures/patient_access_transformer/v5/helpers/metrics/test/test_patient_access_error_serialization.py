import json
import datetime

from helixtelemetry.telemetry.context.telemetry_context import TelemetryContext

from helixcore.utilities.async_pandas_udf.v1.async_pandas_udf_parameters import (
    AsyncPandasUdfParameters,
)

from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)

from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_run_context import (
    PatientAccessRunContext,
)
from helixcore.structures.token_service_receiver.v3.connection_entry import (
    ConnectionEntry,
)


def test_patient_access_error_serialization() -> None:
    """
    Tests serialization of PatientAccessError to dict and json

    :return:
    """
    scope: str = "patient/Practitioner.read"
    custom_api_parameters: str = ""
    current_date_time = datetime.datetime.fromisoformat("2023-03-16T04:46:39+00:00")
    run_context: PatientAccessRunContext = PatientAccessRunContext(
        connection_type="proa",
        run_id="abc123",
        run_date_time=current_date_time,
        pipeline_category=None,
        new_tokens_only=None,
        pipeline_version=None,
        intelligence_layer_run_context=None,
        metrics_writer_parameters=None,
        pandas_udf_parameters=AsyncPandasUdfParameters(maximum_concurrent_tasks=1),
        current_date_time=current_date_time,
        flow_name="zebra",
        page_size_for_person_clinical_data_pipeline=1000,
        telemetry_parent=None,
        log_level=None,
    )
    connection_entry: ConnectionEntry = ConnectionEntry(
        id="xyz789", scope=scope, custom_api_parameters=custom_api_parameters
    )
    row_context: PatientAccessRowContext = PatientAccessRowContext(
        run_context=run_context, connection_entry=connection_entry
    )
    patient_access_error: PatientAccessError = PatientAccessError.construct(
        row_context=row_context,
        request_id="123",
        resource_id="abc123",
        resource_type="Practitioner",
        url="https://fhir-server.com/Practitioner/abc123",
        error_text="Resource not found",
        status_code=404,
        step="fetch",
        resource_json=json.dumps({"resourceType": "Practitioner", "id": "abc123"}),
        severity="error",
        error_code="resource_not_found",
        raw_resource_json=json.dumps({"resourceType": "Practitioner", "id": "abc123"}),
        exception=None,
    )

    result_dict = patient_access_error.to_dict()
    expected_dict = {
        "client_person_id": None,
        "client_source_url": None,
        "connection_type": "proa",
        "created_date": None,
        "error_code": "resource_not_found",
        "error_text": "Resource not found",
        "expiry": None,
        "fhir_version": None,
        "last_updated": None,
        "master_person_id": None,
        "new_tokens_only": None,
        "patient_id": None,
        "pipeline_category": None,
        "pipeline_version": None,
        "raw_resource_json": '{"resourceType": "Practitioner", "id": "abc123"}',
        "request_id": "123",
        "resourceType": "Practitioner",
        "resource_id": "abc123",
        "resource_json": '{"resourceType": "Practitioner", "id": "abc123"}',
        "run_date_time": current_date_time,
        "run_id": "abc123",
        "scope": "patient/Practitioner.read",
        "severity": "error",
        "slug": None,
        "source_system_type": None,
        "status_code": 404,
        "step": "fetch",
        "token": None,
        "url": "https://fhir-server.com/Practitioner/abc123",
    }
    assert result_dict == expected_dict

    result_json = patient_access_error.to_json()
    result = json.loads(result_json)
    result["run_date_time"] = current_date_time

    assert result == expected_dict
