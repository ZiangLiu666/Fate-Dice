import numpy as np
import time
from multiprocessing import Process, Array

matrix_size = 8400

def memory_bound_task(matrix, start_row, end_row):
    matrix_np = np.frombuffer(matrix.get_obj()).reshape((matrix_size, matrix_size))
    rows, cols = matrix_np.shape
    
    for i in range(start_row, end_row):
        for j in range(cols):
            matrix_np[i][j] *= 1.01

if __name__ == '__main__':
    start_time = time.time()

    matrix = Array('d', matrix_size * matrix_size)
    matrix_np = np.frombuffer(matrix.get_obj()).reshape((matrix_size, matrix_size))

    np.random.seed(0)
    matrix_np[:] = np.random.rand(matrix_size, matrix_size)

    processes = []
    num_processes = 4
    rows_per_process = matrix_size // num_processes

    for i in range(num_processes):
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i < num_processes - 1 else matrix_size
        process = Process(target=memory_bound_task, args=(matrix, start_row, end_row))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()

    print((end_time - start_time)*1000)
