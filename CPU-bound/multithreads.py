import numpy as np
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def sum_segment(data):
    return sum(data)

def sum_random_numbers():
    data = np.random.randint(low=1, high=100, size=1000000)
    num_threads = 4
    segment_size = len(data) // num_threads

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(sum_segment, data[i * segment_size:(i + 1) * segment_size]) for i in range(num_threads)]
        total_sum = sum(f.result() for f in futures)

    print("Sum:", total_sum)
    print("Time taken:", time.time() - start_time, "seconds")

if __name__ == '__main__':
    start_time = time.time()
    sum_random_numbers()
