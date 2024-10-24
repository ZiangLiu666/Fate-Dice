import numpy as np
import time
import threading

def cpu_bound_task(start_index, end_index):
    """Task to sum a segment of numbers."""
    global data  # Ensure that the thread can access the global data array
    segment_sum = np.sum(data[start_index:end_index])
    with thread_lock:
        global total_sum
        total_sum += segment_sum

num_elements = 100000000  # 10 million elements
data = np.random.randint(low=1, high=100, size=num_elements)
total_sum = 0
thread_lock = threading.Lock()  # A lock to manage access to the total_sum

start_time = time.time()

num_threads = 4
segment_size = num_elements // num_threads
threads = []

for i in range(num_threads):
    start_index = i * segment_size
    end_index = (i + 1) * segment_size if i < num_threads - 1 else num_elements
    thread = threading.Thread(target=cpu_bound_task, args=(start_index, end_index))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()

print((end_time - start_time) * 1000)
