class TelemetryMetricNames:
    """
    This class contains the metric names for telemetry
    Keep this list sorted alphabetically to make it easier to find the metric you are looking for.


    """

    PROA_INTELLIGENCE_LAYER_DELETE_COUNT: str = (
        "bwell.pipelines.proa.intelligence_layer.delete.count"
    )
    PROA_INTELLIGENCE_LAYER_ERROR_COUNT: str = (
        "bwell.pipelines.proa.intelligence_layer.error.count"
    )
    PROA_INTELLIGENCE_LAYER_MERGE_COUNT: str = (
        "bwell.pipelines.proa.intelligence_layer.merge.count"
    )
    PROA_INTELLIGENCE_LAYER_UPDATED_COUNT: str = (
        "bwell.pipelines.proa.intelligence_layer.updated.count"
    )
    PROA_MATCH_ERROR_COUNT: str = "bwell.pipelines.proa.match.error.count"
    PROA_METRIC_WRITTEN_COUNT: str = "bwell.pipelines.proa.metrics.written.count"
    PROA_PROCESSED_PATIENT_COUNT: str = "bwell.pipelines.proa.processed.patients.count"
    PROA_PROCESSED_TOKEN_FROM_UPDATED_OR_CREATED_DATE: str = (
        "bwell.pipelines.proa.processed.tokens.from_updated_or_created.time"
    )
    PROA_RESOURCE_RETRIEVAL_COUNT: str = "bwell.pipelines.proa.retrieval.resource.count"
    PROA_RESOURCE_RETRIEVAL_ERROR_COUNT: str = (
        "bwell.pipelines.proa.retrieval.error.count"
    )
    PROA_RESOURCE_SAVE_COUNT: str = "bwell.pipelines.proa.save.resources.count"
    PROA_STREAMING_TOKEN_PROCESSED_COUNT: str = (
        "bwell.pipelines.proa.streaming.tokens.processed.count"
    )
    PROA_STREAMING_TOKEN_PROCESSED_HISTOGRAM: str = (
        "bwell.pipelines.proa.streaming.tokens.processed.histogram"
    )
    PROA_STREAMING_TOKEN_RETRIEVED_COUNT: str = (
        "bwell.pipelines.proa.streaming.tokens.retrieved.count"
    )
    PROA_STREAMING_TOKEN_RETRIEVED_HISTOGRAM: str = (
        "bwell.pipelines.proa.streaming.tokens.retrieved.histogram"
    )
    PROA_STREAMING_TOKEN_RETRIEVING_TIME: str = (
        "bwell.pipelines.proa.streaming.tokens.retrieving.time"
    )
    PROA_STREAMING_TOKEN_SLEEP_TIME: str = (
        "bwell.pipelines.proa.streaming.tokens.sleep.time"
    )
    PROA_STREAMING_TOKEN_UPDATING_STATUS_TIME: str = (
        "bwell.pipelines.proa.streaming.tokens.updating_status.time"
    )
    PROA_TOKEN_ERROR_COUNT: str = "bwell.pipelines.proa.tokens.error.count"
    PROA_TOKEN_REFRESHED_COUNT: str = "bwell.pipelines.proa.token.refreshed.count"
    PROA_TOKEN_REFRESHED_ERROR_COUNT: str = (
        "bwell.pipelines.proa.token.refreshed.error.count"
    )
    PROA_TOKEN_REFRESHED_ABORT_COUNT: str = (
        "bwell.pipelines.proa.token.refreshed.abort.count"
    )
    PROA_TOKEN_SINGLE_TOKEN_RETRIEVAL_COUNT: str = (
        "bwell.pipelines.proa.tokens.single_token_retrieval.count"
    )
    PROA_TOKEN_SINGLE_TOKEN_RETRIEVAL_ERROR_COUNT: str = (
        "bwell.pipelines.proa.tokens.single_token_retrieval.error.count"
    )
    PROA_TOKEN_UPDATED_COUNT: str = "bwell.pipelines.proa.tokens.updated.count"
    PROA_TOKEN_UPDATED_ERROR_COUNT: str = (
        "bwell.pipelines.proa.tokens.updated.error.count"
    )
    PROA_RESOURCE_RETRIEVAL_TRACE_COUNT: str = (
        "bwell.pipelines.proa.retrieval.resource.trace.count"
    )

    PROA_PROCESSED_PATIENT_MEMORY: str = (
        "bwell.pipelines.proa.processed.patients.memory.count"
    )
