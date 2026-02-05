"""
Test edge cases for telemetry channel type conversion.
"""

import pytest
from fprime_xtce.convert import convert_fprime_types


# Test with duplicate types and edge cases
test_dict = {
    "metadata": {
        "deploymentName": "EdgeCaseTest",
        "frameworkVersion": "3.3.2",
        "projectVersion": "1.0.0",
        "libraryVersions": [],
        "dictionarySpecVersion": "1.0.0"
    },
    "typeDefinitions": [
        {
            "kind": "alias",
            "qualifiedName": "MyU32",
            "type": {
                "name": "U32",
                "kind": "integer",
                "size": 32,
                "signed": False
            },
            "underlyingType": {
                "name": "U32",
                "kind": "integer",
                "size": 32,
                "signed": False
            }
        }
    ],
    "telemetryChannels": [
        # Channel 1: Uses a primitive type not in typeDefinitions
        {
            "name": "Component.Temp",
            "type": {
                "name": "F32",
                "kind": "float",
                "size": 32
            },
            "id": 1,
            "telemetryUpdate": "always"
        },
        # Channel 2: Same primitive type as Channel 1 (should not duplicate)
        {
            "name": "Component.Temp2",
            "type": {
                "name": "F32",
                "kind": "float",
                "size": 32
            },
            "id": 2,
            "telemetryUpdate": "always"
        },
        # Channel 3: Uses type from typeDefinitions (should not create new type)
        {
            "name": "Component.Counter",
            "type": {
                "name": "MyU32",
                "kind": "qualifiedIdentifier"
            },
            "id": 3,
            "telemetryUpdate": "on change"
        },
        # Channel 4: Uses different primitive type
        {
            "name": "Component.IsEnabled",
            "type": {
                "name": "bool",
                "kind": "bool",
                "size": 8
            },
            "id": 4,
            "telemetryUpdate": "always"
        },
        # Channel 5: Uses signed integer
        {
            "name": "Component.SignedValue",
            "type": {
                "name": "I16",
                "kind": "integer",
                "size": 16,
                "signed": True
            },
            "id": 5,
            "telemetryUpdate": "always"
        }
    ]
}

def test_no_duplicate_types():
    """Test that no duplicate types result from multiple primitive channels."""
    result = convert_fprime_types(test_dict)
    
    # Check for duplicates
    type_names = [t.get('name') for t in result['xtce_types']]
    duplicates = [name for name in set(type_names) if type_names.count(name) > 1]
    
    assert not duplicates, f"Found duplicate type names: {duplicates}"

    f32_types = [t for t in result['xtce_types'] if t.get('type') == 'FloatParameterType' and t.get("FloatDataEncoding").get('sizeInBits') == 32]
    assert len(f32_types) == 1, f"Expected only one F32 type, found {len(f32_types)}"


def test_expected_types_present():
    """Test that all expected types are present."""
    result = convert_fprime_types(test_dict)
    
    type_names = [t.get('name') for t in result['xtce_types']]
    expected_types = {'MyU32', 'F32', 'bool', 'I16'}
    actual_types = set(type_names)
    
    assert actual_types == expected_types, f"Type mismatch. Missing: {expected_types - actual_types}, Extra: {actual_types - expected_types}"


def test_correct_number_of_types():
    """Test that the correct number of types are created."""
    result = convert_fprime_types(test_dict)
    
    # Should have: MyU32 (from typeDef), F32, bool, I16 (from channels)
    assert len(result['xtce_types']) == 4, f"Expected 4 types, got {len(result['xtce_types'])}"


def test_qualified_identifier_not_duplicated():
    """Test that qualified identifiers don't create new types."""
    result = convert_fprime_types(test_dict)
    
    # Count how many types come from channel definitions
    # Channel using MyU32 as qualifiedIdentifier should NOT create a new MyU32
    type_names = [t.get('name') for t in result['xtce_types']]
    my_u32_count = type_names.count('MyU32')
    
    assert my_u32_count == 1, f"MyU32 should appear only once (from typeDef), appeared {my_u32_count} times"
