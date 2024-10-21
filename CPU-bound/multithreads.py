import numpy as np
import time
import threading

MATRIX_SIZE = 200
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generates a matrix with random values."""
    return np.random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX, (size, size))

def thread_task(matrix, start_row, end_row):
    """Thread task to multiply matrix rows."""
    for i in range(start_row, end_row):
        for j in range(matrix.shape[1]):
            matrix[i][j] *= 1.01  # Example operation, replace with actual matrix multiplication logic if needed

if __name__ == '__main__':
    # Initialize matrix
    matrix = generate_matrix(MATRIX_SIZE)

    # Start timing
    start_time = time.time()

    threads = []
    rows_per_thread = MATRIX_SIZE // 4  # Adjust the number of threads
    for i in range(4):  # Example uses 4 threads
        start_row = i * rows_per_thread
        end_row = (i + 1) * rows_per_thread if i < 3 else MATRIX_SIZE
        t = threading.Thread(target=thread_task, args=(matrix, start_row, end_row))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Stop timing
    elapsed_time = time.time() - start_time

    print("Result Matrix:")
    print(matrix)
    print(elapsed_time)
