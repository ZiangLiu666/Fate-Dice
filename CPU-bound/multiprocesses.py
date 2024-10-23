import numpy as np
import time
from multiprocessing import Process, Array, Value

def sum_segment(array, start, end, total):
    local_sum = sum(array[start:end])
    with total.get_lock():
        total.value += local_sum

def sum_random_numbers():
    data = np.random.randint(low=1, high=100, size=1000000)
    num_processes = 4
    total = Value('i', 0)
    segment_size = len(data) // num_processes
    processes = []

    start_time = time.time()

    for i in range(num_processes):
        start = i * segment_size
        end = (i + 1) * segment_size if i < num_processes - 1 else len(data)
        p = Process(target=sum_segment, args=(data, start, end, total))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    end_time = time.time()
    print("Sum:", total.value)
    print("Time taken:", end_time - start_time, "seconds")

if __name__ == '__main__':
    sum_random_numbers()
