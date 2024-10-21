# create 4 processes
from multiprocessing import Process
from time import sleep

def task():
    sleep(5)

if __name__ == '__main__':
    processes = []
    for i in range(4):
        process = Process(target=task)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()