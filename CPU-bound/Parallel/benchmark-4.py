import threading
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

def thread_function(result, matrix1, matrix2, assignments):
    """Thread function to compute assigned cells of the result matrix."""
    for i, j in assignments:
        result[i][j] = sum(matrix1[i][k] * matrix2[k][j] for k in range(len(matrix1)))

def distribute_tasks(matrix_size, num_threads):
    """Distribute matrix cells across threads."""
    assignments = [[] for _ in range(num_threads)]
    for i in range(matrix_size):
        for j in range(matrix_size):
            index = (i * matrix_size + j) % num_threads
            assignments[index].append((i, j))
    return assignments

def multiply_matrices(matrix1, matrix2):
    """Multiply two matrices using threading with distributed tasks."""
    size = len(matrix1)
    result = [[0] * size for _ in range(size)]
    threads = []
    task_assignments = distribute_tasks(size, NUMBER_OF_THREADS)

    for assignments in task_assignments:
        thread = threading.Thread(target=thread_function, args=(result, matrix1, matrix2, assignments))
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

# Print the result and the time taken
print(f"Elapsed time for matrix multiplication: {elapsed_time:.2f} seconds")

# Optionally, print a part of the matrix to verify correctness
for i in range(min(10, MATRIX_SIZE)):
    print(result_matrix[i][:min(10, MATRIX_SIZE)])
