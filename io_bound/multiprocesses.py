import multiprocessing
import time

def read_and_write_file(file_path):
    for i in range(100):
        with open(file_path, 'r') as file:
            content = file.read()
        with open(file_path, 'w') as file:
            file.write(content)

file_paths = ['test0.txt', 'test1.txt', 'test2.txt', 'test3.txt']

start_time = time.time()

processes = []
for file in file_paths:
    process = multiprocessing.Process(target=read_and_write_file, args=(file,))
    processes.append(process)
    process.start()

for process in processes:
    process.join()

end_time = time.time

print((end_time - start_time) * 1000)
