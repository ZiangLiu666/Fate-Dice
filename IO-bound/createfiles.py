import os
import random
import string

# Generate a random file with the specified size (in MB)
def generate_file(file_name, size_in_mb):
    with open(file_name, 'w') as f:
        for _ in range(size_in_mb * 1024 * 1024 // 100):  # 100 bytes per line
            line = ''.join(random.choices(string.ascii_letters + string.digits, k=100))
            f.write(line + '\n')

# Create multiple files in the input folder
def create_files(num_files=20, file_size=50):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the input folder path relative to the script directory
    folder_path = os.path.join(script_dir, 'input')
    
    # Create the folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Generate the specified number of files
    for i in range(num_files):
        file_name = os.path.join(folder_path, f'file_{i}.txt')
        print(f"Creating {file_name}...")
        generate_file(file_name, file_size)
        print(f"{file_name} created.")

# Call the function to create files
create_files()
