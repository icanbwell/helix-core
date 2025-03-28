from datetime import datetime
from pytest import mark
from typing import Tuple

from helixcore.utilities.telemetry.telemetry_context import (
    TelemetryContext,
)

from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_issue_severity import (
    PatientAccessIssueSeverity,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_row_context import (
    PatientAccessRowContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.structures.patient_access_run_context import (
    PatientAccessRunContext,
)
from helixcore.structures.patient_access_transformer.v5.helpers.metrics.patient_access_error import (
    PatientAccessError,
)
from helixcore.structures.token_service_receiver.v3.connection_entry import (
    ConnectionEntry,
)
from helixcore.utilities.async_pandas_udf.v1.async_pandas_udf_parameters import (
    AsyncPandasUdfParameters,
)


def get_check_clientside_error_severity_inputs(
    resource_id: str,
    scope: str,
    custom_api_parameters: str,
) -> Tuple[PatientAccessRowContext, str]:
    """
    Get inputs for ``PatientAccessError.check_clientside_error_severity()`` with required fields defaulted

    :param resource_id: resource ID on client server
    :param scope: scope to include in ``ConnectionEntry``
    :param custom_api_parameters: custom api parameters to include in ``ConnectionEntry``
    :return: ``BundleEntry`` populated with params
    """
    test_url = f"https://fhir-server.com/{resource_id}"
    current_date_time = datetime.now()
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
        telemetry_context=TelemetryContext.get_null_context(),
        telemetry_parent=None,
        log_level=None,
    )
    connection_entry: ConnectionEntry = ConnectionEntry(
        id="xyz789", scope=scope, custom_api_parameters=custom_api_parameters
    )
    row_context: PatientAccessRowContext = PatientAccessRowContext(
        run_context=run_context, connection_entry=connection_entry
    )

    return row_context, test_url


@mark.patient_access
@mark.parametrize(
    argnames=[
        "resource_id",
        "scope",
        "custom_api_parameters",
        "status_code",
        "input_severity",
        "expected_severity",
    ],
    argvalues=[
        (
            "Practitioner/abc123",
            "patient/Practitioner.read",
            "",
            404,
            PatientAccessIssueSeverity.ERROR,
            PatientAccessIssueSeverity.WARNING,
        ),
        (
            "invalid/resource/id",
            "patient/Practitioner.read",
            "",
            404,
            PatientAccessIssueSeverity.ERROR,
            PatientAccessIssueSeverity.ERROR,
        ),
        (
            "Observation/xyz789",
            "patient/Observation.read",
            "",
            500,
            PatientAccessIssueSeverity.ERROR,
            PatientAccessIssueSeverity.ERROR,
        ),
        (
            "Encounter/def456",
            "patient/Encounter.read patient/Practitioner.read",
            "epic",
            403,
            PatientAccessIssueSeverity.ERROR,
            PatientAccessIssueSeverity.WARNING,
        ),
        (
            "Encounter/def456",
            "patient/Practitioner.read",
            "",
            403,
            PatientAccessIssueSeverity.ERROR,
            PatientAccessIssueSeverity.ERROR,
        ),
    ],
    ids=[
        "404: Valid resource ID",
        "404: Invalid resource ID",
        "500: Server error",
        "403: Epic MyChart message",
        "403: Valid Unauthorized error",
    ],
)
def test_set_clientside_error_to_warning(
    resource_id: str,
    scope: str,
    custom_api_parameters: str,
    status_code: int,
    input_severity: str,
    expected_severity: str,
) -> None:
    row_context, url = get_check_clientside_error_severity_inputs(
        resource_id=resource_id,
        scope=scope,
        custom_api_parameters=custom_api_parameters,
    )
    assert (
        PatientAccessError.check_clientside_error_severity(
            row_context=row_context,
            scope=scope,
            status_code=status_code,
            resource_type=resource_id.split("/")[0],
            url=url,
            severity=input_severity,
        )
        == expected_severity
    )
