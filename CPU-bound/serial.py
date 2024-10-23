import numpy as np
import time

def sum_random_numbers():
    data = np.random.randint(low=1, high=100, size=1000000)
    start_time = time.time()
    total_sum = np.sum(data)
    end_time = time.time()
    print("Sum:", total_sum)
    print((time.time() - start_time)*1000)

if __name__ == '__main__':
    sum_random_numbers()
