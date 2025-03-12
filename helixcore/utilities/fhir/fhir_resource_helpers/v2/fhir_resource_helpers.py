import json
import uuid
import re
from collections import OrderedDict
from typing import Dict, Any, Optional, List, cast
from urllib.parse import urlparse
from uuid import UUID

from fhir.resources.R4B.binary import Binary
from fhir.resources.R4B.domainresource import DomainResource
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.resource import Resource

from helixcore.utilities.fhir.fhir_resource_helpers.v2.types import (
    FhirReceivedResourceType,
)
from helixcore.utilities.json_serializer.json_serializer import EnhancedJSONEncoder


class FhirResourceHelpers:
    @staticmethod
    def configure_constraints_global_scope() -> None:
        """
        These settings are for fhir.resources package
        """
        regex = re.compile(
            r"^[A-Za-z0-9\-_.]+$"
        )  # allow _ since some resources in our fhir server have that
        # remove the 64-character limit on ids
        Id.configure_constraints(min_length=1, max_length=1024 * 1024, regex=regex)

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
        Generates a UUID5 using {id}|{slug} with the namespace of OID, if ``id`` is not a valid UUID.
        Valid UUID versions include 1, 2, 3, 4, 5

        """
        valid_uuid_versions = [1, 2, 3, 4, 5]
        for version in valid_uuid_versions:
            if FhirResourceHelpers.is_valid_uuid(id_, version=version):
                return id_
        return str(uuid.uuid5(uuid.NAMESPACE_OID, f"{id_}|{slug}"))

    @staticmethod
    def get_uuid_from_resource(*, resource: Dict[str, Any] | Resource) -> Optional[str]:
        """
        Reads the uuid field from identifier in the resource

        :param resource: the resource to read the uuid from
        :return: the uuid or None if not found
        """
        if isinstance(resource, Binary):
            return (
                resource.id
                if FhirResourceHelpers.is_valid_uuid(resource.id, 5)
                else None
            )
        elif isinstance(resource, Resource):
            assert isinstance(
                resource, DomainResource
            ), f"{resource} is not a DomainResource"
            resource1: DomainResource = resource
            assert hasattr(resource1, "identifier")
            # noinspection PyUnresolvedReferences
            identifiers1: List[Identifier] = cast(
                List[Identifier], resource1.identifier
            )
            if not identifiers1 or len(identifiers1) == 0:
                return None
            uuid_identifiers1: List[Identifier] = [
                i for i in identifiers1 if i.system == "https://www.icanbwell.com/uuid"
            ]
            if not uuid_identifiers1 or len(uuid_identifiers1) == 0:
                return None
            return uuid_identifiers1[0].value
        else:
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
    def get_owner_from_resource(
        *, resource: Dict[str, Any] | Resource
    ) -> Optional[str]:
        """
        reads owner tag from meta security

        """
        if isinstance(resource, Resource):
            assert isinstance(resource, DomainResource) or isinstance(
                resource, Binary
            ), f"{resource} is not Binary or a DomainResource"
            resource = resource.dict()

        assert isinstance(resource, dict)
        security_tags = resource.get("meta", {}).get("security", [])
        owner_tags = [
            i
            for i in security_tags
            if i.get("system") == "https://www.icanbwell.com/owner"
        ]

        return owner_tags[0].get("code") if owner_tags else None

    @staticmethod
    def get_uuid_or_id_from_resource(*, resource: Dict[str, Any]) -> Optional[str]:
        """
        Retrieves the uuid of the resource.  If none then reads the id of the resource


        """
        return FhirResourceHelpers.get_uuid_from_resource(
            resource=resource
        ) or resource.get("id")

    @staticmethod
    def add_uuid_if_missing(
        *, resource: FhirReceivedResourceType
    ) -> FhirReceivedResourceType:
        """
        Adds identifier for uuid if missing.  Calculates it using
        generate_uuid_for_id_and_slug()


        """
        if not FhirResourceHelpers.get_uuid_from_resource(resource=resource):
            identifiers: Optional[List[FhirReceivedResourceType]] = cast(
                Optional[List[FhirReceivedResourceType]], resource.get("identifier")
            )
            if not identifiers:
                resource["identifier"] = identifiers = []

            slug: Optional[str] = FhirResourceHelpers.get_owner_from_resource(
                resource=resource
            )
            assert slug, json.dumps(resource, cls=EnhancedJSONEncoder)
            resource_id: str = cast(str, resource.get("id"))
            assert resource_id, json.dumps(resource, cls=EnhancedJSONEncoder)
            identifiers.append(
                OrderedDict(
                    {
                        "id": "uuid",
                        "system": "https://www.icanbwell.com/uuid",
                        "value": FhirResourceHelpers.generate_uuid_for_id_and_slug(
                            id_=resource_id, slug=slug
                        ),
                    }
                )
            )
        return resource

    @staticmethod
    def fhir_add_uuid_if_missing(*, resource: Resource) -> Resource:
        """
        Adds identifier for uuid if missing.  Calculates it using
        generate_uuid_for_id_and_slug()


        """
        if not FhirResourceHelpers.get_uuid_from_resource(resource=resource):
            slug = FhirResourceHelpers.get_owner_from_resource(resource=resource)
            assert slug, "Owner is required to add missing UUID"

            resource_id = cast(str, resource.id)
            assert resource_id, "Id is required to add missing UUID"

            if isinstance(resource, Binary):
                # Binary does not have an identifiers section - put a UUID in the id
                # to ensure uniqueness
                resource.id = Id(
                    FhirResourceHelpers.generate_uuid_for_id_and_slug(
                        id_=str(resource.id), slug=slug
                    )
                )
            else:
                assert isinstance(
                    resource, DomainResource
                ), f"{resource} is not a DomainResource"
                assert hasattr(resource, "identifier")
                if not resource.identifier:
                    resource.identifier = []

                resource.identifier.append(
                    Identifier.construct(
                        id="uuid",
                        system="https://www.icanbwell.com/uuid",
                        value=FhirResourceHelpers.generate_uuid_for_id_and_slug(
                            id_=resource_id, slug=slug
                        ),
                    )
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

    @staticmethod
    def remove_none_values_from_ordered_dict(
        item: OrderedDict[str, Any],
    ) -> OrderedDict[str, Any]:
        """
        Recursively removes null, empty lists and empty strings to comply with FHIR specifications

        :param item: the item to clean
        :return: the cleaned item
        """
        cleaned_od: OrderedDict[str, Any] = OrderedDict()
        for key, value in item.items():
            if isinstance(value, OrderedDict):
                cleaned_value = (
                    FhirResourceHelpers.remove_none_values_from_ordered_dict(value)
                )
                if cleaned_value:
                    cleaned_od[key] = cleaned_value
            elif isinstance(value, list):
                cleaned_list: List[OrderedDict[str, Any]] = [
                    (
                        FhirResourceHelpers.remove_none_values_from_ordered_dict(item)
                        if isinstance(item, OrderedDict)
                        else item
                    )
                    for item in value
                    if item != []
                    and item is not None
                    and not (isinstance(item, str) and item == "")
                ]
                if cleaned_list:
                    cleaned_od[key] = cleaned_list
            elif (
                value is not None
                and value != []
                and not (isinstance(value, str) and value == "")
            ):
                cleaned_od[key] = value
        return cleaned_od

    @staticmethod
    def sanitize_text(value: str) -> str:
        """
        Replaces invalid characters with dashes to create a valid FHIR text

        :param value: the value to sanitize
        :return: the sanitized value
        """
        return re.sub(r"[^\w\r\n\t _.,!\"'/$-]", "-", value)

    @staticmethod
    def sanitize_id(value: str | Any | None) -> Optional[str]:
        """
        Replaces invalid characters with dashes to create a valid FHIR ID

        :param value: the value to sanitize
        :return: the sanitized value
        """
        if value is None:
            return None
        # noinspection RegExpRedundantEscape
        return re.sub(r"[^A-Za-z0-9\-\.]", "-", value)

    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Removes invalid characters in a string value, per the FHIR specification:
        https://hl7.org/fhir/R4B/datatypes.html#string

        :param value: string value to sanitize
        :return: string value with invalid characters removed
        """
        return re.sub(r"[^ \r\n\t\S]", "", value)

    @staticmethod
    def sanitize_reference(
        value: str, extract_relative_url: bool = True, remove_history: bool = True
    ) -> Optional[str]:
        """
        Ensures values of reference follow one of the following valid formats:
        1) A relative FHIR resource reference (e.g., `Encounter/123`)
        2) An absolute FHIR resource reference (e.g., `https://<some-fhir-server-location>/<version>/Encounter/123`)
        3) An internal reference, with the referenced entity residing in a contained resource (e.g., `#abc123`)

        Docs (including regex): https://hl7.org/fhir/R4B/references.html#Reference

        :param value: the `reference` value to sanitize
        :param remove_history: A flag to indicate that "_history" should be removed from the reference
        :param extract_relative_url: True to return only the relative URL portion of an absolute URL, False to return the entire absolute URL
        :return: the sanitized value, or `None` for invalid values
        """
        # Relative and absolute URL handling (regex matches on both)
        # Source for this beast of a regex: https://hl7.org/fhir/R4/references.html#literal
        absolute_url_regex = r"((http|https):\/\/([A-Za-z0-9\-\_\\\.\:\%\$]*\/)+)?"
        resource_types_regex = (
            "(Account|ActivityDefinition|AdverseEvent|AllergyIntolerance|Appointment|Appointm"
            "entResponse|AuditEvent|Basic|Binary|BiologicallyDerivedProduct|BodyStructure|Bu"
            "ndle|CapabilityStatement|CarePlan|CareTeam|CatalogEntry|ChargeItem|ChargeItemDe"
            "finition|Claim|ClaimResponse|ClinicalImpression|CodeSystem|Communication|Commun"
            "icationRequest|CompartmentDefinition|Composition|ConceptMap|Condition|Consent|C"
            "ontract|Coverage|CoverageEligibilityRequest|CoverageEligibilityResponse|Detecte"
            "dIssue|Device|DeviceDefinition|DeviceMetric|DeviceRequest|DeviceUseStatement|Di"
            "agnosticReport|DocumentManifest|DocumentReference|EffectEvidenceSynthesis|Encou"
            "nter|Endpoint|EnrollmentRequest|EnrollmentResponse|EpisodeOfCare|EventDefinitio"
            "n|Evidence|EvidenceVariable|ExampleScenario|ExplanationOfBenefit|FamilyMemberHi"
            "story|Flag|Goal|GraphDefinition|Group|GuidanceResponse|HealthcareService|Imagin"
            "gStudy|Immunization|ImmunizationEvaluation|ImmunizationRecommendation|Implement"
            "ationGuide|InsurancePlan|Invoice|Library|Linkage|List|Location|Measure|MeasureR"
            "eport|Media|Medication|MedicationAdministration|MedicationDispense|MedicationKn"
            "owledge|MedicationRequest|MedicationStatement|MedicinalProduct|MedicinalProduct"
            "Authorization|MedicinalProductContraindication|MedicinalProductIndication|Medic"
            "inalProductIngredient|MedicinalProductInteraction|MedicinalProductManufactured|"
            "MedicinalProductPackaged|MedicinalProductPharmaceutical|MedicinalProductUndesir"
            "ableEffect|MessageDefinition|MessageHeader|MolecularSequence|NamingSystem|Nutri"
            "tionOrder|Observation|ObservationDefinition|OperationDefinition|OperationOutcom"
            "e|Organization|OrganizationAffiliation|Patient|PaymentNotice|PaymentReconciliat"
            "ion|Person|PlanDefinition|Practitioner|PractitionerRole|Procedure|Provenance|Qu"
            "estionnaire|QuestionnaireResponse|RelatedPerson|RequestGroup|ResearchDefinition"
            "|ResearchElementDefinition|ResearchStudy|ResearchSubject|RiskAssessment|RiskEvi"
            "denceSynthesis|Schedule|SearchParameter|ServiceRequest|Slot|Specimen|SpecimenDe"
            "finition|StructureDefinition|StructureMap|Subscription|Substance|SubstanceNucle"
            "icAcid|SubstancePolymer|SubstanceProtein|SubstanceReferenceInformation|Substanc"
            "eSourceMaterial|SubstanceSpecification|SupplyDelivery|SupplyRequest|Task|Termin"
            "ologyCapabilities|TestReport|TestScript|ValueSet|VerificationResult|VisionPresc"
            "ription)"
        )
        resource_id_regex = r"\/[A-Za-z0-9\-\.|]+(\/_history\/[A-Za-z0-9\-\.]{1,64})?"
        consolidated_url_regex = (
            f"{absolute_url_regex}{resource_types_regex}{resource_id_regex}"
        )
        # Internal references
        if value.startswith("#"):
            return value
        # URL references
        elif re.match(consolidated_url_regex, value):
            # Replace invalid characters within relative URL with "-"
            resource_type_match = re.search(f"{resource_types_regex}/", value)
            if not isinstance(resource_type_match, re.Match):
                return None
            resource_id_components = value[resource_type_match.span()[1] :].split("/")
            cleaned_resource_id_components = "/".join(
                [
                    re.sub(r"[^A-Za-z0-9\-.|]", "-", l) if l != "_history" else l
                    for l in resource_id_components
                ]
            )
            # Remove the history part from the reference if it exists
            if remove_history:
                history_index = cleaned_resource_id_components.find("/_history/")
                if history_index != -1:
                    cleaned_resource_id_components = cleaned_resource_id_components[
                        :history_index
                    ]
                cleaned_value = (
                    value[: resource_type_match.span()[1]]
                    + cleaned_resource_id_components
                )
            # Extract relative URL from cleaned value, if appropriate
            if extract_relative_url:
                relative_match = re.search(
                    f"{resource_types_regex}{resource_id_regex}", cleaned_value
                )
                if isinstance(relative_match, re.Match):
                    cleaned_value = relative_match.group()
            return cleaned_value

        # Return `None` for values that are not valid relative, absolute, or internal references
        else:
            return None

    @staticmethod
    def does_url_have_valid_scheme(url: str) -> bool:
        """
        Checks whether the passed in url has a valid scheme per RFC 1738

        :param url: the url to check
        :return: True if the url has a valid scheme, False otherwise
        """
        try:
            result = urlparse(url)
            return result.scheme is not None and result.scheme != ""
        except ValueError:
            return False

    @staticmethod
    def does_url_have_valid_netloc(url: str) -> bool:
        """
        Checks whether the passed in url has a valid scheme per RFC 1738

        :param url: the url to check
        :return: True if the url has a valid netloc, False otherwise
        """
        try:
            result = urlparse(url)
            return result.netloc is not None and result.netloc != ""
        except ValueError:
            return False

    @staticmethod
    def is_phone_number(text: str) -> bool:
        """
        Checks whether the passed in text is a phone number in one of the North American phone formats

        :param text: the text to check
        :return: True if the text is a phone number, False otherwise
        """
        pattern = re.compile(r"^\+?1?[-.\s]?(\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}$")
        return bool(pattern.match(text))

    @staticmethod
    def fix_url_scheme(url: str) -> str:
        """
        Checks whether the passed in url has a valid scheme and if not, tries to detect what the scheme should be

        :param url: the url to fix
        :return: the fixed url
        """
        if not url:
            return url
        if FhirResourceHelpers.does_url_have_valid_scheme(url):
            return url
        # now try to detect what the scheme should be
        if FhirResourceHelpers.is_phone_number(url):
            return FhirResourceHelpers.phone_number_to_tel_url(phone_number=url)
        return url

    @staticmethod
    def phone_number_to_tel_url(phone_number: str) -> str:
        """
        Converts a phone number to a tel url.
        If it cannot parse it then it returns the phone number as is.


        :param phone_number: the phone number to convert
        :return: the tel url
        """
        if not phone_number:
            return phone_number
        # Remove non-numeric characters
        numeric_phone_number = re.sub(r"\D", "", phone_number)

        # Check if the phone number is of valid length (10 or 11 digits)
        if len(numeric_phone_number) == 10:
            # Assume it's a North American number without the country code
            return f"tel:+1{numeric_phone_number}"
        elif len(numeric_phone_number) == 11 and numeric_phone_number[0] == "1":
            # It's a North American number with the country code
            return f"tel:+{numeric_phone_number}"
        else:
            return phone_number
