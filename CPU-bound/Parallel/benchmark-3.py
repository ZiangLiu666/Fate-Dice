import threading
import random
import time

# Constants
MATRIX_SIZE = 100
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generate a matrix filled with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]

def calculate_row(result, matrix1, matrix2, row):
    """Calculate one row of the resulting matrix."""
    size = len(matrix1)
    for j in range(size):
        result[row][j] = sum(matrix1[row][k] * matrix2[k][j] for k in range(size))

def multiply_matrices(matrix1, matrix2):
    """Multiply two matrices, assigning one thread per row of the result matrix."""
    size = len(matrix1)
    result = [[0] * size for _ in range(size)]
    threads = []

    for i in range(size):
        thread = threading.Thread(target=calculate_row, args=(result, matrix1, matrix2, i))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

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

# Optionally, uncomment to print the result matrix
# for row in result_matrix:
#     print(row)
