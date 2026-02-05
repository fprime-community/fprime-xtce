"""
Test telemetry channel type conversion functionality.
"""

import pytest
from fprime_xtce.convert import convert_fprime_types, convert_fprime_telemetry


@pytest.fixture
def basic_test_dict():
    """Create a basic test F Prime dictionary with some telemetry channels."""
    return {
        "metadata": {
            "deploymentName": "TestDeployment",
            "frameworkVersion": "3.3.2",
            "projectVersion": "1.0.0",
            "libraryVersions": [],
            "dictionarySpecVersion": "1.0.0"
        },
        "typeDefinitions": [
            {
                "kind": "enum",
                "qualifiedName": "Test.StatusEnum",
                "representationType": {
                    "name": "U8",
                    "kind": "integer",
                    "size": 8,
                    "signed": False
                },
                "enumeratedConstants": [
                    {"name": "OK", "value": 0},
                    {"name": "ERROR", "value": 1}
                ],
                "default": "Test.StatusEnum.OK"
            }
        ],
        "telemetryChannels": [
            {
                "name": "Test.Component.Channel1",
                "type": {
                    "name": "U32",
                    "kind": "integer",
                    "size": 32,
                    "signed": False
                },
                "id": 100,
                "telemetryUpdate": "always",
                "annotation": "Test channel 1 - should create new ParameterType"
            },
            {
                "name": "Test.Component.Channel2",
                "type": {
                    "name": "F64",
                    "kind": "float",
                    "size": 64
                },
                "id": 101,
                "telemetryUpdate": "on change",
                "annotation": "Test channel 2 - should create new ParameterType"
            },
            {
                "name": "Test.Component.Channel3",
                "type": {
                    "name": "Test.StatusEnum",
                    "kind": "qualifiedIdentifier"
                },
                "id": 102,
                "telemetryUpdate": "on change",
                "annotation": "Test channel 3 - uses existing type definition"
            },
            {
                "name": "Test.Component.Channel4",
                "type": {
                    "name": "bool",
                    "kind": "bool",
                    "size": 8
                },
                "id": 103,
                "telemetryUpdate": "always",
                "annotation": "Test channel 4 - should create new ParameterType"
            }
        ]
    }


def test_telemetry_types_created(basic_test_dict):
    """Test that telemetry channel types are created."""
    result = convert_fprime_types(basic_test_dict)
    
    # Should have: Test.StatusEnum (from typeDef), U32, F64, bool (from channels)
    assert len(result['xtce_types']) == 4, f"Expected 4 types, got {len(result['xtce_types'])}"


def test_qualified_identifier_not_duplicated(basic_test_dict):
    """Test that qualified identifiers reference existing types, not create new ones."""
    result = convert_fprime_types(basic_test_dict)
    
    # Count Test.StatusEnum occurrences (should be 1, from typeDefinitions only)
    type_names = [t.get('name') for t in result['xtce_types']]
    assert type_names.count('Test.StatusEnum') == 1, "Test.StatusEnum should appear only once"


def test_primitive_types_from_channels(basic_test_dict):
    """Test that primitive types from channels are created."""
    result = convert_fprime_types(basic_test_dict)
    
    type_names = set(t.get('name') for t in result['xtce_types'])
    
    # Should have U32, F64, and bool created from channels
    assert 'U32' in type_names, "U32 should be created from Channel1"
    assert 'F64' in type_names, "F64 should be created from Channel2"
    assert 'bool' in type_names, "bool should be created from Channel4"


def test_enum_from_typedef_present(basic_test_dict):
    """Test that enum from typeDefinitions is included."""
    result = convert_fprime_types(basic_test_dict)
    
    type_names = set(t.get('name') for t in result['xtce_types'])
    assert 'Test.StatusEnum' in type_names, "Test.StatusEnum from typeDefinitions should be present"


def test_channel_type_map_matches_channel_types(basic_test_dict):
    """Test that each telemetry channel maps to the expected type name."""
    result = convert_fprime_types(basic_test_dict)

    channel_map = result.get('channel_type_map', {})
    assert channel_map, "channel_type_map should be populated"

    expected = {
        "Test.Component.Channel1": "U32",
        "Test.Component.Channel2": "F64",
        "Test.Component.Channel3": "Test.StatusEnum",
        "Test.Component.Channel4": "bool",
    }

    # Every channel should appear in the map with the correct type name
    assert channel_map == expected, f"Channel type map mismatch. Expected {expected}, got {channel_map}"


def test_build_xtce_parameters(basic_test_dict):
    """Each telemetry channel should produce an XTCE Parameter with the mapped type."""
    type_result = convert_fprime_types(basic_test_dict)
    params_result = convert_fprime_telemetry(basic_test_dict, type_result["channel_type_map"])

    params = params_result["xtce_parameters"]
    assert params_result["errors"] == [], f"Unexpected errors: {params_result['errors']}"
    assert len(params) == 4, f"Expected 4 parameters, got {len(params)}"

    by_name = {p["name"]: p for p in params}
    assert by_name.keys() == {
        "Test.Component.Channel1",
        "Test.Component.Channel2",
        "Test.Component.Channel3",
        "Test.Component.Channel4",
    }, "Parameter names should match channel names"

    assert by_name["Test.Component.Channel1"]["parameterTypeRef"] == "U32"
    assert by_name["Test.Component.Channel2"]["parameterTypeRef"] == "F64"
    assert by_name["Test.Component.Channel3"]["parameterTypeRef"] == "Test.StatusEnum"
    assert by_name["Test.Component.Channel4"]["parameterTypeRef"] == "bool"



def test_type_properties(basic_test_dict):
    """Test that converted types have correct properties."""
    result = convert_fprime_types(basic_test_dict)    
    # Check U32 is unsigned integer
    u32_type = next((t for t in result['xtce_types'] if t.get('name') == 'U32'), None)
    assert u32_type is not None, "U32 type should exist"
    assert u32_type['type'] == 'IntegerParameterType', "U32 should be IntegerParameterType"
    assert u32_type['signed'] == False, "U32 should be unsigned"
    assert u32_type['sizeInBits'] == 32, "U32 should be 32 bits"
    
    # Check F64 is float
    f64_type = next((t for t in result['xtce_types'] if t.get('name') == 'F64'), None)
    assert f64_type is not None, "F64 type should exist"
    assert f64_type['type'] == 'FloatParameterType', "F64 should be FloatParameterType"
    assert f64_type['sizeInBits'] == 64, "F64 should be 64 bits"
    
    # Check bool is boolean
    bool_type = next((t for t in result['xtce_types'] if t.get('name') == 'bool'), None)
    assert bool_type is not None, "bool type should exist"
    assert bool_type['type'] == 'BooleanParameterType', "bool should be BooleanParameterType"


def test_no_errors(basic_test_dict):
    """Test that conversion produces no errors."""
    result = convert_fprime_types(basic_test_dict)
    assert result['errors'] == [], f"Conversion should have no errors, got: {result['errors']}"

