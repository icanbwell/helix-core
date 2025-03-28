import typing
from typing import List, Optional, ItemsView


from helixcore.structures.patient_access_transformer.v5.helpers.structures.raw_resource_info import (
    RawResourceInfo,
)


class ResourcesByTypeMap:
    """
    This class holds list of resources by type


    """

    def __init__(self) -> None:
        """
        This class holds list of resources by type

        """
        self.map: typing.Dict[str, List[RawResourceInfo]] = {}

    def add(self, *, url: Optional[str], resource_type: str, resource: str) -> None:
        """
        Add a new resource to the map

        :param resource_type: the resource type
        :param resource: the resource
        :param url: the url
        :return: None
        """
        if resource_type not in self.map:
            self.map[resource_type] = []
        self.map[resource_type].append(
            RawResourceInfo(resource_type=resource_type, resource=resource, url=url)
        )

    def append(self, resource_type: str, resources: List[RawResourceInfo]) -> None:
        """
        Add a list of resources to the map

        :param resource_type: the resource type
        :param resources: the resources
        :return: None
        """
        if resource_type not in self.map:
            self.map[resource_type] = []
        self.map[resource_type].extend(resources)

    def get(self, resource_type: str) -> List[RawResourceInfo]:
        return self.map[resource_type]

    def extend(self, other: "ResourcesByTypeMap") -> None:
        """
        Copy the other map to this map

        :param other: the other map
        :return: None
        """
        for resource_type in other.map:
            self.append(resource_type, other.get(resource_type))

    def items(self) -> ItemsView[str, typing.List[RawResourceInfo]]:
        return self.map.items()

    def clear(self) -> None:
        self.map.clear()
