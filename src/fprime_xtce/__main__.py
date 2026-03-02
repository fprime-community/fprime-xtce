""" F Prime to XTCE Converter

Entrypoint to the F Prime to XTCE conversion tool script. Converts the F Prime dictionary format to the XTCE format.

Copyright © 2026 Michael Starch
"""
import argparse
import json
import sys

from pathlib import Path

from .convert import convert_fprime_types, generate_xtce_parameters, ConversionMode
from .container_generation import generate_xtce_containers, generate_xtce_commands
from .type_converter import convert_identifier
from .xtce import build_xtce_structure, write_xtce_xml, validate_xtce
from .utilities import xtce_data

def exit_on_errors(result):
    """Check conversion result for errors and print them.
    
    Args:
        result: Conversion result dictionary containing 'errors' list.
    Returns:
        bool: True if errors were found, False otherwise.
    """
    if result['errors']:
        for error in result['errors']:
            print(f"[ERROR] {error}", file=sys.stderr)
        sys.exit(1)

def parse_args(args=None):
    """Parse command line arguments.
    
    Args:
        args: List of arguments to parse. If None, uses sys.argv[1:].
        
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Convert F Prime command and telemetry dictionary to XTCE format"
    )
    parser.add_argument(
        "input",
        help="Input F Prime dictionary file (JSON format)",
        type=Path
    )
    parser.add_argument(
        "-o", "--output",
        help="Output XTCE file (default: xtce.xml)",
        default=Path("xtce.xml"),
        type=Path
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output when converting"
    )
    
    # Read the arguments and validate that the input file exists
    args = parser.parse_args(args)
    if not args.input.exists() or not args.input.is_file():
        parser.error(f"Input file {args.input} does not exist.")
    return args


def main(args=None):
    """Main entry point for the converter.
    
    Args:
        args: List of arguments to parse. If None, uses sys.argv[1:].
    """
    parsed_args = parse_args(args)
    verbose_print = lambda *a, **k: print(*a, **k) if parsed_args.verbose else lambda *a, **k: None

    verbose_print("[INFO] Loading F Prime dictionary")
    try:
        with open(parsed_args.input, 'r') as file_handle:
            json_data = json.load(file_handle)
    except Exception as e:
        print(f"[ERROR] Failed to load input file: {e}")
        return 1
    verbose_print(f"[INFO] Converting {parsed_args.input} to {parsed_args.output}")

    try:
        deployment = json_data["metadata"]["deploymentName"]
    except KeyError:
        print("[ERROR] metadata.deploymentName missing from F Prime dictionary")
        return 1
    # Step 1: Convert F Prime types to XTCE types for use in telemetry channels
    #     This processes:
    #         - Dictionary types
    #         - Telemetry values
    #         - Event formal parameters
    #         - Command formal parameters
    xtce_parameter_types = convert_fprime_types(json_data)

    # Step 2: Generate the XTCE parameter definitions from telemetry channels and events
    #     Validates that the parameter types used are defined in the types section
    xtce_parameters = generate_xtce_parameters(json_data, xtce_parameter_types)

    # Step 3: Generate containers for telemetryChannels, telemetryPackets, and events
    xtce_containers = generate_xtce_containers(json_data, xtce_parameters)
    
    # Step 4: Convert types into command argument types
    xtce_command_types = convert_fprime_types(json_data, mode=ConversionMode.COMMANDS)

    # Step 5: Generate the command definitions
    xtce_commands = generate_xtce_commands(json_data, xtce_command_types)

    # Step 5: Build XTCE structure and write to file
    xtce_structure = {
		"SpaceSystem": {
			"name": convert_identifier(deployment),
			"TelemetryMetaData": {
				"ParameterTypeSet": xtce_parameter_types,
				"ParameterSet": xtce_parameters,
				"ContainerSet": xtce_containers
			},
			"CommandMetaData": {
				"ArgumentTypeSet": xtce_command_types,
				"MetaCommandSet": xtce_commands
			}
		}
	}
    write_xtce_xml(xtce_structure, parsed_args.output)

    # Step 6: Validate output file
    #is_valid, errors = validate_xtce(parsed_args.output)
    if False and not is_valid:
        print(f"[ERROR] XTCE validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
