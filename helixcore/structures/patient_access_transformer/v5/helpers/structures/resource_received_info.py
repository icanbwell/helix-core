import dataclasses
import json
from typing import Any, Dict, Optional, cast

from dataclasses import field
from dataclasses_json import DataClassJsonMixin, config
from fhir.resources.R4B import construct_fhir_element
from fhir.resources.R4B.resource import Resource
from helixcore.utilities.json_helpers import convert_dict_to_fhir_json


def encode_resource(resource: Resource) -> str:
    return cast(str, resource.json())


def decode_resource(resource_json: str) -> Resource:
    resource_type: str = json.loads(resource_json)["resourceType"]
    return cast(
        Resource,
        construct_fhir_element(element_type=resource_type, data=resource_json),
    )


@dataclasses.dataclass
class ResourceReceivedInfo(DataClassJsonMixin):
    resource_id: str
    resourceType: str
    resource: Resource = field(
        metadata=config(
            encoder=encode_resource,
            decoder=decode_resource,
        )
    )
    resource_url: str
    service_slug: Optional[str]
    client_source_url: Optional[str]
    master_person_id: Optional[str]

    def get_resource(self) -> Resource:
        """
        Returns resource as a dict.  Converts from OrderedDict if necessary


        """
        return self.resource

    def get_resource_as_json(self) -> str:
        """
        Returns resource as a json string.  Converts from OrderedDict if necessary

        """
        resource: str = cast(str, self.get_resource().json())
        return resource

    def get_resource_plus_extra_data_as_json(self) -> str:
        """
        Returns resource as a json string.  Converts from OrderedDict if necessary

        """
        dict_: Dict[str, Any] = json.loads(self.get_resource().json())
        # add additional fields to help with processing
        dict_["service_slug"] = self.service_slug
        dict_["client_source_url"] = self.client_source_url
        dict_["master_person_id"] = self.master_person_id
        resource: str = convert_dict_to_fhir_json(dict_)
        return resource
