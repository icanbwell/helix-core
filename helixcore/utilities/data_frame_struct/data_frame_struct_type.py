import dataclasses
from typing import List


class DataFrameType:
    pass


class DataFrameStringType(DataFrameType):
    pass


class DataFrameIntegerType(DataFrameType):
    pass


class DataFrameTimestampType(DataFrameType):
    pass


class DataFrameBooleanType(DataFrameType):
    pass


class DataFrameFloatType(DataFrameType):
    pass


@dataclasses.dataclass
class DataFrameStructField:
    name: str
    data_type: DataFrameType
    nullable: bool = True


@dataclasses.dataclass
class DataFrameStructType:
    def __init__(self, fields: List[DataFrameStructField] = []):
        self.list: List[DataFrameStructField] = fields

    @property
    def fields(self) -> List[DataFrameStructField]:
        return self.list


class DataFrameArrayType(DataFrameType):
    def __init__(self, struct_type: DataFrameStructType) -> None:
        self.struct_type = struct_type
