# Copyright 2026
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Convert F Prime type definitions to XTCE ParameterType equivalents."""

from collections.abc import Iterable, Mapping
from .utilities import convert_identifier, xtce_names


def convert_type_definitions(fprime_type_def_or_defs, prefix_or_prefixes = None):
    """ Convert an F Prime type definition or list of type definitions to XTCE ParameterType equivalents.
    
    This dispatcher iterates over F Prime type definitions and routes each to the appropriate converter based on the
    "kind" field.
    
    Args:
        fprime_type_def_or_defs: F Prime type definition dictionary or list of dictionaries with "kind"
            
    Returns:
        list of XTCE ParameterType dictionaries
    """
    # Recurse for each entry if this is a list of type definitions
    assert isinstance(fprime_type_def_or_defs, (Iterable)) and not isinstance(fprime_type_def_or_defs, (bytes, str)), \
        "Expected a list of type definitions or a single type definition"
    if isinstance(fprime_type_def_or_defs, Iterable) and not isinstance(fprime_type_def_or_defs, Mapping):
        assert prefix_or_prefixes is None or isinstance(prefix_or_prefixes, Iterable), \
            "Prefix must be same dimension as type definitions"
        pairs = zip(
            fprime_type_def_or_defs,
            prefix_or_prefixes if prefix_or_prefixes is not None else [None] * len(fprime_type_def_or_defs)
        ) 
        return [convert_type_definitions(item, prefix) for item, prefix in pairs]
    # Otherwise convert one entry based on its kind
    kind = fprime_type_def_or_defs.get("kind")
    if kind == "enum":
        return convert_enum_definition(fprime_type_def_or_defs)
    elif kind == "array":
        return convert_array_definition(fprime_type_def_or_defs)
    elif kind == "struct":
        return convert_struct_definition(fprime_type_def_or_defs)
    elif kind == "alias":
        return convert_alias_definition(fprime_type_def_or_defs)
    elif kind == "integer":
        return _convert_integer_type(fprime_type_def_or_defs)
    elif kind == "float":
        return _convert_float_type(fprime_type_def_or_defs)
    elif kind == "bool":
        return _convert_boolean_type(fprime_type_def_or_defs)
    elif kind == "string":
        return _convert_string_type(fprime_type_def_or_defs, prefix_or_prefixes)
    elif kind == "qualifiedIdentifier":
        # References to other types (enums, arrays, structs)
        # These need to be resolved in the type definitions section
        return _convert_qualified_identifier_type(fprime_type_def_or_defs)
    raise ValueError(f"Unknown type kind: {kind}")            


def _convert_integer_type(fprime_type_desc):
    """
    Convert F Prime integer type to XTCE IntegerParameterType.
    
    Maps:
    - U8, U16, U32, U64 (unsigned) to IntegerParameterType with unsigned encoding
    - I8, I16, I32, I64 (signed) to IntegerParameterType with signed encoding
    """
    name = convert_identifier(fprime_type_desc["name"])
    size_in_bits = fprime_type_desc["size"]
    signed = fprime_type_desc.get("signed", False)
    
    xtce_type = {
        "IntegerParameterType": {
            "name": name,
            "signed": signed,
            "sizeInBits": size_in_bits,
            "IntegerDataEncoding": {
                "sizeInBits": size_in_bits,
                "encoding": "twosComplement" if signed else "unsigned",
                "byteOrder": "mostSignificantByteFirst"
            }
        }
    }
    
    return xtce_type


def _convert_float_type(fprime_type_desc):
    """
    Convert F Prime float type to XTCE FloatParameterType.
    
    Maps:
    - F32 (32-bit float) to FloatParameterType with IEEE754 encoding
    - F64 (64-bit float) to FloatParameterType with IEEE754 encoding
    """
    name = convert_identifier(fprime_type_desc["name"])
    size_in_bits = fprime_type_desc["size"]
    
    xtce_type = {
        "FloatParameterType": {
            "name": name,
            "sizeInBits": size_in_bits,
            "FloatDataEncoding": {
                "sizeInBits": size_in_bits,
                "encoding": "IEEE754_1985",
                "byteOrder": "mostSignificantByteFirst"
            }
        }
    }
    
    return xtce_type


def _convert_boolean_type(fprime_type_desc):
    """
    Convert F Prime bool type to XTCE BooleanParameterType.
    
    Maps:
    - bool (8-bit boolean) to BooleanParameterType
    """
    name = convert_identifier(fprime_type_desc["name"])
    size_in_bits = fprime_type_desc.get("size", 8)
    
    xtce_type = {
        "BooleanParameterType": {
            "name": name,
            "oneStringValue": "True",
            "zeroStringValue": "False",
            "IntegerDataEncoding": {
                "sizeInBits": size_in_bits,
                "encoding": "unsigned",
                "byteOrder": "mostSignificantByteFirst"
            }
        }
    }
    
    return xtce_type


def _convert_string_type(fprime_type_desc, prefix):
    """
    Convert F Prime string type to XTCE StringParameterType.
    
    Maps:
    - string with size to StringParameterType with fixed or variable length
    """
    assert prefix is not None, "Prefix is required for string type conversion to resolve length parameter reference"
    name = convert_identifier(fprime_type_desc["name"])
    size_in_bytes = fprime_type_desc["size"]
    size_in_bits = size_in_bytes * 8
    
    xtce_type = {
        "StringParameterType": {
            "name": convert_identifier(f"{prefix}.{name}"),
            "StringDataEncoding": {
                "encoding": "UTF-8",
                "Variable": {
                    "maxSizeInBits": size_in_bits,
                    "DynamicValue": {
                        "ParameterInstanceRef": {
                            # This is resolved from the top level parameter definition and injected by the container
                            "parameterRef": convert_identifier(f"{prefix}.{name}_length")
                        },
                        "LinearAdjustment": {
                            "slope": 8,
                            "intercept": 0
                        }
                    }
                }
            }
        }
    }
    return xtce_type


def _convert_qualified_identifier_type(fprime_type_desc):
    """
    Convert F Prime qualified identifier (reference to enum, array, or struct).
    
    This creates a reference that needs to be resolved later against
    the type definitions in the F Prime dictionary.
    """
    name = convert_identifier(fprime_type_desc["name"])
    
    # This is a reference type - the actual conversion depends on what it references
    xtce_type = {
        "QualifiedIdentifier": {
            "name": name,
            "typeRef": name  # Reference to be resolved
        }
    }
    
    return xtce_type


def convert_enum_definition(fprime_enum_def):
    """
    Convert F Prime enumeration type definition to XTCE EnumeratedParameterType.
    
    Args:
        fprime_enum_def: F Prime enum definition with fields:
            - kind: "enum"
            - qualifiedName: Fully qualified enum name
            - representationType: Underlying integer type
            - enumeratedConstants: List of {name, value, annotation?}
            - default: Default value
            - annotation: Description (optional)
            
    Returns:
        dict: XTCE EnumeratedParameterType structure
    """
    name = convert_identifier(fprime_enum_def["qualifiedName"])
    repr_type = fprime_enum_def["representationType"]
    constants = fprime_enum_def["enumeratedConstants"]
    
    # Build enumeration list
    enum_list = []
    for const in constants:
        enum_entry = {
            "Enumeration": {
                "value": const["value"],
                "label": const["name"]
            }
        }
        if "annotation" in const:
            enum_entry["Enumeration"]["shortDescription"] = const["annotation"]
        enum_list.append(enum_entry)
    
    xtce_type = {
        "EnumeratedParameterType": {
            "name": name,
            "IntegerDataEncoding": {
                "sizeInBits": repr_type["size"],
                "encoding": "twosComplement" if repr_type.get("signed", False) else "unsigned",
                "byteOrder": "mostSignificantByteFirst"
            },
            "EnumerationList": enum_list,
        }
    }
    
    if "annotation" in fprime_enum_def:
        xtce_type["EnumeratedParameterType"]["shortDescription"] = fprime_enum_def["annotation"]
    
#    if "default" in fprime_enum_def:
#        xtce_type["EnumeratedParameterType"]["initialValue"] = fprime_enum_def["default"]
    return xtce_type


def convert_array_definition(fprime_array_def):
    """
    Convert F Prime array type definition to XTCE ArrayParameterType.
    
    Args:
        fprime_array_def: F Prime array definition with fields:
            - kind: "array"
            - qualifiedName: Fully qualified array name
            - size: Number of elements
            - elementType: Type descriptor of array elements
            - default: Default array value (optional)
            - annotation: Description (optional)
            
    Returns:
        dict: XTCE ArrayParameterType structure
    """
    name = convert_identifier(fprime_array_def["qualifiedName"])
    array_size = fprime_array_def["size"]
    element_type = fprime_array_def["elementType"]

    assert element_type["kind"] != "string", "Strings in arrays are not supported"
    
    # Convert element type
    element_type_name = convert_identifier(element_type["name"])
    
    xtce_type = {
        "ArrayParameterType": {
            "name": name,
            "arrayTypeRef": element_type_name,
            "DimensionList": {
                # Note: XTCE supports multi-dimensional arrays, F-Prime has 1D arrays
                "Dimension": {
                    "StartingIndex": {"FixedValue": 0},
                    "EndingIndex": {"FixedValue": array_size - 1}
                }
            }
        }
    }
    
    if "annotation" in fprime_array_def:
        xtce_type["ArrayParameterType"]["shortDescription"] = fprime_array_def["annotation"]
    
#    if "default" in fprime_array_def:
#        xtce_type["ArrayParameterType"]["initialValue"] = str(fprime_array_def["default"])
    
    return xtce_type


def convert_struct_definition(fprime_struct_def):
    """
    Convert F Prime struct type definition to XTCE AggregateParameterType.
    
    Args:
        fprime_struct_def: F Prime struct definition with fields:
            - kind: "struct"
            - qualifiedName: Fully qualified struct name
            - members: Dict of member names to member descriptors
                - Each member has: type, index, size?, format?, annotation?
            - default: Default struct value (optional)
            - annotation: Description (optional)
            
    Returns:
        dict: XTCE AggregateParameterType structure
    """
    name = convert_identifier(fprime_struct_def["qualifiedName"])
    members = fprime_struct_def["members"]
    
    # Build member list - sort by index to maintain order
    member_list = []
    for member_name, member_desc in members.items():
        member_type = member_desc["type"]
        member_type_name = convert_identifier(member_type["name"])

        assert member_type["kind"] != "string", "Struct members of type string are not supported"
        
        member_entry = {
            "name": member_name,
            "typeRef": member_type_name
        }
        
        if "annotation" in member_desc:
            member_entry["shortDescription"] = member_desc["annotation"]
#        if "default" in fprime_struct_def and member_type["kind"] == "enum":
#            member_entry["initialValue"] = fprime_struct_def["default"][member_name]
#        if "default" in fprime_struct_def and member_type["kind"] == "string":
#            member_entry["initialValue"] = f'{{"length": {len(fprime_struct_def["default"][member_name])}, "value": "{fprime_struct_def["default"][member_name]}"}}'
#        if "default" in fprime_struct_def and isinstance(fprime_struct_def["default"][member_name], (int, bool)):
#            member_entry["initialValue"] = fprime_struct_def["default"][member_name]
        
        
        member_list.append((member_desc["index"], member_entry))
    
    # Sort by index and extract member entries
    member_list.sort(key=lambda x: x[0])
    sorted_members = [m[1] for m in member_list]
    
    xtce_type = {
        "AggregateParameterType": {
            "name": name,
            "MemberList": [{"Member": member} for member in sorted_members]
        }
    }
    
    if "annotation" in fprime_struct_def:
        xtce_type["AggregateParameterType"]["shortDescription"] = fprime_struct_def["annotation"]
    
#    if "default" in fprime_struct_def:
#        xtce_type["AggregateParameterType"]["initialValue"] = str()
    
    return xtce_type


def convert_alias_definition(fprime_alias_def):
    """
    Convert F Prime type alias definition to XTCE type reference.
    
    In XTCE, type aliases are typically represented by using the baseType
    attribute to derive from another type. However, for simple aliases,
    we can create a new type that references the underlying type.
    
    Args:
        fprime_alias_def: F Prime alias definition with fields:
            - kind: "alias"
            - qualifiedName: Fully qualified alias name
            - type: Type descriptor being aliased
            - underlyingType: The ultimate underlying type (following alias chain)
            - annotation: Description (optional)
            
    Returns:
        dict: XTCE type structure with baseType reference
    """
    name = convert_identifier(fprime_alias_def["qualifiedName"])

    aliased_type = fprime_alias_def["type"]
    underlying_type = fprime_alias_def["underlyingType"]
    
    # Determine the XTCE type based on the underlying type
    underlying_kind = underlying_type["kind"]
    
    # Create a new type that extends the aliased type
    if underlying_kind == "integer":
        xtce_type = {
            "IntegerParameterType": {
                "name": name,
                "baseType": aliased_type["name"],
                "signed": underlying_type.get("signed", False),
                "sizeInBits": underlying_type["size"]
            }
        }
    elif underlying_kind == "float":
        xtce_type = {
            "FloatParameterType": {
                "name": name,
                "baseType": aliased_type["name"],
                "sizeInBits": underlying_type["size"]
            }
        }
    elif underlying_kind == "bool":
        xtce_type = {
            "BooleanParameterType": {
                "name": name,
                "baseType": aliased_type["name"]
            }
        }
    elif underlying_kind == "string":
        xtce_type = {
            "TypeAlias": {
                "name": name,
                "baseType": "string"
            }
        }
    else:
        # For other types, create a generic reference
        xtce_type = {
            "TypeAlias": {
                "name": name,
                "baseType": aliased_type["name"]
            }
        }
    
    if "annotation" in fprime_alias_def:
        xtce_type[list(xtce_type)[0]]["shortDescription"] = fprime_alias_def["annotation"]
    
    return xtce_type