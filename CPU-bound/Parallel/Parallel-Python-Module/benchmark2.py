import pp
import random
import time

# Constants
MATRIX_SIZE = 2
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generate a matrix filled with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]

def calculate_cell(matrix1, matrix2, i, j):
    """Calculate the value of one cell in the result matrix."""
    return sum(matrix1[i][k] * matrix2[k][j] for k in range(len(matrix1)))

def multiply_matrices(matrix1, matrix2):
    """Multiply two matrices using Parallel Python for each cell."""
    size = len(matrix1)
    result = [[0] * size for _ in range(size)]

    # Creates job server with automatically detected number of workers
    job_server = pp.Server()

    jobs = []
    for i in range(size):
        for j in range(size):
            # Each cell calculation is submitted as a job
            job = job_server.submit(calculate_cell, (matrix1, matrix2, i, j), (), ("math",))
            jobs.append((i, j, job))

    # Retrieve results
    for i, j, job in jobs:
        result[i][j] = job()

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

# Print the result and the time taken
print(f"Elapsed time for matrix multiplication: {elapsed_time:.6f} seconds")

# Optionally, display the result matrix
for row in result_matrix:
    print(row)
