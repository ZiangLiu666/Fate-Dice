import numpy as np
import time
from multiprocessing import Process, Array

MATRIX_SIZE = 200
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generates a matrix with random values."""
    return np.random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX, (size, size))

def worker_task(shared_array, size, start_row, end_row):
    """Worker task to multiply matrix rows."""
    matrix = np.frombuffer(shared_array.get_obj()).reshape((size, size))
    for i in range(start_row, end_row):
        for j in range(size):
            matrix[i][j] *= 1.01  # Example operation, replace with actual matrix multiplication logic if needed

if __name__ == '__main__':
    # Initialize matrices
    matrix_a = generate_matrix(MATRIX_SIZE)
    matrix_b = generate_matrix(MATRIX_SIZE)
    result = Array('d', MATRIX_SIZE * MATRIX_SIZE)  # Shared memory
    result_matrix = np.frombuffer(result.get_obj()).reshape((MATRIX_SIZE, MATRIX_SIZE))

    # Start timing
    start_time = time.time()

    processes = []
    rows_per_process = MATRIX_SIZE // 4  # Adjust the number of processes if MATRIX_SIZE is large
    for i in range(4):  # Example uses 4 processes
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i < 3 else MATRIX_SIZE
        p = Process(target=worker_task, args=(result, MATRIX_SIZE, start_row, end_row))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Stop timing
    elapsed_time = time.time() - start_time

 
    print(f"Elapsed time for matrix multiplication: {elapsed_time:.6f} seconds")
