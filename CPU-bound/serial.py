import random
import time

# n*n matrix
MATRIX_SIZE = 200
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generates a matrix of the specified size with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]

def multiply_matrices(matrix1, matrix2):
    """Multiplies two matrices."""
    size = len(matrix1)
    result_matrix = [[0] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            result_matrix[i][j] = sum(matrix1[i][k] * matrix2[k][j] for k in range(size))
    return result_matrix

def display_matrix(matrix, title):
    """Displays the matrix with a title."""
    print(title)
    for row in matrix:
        print("\t" + " ".join(f"{num:5d}" for num in row))

# Generating two 2x2 matrices
matrix_a = generate_matrix(MATRIX_SIZE)
matrix_b = generate_matrix(MATRIX_SIZE)

# Timing the multiplication
start_time = time.time()
result_matrix = multiply_matrices(matrix_a, matrix_b)
elapsed_time = time.time() - start_time



print(f"Elapsed time for matrix multiplication: {elapsed_time:.6f} seconds")
