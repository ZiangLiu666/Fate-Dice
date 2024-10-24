import pp
import os
import time
import shutil

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
    return file_name  # Return the file name for job tracking

# Main function to run the parallel processing task
def parallel_io(input_folder, output_folder, num_processes=4):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get list of all files in the input folder
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Set up the Parallel Python job server
    job_server = pp.Server(ncpus=num_processes)
    print(f"Starting job server with {num_processes} processes")

    # Submit tasks to the job server
    jobs = [(file_name, job_server.submit(io_task, (file_name, output_folder), (), ("os", "time", "shutil"))) for file_name in input_files]

    # Wait for jobs to finish and collect results
    for file_name, job in jobs:
        try:
            result = job()  # Block until job finishes
            print(f"Job for {result} completed.")
        except Exception as e:
            print(f"Error occurred while processing {file_name}: {e}")

    # Shut down the job server
    job_server.print_stats()

# Run the parallel I/O task using pp library
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

    # Run parallel I/O task with 4 processes
    parallel_io(input_folder, output_folder, num_processes=4)

    # Record end time
    end_time = time.time()

    print(f"Total time taken: {end_time - start_time:.2f} seconds")
