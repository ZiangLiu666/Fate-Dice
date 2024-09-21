import pp  # Import the Parallel Python module
import random
import time

# Constants
MATRIX_SIZE = 100
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generate a matrix filled with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]

def calculate_row(matrix1, matrix2, row):
    """Calculate one row of the resulting matrix."""
    size = len(matrix1)
    return [sum(matrix1[row][k] * matrix2[k][j] for k in range(size)) for j in range(size)]

def multiply_matrices(matrix1, matrix2):
    """Multiply two matrices, assigning one thread per row of the result matrix using Parallel Python."""
    size = len(matrix1)
    result = [[0] * size for _ in range(size)]

    # Set up the Parallel Python server
    job_server = pp.Server()  # Automatically detect number of cores

    jobs = []
    # Submit jobs for each row calculation
    for i in range(size):
        job = job_server.submit(calculate_row, (matrix1, matrix2, i), (), ("math",))
        jobs.append((i, job))

    # Retrieve results and fill the result matrix
    for i, job in jobs:
        result[i] = job()

    job_server.print_stats()
    job_server.destroy()

    return result

# Generate matrices
matrix_a = generate_matrix(MATRIX_SIZE)
matrix_b = generate_matrix(MATRIX_SIZE)

# Measure time
start_time = time.time()
result_matrix = multiply_matrices(matrix_a, matrix_b)
elapsed_time = time.time() - start_time

# Print the time taken to compute the matrix multiplication
print(f"Elapsed time for matrix multiplication: {elapsed_time:.2f} seconds")


