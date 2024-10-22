import psutil
import time
import sys

def get_process_cpu_times(pids):
    """获取多个进程的CPU时间，包括用户态、系统态和I/O等待时间的总和"""
    total_user_time = 0.0
    total_system_time = 0.0
    total_iowait_time = 0.0

    for pid in pids:
        try:
            proc = psutil.Process(pid)
            cpu_times = proc.cpu_times()  # 获取进程的CPU时间
            total_user_time += cpu_times.user
            total_system_time += cpu_times.system
            total_iowait_time += cpu_times.io_wait
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # 进程可能已经结束，忽略这些异常
    
    return total_user_time, total_system_time, total_iowait_time

def monitor_processes(pids):
    """监控多个进程的CPU使用情况，直到它们结束"""
    total_user_time_records = []
    total_system_time_records = []
    total_iowait_time_records = []

    while pids:
        # 获取所有进程的用户态、系统态和等待I/O的CPU时间总和
        total_user_time, total_system_time, total_iowait_time = get_process_cpu_times(pids)

        # 记录每秒的CPU时间总和
        total_user_time_records.append(total_user_time)
        total_system_time_records.append(total_system_time)
        total_iowait_time_records.append(total_iowait_time)

        # 移除已经结束的进程
        for pid in pids[:]:
            if not psutil.pid_exists(pid):
                pids.remove(pid)

        time.sleep(1)  # 每秒采样一次

    return total_user_time_records, total_system_time_records, total_iowait_time_records

def calculate_average_cpu_usage(user_records, system_records, iowait_records):
    """计算各类CPU占用的时间平均值"""
    count = len(user_records)

    if count > 0:
        avg_user_time = sum(user_records) / count
        avg_system_time = sum(system_records) / count
        avg_iowait_time = sum(iowait_records) / count
    else:
        avg_user_time = avg_system_time = avg_iowait_time = 0

    return avg_user_time, avg_system_time, avg_iowait_time

if __name__ == "__main__":
    # 从命令行获取进程ID
    if len(sys.argv) < 2:
        print("Usage: python monitor_cpu.py <pid1> <pid2> ...")
        sys.exit(1)

    # 将传入的进程ID转换为整数
    pids = [int(pid) for pid in sys.argv[1:]]

    # 监控进程的CPU使用情况，直到所有进程结束
    user_records, system_records, iowait_records = monitor_processes(pids)

    # 计算并打印平均CPU使用情况
    avg_user_time, avg_system_time, avg_iowait_time = calculate_average_cpu_usage(user_records, system_records, iowait_records)

    print("Average CPU usage (in seconds):")
    print(f"User: {avg_user_time:.4f} seconds")
    print(f"System: {avg_system_time:.4f} seconds")
    print(f"IOWait: {avg_iowait_time:.4f} seconds")
