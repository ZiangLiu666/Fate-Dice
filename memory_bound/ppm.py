import numpy as np
import time
import pp
from multiprocessing import Array

matrix_size = 4800

def memory_bound_task(start_row, end_row, matrix):
    matrix_np = np.frombuffer(matrix.get_obj()).reshape((matrix_size, matrix_size))
    rows, cols = matrix_np.shape

    for i in range(start_row, end_row):
        for j in range(cols):
            matrix_np[i][j] *= 1.01
    return

if __name__ == '__main__':
    start_time = time.time()

    matrix = Array('d', matrix_size * matrix_size)
    matrix_np = np.frombuffer(matrix.get_obj()).reshape((matrix_size, matrix_size))

    np.random.seed(0)
    matrix_np[:] = np.random.rand(matrix_size, matrix_size)

    job_server = pp.Server()

    num_processes = 4
    rows_per_process = matrix_size // num_processes
    jobs = []

    for i in range(num_processes):
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i < num_processes - 1 else matrix_size
        job = job_server.submit(memory_bound_task, (start_row, end_row, matrix))
        jobs.append(job)

    for job in jobs:
        job()

    end_time = time.time()

    print((end_time - start_time)*1000)
