import psutil
import time
import sys

def get_process_cpu_info(pid):
    """获取进程的 CPU 使用信息（用户、系统、等待I/O等）。"""
    try:
        proc = psutil.Process(pid)
        cpu_times = proc.cpu_times()  # 获取进程的CPU时间
        return {
            "user": cpu_times.user,    # 用户态CPU时间
            "system": cpu_times.system,  # 内核态CPU时间
            "iowait": getattr(cpu_times, 'iowait', 0)  # 一些系统不支持 iowait
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def monitor_processes(pids):
    """监控多个进程的CPU使用情况，直到它们结束。"""
    cpu_records = {pid: [] for pid in pids}  # 记录每个进程的CPU使用情况

    while pids:
        for pid in pids[:]:
            cpu_info = get_process_cpu_info(pid)
            if cpu_info is None:
                print(f"Process {pid} has finished.")
                pids.remove(pid)  # 进程已结束，移出PID列表
            else:
                cpu_records[pid].append(cpu_info)

        time.sleep(1)  # 每秒记录一次数据

    return cpu_records

def calculate_average_cpu_usage(cpu_records):
    """计算各类CPU占用的平均值。"""
    total_cpu_times = {"user": 0, "system": 0, "iowait": 0}
    count = 0

    for pid, records in cpu_records.items():
        for record in records:
            total_cpu_times["user"] += record["user"]
            total_cpu_times["system"] += record["system"]
            total_cpu_times["iowait"] += record["iowait"]
            count += 1

    # 计算平均值
    if count > 0:
        average_cpu_times = {
            "user": total_cpu_times["user"] / count,
            "system": total_cpu_times["system"] / count,
            "iowait": total_cpu_times["iowait"] / count
        }
    else:
        average_cpu_times = {"user": 0, "system": 0, "iowait": 0}

    return average_cpu_times

if __name__ == "__main__":
    # 从命令行获取进程ID
    if len(sys.argv) < 2:
        print("Usage: python monitor_cpu.py <pid1> <pid2> ...")
        sys.exit(1)

    # 将传入的进程ID转换为整数
    pids = [int(pid) for pid in sys.argv[1:]]

    # 监控进程的CPU使用情况
    cpu_records = monitor_processes(pids)

    # 计算并打印平均CPU使用情况
    average_cpu_times = calculate_average_cpu_usage(cpu_records)
    print("Average CPU usage:")
    print(f"User: {average_cpu_times['user']} seconds")
    print(f"System: {average_cpu_times['system']} seconds")
    print(f"IOWait: {average_cpu_times['iowait']} seconds")
