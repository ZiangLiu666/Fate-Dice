import os
import shutil
import time
import multiprocessing

# Function to check if output/<python file name> exists and delete it
def check_and_delete_output_folder(output_folder):
    if os.path.exists(output_folder):
        print(f"Deleting existing folder: {output_folder}")
        shutil.rmtree(output_folder)  # Remove the entire folder and its contents
    else:
        print(f"No existing folder found for: {output_folder}")

# Simulate file reading and writing (I/O intensive task) with better positioned sleep
def io_task(file_name, output_folder):
    print(f"Processing {file_name} started.")
    
    # Simulate a delay before starting to read from the file
    time.sleep(1)  # Simulate I/O delay before starting to read (1 second)
    
    # Read from the input file
    with open(file_name, 'r') as f:
        content = []
        while True:
            data = f.read(1024 * 1024)  # Read 1MB at a time
            if not data:
                break
            content.append(data)

    # Simulate a delay before starting to write to the file
    time.sleep(1)  # Simulate I/O delay before starting to write (1 second)
    
    # Write to the output file
    output_file_name = os.path.join(output_folder, os.path.basename(file_name))
    with open(output_file_name, 'w') as f:
        for chunk in content:
            f.write(chunk)

    print(f"Processing {file_name} completed.")

# Multi-process I/O task using multiprocessing
def multi_process_io(input_folder, output_folder, num_processes=4):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of all files in the input folder
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Create a pool of processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Use pool.starmap to assign files to processes
        pool.starmap(io_task, [(file_name, output_folder) for file_name in input_files])

# Run the multi-process I/O intensive task
if __name__ == "__main__":
    # Get the name of the current script file without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Folder paths (input and output)
    input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')  # Input folder
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', script_name)  # Output folder: output/<script_name>

    # Check and delete the output folder if it exists
    check_and_delete_output_folder(output_folder)

    # Record start time
    start_time = time.time()

    # Run multi-process I/O task with 4 processes
    multi_process_io(input_folder, output_folder, num_processes=4)

    # Record end time
    end_time = time.time()

    print(f"Total time taken: {end_time - start_time:.2f} seconds")
