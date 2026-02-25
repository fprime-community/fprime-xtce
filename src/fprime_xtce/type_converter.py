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


BUILT_IN_TYPES = [
    {
    "StringParameterType": {
        "name": "raw_string",
        "StringDataEncoding": {
            "encoding": "UTF-8",
            "Variable": {
                "maxSizeInBits": 2048,
                "DynamicValue": {
                    "ParameterInstanceRef": {
                        "parameterRef": "length"
                    },
                    "LinearAdjustment": {
                        "slope": 8,
                        "intercept": 0
                    }
                }
            }
        }
    }},
     {
   "AggregateParameterType": {
       "name": "fprime_string",
       "initialValue": "{length: 0, value: ''}",
       "MemberList": [
           {
                "Member": {
                    "name": "length",
                    "typeRef": "FwSizeStoreType"
                }
            },
            {
                "Member": {
                    "name": "value",
                    "typeRef":"raw_string"
                }
            }
        ]},
    },
#    {
#        "StringParameterType": {
#            "name": "string",
#            "StringDataEncoding": {
#                "encoding": "UTF-8",
#                "Variable": {
#                    "maxSizeInBits": "2048",
#                    "DynamicValue": {
#                        "ParameterInstanceRef": {
#                            "parameterRef": "FwSizeStoreType"
#                        },
#                        "LinearAdjustment": {
#                            "slope": 8,
#                            "intercept": 0
#                        }
#                    }
#                }
#            }
#        }
#    },
{
    "IntegerParameterType": {
      "name": "CCSDS_TM_Sc_Id_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "12"
      }
    }
  },
  {
    "IntegerParameterType": {
      "name": "CCSDS_TM_Vc_Id_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "4"
      }
    }
  },
  {
    "IntegerParameterType": {
      "name": "CCSDS_TM_Other_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "32"
      }
    }
  },

  {
    "AggregateParameterType": {
      "name": "CCSDS_Packet_ID_Type",
      "MemberList": [
        { "Member": { "name": "Version", "typeRef": "CCSDS_Version_Type" } },
        { "Member": { "name": "Type", "typeRef": "CCSDS_Type_Type" } },
        { "Member": { "name": "SecHdrFlag", "typeRef": "CCSDS_Sec_Hdr_Flag_Type" } },
        { "Member": { "name": "APID", "typeRef": "CCSDS_APID_Type" } }
      ]
    }
  },
  {
    "IntegerParameterType": {
      "name": "CCSDS_Version_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "3"
      }
    }
  },
  {
    "BooleanParameterType": {
      "name": "CCSDS_Type_Type",
      "zeroStringValue": "TM",
      "oneStringValue": "TC",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "1"
      }
    }
  },
  {
    "BooleanParameterType": {
      "name": "CCSDS_Sec_Hdr_Flag_Type",
      "zeroStringValue": "NotPresent",
      "oneStringValue": "Present",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "1"
      }
    }
  },
  {
    "IntegerParameterType": {
      "name": "CCSDS_APID_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "11"
      }
    }
  },

  {
    "AggregateParameterType": {
      "name": "CCSDS_Packet_Sequence_Type",
      "MemberList": [
        { "Member": { "name": "GroupFlags", "typeRef": "CCSDS_Group_Flags_Type" } },
        { "Member": { "name": "Count", "typeRef": "CCSDS_Source_Sequence_Count_Type" } }
      ]
    }
  },
  {
    "EnumeratedParameterType": {
      "name": "CCSDS_Group_Flags_Type",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "2"
      },
      "EnumerationList": [
        { "Enumeration": { "value": "0", "label": "Continuation" } },
        { "Enumeration": { "value": "1", "label": "First" } },
        { "Enumeration": { "value": "2", "label": "Last" } },
        { "Enumeration": { "value": "3", "label": "Standalone" } }
      ]
    }
  },
  {
    "IntegerParameterType": {
      "name": "CCSDS_Source_Sequence_Count_Type",
      "signed": "false",
      "UnitSet": {},
      "IntegerDataEncoding": {
        "sizeInBits": "14"
      }
    }
  },

  {
    "IntegerParameterType": {
      "name": "CCSDS_Packet_Length_Type",
      "signed": "false",
#      "initialValue": "0",
      "UnitSet": {
        "Unit": {
          "description": "Size",
          #"text": "Octets"
        }
      },
      "IntegerDataEncoding": {
        "sizeInBits": "16"
      }
    }
  },
   {
     "IntegerParameterType": {
       "name": "U8",
       "signed": "false",
 #      "initialValue": "0",
       "IntegerDataEncoding": {
         "encoding": "unsigned",
         "sizeInBits": "8"
       }
     }
   },
     {
     "IntegerParameterType": {
       "name": "U16",
       "signed": "false",
# #      "initialValue": "0",
       "IntegerDataEncoding": {
         "encoding": "unsigned",
         "sizeInBits": "16"
       }
     }
   },
#   {
#     "IntegerParameterType": {
#       "name": "U32",
#       "signed": "false",
# #      "initialValue": "0",
#       "IntegerDataEncoding": {
#         "encoding": "unsigned",
#         "sizeInBits": "32"
#       }
#     }
#   },
#   {
#     "IntegerParameterType": {
#       "name": "U64",
#       "signed": "false",
# #      "initialValue": "0",
#       "IntegerDataEncoding": {
#         "encoding": "unsigned",
#         "sizeInBits": "64"
#       }
#     }
#   },
#     {
#     "IntegerParameterType": {
#       "name": "char",
#       "signed": "true",
# #      "initialValue": "0",
#       "IntegerDataEncoding": {
#         "encoding": "twosComplement",
#         "sizeInBits": "8"
#       }
#     }
#   },
#   {
#     "IntegerParameterType": {
#       "name": "I8",
#       "signed": "true",
# #      "initialValue": "0",
#       "IntegerDataEncoding": {
#         "encoding": "twosComplement",
#         "sizeInBits": "8"
#       }
#     }
#   },
     {
     "IntegerParameterType": {
       "name": "I16",
       "signed": "true",
 #      "initialValue": "0",
       "IntegerDataEncoding": {
         "encoding": "twosComplement",
         "sizeInBits": "16"
       }
     }
   },  {
    "IntegerParameterType": {
      "name": "I32",
      "signed": "true",
#      "initialValue": "0",
      "IntegerDataEncoding": {
        "encoding": "twosComplement",
        "sizeInBits": "32"
      }
    }
  },#{
#     "IntegerParameterType": {
#       "name": "I64",
#       "signed": "true",
# #      "initialValue": "0",
#       "IntegerDataEncoding": {
#         "encoding": "twosComplement",
#         "sizeInBits": "64"
#       }
#     }
#   },
 {
     "IntegerParameterType": {
         "name": "bool",
 #        "zeroStringValue": "False",
 #        "oneStringValue": "True",
 #        "initialValue": "0",
         "IntegerDataEncoding": {
             "sizeInBits": 8,
             "encoding": "unsigned",
         }
     }
   },
#   {
#       "FloatParameterType": {
#             "name": "F32",
# #            "initialValue": "0.0",
#             "FloatDataEncoding": {
#                 "sizeInBits": 32,
#                 "encoding": "IEEE754_1985",
#             }
#       },
#   },
#     {
#       "FloatParameterType": {
#             "name": "F64",
# #            "initialValue": "0.0",
#             "FloatDataEncoding": {
#                 "sizeInBits": 64,
#                 "encoding": "IEEE754_1985",
#             }
#       },
#   }

]


def convert_identifier(identifier: str) -> str:
    """Convert F Prime qualified FPP names to XTCE-compatible names.
    
    This function replaces dots with slashes and ensures the name starts with a letter.
    
    Args:
        name: Original F Prime qualified name (e.g., "fprime.types.U32")
        
    Returns:
        str: Converted name suitable for XTCE (e.g., "fprime/types/U32")
    """
    # F Prime type names
    assert identifier[0].isalpha(), "Type names must start with a letter w.r.t FPP names"    
    
    # Convert dots to slashes for XTCE compatibility
    converted = identifier.replace('.', '|')
    return converted


def convert_type_definitions(fprime_type_defs):
    """
    Convert a list of F Prime type definitions to XTCE ParameterType equivalents.
    
    This dispatcher iterates over F Prime type definitions and routes each to the
    appropriate converter based on the "kind" field.
    
    Args:
        fprime_type_defs: List of F Prime type definition dictionaries, each with:
            - kind: "enum", "array", "struct", or "alias"
            - qualifiedName: Fully qualified type name
            - ... (other fields specific to each kind)
            
    Returns:
        list: List of XTCE ParameterType dictionaries
    """
    xtce_types = BUILT_IN_TYPES
    errors = []

    for type_def in fprime_type_defs:
        kind = type_def.get("kind")
        
        try:
            if kind == "enum":
                xtce_type = convert_enum_definition(type_def)
            elif kind == "array":
                xtce_type = convert_array_definition(type_def)
            elif kind == "struct":
                xtce_type = convert_struct_definition(type_def)
            elif kind == "alias":
                xtce_type = convert_alias_definition(type_def)
            else:
                raise ValueError(f"Unknown type definition kind: {kind}")
            
            xtce_types.append(xtce_type)
            
        except Exception as e:
            # Log error but continue processing other types
            qualified_name = type_def.get("qualifiedName", "unknown")
            errors.append(f"Error converting type {qualified_name}: {e}")
            continue
    
    return xtce_types, errors


def convert_type_to_parameter_type(fprime_type_desc):
    """
    Convert an F Prime type descriptor to an XTCE ParameterType.
    
    Args:
        fprime_type_desc: F Prime type descriptor dictionary with fields:
            - name: Type name (e.g., "U32", "F64", "bool", "string", etc.)
            - kind: Type kind ("integer", "float", "bool", "string", "qualifiedIdentifier")
            - size: Size in bits
            - signed: For integer types, whether signed (optional)
            
    Returns:
        dict: XTCE ParameterType dictionary structure
    """
    kind = fprime_type_desc.get("kind")
    
    if kind == "integer":
        return _convert_integer_type(fprime_type_desc)
    elif kind == "float":
        return _convert_float_type(fprime_type_desc)
    elif kind == "bool":
        return _convert_boolean_type(fprime_type_desc)
    elif kind == "string":
        return _convert_string_type(fprime_type_desc)
    elif kind == "qualifiedIdentifier":
        # References to other types (enums, arrays, structs)
        # These need to be resolved in the type definitions section
        return _convert_qualified_identifier_type(fprime_type_desc)
    else:
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


def _convert_string_type(fprime_type_desc):
    """
    Convert F Prime string type to XTCE StringParameterType.
    
    Maps:
    - string with size to StringParameterType with fixed or variable length
    """
    name = convert_identifier(fprime_type_desc["name"])
    size_in_bytes = fprime_type_desc["size"]
    size_in_bits = size_in_bytes * 8
    
    xtce_type = {
        "StringParameterType": {
            "name": name,
            "StringDataEncoding": {
                "encoding": "UTF-8",
                "DynamicValue": {
                    "ParameterInstanceRef": {
                        "parameterRef": "FwSizeStoreType"
                    },
                    "LinearAdjustment": {
                        "slope": 8,
                        "intercept": 0
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

def convert_telemetry_channel_types(fprime_telemetry_channels, existing_type_names):
    """
    Convert F Prime telemetry channel definitions to XTCE ParameterType definitions.
    
    This function creates new ParameterTypes for telemetry channel types that were
    not already converted from the typeDefinitions section. This ensures that all
    telemetry channel types have corresponding ParameterType definitions in XTCE.
    
    Args:
        fprime_telemetry_channels: List of F Prime telemetry channel dictionaries, each with:
            - name: Fully qualified channel name
            - type: Type descriptor (primitive or qualified identifier)
            - id: Channel numeric identifier
            - telemetryUpdate: "always" or "on change"
            - annotation: Description (optional)
            - format: Format string (optional)
            - limit: Low/high limits (optional)
            
        existing_type_names: Set of type names already converted from typeDefinitions
            This is used to avoid creating duplicate ParameterTypes
            
    Returns:
        list: List of XTCE ParameterType dictionaries for channel types not in existing_type_names
    """
    xtce_types = []
    created_types = set()
    created_types.add("string")
    errors = []
    channel_type_map = {}
    for channel in fprime_telemetry_channels:
        channel_name = "unset"

        try:
            channel_type = channel["type"]
            channel_name = convert_identifier(channel["name"])
            # Read the channel type descriptor
            if not channel_type:
                raise Exception(f"Channel {channel_name} has no type defined")

            # Get type name - can be either direct type or qualified identifier
            type_name = convert_identifier(channel_type.get("name"))
            if not type_name:
                raise Exception(f"Channel {channel_name} type has no name defined")
            channel_type_map[channel_name] = type_name

            # If they type definition was created, skip
            if type_name in created_types:
                continue

            kind = channel_type.get("kind")            
            if kind == "integer":
                xtce_type = _convert_integer_type(channel_type)
            elif kind == "float":
                xtce_type = _convert_float_type(channel_type)
            elif kind == "bool":
                xtce_type = _convert_boolean_type(channel_type)
            elif kind == "string":
                xtce_type = _convert_string_type(channel_type)
            elif kind == "qualifiedIdentifier" and type_name not in existing_type_names:
                raise Exception(f"Channel {channel_name} references unknown qualifiedIdentifier type {type_name}")
            elif kind == "qualifiedIdentifier":
                # Skip qualified identifiers that are already defined
                continue
            else:
                raise Exception(f"Channel {channel_name} has unknown type kind: {kind}")            
            xtce_types.append(xtce_type)
            created_types.add(type_name)
        except Exception as e:
            errors.append(f"Error converting channel {channel_name}: {e}")
            raise
            continue
    
    return xtce_types, channel_type_map, errors