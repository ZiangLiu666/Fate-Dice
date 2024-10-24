import random
import time
import pp

# 定义一个函数，用于在一个任务中生成随机数并计算它们的总和
def add_random_numbers(count):
    return sum(random.random() for _ in range(count))

def main():
    # 进程数量
    job_count = 4
    # 每个任务处理的随机数数量
    numbers_per_job = 10000 // job_count

    start_time = time.time()

    # 创建 job server
    job_server = pp.Server(ncpus=job_count)

    # 提交任务到 job server
    jobs = [job_server.submit(add_random_numbers, (numbers_per_job,), (), ('random',)) for _ in range(job_count)]

    # 等待所有任务完成并收集结果
    results = [job() for job in jobs]

    # 计算总和
    total_sum = sum(results)

    end_time = time.time()

    print((end_time - start_time) * 1000)

    # 关闭 job server
    job_server.destroy()

if __name__ == '__main__':
    main()
