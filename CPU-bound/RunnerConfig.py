from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath

import subprocess
import time
import signal
import os
import psutil
import shlex
import pandas as pd

def get_all_child_pids(pid):
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    child_pids = [child.pid for child in children]
    return child_pids

class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    name: str = "new_cpu_bound_experiment"
    results_output_path: Path = ROOT_DIR / 'experiments'
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 1000

    def __init__(self):
        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment)
        ])
        self.run_table_model = None  # Initialized later
        output.console_log("CPU-bound custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        technique_factor = FactorModel("technique", ['multithreads', 'multiprocesses', 'ppm', 'mpi'])
        self.run_table_model = RunTableModel(
            factors=[technique_factor],
            repetitions=30,
            data_columns=['total_energy', 'execution_time', 'cpu_user_time', 'cpu_system_time', 'cpu_iowait_time', 'mem_usage']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        pass

    def before_run(self) -> None:
        time.sleep(60)  # Cool down period between runs

    def start_run(self, context: RunnerContext) -> None:
        if context.run_variation['technique'] == 'mpi':
            target_file = 'mpi.py'
            self.target = subprocess.Popen(['mpirun', '-np', '4', 'python3', target_file],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR)
        else:
            target_file = context.run_variation['technique'] + '.py'
            self.target = subprocess.Popen(['python3', target_file],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR)

    def start_measurement(self, context: RunnerContext) -> None:
        if context.run_variation['technique'] != 'multithreads':
            while len(get_all_child_pids(self.target.pid)) != 4:
                time.sleep(0.2)
        self.pids = get_all_child_pids(self.target.pid)
        self.pids.append(self.target.pid)
        print("PIDs: ", self.pids)
        self.profilers = [subprocess.Popen(['powerjoular -l -p {pid} -f {context.run_dir / "powerjoular.csv"}'.format(pid=pid)], shell=True) for pid in self.pids]
        self.cpumonitor = subprocess.Popen(['python3', 'cpumonitor.py'] + [str(pid) for pid in self.pids], stdout=subprocess.PIPE, cwd=self.ROOT_DIR)
        self.memmonitor = subprocess.Popen(['python3', 'memmonitor.py'] + [str(pid) for pid in self.pids], stdout=subprocess.PIPE, cwd=self.ROOT_DIR)

    def interact(self, context: RunnerContext) -> None:
        self.target.wait()

    def stop_measurement(self, context: RunnerContext) -> None:
        self.cpumonitor.wait()
        self.memmonitor.wait()
        for profiler in self.profilers:
            os.kill(profiler.pid, signal.SIGINT)
            profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        pass

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        total_energy = sum(pd.read_csv(context.run_dir / f"powerjoular.csv-{pid}.csv")['CPU Power'].sum() for pid in self.pids)
        run_data = {
            'total_energy': round(total_energy, 3),
            'execution_time': self.target.stdout.readline().strip(),
            'cpu_user_time': self.cpumonitor.stdout.readline().strip(),
            'cpu_system_time': self.cpumonitor.stdout.readline().strip(),
            'cpu_iowait_time': self.cpumonitor.stdout.readline().strip(),
            'mem_usage': self.memmonitor.stdout.readline().strip()
        }
        return run_data

    def after_experiment(self) -> None:
        pass
