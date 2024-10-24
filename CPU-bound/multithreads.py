import random
import time
import threading

# 定义一个函数，用于在一个线程中生成随机数并累加
def add_random_numbers(count, result, index):
    subtotal = sum(random.random() for _ in range(count))
    result[index] = subtotal

# 线程数量
thread_count = 4
# 每个线程处理的随机数数量
numbers_per_thread = 10000 // thread_count

# 存储每个线程结果的列表
results = [0] * thread_count
threads = []

start_time = time.time()

# 创建并启动线程
for i in range(thread_count):
    thread = threading.Thread(target=add_random_numbers, args=(numbers_per_thread, results, i))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

# 计算总和
total_sum = sum(results)

end_time = time.time()

print(end_time - start_time)
