import uuid
from typing import Dict, Any, Optional, List, cast
from uuid import UUID


class FhirResourceHelpers:
    @staticmethod
    def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
        """
        Check if uuid_to_test is a valid UUID.

         Parameters
        ----------
        uuid_to_test : str
        version : {1, 2, 3, 4}

         Returns
        -------
        `True` if uuid_to_test is a valid UUID, otherwise `False`.

         Examples
        --------
        >>> FhirResourceHelpers.is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
        True
        >>> FhirResourceHelpers.is_valid_uuid('c9bf9e58')
        False
        """

        try:
            uuid_obj = UUID(uuid_to_test, version=version)
        except ValueError:
            return False
        return str(uuid_obj) == uuid_to_test

    @staticmethod
    def generate_uuid_for_id_and_slug(*, id_: str, slug: str) -> str:
        """
        Generates a UUID5 using {id}|{slug} with the namespace of OID

        """
        if FhirResourceHelpers.is_valid_uuid(
            id_, version=4
        ) or FhirResourceHelpers.is_valid_uuid(id_, version=5):
            return id_
        return str(uuid.uuid5(uuid.NAMESPACE_OID, f"{id_}|{slug}"))

    @staticmethod
    def get_uuid_from_resource(*, resource: Dict[str, Any]) -> Optional[str]:
        """
        Reads the uuid field from identifier in the resource

        """
        identifiers: Optional[List[Dict[str, Any]]] = cast(
            Optional[List[Dict[str, Any]]], resource.get("identifier")
        )
        if not identifiers or len(identifiers) == 0:
            return None
        uuid_identifiers = [
            i
            for i in identifiers
            if i.get("system") == "https://www.icanbwell.com/uuid"
        ]
        if not uuid_identifiers or len(uuid_identifiers) == 0:
            return None
        return uuid_identifiers[0].get("value")

    @staticmethod
    def get_owner_from_resource(*, resource: Dict[str, Any]) -> Optional[str]:
        """
        reads owner tag from meta security

        """
        meta = resource.get("meta")
        if not meta:
            return None
        security_tags: Optional[List[Dict[str, Any]]] = cast(
            Optional[List[Dict[str, Any]]], meta.get("security")
        )
        if not security_tags or len(security_tags) == 0:
            return None
        owner_tags = [
            i
            for i in security_tags
            if i.get("system") == "https://www.icanbwell.com/owner"
        ]
        if not owner_tags or len(owner_tags) == 0:
            return None
        return owner_tags[0].get("code")

    @staticmethod
    def get_uuid_or_id_from_resource(*, resource: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the uuid of the resource.  If none then reads the id of the resource


        """
        return FhirResourceHelpers.get_uuid_from_resource(
            resource=resource
        ) or resource.get("id")

    @staticmethod
    def add_uuid_if_missing(*, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds identifier for uuid if missing.  Calculates it using
        generate_uuid_for_id_and_slug()


        """
        if not FhirResourceHelpers.get_uuid_from_resource(resource=resource):
            identifiers: Optional[List[Dict[str, Any]]] = cast(
                Optional[List[Dict[str, Any]]], resource.get("identifier")
            )
            if not identifiers:
                resource["identifier"] = identifiers = []

            slug: Optional[str] = FhirResourceHelpers.get_owner_from_resource(
                resource=resource
            )
            assert slug
            resource_id: str = cast(str, resource.get("id"))
            assert resource_id
            identifiers.append(
                {
                    "id": "uuid",
                    "system": "https://www.icanbwell.com/uuid",
                    "value": FhirResourceHelpers.generate_uuid_for_id_and_slug(
                        id_=resource_id, slug=slug
                    ),
                }
            )
        return resource

    @staticmethod
    def remove_none_values_from_dict_or_list(
        item: Dict[str, Any],
    ) -> Dict[str, Any] | List[Dict[str, Any]]:
        if isinstance(item, list):
            return [FhirResourceHelpers.remove_none_values_from_dict(i) for i in item]
        if not isinstance(item, dict):
            return item
        return {
            k: FhirResourceHelpers.remove_none_values_from_dict(v)
            for k, v in item.items()
            if v is not None
        }

    @staticmethod
    def remove_none_values_from_dict(item: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(item, dict):
            return item
        return {
            k: FhirResourceHelpers.remove_none_values_from_dict_or_list(v)
            for k, v in item.items()
            if v is not None
        }
