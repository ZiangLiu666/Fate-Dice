from mpi4py import MPI
import random
import time

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        start_time = time.time()

    # 总随机数的数量
    total_numbers = 10000
    numbers_per_process = total_numbers // size

    # 每个进程生成它的随机数并计算它们的总和
    subtotal = sum(random.random() for _ in range(numbers_per_process))

    # 使用 MPI 的 reduce 操作汇总所有进程的结果
    total_sum = comm.reduce(subtotal, op=MPI.SUM, root=0)

    if rank == 0:
        end_time = time.time()
        print((end_time - start_time) * 1000)

if __name__ == '__main__':
    main()
