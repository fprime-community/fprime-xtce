"""Helpers to emit an XTCE-style structure and serialize it to XML.

`build_xtce_structure` produces an in-memory dictionary shaped like XTCE.
`build_xtce_structure` produces a hierarchical XTCE structure from namespaced items.
`write_xtce_xml` serializes that structure to XML (minimal, not schema-validating).

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union
from collections import defaultdict

import xml.etree.ElementTree as ET

import xmlschema

from .utilities import (
    extract_namespace_components,
    get_or_create_nested_space_system,
    xtce_data,
)


def convert_parameter_type(command_type):
    """ParameterType -> ArgumentType for use in commands"""
    if isinstance(command_type, dict):

        def renamer(key, value):
            """Rename function that will rename ParameterType to ArgumentType

            Note: this function skips "_yamcs_ignore" values, which are used to bypass the XTCE spec in YAMCS. This
            allows strings to be length-data encoded without maximum fixed sizes.
            """
            # Skip renaming if this is a _yamcs_ignore value
            if value == "_yamcs_ignore":
                return key
            # And skip renaming if this is a parameter reference this is a _yamcs_ignore value
            if (
                isinstance(value, dict)
                and value.get("parameterRef", None) == "_yamcs_ignore"
            ):
                return key
            return key.replace("Parameter", "Argument").replace("parameter", "argument")

        # If this is a mapping object, rename all keys and recurse on values
        return {
            renamer(k, v): convert_parameter_type(v) for k, v in command_type.items()
        }
    return command_type


def build_xtce_structure(
    parameter_types: List[Dict[str, Any]],
    parameters: List[Dict[str, Any]],
    containers: List[Dict[str, Any]],
    command_types: List[Dict[str, Any]],
    commands: List[Dict[str, Any]],
    space_system_name: str,
) -> Dict[str, Any]:
    """
    This function organizes parameters, types, containers, and commands into a hierarchy
    of SpaceSystems based on their qualified names (e.g., "Comp.SubComp.Item" becomes
    a nested structure: Comp -> SubComp -> Item).

    Args:
            parameter_types: List of XTCE ParameterType dictionaries (already converted).
            parameters: List of XTCE Parameter dictionaries (already converted).
            containers: List of XTCE Container dictionaries (already converted).
            command_types: List of XTCE ArgumentType dictionaries (already converted for commands).
            commands: List of XTCE Command dictionaries (already converted).
            space_system_name: Name for the root SpaceSystem.

    Returns:
            Dict representing the hierarchical XTCE structure with nested SpaceSystems.
    """

    # Build the root SpaceSystem
    root_space_system = {"name": space_system_name}

    # Group items by namespace
    def group_items_by_namespace(
        items: List[Dict[str, Any]], name_key: str = "name"
    ) -> Dict[Tuple[str, ...], List[Dict[str, Any]]]:
        """Group items by their namespace path."""
        grouped: Dict[Tuple[str, ...], List[Dict[str, Any]]] = defaultdict(list)
        for item in items:
            item_data = xtce_data(item)
            item_name = item_data.get(name_key, "")
            namespace_parts, base_name = extract_namespace_components(item_name)
            # Update the item name to just the base name
            item_data[name_key] = base_name
            # Group by namespace tuple
            grouped[tuple(namespace_parts)].append(item)
        return grouped

    # Group all items
    grouped_param_types = group_items_by_namespace(parameter_types)
    grouped_params = group_items_by_namespace(parameters)
    grouped_containers = group_items_by_namespace(containers)
    grouped_cmd_types = group_items_by_namespace(command_types)
    grouped_commands = group_items_by_namespace(commands)

    # Get all unique namespace paths
    all_namespaces = set()
    all_namespaces.update(grouped_param_types.keys())
    all_namespaces.update(grouped_params.keys())
    all_namespaces.update(grouped_containers.keys())
    all_namespaces.update(grouped_cmd_types.keys())
    all_namespaces.update(grouped_commands.keys())

    # Add items to appropriate SpaceSystems
    for namespace_tuple in all_namespaces:
        namespace_path = list(namespace_tuple)
        target_ss = get_or_create_nested_space_system(root_space_system, namespace_path)

        # Add telemetry metadata if there are any telemetry items
        param_types_here = grouped_param_types.get(namespace_tuple, [])
        params_here = grouped_params.get(namespace_tuple, [])
        containers_here = grouped_containers.get(namespace_tuple, [])

        if param_types_here or params_here or containers_here:
            if "TelemetryMetaData" not in target_ss:
                target_ss["TelemetryMetaData"] = {}

            if param_types_here:
                target_ss["TelemetryMetaData"]["ParameterTypeSet"] = param_types_here
            if params_here:
                target_ss["TelemetryMetaData"]["ParameterSet"] = params_here
            if containers_here:
                target_ss["TelemetryMetaData"]["ContainerSet"] = containers_here

        # Add command metadata if there are any command items
        cmd_types_here = grouped_cmd_types.get(namespace_tuple, [])
        commands_here = grouped_commands.get(namespace_tuple, [])

        if cmd_types_here or commands_here:
            if "CommandMetaData" not in target_ss:
                target_ss["CommandMetaData"] = {}

            if cmd_types_here:
                target_ss["CommandMetaData"]["ArgumentTypeSet"] = cmd_types_here
            if commands_here:
                target_ss["CommandMetaData"]["MetaCommandSet"] = commands_here

    return {"SpaceSystem": root_space_system}


def extract_singular_key_value(data: Dict[str, Any]) -> Tuple[str, Any]:
    """Extract the single key-value pair from a dictionary

    This function guarantees that an element has exactly one key-value pair and returns it. It will raise and assertion
    error if the dictionary does not contain exactly one item.

    Args:
            data: Dictionary with exactly one key-value pair.
    Returns:
            Tuple of the single key and its corresponding value.
    Raises:
            AssertionError: If the dictionary does not contain exactly one key-value pair.
    """
    assert (
        isinstance(data, dict) and len(data) == 1
    ), "Dictionary must contain exactly one key-value pair."
    for k, v in data.items():
        return k, v


INDENT = 0


def recurse_xml_dictionary(element: Optional[ET.Element], node_data: Dict[str, Any]):
    """Recursively convert a dictionary to XML elements"""
    global INDENT
    INDENT += 1

    try:
        # Process keys in a specific order to match XTCE XSD schema requirements
        # For SpaceSystem: Header, TelemetryMetaData, CommandMetaData, ServiceSet, then nested SpaceSystems
        ordered_keys = []
        special_order = ["name", "shortDescription", "Header", "TelemetryMetaData", "CommandMetaData", "ServiceSet"]

        # First, add keys in the special order if they exist
        for key in special_order:
            if key in node_data:
                ordered_keys.append(key)

        # Then add SpaceSystem if it exists (must come after metadata)
        if "SpaceSystem" in node_data:
            ordered_keys.append("SpaceSystem")

        # Finally, add any remaining keys
        for key in node_data:
            if key not in ordered_keys:
                ordered_keys.append(key)

        for data_key in ordered_keys:
            data_value = node_data[data_key]
            # If the value is a list, create multiple child elements
            if isinstance(data_value, list):
                assert (
                    data_key[0].capitalize() == data_key[0]
                ), f"List keys must be capitalized to create child elements: {data_key}"

                # Special case for SpaceSystem: create direct child elements without wrapper
                if data_key == "SpaceSystem":
                    for item in data_value:
                        assert isinstance(
                            item, dict
                        ), "SpaceSystem list items must be dictionaries"
                        # Create SpaceSystem element directly under current element
                        child = ET.SubElement(element, data_key)
                        recurse_xml_dictionary(child, item)
                else:
                    # For other lists, create a wrapper element
                    list_element = ET.SubElement(element, data_key)
                    for item in data_value:
                        assert isinstance(
                            item, dict
                        ), "No list items permitted with primitive or list types"
                        key, value = extract_singular_key_value(item)
                        child = ET.SubElement(list_element, key)
                        recurse_xml_dictionary(child, value)
            # If the key is capitalized, and maps to a dict, create a child element and recurse
            elif isinstance(data_value, dict):
                assert (
                    data_key[0].capitalize() == data_key[0]
                ), "Dict keys must be capitalized to create child elements"
                child = ET.SubElement(element, data_key)
                recurse_xml_dictionary(child, data_value)
            # If the key is capitalized, and maps to a primitive, create a child element with text
            elif data_key[0].capitalize() == data_key[0] and isinstance(
                data_value, (str, int, float)
            ):
                child = ET.SubElement(element, data_key)
                child.text = str(data_value)
            # If the key is capitalized, and maps to a primitive, create a child element with text
            elif data_key[0].capitalize() == data_key[0] and isinstance(
                data_value, (bool)
            ):
                child = ET.SubElement(element, data_key)
                child.text = str("true" if data_value else "false")
            # If the key is lowercase, and maps to a boolean, set attribute on the current element as "true"/"false"
            elif isinstance(data_value, (bool)):
                assert not isinstance(
                    data_value, (list, dict)
                ), "No list or dict types permitted for attribute keys"
                element.set(data_key, str("true" if data_value else "false"))
            # Otherwise for not capitalized elements, set attributes on the current element
            else:
                assert data_key[0].islower(), "Attribute keys must be lowercase"
                assert not isinstance(
                    data_value, (list, dict)
                ), "No list or dict types permitted for attribute keys"
                element.set(data_key, str(data_value))
    except Exception as e:
        print(f"[ERROR] {node_data} {str(e)}")
        raise
    INDENT -= 1
    return element


def write_xtce_xml(structure: Dict[str, Any], file_path: str):
    """Serialize the XTCE-like structure to XML.

    Args:
            structure: Dict produced by `build_xtce_structure`.
            file_path: Destination XML file path.

    Note:
            This creates a minimal XML tree; it does not enforce the full XTCE XSD.
    """
    # Define namespaces and schema locations for XTCE
    xtce_namespace = "http://www.omg.org/spec/XTCE/20180204"
    schema_instance_namespace = "http://www.w3.org/2001/XMLSchema-instance"
    schema_location = (
        f"{xtce_namespace} {xtce_namespace.replace('http:', 'https:')}/SpaceSystem.xsd"
    )

    # Register namespaces with ET
    ET.register_namespace("", "http://www.omg.org/spec/XTCE/20180204")
    ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

    assert structure.keys() == {
        "SpaceSystem"
    }, "Top-level structure must have 'SpaceSystem' key and nothing else."

    # Add the top-level SpaceSystem element with appropriate namespaces
    element = ET.Element(f"{{{ xtce_namespace }}}SpaceSystem")
    element.set(f"{{{ schema_instance_namespace }}}schemaLocation", schema_location)

    # Recurse through the structure to build XML
    recurse_xml_dictionary(element, structure["SpaceSystem"])

    # Write the XML tree to file with declaration and indentation
    tree = ET.ElementTree(element)
    ET.indent(tree, space="  ", level=0)
    tree.write(file_or_filename=file_path, encoding="utf-8", xml_declaration=True)


def validate_xtce(xml_path: Union[str, Path] = None) -> Tuple[bool, List[str]]:
    """Validate an XTCE XML document against the XTCE schema.

    Args:
            xml_path: Path to the XML document to validate.
            schema_path: Optional path or URL to the XTCE XSD. If omitted, uses the official XTCE 1.2 schema URL.

    Returns:
            Tuple of (is_valid, errors). `errors` contains human-readable validation issues when not valid.

    Raises:
            ImportError: If the optional `xmlschema` package is not installed.
            FileNotFoundError: If the XML file does not exist.
            ValueError: If the schema cannot be loaded.
    """
    xml_file = Path(xml_path)
    if not xml_file.exists():
        raise FileNotFoundError(f"XML file not found: {xml_file}")

    schema_location: Union[str, Path] = Path(__file__).parent / "data" / "xtce.xsd"
    try:
        schema = xmlschema.XMLSchema(schema_location)
    except xmlschema.XMLSchemaException as exc:
        raise ValueError(
            f"Failed to load XTCE schema from {schema_location}: {exc}"
        ) from exc

    errors = [str(err) for err in schema.iter_errors(xml_file)]
    return len(errors) == 0, errors
