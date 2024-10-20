import pp
import random
import time

MATRIX_SIZE = 200
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generates a matrix of the specified size with random values."""
    return [[random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX) for _ in range(size)] for _ in range(size)]

def multiply_row_by_matrix(matrix1, row_index, matrix2):
    """Multiplies a single row of matrix1 by matrix2."""
    size = len(matrix1)
    result_row = [0] * size
    for j in range(size):
        result_row[j] = sum(matrix1[row_index][k] * matrix2[k][j] for k in range(size))
    return result_row

def main():
    matrix_a = generate_matrix(MATRIX_SIZE)
    matrix_b = generate_matrix(MATRIX_SIZE)
    result_matrix = [[0] * MATRIX_SIZE for _ in range(MATRIX_SIZE)]

    # Set up the Parallel Python server
    job_server = pp.Server()

    # Start timing
    start_time = time.time()

    # Submit jobs for each row of matrix A
    jobs = [job_server.submit(multiply_row_by_matrix, (matrix_a, i, matrix_b), (), ("time", "random")) for i in range(MATRIX_SIZE)]

    # Retrieve results
    for i in range(MATRIX_SIZE):
        result_matrix[i] = jobs[i]()

    # End timing
    elapsed_time = time.time() - start_time

    # Print results
    print("Matrix A:", matrix_a)
    print("Matrix B:", matrix_b)
    print("Result Matrix (A x B):", result_matrix)
    print(f"Elapsed time for matrix multiplication: {elapsed_time:.6f} seconds")

    job_server.print_stats()
    job_server.destroy()

if __name__ == "__main__":
    main()
