from multiprocessing import Process
from time import sleep
import threading

def task():
    sleep(30)

if __name__ == '__main__':
    for i in range(4):
        # thread = threading.Thread(target=task)
        # thread.start()
        process = Process(target=task)
        process.start()