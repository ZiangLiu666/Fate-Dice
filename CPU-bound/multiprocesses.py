import numpy as np
import time
from multiprocessing import Process, Array

def cpu_bound_task(shared_array, size, start_row, end_row):
    """CPU-intensive task."""
    matrix = np.frombuffer(shared_array.get_obj()).reshape((size, size))
    # Example CPU-intensive operation: increase each element uniquely
    for i in range(start_row, end_row):
        for j in range(size):
            matrix[i][j] += i * j  # or any other CPU-intensive operation

if __name__ == '__main__':
    matrix_size = 500
    start_time = time.time()
    result = Array('d', matrix_size * matrix_size)
    result_matrix = np.frombuffer(result.get_obj()).reshape((matrix_size, matrix_size))
    np.random.seed(0)
    result_matrix[:] = np.random.rand(matrix_size, matrix_size)

    processes = []
    rows_per_process = matrix_size // 4
    for i in range(4):
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i < 3 else matrix_size
        p = Process(target=cpu_bound_task, args=(result, matrix_size, start_row, end_row))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    elapsed_time = time.time() - start_time
    print(elapsed_time)
