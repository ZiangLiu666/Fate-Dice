import subprocess
import psutil

def get_all_child_pids(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    child_pids = [child.pid for child in children]
    return child_pids


process = subprocess.Popen(['python3', 'test.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pids = get_all_child_pids(process.pid)
pids.append(process.pid)
print(process.pid)
print(pids)