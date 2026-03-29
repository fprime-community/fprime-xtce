""" Utilities used within the fprime_xtce package

These utilities are helper functions that are used within the fprime_xtce.

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""
import itertools
from typing import List, Dict, Union, Tuple, Any, Optional
DELIMITER = "|"

def convert_identifier(identifier: str) -> str:
    """Convert F Prime qualified FPP names to XTCE-compatible names.

    This function replaces dots with the defined delimiter and ensures the name starts with a letter.
    Note: This function is deprecated for hierarchical structure but kept for compatibility.

    Args:
        name: Original F Prime qualified name (e.g., "fprime.types.U32")

    Returns:
        str: Converted name suitable for XTCE (e.g., "fprime|types|U32")
    """
    # F Prime type names
    assert identifier[0].isalpha(), "Type names must start with a letter w.r.t FPP names"

    # Convert dots to the defined delimiter for XTCE compatibility
    converted = identifier.replace('.', DELIMITER)
    return converted


def convert_to_xtce_reference(identifier: str) -> str:
    """Convert F Prime qualified name to XTCE reference path.

    In XTCE hierarchical structures, references use '/' as the path separator
    to navigate through nested SpaceSystems.

    Args:
        identifier: Original F Prime qualified name (e.g., "FprimeSensors.GeometricVector3")

    Returns:
        str: XTCE reference path (e.g., "FprimeSensors/GeometricVector3")

    Examples:
        "Component.Subsystem.Temperature" -> "Component/Subsystem/Temperature"
        "SimpleType" -> "SimpleType"
    """
    assert identifier and identifier[0].isalpha(), "Identifiers must start with a letter"
    # Convert dots to forward slashes for XTCE path references
    return identifier.replace('.', '/')


def extract_namespace_components(identifier: str, delimiter: Optional[str] = None) -> Tuple[List[str], str]:
    """Extract namespace components and base name from a qualified identifier.

    Splits an F Prime qualified name into namespace components and the final name.
    Supports both dot-delimited (raw FPrime) and pipe-delimited (XTCE converted) names.

    Args:
        identifier: Qualified name (e.g., "fprime.types.U32" or "fprime|types|U32")
        delimiter: Delimiter to use for splitting. If None, auto-detects using DELIMITER constant.

    Returns:
        Tuple of (namespace_components, base_name) where:
        - namespace_components: List of namespace parts (e.g., ["fprime", "types"])
        - base_name: Final name component (e.g., "U32")

    Examples:
        "fprime.types.U32" -> (["fprime", "types"], "U32")
        "fprime|types|U32" -> (["fprime", "types"], "U32")
        "MyComponent.Temperature" -> (["MyComponent"], "Temperature")
        "SimpleType" -> ([], "SimpleType")
    """
    assert identifier and identifier[0].isalpha(), "Identifiers must start with a letter"

    # Auto-detect delimiter if not specified
    # Prefer dots over pipes for splitting (dots are the original F Prime format)
    if delimiter is None:
        delimiter = '.' if '.' in identifier else DELIMITER

    parts = identifier.split(delimiter)
    if len(parts) == 1:
        return [], parts[0]
    return parts[:-1], parts[-1]

def xtce_names(list_of_dicts, key="name"):
    """Helper function to extract a list of names from a list of dictionaries with a common key.
    
    Args:
        list_of_dicts: List of dictionaries containing the key
        key: The key to extract from each dictionary (default: "name")
        
    Returns:
        set: Set of names extracted from the list of dictionaries
    """
    return set([item[key] for item in xtce_data(list_of_dicts) if key in item])

def xtce_data(xtce_dict_or_list: Union[List, Dict]):
    """ Helper function to extract the data blob from an XTCE dictionary object
    
    XTCE data structue is a dictionary with a single key (e.g., "ParameterType") whose value is the actual data. This
    function extracts that data for easier processing.

    Args:
        xtce_dict_or_list: An XTCE dictionary or list of dictionaries to extract data from
    Returns:
        The extracted data blob from the XTCE structure or a list of extracted data blobs
    """
    if hasattr(xtce_dict_or_list, "keys"):
        assert len(list(xtce_dict_or_list.keys())) == 1, f"Expected a single key in the XTCE dictionary: {xtce_dict_or_list}"
        return list(xtce_dict_or_list.values())[0]
    return [xtce_data(item) for item in xtce_dict_or_list]


def safe_combine(list1: List, list2: List, match_key: str ="name", typed: bool = True) -> List:
    """Safely combine two lists removing duplicates based on a matching key.

    This function combines two lists of dictionaries and removing duplicates. If a duplicate does exist it is removed
    after being checked for consistency. If inconsistent, an error is raised.
    
    Args:
        list1: First list to combine
        list2: Second list to combine
        typed: whether there is a top-level type key or not
        
    Returns:
        List: Combined list with unique elements
    """
    def data_refiner(data):
        """ Pull data blob out of the list items, which may be wrapped in a type key """
        return xtce_data(data) if typed else data

    combined = list1.copy()
    # Create a mapping from the first list based on the match key for quick lookup
    try:
        list1_data = {item[match_key]: item for item in data_refiner(list1)}
    except KeyError as e:
        raise AssertionError(f"Malformed data: {str(e)} not found in: {data_refiner(list1)}") from e
    try:
        for item in list2:
            data_blob = data_refiner(item)
            matching_key = data_blob[match_key]
            match_value = list1_data.get(matching_key, None)

            # If no match was found, then add the item
            if match_value is None:
                list1_data[matching_key] = data_blob
                combined.append(item)
            # If a match was found, check for consistency and raise an error if inconsistent
            elif match_value != data_blob:
                raise ValueError(f"Conflict for {data_blob[match_key]}: Expected {match_value} got {data_blob}")
    # KeyError indicates this function was called on inappropriate data so transform into an assertion error
    except KeyError as e:
        raise AssertionError(f"Malformed data: {e} not found in {data_blob}") from e
    return combined


def formal_parameters(fprime_section):
    """ Helper function to extract the formal parameters from F Prime
    
    This function extracts the formal parameters from the F Prime dictionary sections "commands" and "events".

    Args:
        fprime_section: The section of the F Prime dictionary to extract from (e.g., "commands" or "events")
    Returns:
        A list of formal parameters used in the specified section of the F Prime dictionary
    """
    formal_parameters = [item["formalParams"] for item in fprime_section]
    return itertools.chain.from_iterable(formal_parameters)


def formal_parameter_types(fprime_section):
    """ Helper function to extract the formal parameter types from F Prime

    This function extracts the formal parameter types from the F Prime dictionary sections "commands" and "events".

    Args:
        fprime_section: The section of the F Prime dictionary to extract from (e.g., "commands" or "events")
    Returns:
        A set of formal parameter types used in the specified section of the F Prime dictionary
    """
    return [parameter["type"] for parameter in formal_parameters(fprime_section)]


def get_or_create_nested_space_system(root: Dict[str, Any], namespace_path: List[str]) -> Dict[str, Any]:
    """Navigate or create nested SpaceSystem hierarchy.

    Given a root SpaceSystem dictionary and a namespace path, navigate to or create
    the nested SpaceSystem at that path.

    Args:
        root: Root SpaceSystem dictionary
        namespace_path: List of namespace components (e.g., ["fprime", "types"])

    Returns:
        The SpaceSystem dictionary at the specified path
    """
    current: Dict[str, Any] = root
    for component in namespace_path:
        # Ensure SpaceSystem list exists
        if "SpaceSystem" not in current:
            current["SpaceSystem"] = []

        # Find or create the SpaceSystem for this component
        space_systems: List = current["SpaceSystem"]
        found: Optional[Dict[str, Any]] = None
        for ss in space_systems:
            ss_data = xtce_data(ss) if isinstance(ss, dict) and len(ss) == 1 else ss
            if isinstance(ss_data, dict) and ss_data.get("name") == component:
                found = ss_data
                break

        if found is None:
            # Create new SpaceSystem
            new_ss: Dict[str, Any] = {"name": component}
            space_systems.append(new_ss)
            found = new_ss

        current = found

    return current
