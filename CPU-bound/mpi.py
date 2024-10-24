import numpy as np
import time
from mpi4py import MPI

def cpu_bound_task(data):
    """Sum a segment of numbers."""
    return np.sum(data)

if __name__ == '__main__':
    num_elements = 100000000  # 10 million elements

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        # Generate random data only on the root process
        data = np.random.randint(low=1, high=100, size=num_elements)
        start_time = time.time()
    else:
        # Prepare a buffer for other processes
        data = np.empty(num_elements, dtype='int')

    # Divide data among processes
    segment_size = num_elements // size
    if rank == size - 1:
        segment_size += num_elements % size  # Handle any remainder on the last process

    # Scatter data to all processes
    segment = np.empty(segment_size, dtype='int')
    comm.Scatter([data, MPI.INT], [segment, MPI.INT], root=0)

    # Each process performs its computation
    local_sum = cpu_bound_task(segment)

    # Gather all partial sums at the root process
    if rank == 0:
        all_sums = np.empty(size, dtype='int')
    else:
        all_sums = None

    comm.Gather([np.array(local_sum, dtype='int'), MPI.INT], [all_sums, MPI.INT], root=0)

    if rank == 0:
        total_sum = np.sum(all_sums)
        end_time = time.time()

        print((end_time - start_time) * 1000)
