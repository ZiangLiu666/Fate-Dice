import numpy as np
import time
import pp

def memory_bound_task(start_row, end_row, matrix):
    rows, cols = matrix.shape
    for i in range(start_row, end_row):
        for j in range(cols):
            matrix[i][j] *= 1.01
    return

if __name__ == '__main__':
    start_time = time.time()

    matrix_size = 4800
    matrix = np.random.rand(matrix_size, matrix_size)

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
