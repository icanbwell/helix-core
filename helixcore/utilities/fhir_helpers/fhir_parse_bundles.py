from typing import Any, Dict, List, Union
import json


def combine_bundles(contents: str) -> Dict[str, Any]:
    resources_or_bundles: List[Dict[str, Any]] = json.loads(contents)
    # create a bundle
    bundle: Dict[str, Union[str, List[Dict[str, Any]]]] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [],
    }
    # iterate over each bundle in resources_or_bundles.
    # resources_or_bundles can either be a normal resource or a bundle resource
    for resource_or_bundle in resources_or_bundles:
        if (
            not isinstance(resource_or_bundle, dict)
            or "resourceType" not in resource_or_bundle
        ):  # bad/corrupt entry
            continue
        if resource_or_bundle["resourceType"] != "Bundle":  # normal resource
            assert isinstance(bundle["entry"], list)
            bundle["entry"].append({"resource": resource_or_bundle})
        else:  # if it is a bundle then just add to bundle entries
            entry: Dict[str, Any]
            for entry in resource_or_bundle["entry"]:
                assert isinstance(bundle["entry"], list)
                if (
                    isinstance(entry, dict) and "resource" in entry
                ):  # it is a valid entry
                    bundle["entry"].append(entry)

    return bundle
