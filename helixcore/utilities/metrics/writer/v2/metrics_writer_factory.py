from logging import Logger
from typing import Optional

from helixcore.utilities.telemetry.telemetry_span_creator import (
    TelemetrySpanCreator,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_async import (
    BaseMetricsWriterAsync,
)
from helixcore.utilities.metrics.writer.base_metrics_writer_parameters import (
    BaseMetricsWriterParameters,
)
from helixcore.utilities.metrics.writer.v2.metrics_writer import (
    MetricsWriter,
)
from helixcore.utilities.metrics.writer.v2.metrics_writer_parallel import (
    MetricsWriterParallel,
)


class MetricsWriterFactory:
    def __init__(
        self,
        *,
        parameters: BaseMetricsWriterParameters,
        logger: Optional[Logger],
    ) -> None:
        """
        This class creates a metrics writer


        :param parameters: parameters for the metrics writer
        :param logger: logger to use
        """

        assert parameters is not None, "parameters should not be None"
        assert isinstance(
            parameters, BaseMetricsWriterParameters
        ), "parameters should be an instance of BaseMetricsWriterParameters"

        self.logger: Optional[Logger] = logger

        self.parameters: BaseMetricsWriterParameters = parameters

    def create_metrics_writer(
        self, *, telemetry_span_creator: TelemetrySpanCreator
    ) -> BaseMetricsWriterAsync:
        """
        Creates a metrics writer

        :return: metrics writer
        """
        return (
            MetricsWriter(
                logger=self.logger,
                parameters=self.parameters,
                telemetry_span_creator=telemetry_span_creator,
            )
            if not self.parameters.buffer_length
            else MetricsWriterParallel(
                logger=self.logger,
                parameters=self.parameters,
                telemetry_span_creator=telemetry_span_creator,
            )
        )
