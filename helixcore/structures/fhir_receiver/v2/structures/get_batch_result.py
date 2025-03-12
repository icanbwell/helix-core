import dataclasses
from typing import List, AsyncGenerator, Optional

from dataclasses_json import DataClassJsonMixin

from helixcore.structures.fhir_receiver.v2.structures.get_batch_error import (
    GetBatchError,
)


@dataclasses.dataclass
class GetBatchResult(DataClassJsonMixin):
    resources: List[str]
    errors: List[GetBatchError]

    def append(self, result: "GetBatchResult") -> "GetBatchResult":
        self.resources = self.resources + result.resources
        self.errors = self.errors + result.errors
        return self

    @classmethod
    def from_list(cls, data: List["GetBatchResult"]) -> "GetBatchResult":
        return cls(
            resources=[f for r in data for f in r.resources],
            errors=[f for r in data for f in r.errors],
        )

    @staticmethod
    async def from_async_generator(
        generator: AsyncGenerator["GetBatchResult", None],
    ) -> Optional["GetBatchResult"]:
        """
        Reads a generator of FhirGetResponse and returns a single FhirGetResponse by appending all the FhirGetResponse

        :param generator: generator of FhirGetResponse items
        :return: FhirGetResponse
        """
        result: GetBatchResult | None = None
        async for value in generator:
            if not result:
                result = value
            else:
                result.append(value)

        assert result
        return result
