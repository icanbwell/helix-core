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
