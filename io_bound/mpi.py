from mpi4py import MPI
import time

def read_and_write_file(file_path):
    for i in range(100):
        with open(file_path, 'r') as file:
            content = file.read()
        with open(file_path, 'w') as file:
            file.write(content)

file_paths = ['test0.txt', 'test1.txt', 'test2.txt', 'test3.txt']

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

start_time = time.time() if rank == 0 else None

for i in range(rank, len(file_paths), size):
    read_and_write_file(file_paths[i])

comm.Barrier()

end_time = time.time() if rank == 0 else None

if rank == 0:
    print((end_time - start_time) * 1000)
