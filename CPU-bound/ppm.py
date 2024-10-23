import numpy as np
import pp
import time

def sum_segment(data):
    return sum(data)

def sum_random_numbers():
    data = np.random.randint(low=1, high=100, size=10000000)
    num_processes = 4
    job_server = pp.Server(num_processes)
    segment_size = len(data) // num_processes

    start_time = time.time()

    jobs = [job_server.submit(sum_segment, (data[i * segment_size:(i + 1) * segment_size],), modules=('numpy',)) for i in range(num_processes)]
    total_sum = sum(job() for job in jobs)

    print((time.time() - start_time)*1000)

if __name__ == '__main__':
    sum_random_numbers()
