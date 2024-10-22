import psutil
import time
import sys

# def get_process_memory(pids):
#     """获取给定pids列表中正在运行的进程的内存占用"""
#     total_memory = 0
#     running_pids = []
#     for pid in pids:
#         try:
#             p = psutil.Process(pid)
#             if p.is_running():
#                 mem_info = p.memory_info()
#                 total_memory += mem_info.rss  # 以字节为单位
#                 running_pids.append(pid)
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             # 进程不存在或者访问被拒绝，忽略
#             pass
#     return total_memory, running_pids

def get_pss_memory(pid):
    """获取指定PID的进程的PSS内存总量 单位：字节"""
    pss_memory = 0
    try:
        with open(f"/proc/{pid}/smaps", 'r') as f:
            for line in f:
                if line.startswith("Pss:"):
                    pss_memory += int(line.split()[1])  # PSS大小以KB为单位
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        # 进程不存在或访问被拒绝
        pass
    
    return pss_memory * 1024  # 转换为字节

def get_process_memory(pids):
    """获取给定pids列表中正在运行的进程的PSS内存占用"""
    total_memory = 0
    running_pids = []
    
    for pid in pids:
        pss_memory = get_pss_memory(pid)
        if pss_memory > 0:
            total_memory += pss_memory
            running_pids.append(pid)
    
    return total_memory, running_pids

def monitor_processes(pids):
    """监控给定pids列表中的进程内存使用情况，直到所有进程结束"""
    memory_snapshots = []

    while pids:
        # 获取当前时间的内存总使用量
        total_memory, running_pids = get_process_memory(pids)
        
        # 记录该时刻的内存使用总和
        memory_snapshots.append(total_memory)
        
        # 更新当前活跃的pids
        pids = running_pids
        
        # 等待1秒
        time.sleep(1)

    # 计算平均内存占用
    avg_memory = sum(memory_snapshots) / len(memory_snapshots) if memory_snapshots else 0

    # 返回平均内存占用
    return avg_memory

if __name__ == "__main__":
    # 示例PID列表
    pid_list = [int(pid) for pid in sys.argv[1:]]

    avg_memory_usage = monitor_processes(pid_list)
    print(f"平均内存使用量: {avg_memory_usage / (1024 ** 2):.2f} MB")
    print(avg_memory_usage)
