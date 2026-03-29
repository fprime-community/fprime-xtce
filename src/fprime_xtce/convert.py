"""Convert F-Prime definitions to XTCE format

This file provides entry points for the conversion functions.

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""
import itertools
from enum import Enum
from collections.abc import Mapping
from .type_converter import convert_type_definitions, convert_to_xtce_reference
from .primitive_types import BASE_FPRIME_TYPES, SPACE_PACKET_TYPES, BASE_PARAMETERS
from .utilities import safe_combine, formal_parameter_types, xtce_names


class ConversionMode(Enum):
    """ An enumeration for the various conversion modes """
    TELEMETRY = "telemetry"
    TELEMETRY_AND_EVENTS = "events"
    COMMANDS = "commands"


def commandTypeRewriter(type_data):
    """ ParameterType -> ArgumentType for use in commands"""
    if isinstance(type_data, Mapping):
        def renamer(key, value):
            """ Rename function that will rename ParameterType to ArgumentType
            
            Note: this function skips "_yamcs_ignore" values, which are used to bypass the the XTCE spec in YAMCS. This
            allows strings to be length-data encoded without maximum fixed sizes.
            """
            # Skip renaming if this is a _yamcs_ignore value
            if value == "_yamcs_ignore":
                return key
            # And skip renaming if this is a parameter reference this is a _yamcs_ignore value
            if isinstance(value, Mapping) and value.get("parameterRef", None) == "_yamcs_ignore":
                return key
            return key.replace("Parameter", "Argument").replace("parameter", "argument")
        # If this is a mapping object, rename all keys and recurse on values
        return {
            renamer(k, v): commandTypeRewriter(v) for k, v in type_data.items()
        }
    return type_data


def convert_fprime_types(fprime_dict, mode=ConversionMode.TELEMETRY_AND_EVENTS):
    """
    Convert F Prime type definitions to XTCE ParameterType equivalents.
    
    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - typeDefinitions: List of F Prime type definition dictionaries
            - telemetryChannels: List of telemetry channel definitions (optional)
            - Other dictionary sections (commands, telemetry, etc.)
        mode: conversion mode to run
            
    Returns:
        dict: Dictionary containing:
            - xtce_types: List of converted XTCE ParameterType structures
            - type_map: Mapping of F Prime type names to XTCE types
            - errors: List of any conversion errors encountered
    """
    xtce_types = BASE_FPRIME_TYPES + SPACE_PACKET_TYPES
    detected_string_types = {}

    # First, convert the type definitions provided directly from the dictionary
    xtce_types = safe_combine(xtce_types, convert_type_definitions(fprime_dict["typeDefinitions"], detected_string_types))

    # Second, convert channel types from the telemetry channel definitions. This must strip out qualified identifiers
    # since those be defined in step one.
    if mode in [ConversionMode.TELEMETRY, ConversionMode.TELEMETRY_AND_EVENTS]:
        channel_types = [channel["type"] for channel in fprime_dict["telemetryChannels"]]
        channel_types = [channel_type for channel_type in channel_types if channel_type["kind"] != "qualifiedIdentifier"]
        xtce_types = safe_combine(xtce_types, convert_type_definitions(channel_types, detected_string_types))

    # Third, convert event and command types
    if mode in [ConversionMode.COMMANDS, ConversionMode.TELEMETRY_AND_EVENTS]:
        parameters = formal_parameter_types(fprime_dict[mode.value])
        parameters = [param for param in parameters if param["kind"] != "qualifiedIdentifier"]
        xtce_types = safe_combine(xtce_types, convert_type_definitions(parameters, detected_string_types))   

    # Rewrite for commands
    if mode == ConversionMode.COMMANDS:
        xtce_types = [commandTypeRewriter(type_data) for type_data in xtce_types]

    return xtce_types


def build_parameter(fprime_data, prefix=""):
    """ Helper function to build an XTCE parameter definition from F Prime data

    This function takes in a data item from a dictionary (e.g. a telemetry channel, or event formal parameter) and
    builds the corresponding XTCE parameter definition. The prefix argument is used to build the parameter name
    in cases where the parameter is nested (e.g. event formal parameters should have the event name as a prefix).

    Args:
        fprime_data: The F Prime data item to convert (e.g. a telemetry channel definition)
        prefix: A string prefix to add to the parameter name
    Returns:
        XTCE parameter definition converted from the F Prime data
    """
    # Make base parameter
    type_data = fprime_data["type"]
    type_ref = type_data["name"] if type_data["kind"] != "string" else f"string{type_data['size']}"
    parameter = {
        "name": convert_to_xtce_reference(f"{prefix}{'.' if prefix else ''}{fprime_data['name']}"),
        "parameterTypeRef": convert_to_xtce_reference(type_ref),
    }

    # Add in parameter optional metadata if it exists
    if "annotation" in fprime_data:
        parameter["shortDescription"] = fprime_data["annotation"]
    return {"Parameter": parameter}


def generate_xtce_parameters(fprime_dict, xtce_types, mode=ConversionMode.TELEMETRY):
    """ Generate the XTCE parameter defininitions from the F Prime dictionary
    
    XTCE parameters are things in a container than can be parameterized in an XTCE container. In F Prime nomenclature,
    these will be telemetry channel values and event formal parameters.

    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - telemetryChannels: List of telemetry channel definitions
            - events: List of event definitions
            - Other dictionary sections (commands, etc.)
        xtce_types: List of XTCE type definitions to validate against
    Returns:
        List of XTCE parameter definitions converted from the F Prime dictionary
    """
    parameters = BASE_PARAMETERS.copy()
    # Convert telemetry channel definitions into XTCE Parameter entries
    if mode in [ConversionMode.TELEMETRY, ConversionMode.TELEMETRY_AND_EVENTS]:
      telemetry_parameters = [build_parameter(channel, "") for channel in fprime_dict["telemetryChannels"]]
      parameters = safe_combine(parameters, telemetry_parameters)
    # Convert event formal parameters into XTCE Parameters, adding the event name as a prefix for collision avoidance
    if mode in [ConversionMode.TELEMETRY_AND_EVENTS]:
      event_parameters = [
          build_parameter(param, event["name"]) for event in fprime_dict["events"] for param in event["formalParams"]
      ]
      parameters = safe_combine(parameters, event_parameters)
    
    # Validate parameter type references were previously found and implemented
    type_names = xtce_names(xtce_types)
    for param in parameters:
        type_name = param["Parameter"]["parameterTypeRef"]
        assert type_name in type_names, f"Parameter {param['Parameter']['name']} has unknown type {type_name}"
    return parameters
