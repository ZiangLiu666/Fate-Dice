import numpy as np
import time
import threading

matrix_size = 10000
matrix = np.random.rand(matrix_size, matrix_size)

def memory_bound_task(start_row, end_row):
    rows, cols = matrix.shape
    
    for i in range(start_row, end_row):
        for j in range(cols):
            matrix[i][j] = matrix[i][j] * 1.01

start_time = time.time()

threads = []
num_threads = 4
rows_per_thread = matrix_size // num_threads

for i in range(num_threads):
    start_row = i * rows_per_thread
    end_row = (i + 1) * rows_per_thread if i < num_threads - 1 else matrix_size
    thread = threading.Thread(target=memory_bound_task, args=(start_row, end_row))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()

print(end_time - start_time)
