""" Helpers to emit an XTCE-style structure and serialize it to XML.

`build_xtce_structure` produces an in-memory dictionary shaped like XTCE.
`write_xtce_xml` serializes that structure to XML (minimal, not schema-validating).

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Union

import xml.etree.ElementTree as ET

import xmlschema


def build_xtce_structure(
	parameter_types: List[Dict[str, Any]],
	parameters: List[Dict[str, Any]],
	containers: List[Dict[str, Any]],
	commands: List[Dict[str, Any]],
	space_system_name: str,
) -> Dict[str, Any]:
	"""
	Build a minimal XTCE structure from provided ParameterTypes and Parameters.

	Args:
		parameter_types: List of XTCE ParameterType dictionaries (already converted).
		parameters: List of XTCE Parameter dictionaries (already converted).
		containers: List of XTCE Container dictionaries (already converted).
		commands: List of XTCE Command dictionaries (already converted).
		space_system_name: Optional name for the root SpaceSystem.

	Returns:
		Dict representing the XTCE hierarchy:
		{
			"SpaceSystem": {
				"name": <space_system_name>,
				"TelemetryMetaData": {
					"ParameterTypeSet": [{"XYZParameterType": ...}, ...],
					"ParameterSet": [{"Parameter": ...}, ...],
				},
			}
		}
	"""


	command_types = parameter_types.copy()
	command_types = [convert_parameter_type(command_type) for command_type in command_types]
	return {
		"SpaceSystem": {
			"name": space_system_name,
			"TelemetryMetaData": {
				"ParameterTypeSet": parameter_types,
				"ParameterSet": [{"Parameter": parameter} for parameter in parameters],
				"ContainerSet": containers
			},
			"CommandMetaData": {
				"ArgumentTypeSet": command_types,
				"MetaCommandSet": commands
			}
		}
	}


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
	assert isinstance(data, dict) and len(data) == 1, "Dictionary must contain exactly one key-value pair."
	for k, v in data.items():
		return k, v

INDENT = 0

def recurse_xml_dictionary(element: Optional[ET.Element], node_data: Dict[str, Any]):
	""" Recursively convert a dictionary to XML elements"""
	global INDENT
	INDENT += 1

	try:
		for data_key, data_value in node_data.items():
			# If the value is a list, create multiple child elements
			if isinstance(data_value, list):
				list_element = ET.SubElement(element, data_key)
				assert data_key[0].capitalize() == data_key[0], f"List keys must be capitalized to create child elements: {data_key}"
				for item in data_value:
					assert isinstance(item, dict), "No list items permitted with primitive or list types"
					key, value = extract_singular_key_value(item)
					child = ET.SubElement(list_element, key)
					recurse_xml_dictionary(child, value)
			# If the key is capitalized, and maps to a dict, create a child element and recurse
			elif isinstance(data_value, dict):
				assert data_key[0].capitalize() == data_key[0], "Dict keys must be capitalized to create child elements"
				child = ET.SubElement(element, data_key)
				recurse_xml_dictionary(child, data_value)
			# If the key is capitalized, and maps to a primitive, create a child element with text
			elif data_key[0].capitalize() == data_key[0] and isinstance(data_value, (str, int, float)):
				child = ET.SubElement(element, data_key)
				child.text = str(data_value)
			# If the key is capitalized, and maps to a primitive, create a child element with text
			elif data_key[0].capitalize() == data_key[0] and isinstance(data_value, (bool)):
				child = ET.SubElement(element, data_key)
				child.text = str("true"  if data_value else "false")
			# If the key is lowercase, and maps to a boolean, set attribute on the current element as "true"/"false"
			elif isinstance(data_value, (bool)):
				assert not isinstance(data_value, (list, dict)), "No list or dict types permitted for attribute keys"
				element.set(data_key, str("true" if data_value else "false"))
			# Otherwise for not capitalized elements, set attributes on the current element 
			else:
				assert data_key[0].islower(), "Attribute keys must be lowercase"
				assert not isinstance(data_value, (list, dict)), "No list or dict types permitted for attribute keys"
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
	schema_location = f"{xtce_namespace} {xtce_namespace.replace('http:', 'https:')}/SpaceSystem.xsd"

	# Register namespaces with ET
	ET.register_namespace("", "http://www.omg.org/spec/XTCE/20180204")
	ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

	assert structure.keys() == {"SpaceSystem"}, "Top-level structure must have 'SpaceSystem' key and nothing else."
	
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
		raise ValueError(f"Failed to load XTCE schema from {schema_location}: {exc}") from exc

	errors = [str(err) for err in schema.iter_errors(xml_file)]
	return len(errors) == 0, errors

