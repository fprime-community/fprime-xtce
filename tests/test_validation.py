"""Regression tests for installed-package XTCE validation."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

import fprime_xtce.xtce as xtce_module
from fprime_xtce.__main__ import main


class TestXTCEValidation(unittest.TestCase):
    """Verify schema lookup and CLI validation behavior."""

    def test_validate_xtce_uses_packaged_schema(self):
        """The validator must resolve xtce.xsd relative to the installed package."""
        with tempfile.NamedTemporaryFile(suffix=".xml") as xml_file:
            xml_path = Path(xml_file.name)

            with patch.object(xtce_module.xmlschema, "XMLSchema") as schema_class:
                schema_class.return_value.iter_errors.return_value = []
                is_valid, errors = xtce_module.validate_xtce(xml_path)

        expected_schema = (
            Path(xtce_module.__file__).resolve().parent / "data" / "xtce.xsd"
        )
        self.assertTrue(expected_schema.is_file())
        self.assertEqual(Path(schema_class.call_args[0][0]), expected_schema)
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])

    def test_cli_fails_when_generated_xtce_is_invalid(self):
        """A generated document that fails schema validation must fail the CLI."""
        dictionary = Path(__file__).parent / "data" / "SimpleTestDictionary.json"

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as output_file:
            output_path = Path(output_file.name)

        try:
            stderr = io.StringIO()
            with patch(
                "fprime_xtce.__main__.validate_xtce",
                return_value=(False, ["synthetic validation failure"]),
            ), redirect_stderr(stderr):
                result = main([str(dictionary), "-o", str(output_path)])

            self.assertEqual(result, 1)
            self.assertIn("XTCE validation errors", stderr.getvalue())
            self.assertIn("synthetic validation failure", stderr.getvalue())
        finally:
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
