"""
Author: Rafael Lemos - rafaellemos42@gmail.com
Date: 12/08/2024

License: MIT License
"""

from sys import exit
from argparse import ArgumentParser, ArgumentError, ArgumentTypeError
from multiprocessing import cpu_count
import re


def cl_parse():
    """
    Parses command-line arguments for a PDB/mmCIF parser and contact detection tool.

    Returns:
        tuple: A tuple containing the parsed values:
            - files (list): List of input files.
            - multicore (bool): Select MultiCore mode.
            - core (int): Select cores to use.
            - output (bool): Whether to output results to files.

    Raises:
        ArgumentError: If there's an issue with the command-line arguments.
        ValueError: If an invalid processing mode is specified.
        Exception: For any other unexpected errors during argument parsing.
    """
    
    try:
        parser = ArgumentParser(description='COCαDA - Large-Scale Protein Interatomic Contact Cutoff Optimization by Cα Distance Matrices.')
        parser.add_argument('-f', '--files', nargs='+', required=True, type=validate_file, help='List of files in pdb/cif format (at least one required). Wildcards are accepted (ex. -f *.cif).')
        parser.add_argument('-m', '--multicore', required=False, nargs='?', const=0, help='Use MultiCore mode. Default uses all available cores, and selections can be defined based on the following: -m X = specific single core. -m X-Y = range of cores from X to Y. -m X,Y,Z... = specific multiple cores.')
        parser.add_argument('-o', '--output', required=False, nargs='?', const='./outputs', help='Outputs the results to files in the given folder. Default is ./outputs.')
        parser.add_argument('-r', '--region', required=False, nargs='?', help='Define only a region of residues to be analyzed. Selections can be defined based on the following: -r X-Y = range of residues from X to Y. -r X,Y,Z... = specific multiple residues.')
        parser.add_argument('-i', '--interface', required=False, action='store_true', help='Calculate only interface contacts.')
        parser.add_argument('-d', '--distances', required=False, help='Processes custom contact distances defined by the user. Input is 14 positive float values separated by commas (min-max values for each of the 7 contact types).')

        args = parser.parse_args()

        files = args.files
        output = args.output
        interface = args.interface
                
        ncores = cpu_count()
        multi = args.multicore
        if multi is not None:
            if multi == 0:
                core = list(range(ncores))
            else:
                core = validate_core(multi, ncores)
        else:
            core = None
            
        region_values = args.region
        if region_values is not None:
            region = validate_region(region_values)
        else:
            region = None
            
        custom_distances = args.distances
        if custom_distances is not None:
            distances = validate_distances(custom_distances)
        else:
            distances = None
            
    except ArgumentError as e:
        print(f"Argument Error: {str(e)}")
        exit(1)

    except ValueError as e:
        print(f"Error: {str(e)}")
        exit(1)

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        exit(1)
    
    return files, core, output, region, interface, distances
        
        
def validate_file(value):
    """
    Validates a file path to ensure it has a proper extension for PDB or mmCIF files.

    If the file has a valid extension, the function returns the file path. Otherwise, it raises an `ArgumentTypeError`.

    Args:
        value (str): The file path to validate.

    Returns:
        str: The validated file path.

    Raises:
        ArgumentTypeError: If the file does not have a valid extension.
    """
    
    if value.endswith('.pdb') or value.endswith('.cif'):
        return value
    else:
        raise ArgumentTypeError(f"{value} is not a valid file. File must end with '.pdb' or '.cif'")


def validate_core(value, ncores):
    """
    Validates the --core argument to ensure it follows the correct format.
    Supports single core, range of cores, and list of cores.

    Args:
        value (str): The value input by the user for the --core argument.
        ncores (int): The maximum number of cores on the system.

    Returns:
        list: A list of valid cores to use.

    Raises:
        ArgumentTypeError: If the input is not valid or exceeds available cores.
    """
    # Check if it's a single core
    if value.isdigit():
        core = int(value)
        if core < 0 or core >= ncores:
            raise ArgumentTypeError(f"Core number {core} exceeds available cores (max: {ncores - 1})")
        return [core]
    
    # Check if it's a range (e.g. 10-19)
    range_match = re.match(r'^(\d+)-(\d+)$', value)
    if range_match:
        start_core, end_core = map(int, range_match.groups())
        if start_core < 0 or end_core >= ncores or start_core > end_core:
            raise ArgumentTypeError(f"Invalid range {start_core}-{end_core}, ensure it's within [0-{ncores - 1}]")
        return list(range(start_core, end_core + 1))

    # Check if it's a list of cores (e.g. 10,32,65)
    list_match = re.match(r'^(\d+(,\d+)+)$', value)
    if list_match:
        core_list = list(map(int, value.split(',')))
        if any(core < 0 or core >= ncores for core in core_list):
            raise ArgumentTypeError(f"One or more cores exceed available cores (max: {ncores - 1})")
        return core_list
    
    raise ArgumentTypeError(f"Invalid core format: {value}. Use a single core, a range (x-y), or a list (x,y,z).")


def validate_region(region):
    """
    Validates and parses a region input, which can be either a range (e.g., "10-19")
    or a comma-separated list of values (e.g., "10,32,65").

    Args:
        region (str): The input string representing the region selection.

    Returns:
        list: A list of integers representing the parsed region values.

    Raises:
        ArgumentTypeError: If the input format is invalid or contains negative values.
    """
    
    # Check if it's a range (e.g. 10-19)
    range_match = re.match(r'^(\d+)-(\d+)$', region)
    if range_match:
        start_res, end_res = map(int, range_match.groups())
        if start_res < 0 or start_res > end_res:
            raise ArgumentTypeError(f"Invalid range {start_res}-{end_res}]")
        return list(range(start_res, end_res + 1))

    # Check if it's a list (e.g. 10,32,65)
    list_match = re.match(r'^(\d+(,\d+)+)$', region)
    if list_match:
        res_list = list(map(int, region.split(',')))
        if any(core < 0 for core in res_list):
            raise ArgumentTypeError("One or more value is not valid.")
        return res_list
    
    raise ArgumentTypeError(f"Invalid region format: {region}. Use a range (x-y) or a list (x,y,z).")


def validate_distances(distances):
    """
    Validates that the custom_distances string contains exactly 14 positive float numbers separated by commas.
    Groups the numbers into specific pairs and keys in a dictionary.
    Ensures that for each pair (min, max), the second value is strictly greater than the first.
    Raises ArgumentTypeError if the format is incorrect or any validation fails.

    Args:
        value (str): The custom_distances string to validate.

    Returns:
        dict[str, list[float]]: The conditions dictionary for contact detection.
    """
    
    keys = [
        "salt_bridge", "hydrophobic", "hydrogen_bond", "repulsive", "attractive", "disulfide_bond", "aromatic"
    ]
    
    pattern = r'^(\d+(?:\.\d+)?,){13}\d+(?:\.\d+)?$'
    if not re.fullmatch(pattern, distances.strip()):
        raise ArgumentTypeError("Input must contain exactly 14 positive float numbers separated by commas.")

    numbers = [float(x) for x in distances.strip().split(",")]
    
    result = {}
    for idx, key in enumerate(keys):
        min_val = numbers[2 * idx]
        max_val = numbers[2 * idx + 1]
        if min_val >= max_val:
            raise ArgumentTypeError(
                f"For the '{key}' type, the second value must be greater than the first (got {min_val} and {max_val})."
            )
        result[key] = [min_val, max_val]

    return result