import random
import time

start_time = time.time()

total_sum = 0

for _ in range(10000):
    total_sum += random.random()

end_time = time.time()

print((end_time - start_time) * 1000)
