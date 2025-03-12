import typing
from typing import Any, TypeAlias

"""
This is the type alias for the FHIR resource type when it is has been cleaned and is valid R4
"""
FhirResourceType: TypeAlias = typing.OrderedDict[str, Any]

"""
This is the type alias for the FHIR resource type when it is has been received from the FHIR server but 
may not conform to R4 properly yet
"""
FhirReceivedResourceType: TypeAlias = typing.OrderedDict[str, Any]

"""
This is the type alias for the Human API resource type when it is received from the Human API server
"""
HumanApiResourceType: TypeAlias = typing.OrderedDict[str, Any]

# noinspection SpellCheckingInspection
"""
This is the type alias for the FHIR resource type when it is received as DSTU2
"""
# noinspection SpellCheckingInspection
FhirDstu2ResourceType: TypeAlias = typing.OrderedDict[str, Any]

# noinspection SpellCheckingInspection
"""
This is the type alias for the FHIR resource type when it is received as STU3
"""
# noinspection SpellCheckingInspection
FhirStu3ResourceType: TypeAlias = typing.OrderedDict[str, Any]
