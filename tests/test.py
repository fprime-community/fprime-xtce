"""Test hierarchical XTCE structure generation

This module tests that the fprime-xtce converter properly creates hierarchical
SpaceSystem structures from F Prime JSON dictionaries with namespaced items.

Copyright (c) 2026 Andrei Tumbar. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""

import json
import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple

from fprime_xtce.convert import (
    convert_fprime_types,
    generate_xtce_parameters,
    ConversionMode,
)
from fprime_xtce.container_generation import (
    generate_xtce_containers,
    generate_xtce_commands,
)
from fprime_xtce.xtce import build_xtce_structure, write_xtce_xml, validate_xtce
from fprime_xtce.utilities import extract_namespace_components


class TestNamespaceExtraction(unittest.TestCase):
    """Test namespace component extraction from qualified names"""

    def test_simple_name(self):
        """Test extraction from a simple name without namespace"""
        namespace, base = extract_namespace_components("SimpleType")
        self.assertEqual(namespace, [])
        self.assertEqual(base, "SimpleType")

    def test_single_level_namespace(self):
        """Test extraction from a single-level namespace"""
        namespace, base = extract_namespace_components("Component.Temperature")
        self.assertEqual(namespace, ["Component"])
        self.assertEqual(base, "Temperature")

    def test_multi_level_namespace(self):
        """Test extraction from a multi-level namespace"""
        namespace, base = extract_namespace_components(
            "Component.Subsystem.Temperature"
        )
        self.assertEqual(namespace, ["Component", "Subsystem"])
        self.assertEqual(base, "Temperature")

    def test_pipe_delimiter(self):
        """Test extraction with pipe delimiter (XTCE format)"""
        namespace, base = extract_namespace_components(
            "Component|Subsystem|Temperature"
        )
        self.assertEqual(namespace, ["Component", "Subsystem"])
        self.assertEqual(base, "Temperature")

    def test_mixed_delimiters_dot_preferred(self):
        """Test that dots take precedence over pipes when both exist"""
        namespace, base = extract_namespace_components("A.B|C.D")
        # When both delimiters exist, dots should be used for splitting
        self.assertEqual(namespace, ["A", "B|C"])
        self.assertEqual(base, "D")


class TestXTCEGeneration(unittest.TestCase):
    """Test XTCE generation and validation"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_data_dir = Path(__file__).parent / "data"

    def _load_json_dict(self, path: Path) -> dict:
        """Load a JSON dictionary file"""
        with open(path, "r") as f:
            return json.load(f)

    def _generate_xtce_xml(self, json_path: Path, output_path: Path):
        """Generate XTCE XML from JSON dictionary"""
        # Load JSON data
        json_data = self._load_json_dict(json_path)

        # Convert types
        xtce_parameter_types = convert_fprime_types(json_data)

        # Generate parameters
        xtce_parameters = generate_xtce_parameters(json_data, xtce_parameter_types)

        # Generate containers
        xtce_containers = generate_xtce_containers(json_data, xtce_parameters)

        # Convert command types
        xtce_command_types = convert_fprime_types(
            json_data, mode=ConversionMode.COMMANDS
        )

        # Generate commands
        xtce_commands = generate_xtce_commands(json_data, xtce_command_types)

        # Build hierarchical structure
        deployment = json_data["metadata"]["deploymentName"]
        # Remove dots from deployment name as they're not allowed in XTCE names
        if "." in deployment:
            parts = deployment.split(".")
            assert len(parts) > 0, parts
            deployment = parts[len(parts) - 1]

        xtce_structure = build_xtce_structure(
            xtce_parameter_types,
            xtce_parameters,
            xtce_containers,
            xtce_commands,
            deployment,
        )

        # Write to file
        write_xtce_xml(xtce_structure, str(output_path))

    def _normalize_xml(self, xml_path: Path) -> ET.Element:
        """Parse and normalize XML for comparison"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        # Sort SpaceSystem children by name for consistent comparison
        # (XSD doesn't require a specific order for sibling SpaceSystems)
        self._sort_space_systems(root)
        return root

    def _sort_space_systems(self, element: ET.Element):
        """Recursively sort SpaceSystem children by name attribute"""
        ns = "{http://www.omg.org/spec/XTCE/20180204}"
        space_system_tag = f"{ns}SpaceSystem"

        # Find all direct SpaceSystem children
        space_systems = [child for child in element if child.tag == space_system_tag]

        if space_systems:
            # Sort by name attribute
            space_systems.sort(key=lambda e: e.get("name", ""))

            # Remove old SpaceSystems and reinsert sorted ones at the end
            for ss in space_systems:
                element.remove(ss)
            for ss in space_systems:
                element.append(ss)

        # Recursively sort children
        for child in element:
            self._sort_space_systems(child)

    def _xml_elements_equal(self, e1: ET.Element, e2: ET.Element) -> Tuple[bool, str]:
        """Compare two XML elements recursively, ignoring whitespace.

        Returns:
            Tuple of (is_equal, error_message)
        """
        # Compare tags
        if e1.tag != e2.tag:
            return False, f"Tags differ: {e1.tag} vs {e2.tag}"

        # Compare attributes
        if e1.attrib != e2.attrib:
            return False, f"Attributes differ for {e1.tag}: {e1.attrib} vs {e2.attrib}"

        # Compare text content (ignoring whitespace-only text)
        text1 = (e1.text or "").strip()
        text2 = (e2.text or "").strip()
        if text1 != text2:
            return False, f"Text differs for {e1.tag}: '{text1}' vs '{text2}'"

        # Compare tail (text after closing tag)
        tail1 = (e1.tail or "").strip()
        tail2 = (e2.tail or "").strip()
        if tail1 != tail2:
            return False, f"Tail differs for {e1.tag}: '{tail1}' vs '{tail2}'"

        # Compare number of children
        children1 = list(e1)
        children2 = list(e2)
        if len(children1) != len(children2):
            return (
                False,
                f"Number of children differs for {e1.tag}: {len(children1)} vs {len(children2)}",
            )

        # Recursively compare children
        for c1, c2 in zip(children1, children2):
            equal, msg = self._xml_elements_equal(c1, c2)
            if not equal:
                return False, msg

        return True, ""

    def _run_conversion_test(self, json_filename: str):
        """Generic test function for converting a JSON dict and comparing with reference"""
        json_path = self.test_data_dir / json_filename
        ref_xml_path = self.test_data_dir / json_filename.replace(".json", ".ref.xml")
        update_ref = os.environ.get("UPDATE_REF", "").lower() in ("1", "true", "yes")

        # Verify input files exist
        self.assertTrue(json_path.exists(), f"Input file not found: {json_path}")
        if not update_ref:
            self.assertTrue(
                ref_xml_path.exists(), f"Reference file not found: {ref_xml_path}"
            )

        # Create temporary output file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".xml", delete=False
        ) as temp_file:
            output_path = Path(temp_file.name)

        try:
            # Generate XTCE XML
            self._generate_xtce_xml(json_path, output_path)

            # Verify output file was created
            self.assertTrue(output_path.exists(), "Output file was not created")
            self.assertGreater(output_path.stat().st_size, 0, "Output file is empty")

            # Validate against XSD schema
            is_valid, errors = validate_xtce(output_path)
            if not is_valid:
                print(f"\nValidation errors for {json_filename}:")
                for error in errors[:10]:  # Print first 10 errors
                    print(f"  - {error}")
            self.assertTrue(
                is_valid,
                f"Generated XML does not validate against XSD schema. Errors: {errors[:5]}",
            )

            # Update reference file if requested
            if update_ref:
                shutil.copy2(output_path, ref_xml_path)
                print(f"Updated reference file: {ref_xml_path}")
            else:
                # Compare with reference XML
                generated_root = self._normalize_xml(output_path)
                reference_root = self._normalize_xml(ref_xml_path)

                # Compare XML structure (ignoring formatting)
                is_equal, error_msg = self._xml_elements_equal(
                    generated_root, reference_root
                )

                # If not equal, provide detailed comparison
                if not is_equal:
                    self.fail(
                        f"Generated XML does not match reference.\n"
                        f"Difference: {error_msg}\n"
                        f"Generated: {output_path}\n"
                        f"Reference: {ref_xml_path}"
                    )

        finally:
            # Clean up temporary file
            if output_path.exists():
                output_path.unlink()

    def test_simple_dictionary(self):
        """Test conversion of simple test dictionary"""
        self._run_conversion_test("SimpleTestDictionary.json")

    def test_reference_deployment_dictionary(self):
        """Test conversion of reference deployment dictionary"""
        self._run_conversion_test("ReferenceDeploymentTopologyDictionary.json")


class TestHierarchicalStructure(unittest.TestCase):
    """Test hierarchical SpaceSystem structure"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.test_data_dir = Path(__file__).parent / "data"

    def _load_and_generate(self, json_filename: str) -> Tuple[Path, ET.Element]:
        """Load JSON, generate XTCE, and return output path and parsed root"""
        json_path = self.test_data_dir / json_filename
        json_data = {}
        with open(json_path, "r") as f:
            json_data = json.load(f)

        # Generate XTCE structure
        xtce_parameter_types = convert_fprime_types(json_data)
        xtce_parameters = generate_xtce_parameters(json_data, xtce_parameter_types)
        xtce_containers = generate_xtce_containers(json_data, xtce_parameters)
        xtce_command_types = convert_fprime_types(
            json_data, mode=ConversionMode.COMMANDS
        )
        xtce_commands = generate_xtce_commands(json_data, xtce_command_types)
        deployment = json_data["metadata"]["deploymentName"]
        # Remove dots from deployment name as they're not allowed in XTCE names
        if "." in deployment:
            parts = deployment.split(".")
            assert len(parts) > 0
            deployment = parts[len(parts) - 1]

        xtce_structure = build_xtce_structure(
            xtce_parameter_types,
            xtce_parameters,
            xtce_containers,
            xtce_commands,
            deployment,
        )

        # Write to temporary file
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False)
        output_path = Path(temp_file.name)
        temp_file.close()

        write_xtce_xml(xtce_structure, str(output_path))

        # Parse and return
        tree = ET.parse(output_path)
        return output_path, tree.getroot()

    def test_nested_space_systems_created(self):
        """Test that nested SpaceSystems are created from namespaced items"""
        output_path, root = self._load_and_generate("SimpleTestDictionary.json")

        try:
            ns = "{http://www.omg.org/spec/XTCE/20180204}"

            # Find all SpaceSystem elements
            all_space_systems = root.findall(f".//{ns}SpaceSystem")

            # Should have multiple nested SpaceSystems
            self.assertGreater(
                len(all_space_systems),
                1,
                "Should have nested SpaceSystems for namespace hierarchy",
            )

            # Find SpaceSystem with name="Component"
            component_ss = [
                ss for ss in all_space_systems if ss.get("name") == "Component"
            ]
            self.assertEqual(
                len(component_ss), 1, "Should have one Component SpaceSystem"
            )

            # Find SpaceSystem with name="Subsystem" (nested under Component)
            subsystem_ss = [
                ss for ss in all_space_systems if ss.get("name") == "Subsystem"
            ]
            self.assertEqual(
                len(subsystem_ss), 1, "Should have one Subsystem SpaceSystem"
            )

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_parameters_use_base_names(self):
        """Test that Parameter elements use base names, not fully qualified names"""
        output_path, root = self._load_and_generate("SimpleTestDictionary.json")

        try:
            ns = "{http://www.omg.org/spec/XTCE/20180204}"

            # Find all Parameter elements
            all_parameters = root.findall(f".//{ns}Parameter")

            # Check that parameter names don't contain pipe delimiters
            for param in all_parameters:
                param_name = param.get("name", "")
                # Skip special FPrime base parameters
                if param_name.startswith("FPrime") or param_name.startswith("CCSDS"):
                    continue

                # User parameters should not contain pipe delimiters
                self.assertNotIn(
                    "|",
                    param_name,
                    f"Parameter name '{param_name}' should not contain pipe delimiter",
                )

        finally:
            if output_path.exists():
                output_path.unlink()

    def test_references_use_qualified_names(self):
        """Test that references use fully qualified names with pipe delimiters"""
        output_path, root = self._load_and_generate("SimpleTestDictionary.json")

        try:
            ns = "{http://www.omg.org/spec/XTCE/20180204}"

            # Find ParameterRefEntry elements
            param_refs = root.findall(f".//{ns}ParameterRefEntry")

            # Check that some references use qualified names with pipes
            qualified_refs = [
                ref.get("parameterRef", "")
                for ref in param_refs
                if "|" in ref.get("parameterRef", "")
            ]

            self.assertGreater(
                len(qualified_refs),
                0,
                "Should have parameter references using pipe-delimited qualified names",
            )

            # Check that at least one reference contains "Component|"
            component_refs = [ref for ref in qualified_refs if "Component|" in ref]
            self.assertGreater(
                len(component_refs),
                0,
                "Should have references to Component namespace items",
            )

        finally:
            if output_path.exists():
                output_path.unlink()


if __name__ == "__main__":
    unittest.main()
