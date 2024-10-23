import numpy as np
import time

num_elements = 10000000  # 10 million elements

def cpu_bound_task(num_elements):
    """Generates num_elements random numbers and sums them up."""
    data = np.random.randint(low=1, high=100, size=num_elements)
    sum_result = np.sum(data)
    return sum_result

start_time = time.time()

total_sum = cpu_bound_task(num_elements)

end_time = time.time()


print(end_time - start_time)
