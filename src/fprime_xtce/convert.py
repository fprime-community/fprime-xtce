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

"""Convert F' (F-Prime) definitions to XTCE format."""

from fprime_xtce.packet_convert import convert_packet_definitions

from . import type_converter

built_ins = [
    { "name": "FPrimePacketId",        "parameterTypeRef": "FwTlmPacketizeIdType" },
    { "name": "FPrimeEventId",         "parameterTypeRef": "U32" },
    { "name": "FPrimeTime",            "parameterTypeRef": "Fw|TimeValue" },
    { "name": "DataDescType",          "parameterTypeRef": "U16" },
    { "name": "CCSDS_TM_Sc_Id",        "parameterTypeRef": "CCSDS_TM_Sc_Id_Type" },
    { "name": "CCSDS_TM_Vc_Id",        "parameterTypeRef": "CCSDS_TM_Vc_Id_Type" },
    { "name": "CCSDS_TM_Other",        "parameterTypeRef": "CCSDS_TM_Other_Type" },
    { "name": "CCSDS_Packet_ID",       "parameterTypeRef": "CCSDS_Packet_ID_Type" },
    { "name": "CCSDS_Packet_Sequence", "parameterTypeRef": "CCSDS_Packet_Sequence_Type" },
    { "name": "CCSDS_Packet_Length",   "parameterTypeRef": "CCSDS_Packet_Length_Type" },
]
built_ins_commands = [
  {
    "MetaCommand": {
      "name": "CCSDSPacket",
      "abstract": "true",
      "ArgumentList": [
        {
          "Argument": {
            "name": "CCSDS_Version",
            "argumentTypeRef": "CCSDS_Version_Type"
          }
        },
        {
          "Argument": {
            "name": "CCSDS_Type",
            "argumentTypeRef": "CCSDS_Type_Type"
          }
        },
        {
          "Argument": {
            "name": "CCSDS_Sec_Hdr_Flag",
            "argumentTypeRef": "CCSDS_Sec_Hdr_Flag_Type"
          }
        },
        {
          "Argument": {
            "name": "CCSDS_APID",
            "argumentTypeRef": "CCSDS_APID_Type"
          }
        },
        {
          "Argument": {
            "name": "CCSDS_Group_Flags",
            "argumentTypeRef": "CCSDS_Group_Flags_Type"
          }
        }
      ],
      "CommandContainer": {
        "name": "CCSDSPacket",
        "EntryList": [
          {
            "ArgumentRefEntry": {
              "argumentRef": "CCSDS_Version"
            }
          },
          {
            "ArgumentRefEntry": {
              "argumentRef": "CCSDS_Type"
            }
          },
          {
            "ArgumentRefEntry": {
              "argumentRef": "CCSDS_Sec_Hdr_Flag"
            }
          },
          {
            "ArgumentRefEntry": {
              "argumentRef": "CCSDS_APID"
            }
          },
          {
            "ArgumentRefEntry": {
              "argumentRef": "CCSDS_Group_Flags"
            }
          },
          {
            "FixedValueEntry": {
              "name": "CCSDS_Source_Sequence_Count",
              "binaryValue": "0000",
              "sizeInBits": "14"
            }
          },
          {
            "FixedValueEntry": {
              "name": "CCSDS_Packet_Length",
              "binaryValue": "0000",
              "sizeInBits": "16"
            }
          }
        ]
      }
    }
  },
  {
    "MetaCommand": {
      "name": "FPrimeCommand",
      "abstract": "true",
      "BaseMetaCommand": {
        "metaCommandRef": "CCSDSPacket",
        "ArgumentAssignmentList": [
          {
            "ArgumentAssignment": {
              "argumentName": "CCSDS_Version",
              "argumentValue": "0"
            }
          },
          {
            "ArgumentAssignment": {
              "argumentName": "CCSDS_Type",
              "argumentValue": "TC"
            }
          },
          {
            "ArgumentAssignment": {
              "argumentName": "CCSDS_Sec_Hdr_Flag",
              "argumentValue": "NotPresent"
            }
          },
          {
            "ArgumentAssignment": {
              "argumentName": "CCSDS_APID",
              "argumentValue": "0"
            }
          },
          {
            "ArgumentAssignment": {
              "argumentName": "CCSDS_Group_Flags",
              "argumentValue": "Standalone"
            }
          }
        ]
      },
      "CommandContainer": {
        "name": "FPrimeCommand",
        "EntryList": [
          {
            "FixedValueEntry": {
              "name": "Fprime_FW_PACKET_COMMAND",
              "binaryValue": "0000",
              "sizeInBits": "16"
            }
          },
          {
            "FixedValueEntry": {
              "name": "Fprime_Dummy_Opcode",
              "binaryValue": "43434343",
              "sizeInBits": "32"
            }
          },
          {
            "FixedValueEntry": {
              "name": "CCSDS_TM_Crc_Trailer",
              "binaryValue": "0000",
              "sizeInBits": "16"
            }
          }
        ],
        "BaseContainer": {
          "containerRef": "CCSDSPacket"
        }
      }
    }
  }
]


def convert_fprime_types(fprime_dict):
    """
    Convert F Prime type definitions to XTCE ParameterType equivalents.
    
    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - typeDefinitions: List of F Prime type definition dictionaries
            - telemetryChannels: List of telemetry channel definitions (optional)
            - Other dictionary sections (commands, telemetry, etc.)
            
    Returns:
        dict: Dictionary containing:
            - xtce_types: List of converted XTCE ParameterType structures
            - type_map: Mapping of F Prime type names to XTCE types
            - errors: List of any conversion errors encountered
    """
    xtce_types = []
    errors = []
    channel_type_maps = {}

    # Convert type definitions
    try:
        type_defs = fprime_dict["typeDefinitions"]
        defined_types, defined_type_errors = type_converter.convert_type_definitions(type_defs)
        errors.extend(defined_type_errors)
        xtce_types.extend(defined_types)
    except Exception as e:
        if isinstance(e, KeyError) and str(e) == "typeDefinitions":
            errors.append("typeDefinitions missing from dictionary")
        else:
            errors.append(f"Error converting type definitions: {str(e)}")
    
    try:
        channels = fprime_dict["telemetryChannels"]
        channel_types, channel_type_maps, channel_errors = type_converter.convert_telemetry_channel_types(
            channels,
            [
                type_converter.convert_identifier(t.get(list(t.keys())[0]).get("name")) for t in xtce_types
            ]
        )
        xtce_types.extend(channel_types)
        errors.extend(channel_errors)                    
    except Exception as e:
        if isinstance(e, KeyError) and str(e) == "telemetryChannels":
            errors.append("telemetryChannels missing from dictionary")
        else:
            errors.append(f"Error converting telemetry channel types: {str(e)}")    
        raise
    return {"xtce_types": xtce_types, "errors": errors, "channel_type_map": channel_type_maps}

class HasStringException(Exception):
    pass

def convert_formal_parameter(param):
    name = param["name"]
    type_data = param["type"]
    if type_data["kind"] == "string":
        raise HasStringException(f"Formal parameter '{name}' has string type, which is not supported in XTCE")
    return {"Argument": {
        "name": name,
        "argumentTypeRef": type_converter.convert_identifier(type_data["name"])
    }}


def convert_fprime_telemetry(fprime_dict, channel_type_map):
    """
    Convert F Prime telemetry channel definitions to XTCE ParameterType equivalents.
    
    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - telemetryChannels: List of telemetry channel definitions
            - Other dictionary sections (commands, telemetry, etc.)
        channel_type_map: Mapping of telemetry channel names to XTCE type names
            
    Returns:
        dict: Dictionary containing:
            - xtce_types: List of converted XTCE ParameterType structures
            - errors: List of any conversion errors encountered
    """
    xtce_parameters = built_ins.copy()
    errors = []

    # Convert telemetry channel definitions into XTCE Parameter entries
    try:
        channels = fprime_dict["telemetryChannels"]
        for channel in channels:
            channel_name = type_converter.convert_identifier(channel.get("name"))

            channel_type_name = type_converter.convert_identifier(channel_type_map.get(channel_name))

            parameter = {
                "name": channel_name,
                "parameterTypeRef": channel_type_name,
            }

            if "annotation" in channel:
                parameter["shortDescription"] = channel["annotation"]
#            if "id" in channel:
#                parameter["id"] = channel["id"]

            xtce_parameters.append(parameter)
        xtce_containers = []
        packets_set = fprime_dict.get("telemetryPacketSets")
        for packet_set in packets_set:
            packet_list = packet_set["members"]
            #TODO can we handle multiple packet sets?  Should we?
            xtce_containers.extend(convert_packet_definitions(packet_list))
        xtce_commands = built_ins_commands.copy()
        commands = fprime_dict["commands"]
        for command in commands:
            try:
                meta_command = {
                    "MetaCommand": {
                        "name": type_converter.convert_identifier(command["name"]),
                        "BaseMetaCommand": {
                            "metaCommandRef": "FPrimeCommand",
                        },
                        "ArgumentList": [convert_formal_parameter(param) for param in command["formalParams"]],
                        "CommandContainer": {
                            "name": type_converter.convert_identifier(command["name"]),
                            "EntryList": [{"ArgumentRefEntry": {"argumentRef": param["name"]}} for param in command["formalParams"]]
                        }
                    }
                }
                # Strip out empty ArgumentList if there are no formal parameters
                if not meta_command["MetaCommand"]["ArgumentList"]:
                    del meta_command["MetaCommand"]["ArgumentList"]
                xtce_commands.append(meta_command)
            except HasStringException as e:
                #errors.append(f"Skipping command '{command['name']}' due to unsupported string parameter: {str(e)}")
                continue


    except Exception as e:
        if isinstance(e, KeyError) and str(e) == "telemetryChannels":
            errors.append("telemetryChannels missing from dictionary")
        else:
            errors.append(f"Error converting telemetry channels: {str(e)}")
            raise
    return {"xtce_parameters": xtce_parameters, "xtce_containers": xtce_containers, "xtce_commands": xtce_commands, "errors": errors}