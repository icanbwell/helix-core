from typing import Dict, Optional

from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BaseMetricsWriterParameters(DataClassJsonMixin):
    """
    This class provides parameters for the metrics writer

    """

    schema_name: str
    """ name of the schema to write to """

    metric_table_map: Dict[str, Optional[str]]
    """ mapping of metric to table name """

    buffer_length: Optional[int]
    """ length of buffer to keep in memory before writing to metrics database """

    max_batch_size: Optional[int]
    """ maximum number of rows to write in a single batch to metrics database """
