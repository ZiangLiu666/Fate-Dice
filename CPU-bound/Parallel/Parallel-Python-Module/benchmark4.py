import pp
import random
import time

# Constants
MATRIX_SIZE = 100
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10
NUMBER_OF_THREADS = 8


def generate_matrix(size):
    """Generate a matrix filled with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]


def calculate_cell(matrix1, matrix2, i, j):
    """Calculate the value of one cell in the result matrix."""
    return sum(matrix1[i][k] * matrix2[k][j] for k in range(len(matrix1)))


def distribute_tasks(matrix_size, num_threads):
    """Distribute matrix cells across processors."""
    assignments = [[] for _ in range(num_threads)]
    for i in range(matrix_size):
        for j in range(matrix_size):
            index = (i * matrix_size + j) % num_threads
            assignments[index].append((i, j))
    return assignments


def multiply_matrices(matrix1, matrix2):
    """Multiply two matrices using Parallel Python with distributed tasks."""
    size = len(matrix1)
    result = [[0] * size for _ in range(size)]

    # Set up the Parallel Python server
    job_server = pp.Server(NUMBER_OF_THREADS)

    # Create jobs for each cell calculation
    jobs = []
    task_assignments = distribute_tasks(size, NUMBER_OF_THREADS)
    for assignments in task_assignments:
        for i, j in assignments:
            job = job_server.submit(calculate_cell, (matrix1, matrix2, i, j), (), ("math",))
            jobs.append((i, j, job))

    # Collect results
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
print(f"Elapsed time for matrix multiplication: {elapsed_time:.2f} seconds")


