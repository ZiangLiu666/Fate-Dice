from mpi4py import MPI
import numpy as np
import time

def sum_random_numbers():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        data = np.random.randint(low=1, high=100, size=1000000)
    else:
        data = None

    data = comm.bcast(data, root=0)
    local_sum = np.sum(data[rank * len(data) // size:(rank + 1) * len(data) // size])

    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

    if rank == 0:
        end_time = time.time()
        print("Sum:", total_sum)
        print("Time taken:", end_time - start_time, "seconds")

if __name__ == "__main__":
    start_time = time.time()
    sum_random_numbers()
