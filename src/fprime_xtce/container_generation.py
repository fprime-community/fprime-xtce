"""Generation functions for creating container constructs

Copyright (c) 2026 LeStarch. All rights reserved.

This software is Licensed under the Apache 2.0 License. See LICENSE for details.
"""

from .utilities import xtce_names, convert_to_xtce_reference
from .primitive_containers import BASE_COMMANDS, BASE_CONTAINERS


def build_container(
    fprime_data, members, base_container_ref, id_field_parameter_ref, parameter_names
):
    """Build a container for F Prime telemetry, packets, and events

    The container structure applies the same format for each of the different F Prime types that would be
    represented as XTCE types.

    Args:
        fprime_data: The F Prime data dictionary containing the name and id fields
        members: The list of member parameters for the container
        base_container_ref: The reference to the base container (e.g., "FPrimeTelemetryPacket" or "FPrimeEventPacket")
        id_field_parameter_ref: The reference to the parameter that contains the ID field (e.g., "FPrimePacketId" or "FPrimeEventId")
        parameter_names: Set of valid parameter names
        deployment: Root SpaceSystem name for fully qualified type references
    Returns:
        A dictionary representing the base container structure for the given F Prime data
    """
    # Convert to reference format for validation
    # Parameter references use relative paths (no deployment prefix)
    members_ref = [member.replace('.', '/') for member in members]
    for member in members_ref:
        assert (
            member in parameter_names
        ), f"Container {fprime_data['name']} has undefined parameters: {member}"
    # Container names use relative paths
    container_name = fprime_data['name'].replace('.', '/')
    return {
        "SequenceContainer": {
            "name": container_name,
            "EntryList": [
                {"ParameterRefEntry": {"parameterRef": member}} for member in members_ref
            ],
            "BaseContainer": {
                "containerRef": base_container_ref,
                "RestrictionCriteria": {
                    "ComparisonList": [
                        {
                            "Comparison": {
                                "parameterRef": id_field_parameter_ref,
                                "value": f"{fprime_data['id']}",
                            }
                        },
                    ]
                },
            },
        }
    }


def generate_xtce_containers(fprime_dict, xtce_parameters):
    """Generate the XTCE container definitions from the F Prime dictionary

    XTCE containers are things that can contain parameters in an XTCE structure. In F Prime nomenclature, these will be
    telemetry packet definitions and event definitions (which are containers for their formal parameters).

    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - telemetryPacketSets: List of telemetry packet set definitions
            - events: List of event definitions
            - Other dictionary sections (commands, etc.)
        xtce_parameters: List of XTCE parameter definitions to validate parameters used in the containers are defined
    Returns:
        List of XTCE container definitions converted from the F Prime dictionary
    """
    params = xtce_names(xtce_parameters)
    xtce_containers = BASE_CONTAINERS.copy()
    # Add containers for bare telemetry channels (pairs with TlmChan)
    channels = fprime_dict["telemetryChannels"]
    xtce_containers.extend(
        [
            build_container(
                chan,
                [chan["name"]],
                "FPrimeTelemetryChannel",
                "FPrimeChannelId",
                params,
            )
            for chan in channels
        ]
    )

    # Add containers for telemetry packets (pairs with TlmPacketizer)
    packets_set = fprime_dict.get("telemetryPacketSets")
    for packet_set in packets_set:
        packet_list = packet_set["members"]
        xtce_containers.extend(
            [
                build_container(
                    packet,
                    packet["members"],
                    "FPrimeTelemetryPacket",
                    "FPrimePacketId",
                    params,
                )
                for packet in packet_list
            ]
        )

    # TODO: Add containers for events (pairs with EventManager) when event support is implemented
    # for event in fprime_dict["events"]:
    #     parameter_refs = [f"{event['name']}.{param['name']}" for param in event["formalParams"]]
    #     xtce_containers.append(
    #         build_container(event, parameter_refs, "FPrimeEvent", "FPrimeEventId", params)
    #     )

    # Validate data output
    names = xtce_names(xtce_containers)
    assert len(names) == len(set(names)), f"Duplicate container names found: {names}"
    return xtce_containers


def generate_xtce_commands(fprime_dict, xtce_command_types, deployment):
    """Generate the XTCE command definitions from the F Prime dictionary

    XTCE commands are things that can be parameterized in an XTCE structure. In F Prime nomenclature, these will be
    command definitions.

    Args:
        fprime_dict: F Prime dictionary (loaded from JSON) containing:
            - commands: List of command definitions
            - Other dictionary sections (telemetryChannels, events, etc.)
        xtce_command_types: List of XTCE command argument type definitions to validate against
        deployment: Root SpaceSystem name for fully qualified type references
    Returns:
        List of XTCE command definitions converted from the F Prime dictionary
    """
    commands = BASE_COMMANDS.copy()
    for fprime_command in fprime_dict["commands"]:
        # Command names use relative paths (no deployment prefix)
        command_name = fprime_command["name"].replace('.', '/')

        argument_list = []
        for param in fprime_command["formalParams"]:
            # Argument type references use absolute paths
            if param["type"]["kind"] != "string":
                type_ref = convert_to_xtce_reference(param["type"]["name"], deployment)
            else:
                type_ref = convert_to_xtce_reference(f"string{param['type']['size']}", deployment)

            argument_list.append({
                "Argument": {
                    "name": param["name"],
                    "argumentTypeRef": type_ref,
                }
            })

        command = {
            "MetaCommand": {
                "name": command_name,
                "BaseMetaCommand": {
                    "metaCommandRef": "FPrimeCommand",
                    "ArgumentAssignmentList": [
                        {
                            "ArgumentAssignment": {
                                "argumentName": "OpCode",
                                "argumentValue": f"{fprime_command['opcode']}",
                            }
                        }
                    ],
                },
                "ArgumentList": argument_list,
                "CommandContainer": {
                    "name": command_name,
                    "EntryList": [
                        {
                            "ArgumentRefEntry": {
                                "argumentRef": param["name"]
                            }
                        }
                        for param in fprime_command["formalParams"]
                    ],
                    "BaseContainer": {"containerRef": "FPrimeCommand"},
                },
            }
        }

        # TODO: Add type validation when needed for debugging
        # for argument in command["MetaCommand"]["ArgumentList"]:
        #     type_ref = argument["Argument"]["argumentTypeRef"]
        #     # Convert reference format (with /) to name format (with |) for comparison
        #     type_name_normalized = type_ref.replace('/', '|')
        #     assert type_name_normalized in xtce_names(xtce_command_types), f"Command {command['MetaCommand']['name']} has unknown argument type reference: {type_ref}"

        # Clean up empty ArgumentList if there are no arguments
        if not command["MetaCommand"]["ArgumentList"]:
            del command["MetaCommand"]["ArgumentList"]

        commands.append(command)
    return commands
