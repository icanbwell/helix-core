from abc import abstractmethod, ABC
from typing import Dict, Any, List

from helixcore.utilities.data_frame_struct.data_frame_struct_type import (
    DataFrameStructType,
)


class BaseMetric(ABC):

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError("schema not implemented by subclass")

    @property
    @abstractmethod
    def spark_schema(self) -> DataFrameStructType:
        """
        Returns the schema for the metrics
        """
        raise NotImplementedError("schema not implemented by subclass")

    @abstractmethod
    def get_create_ddl(self, db_schema_name: str, db_table_name: str) -> str:
        raise NotImplementedError("get_create_ddl not implemented by subclass")

    @property
    def columns(self) -> List[str]:
        schema: DataFrameStructType = self.spark_schema
        columns: List[str] = [f.name for f in schema.fields]
        return columns

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        raise NotImplementedError("get_name not implemented by subclass")
