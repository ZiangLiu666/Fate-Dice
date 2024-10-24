import random
import time
from multiprocessing import Pool

# 定义一个函数，用于在一个进程中生成随机数并计算它们的总和
def add_random_numbers(count):
    return sum(random.random() for _ in range(count))

def main():
    # 进程数量
    process_count = 4
    # 每个进程处理的随机数数量
    numbers_per_process = 80000000 // process_count

    start_time = time.time()

    # 使用进程池
    with Pool(process_count) as pool:
        # 将任务分配给不同的进程，并收集结果
        results = pool.map(add_random_numbers, [numbers_per_process] * process_count)

    # 计算总和
    total_sum = sum(results)

    end_time = time.time()

    print((end_time - start_time) * 1000)

if __name__ == '__main__':
    main()
