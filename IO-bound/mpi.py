from mpi4py import MPI
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
    rank = MPI.COMM_WORLD.Get_rank()  # Get the current process rank
    print(f"Processing {file_name} started by process {rank}")
    
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

    print(f"Processing {file_name} completed by process {rank}.")

# MPI-based multi-process I/O task using mpi4py
def mpi_io(input_folder, output_folder):
    # Get the MPI communicator
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()  # Current process ID
    size = comm.Get_size()  # Total number of processes

    # Ensure output folder exists (only by rank 0 to avoid race conditions)
    if rank == 0 and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Synchronize all processes to ensure the output folder is created
    comm.Barrier()

    # Get list of all files in the input folder
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Split the files across the MPI processes
    files_per_process = len(input_files) // size
    extra_files = len(input_files) % size

    # Assign files to each process
    if rank < extra_files:
        start_idx = rank * (files_per_process + 1)
        end_idx = start_idx + (files_per_process + 1)
    else:
        start_idx = rank * files_per_process + extra_files
        end_idx = start_idx + files_per_process

    assigned_files = input_files[start_idx:end_idx]

    # Each process works on its assigned files
    for file_name in assigned_files:
        io_task(file_name, output_folder)

# Run the MPI-based multi-process I/O intensive task
if __name__ == "__main__":
    # Get the name of the current script file without extension
    script_name = os.path.splitext(os.path.basename(__file__))[0]

    # Folder paths (input and output)
    input_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')  # Input folder
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', script_name)  # Output folder: output/<script_name>

    # Only rank 0 should check and delete the output folder
    if MPI.COMM_WORLD.Get_rank() == 0:
        check_and_delete_output_folder(output_folder)

    # Synchronize all processes before proceeding
    MPI.COMM_WORLD.Barrier()

    # Record start time (by rank 0)
    if MPI.COMM_WORLD.Get_rank() == 0:
        start_time = time.time()

    # Run the MPI I/O task with all processes
    mpi_io(input_folder, output_folder)

    # Record end time and print results (by rank 0)
    if MPI.COMM_WORLD.Get_rank() == 0:
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time:.2f} seconds")
