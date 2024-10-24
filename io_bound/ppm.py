import pp
import time

def read_and_write_file(file_path):
    for i in range(100):
        with open(file_path, 'r') as file:
            content = file.read()
        with open(file_path, 'w') as file:
            file.write(content)

file_paths = ['test0.txt', 'test1.txt', 'test2.txt', 'test3.txt']

start_time = time.time()

ppserver = pp.Server()

jobs = [ppserver.submit(read_and_write_file, (file,), ()) for file in file_paths]

for job in jobs:
    job()

end_time = time.time

print((end_time - start_time) * 1000)

ppserver.destroy()
