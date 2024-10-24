# mpirun -np 4 python3 mpi.py

import numpy as np
import time
from mpi4py import MPI

start_time = 0
end_time = 0

def memory_bound_task(matrix):
    rows, cols = matrix.shape
    for i in range(rows):
        for j in range(cols):
            matrix[i][j] *= 1.01

if __name__ == '__main__':
    matrix_size = 4800

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        matrix = np.random.rand(matrix_size, matrix_size)
        start_time = time.time()
    else:
        matrix = np.empty((matrix_size, matrix_size), dtype='d')

    comm.Bcast(matrix, root=0)

    rows_per_process = matrix_size // size
    start_row = rank * rows_per_process
    end_row = (rank + 1) * rows_per_process if rank < size - 1 else matrix_size

    memory_bound_task(matrix[start_row:end_row])

    if rank == 0:
        for i in range(1, size):
            comm.Recv(matrix[i * rows_per_process:(i + 1) * rows_per_process], source=i)
        end_time = time.time()
    else:
        comm.Send(matrix[start_row:end_row], dest=0)

    if rank == 0:
        print((end_time - start_time)*1000)

