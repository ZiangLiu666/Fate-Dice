from mpi4py import MPI
import numpy as np
import time

MATRIX_SIZE = 200
MATRIX_VALUE_MIN = -10
MATRIX_VALUE_MAX = 10

def generate_matrix(size):
    """Generates a matrix with random values."""
    return np.random.randint(MATRIX_VALUE_MIN, MATRIX_VALUE_MAX, (size, size))

if __name__ == '__main__':
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        matrix = generate_matrix(MATRIX_SIZE)
        start_time = time.time()
    else:
        matrix = np.empty((MATRIX_SIZE, MATRIX_SIZE), dtype=int)

    comm.Bcast(matrix, root=0)

    # Each process handles a portion of rows
    rows_per_process = MATRIX_SIZE // size
    start_row = rank * rows_per_process
    end_row = (rank + 1) * rows_per_process if rank < size - 1 else MATRIX_SIZE

    # Example operation, replace with actual matrix multiplication logic if needed
    for i in range(start_row, end_row):
        for j in range(MATRIX_SIZE):
            matrix[i][j] *= 1.01

    # Gather results at the root process
    if rank == 0:
        full_matrix = np.empty_like(matrix)
        comm.Gather(matrix, full_matrix, root=0)
        elapsed_time = time.time() - start_time
        
        print(f"Elapsed time for matrix multiplication: {elapsed_time:.6f} seconds")
    else:
        comm.Gather(matrix, None, root=0)
