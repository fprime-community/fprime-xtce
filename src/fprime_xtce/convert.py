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

from . import type_converter


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
            [t.get(list(t.keys())[0]).get("name") for t in xtce_types]
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
    xtce_parameters = []
    errors = []

    # Convert telemetry channel definitions into XTCE Parameter entries
    try:
        channels = fprime_dict["telemetryChannels"]
        for channel in channels:
            channel_name = channel.get("name")

            channel_type_name = channel_type_map.get(channel_name)

            parameter = {
                "type": "Parameter",
                "name": channel_name,
                "parameterTypeRef": channel_type_name,
            }

            if "annotation" in channel:
                parameter["shortDescription"] = channel["annotation"]
            if "id" in channel:
                parameter["id"] = channel["id"]

            xtce_parameters.append(parameter)

    except Exception as e:
        if isinstance(e, KeyError) and str(e) == "telemetryChannels":
            errors.append("telemetryChannels missing from dictionary")
        else:
            errors.append(f"Error converting telemetry channels: {str(e)}")    
    return {"xtce_parameters": xtce_parameters, "errors": errors}