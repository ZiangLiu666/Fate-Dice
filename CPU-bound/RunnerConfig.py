from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

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
    name: str = "cpu_bound_experiment"
    results_output_path: Path = ROOT_DIR / 'experiments'
    operation_type: OperationType = OperationType.AUTO
    time_between_runs_in_ms: int = 1000

    def __init__(self):
        """Executes immediately after program start, on config load"""
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
        self.run_table_model = None
        output.console_log("Custom config loaded for CPU-bound experiments")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here."""
        technique_factor = FactorModel("technique", ['multithreads', 'multiprocesses', 'ppm', 'mpi'])
        self.run_table_model = RunTableModel(
            factors=[technique_factor],
            repetitions=1,
            data_columns=['total_energy', 'execution_time']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        pass

    def before_run(self) -> None:
        pass

    def start_run(self, context: RunnerContext) -> None:
        """Start different techniques based on the context."""
        target_file = context.run_variation['technique'] + '.py'
        if context.run_variation['technique'] == 'mpi':
            self.target = subprocess.Popen(['mpirun', '-np', '4', 'python3', target_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR)
        else:
            self.target = subprocess.Popen(['python3', target_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR)

    def start_measurement(self, context: RunnerContext) -> None:
        """Initiate measurements for the current run."""
        self.pids = get_all_child_pids(self.target.pid)
        self.pids.append(self.target.pid)
        output.console_log("PIDs: " + ", ".join(map(str, self.pids)))
        self.profilers = []
        for pid in self.pids:
            profiler_cmd = f'powerjoular -l -p {pid} -f {context.run_dir / "powerjoular.csv"}'
            profiler = subprocess.Popen(shlex.split(profiler_cmd))
            self.profilers.append(profiler)

    def interact(self, context: RunnerContext) -> None:
        """Wait for the target to complete its task."""
        self.target.wait()

    def stop_measurement(self, context: RunnerContext) -> None:
        """Stop all profilers after the run completes."""
        for profiler in self.profilers:
            os.kill(profiler.pid, signal.SIGINT)  # gracefully shutdown
            profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        pass


    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Gather and parse the run data for report generation."""
        total_energy = sum(pd.read_csv(context.run_dir / f"powerjoular.csv-{pid}.csv")['CPU Power'].sum() for pid in self.pids)
        execution_time = float(self.target.stdout.readline().decode('ascii').strip())
        return {'total_energy': round(total_energy, 3), 'execution_time': round(execution_time, 2)}

    def after_experiment(self) -> None:
        pass
