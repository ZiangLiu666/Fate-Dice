import threading
import time

def read_and_write_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        file.close()
    with open(file_path + '.out.txt', 'w') as file:
        file.write(content)
        file.close()

file_paths = ['test0.txt', 'test1.txt', 'test2.txt', 'test3.txt']

threads = []
for file in file_paths:
    thread = threading.Thread(target=read_and_write_file, args=(file,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
