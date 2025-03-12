from logging import Logger
from typing import Dict, Optional

from helixcore.utilities.metrics.writer.v1.metrics_writer import (
    MetricsWriter,
)


class MetricsWriterFactory:
    def __init__(
        self,
        *,
        schema_name: str,
        logger: Optional[Logger],
        metric_table_map: Dict[str, Optional[str]],
    ) -> None:
        """
        This class writes metrics to the database

        :param schema_name: name of the schema to write to
        :param logger: logger to use
        :param metric_table_map: mapping of metric to table name
        """
        assert schema_name, "schema_name should not be None"
        assert isinstance(schema_name, str), "schema_name should be a string"

        self.schema_name: str = schema_name
        self.logger: Optional[Logger] = logger
        self.metric_table_map: Dict[str, Optional[str]] = metric_table_map

    def create_metrics_writer(self) -> MetricsWriter:
        return MetricsWriter(
            schema_name=self.schema_name,
            logger=self.logger,
            metric_table_map=self.metric_table_map,
        )
