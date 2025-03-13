import dataclasses
from typing import List


# -------------
# We define generic DataFrame types here that can be converted to Spark or other dataframe types by clients of this package
# ---------------


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
class DataFrameStructType(DataFrameType):
    fields: List[DataFrameStructField] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class DataFrameArrayType(DataFrameType):
    def __init__(self, item_type: DataFrameType) -> None:
        self.item_type = item_type
