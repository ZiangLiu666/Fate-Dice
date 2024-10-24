import random
import time
import pp

def add_random_numbers(count):
    import random  # 保证在工作函数中导入random
    return sum(random.random() for _ in range(count))

def main():
    job_count = 4
    numbers_per_job = 80000000 // job_count

    start_time = time.time()

    job_server = pp.Server(ncpus=job_count)

    # 提交任务时确保传递所有需要的模块
    jobs = [job_server.submit(add_random_numbers, (numbers_per_job,), modules=('random',)) for _ in range(job_count)]

    results = [job() for job in jobs]
    total_sum = sum(results)

    end_time = time.time()

    print((end_time - start_time))

    job_server.destroy()

if __name__ == '__main__':
    main()
