import numpy as np
import time

matrix_size = 10000
matrix = np.random.rand(matrix_size, matrix_size)

def memory_bound_task(matrix):
    rows, cols = matrix.shape
    
    for i in range(rows):
        for j in range(cols):
            matrix[i][j] = matrix[i][j] * 1.01

    return

start_time = time.time()

memory_bound_task(matrix)

end_time = time.time()

print(end_time - start_time)
