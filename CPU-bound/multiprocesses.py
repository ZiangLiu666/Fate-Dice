import numpy as np
import time
from multiprocessing import Process, Array

def cpu_bound_task(data, start_index, end_index):
    """Task to sum a segment of numbers."""
    data_np = np.frombuffer(data.get_obj(), dtype=np.int32)  # Use shared memory buffer
    segment_sum = np.sum(data_np[start_index:end_index])
    with data.get_lock():  # Use lock to prevent data corruption
        data[0] += segment_sum  # Accumulate results in the first element of the array

if __name__ == '__main__':
    num_elements = 100000000  # 10 million elements
    start_time = time.time()

    data = Array('i', num_elements + 1)  # Extra element for the result
    data_np = np.frombuffer(data.get_obj(), dtype=np.int32)  # Numpy view of the shared array
    np.random.seed(0)
    data_np[1:] = np.random.randint(1, 100, size=num_elements)  # Populate array with random integers

    num_processes = 4
    segment_size = num_elements // num_processes
    processes = []

    for i in range(num_processes):
        start_index = i * segment_size + 1  # Offset by 1 to skip the result element
        end_index = (i + 1) * segment_size + 1 if i < num_processes - 1 else num_elements + 1
        process = Process(target=cpu_bound_task, args=(data, start_index, end_index))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    total_sum = data[0]  # Result is stored in the first element of the shared array
    end_time = time.time()

    print((end_time - start_time) * 1000)
