"""
Author: Rafael Lemos - rafaellemos42@gmail.com
Date: 12/08/2024

License: MIT License
"""

import os
# import json
from timeit import default_timer as timer
from concurrent.futures import ProcessPoolExecutor, as_completed
# from psutil import Process
from itertools import islice

import parser
import argparser
import contacts
import classes


def main():
    """
    Main function for the script.

    This function parses command-line arguments, sets up the environment based on the specified mode,
    and runs the appropriate processing function (single-core or multi-core) on the input files.
    It also manages core affinity, output folder creation, and timing of the entire process.
    """
    global_time_start = timer()
    
    file_list, core, output, region, interface, custom_distances = argparser.cl_parse()
    
    print("--------------COCaDA----------------\n")
    
    # context object for shared parameters
    context = classes.ProcessingContext(core=core, output=output, region=region, interface=interface, custom_distances=custom_distances)

    if core is not None:  # Set specific core affinity
        Process(os.getpid()).cpu_affinity(core)
        print("Multicore mode selected")
                     
        if len(core) == 1: # One specific core
            print(f"Running on core {core[0]}.")
        elif core[-1] - core[0] == len(core) - 1:  # Range
            print(f"Running on cores {core[0]} to {core[-1]}\nTotal number of cores: {len(core)}")
        else: # List
            print(f"Running on cores: {', '.join(map(str, core))}\nTotal number of cores: {len(core)}")

    else:
        print("Running on single mode with no specific core.")

    if interface:
        print("Calculating only interface contacts.") 
               
    if output:
        print(f"Generating outputs in '{output}' folder.")
        if not os.path.exists(output):
            os.makedirs(output)
    else:
        output = None
        
    if custom_distances:
        print("Using custom distances provided by the user.")
        try:
            max_value = max(y for x in context.custom_distances.values() for y in x)
            if max_value > 6:
                context.epsilon = max_value - 6
        except ValueError as e:
            print(e)  
            exit(1)
            
    process_func = single if core is None else multi_process_files
    process_func(file_list, context)
    
    print("\n------------------------------------\n")
    print(f"Total time elapsed: {(timer() - global_time_start):.3f}s\n")


def single(file_list, context):
    """
    Processes a list of files in single-core mode.

    Args:
        file_list (list): List of file paths to process.
        context (ProcessingContext): Context object containing parameters such as core, output, and region.

    This function processes each file in the list sequentially, detects contacts, and outputs the results to the console or to a file, depending on the 'output' flag.
    """
    for file in file_list:
        try:
            result = process_file(file, context)
            process_result(result, context.output)
        except Exception as e:
            print(f"Error: {e}")


def multi_process_files(file_list, context):
    num_cores = len(context.core)
    batch_size = max(1, len(file_list) // num_cores)  # Calculate reasonable batch size
    print(f"Number of files: {len(file_list)} | Batch size: {batch_size}\n")

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = {executor.submit(process_batch, batch, context): batch
                   for batch in batch_generator(file_list, batch_size)}

        for future in as_completed(futures):  # Wait for all batches to complete
            try:
                future.result()  # Process results from batch
            except Exception as e:
                print(f"Error processing batch: {e}")
            finally:
                del futures[future]  # Clean up futures


def process_batch(batch, context):
    #batch_start = timer()
    for file_path in batch:
        result = process_file(file_path, context)
        if result:
            process_result(result, context.output)
    
    #print(f"Batch completed: {batch}, Time: {timer() - batch_start:.3f}s")


def batch_generator(file_list, batch_size):
    it = iter(file_list)
    while batch := list(islice(it, batch_size)):
        yield batch

def process_file(file_path, context):
    """
    Processes a single file for contact detection.

    Args:
        file_path (str): Path to the file to be processed.
        context (ProcessingContext): Context object containing parameters such as core, output, and region.

    Returns:
        tuple: A tuple containing the processed Protein object, the list of detected contacts, and the processing time.
        None: If the file cannot be processed or an error occurs.

    This function parses the PDB or mmCIF file, detects contacts, and returns the results. If an error occurs during processing, it logs the error and returns None.
    """
    start_time = timer()

    try:
        parsed_data = parser.parse_pdb(file_path) if file_path.endswith(".pdb") else parser.parse_cif(file_path)

        if parsed_data.true_count() > 10000:  # Skip very large proteins (customizable)
            print(f"Skipping ID '{parsed_data.id}'. Size: {parsed_data.true_count()} residues") 
            if context.output:
                with open(f"{context.output}/big.csv", "a") as f:
                    f.write(f"{parsed_data.id},{parsed_data.title},{parsed_data.true_count()},x\n")
            return None

        contacts_list, interface_res = contacts.contact_detection(parsed_data, context.region, context.interface, context.custom_distances, context.epsilon)
        process_time = timer() - start_time
        return parsed_data, contacts_list, process_time, interface_res

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def process_result(result, output):
    """
    Handles the result of processing a file.

    Args:
        result (tuple): A tuple containing the processed Protein object, contacts list, and processing time.
        output (str): The directory where output files will be saved.
    """
    if result:
        protein, contacts_list, process_time, interface_res = result
        output_data = f"ID: {protein.id} | Size: {protein.true_count():<7} | Contacts: {len(contacts_list):<7} | Time: {process_time:.3f}s"
        print(output_data)
        
        if output:
            output_folder = f"{output}"
            
            # COCaDA-web exclusive
            number_contacts = contacts.count_contacts(contacts_list)
            number_contacts = ','.join(map(str, number_contacts))
            
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            with open(f"{output_folder}/contacts.csv","w") as f:
                f.write(contacts.show_contacts(contacts_list))
            
            with open(f"{output_folder}/info.csv","w") as f:
                f.write(f"{protein.id},{protein.title},{protein.true_count()},{len(contacts_list)},{number_contacts}")


if __name__ == "__main__":
    main()
