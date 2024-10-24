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
    """The name of the experiment."""
    name: str = "new_runner_experiment"

    """The path in which Experiment Runner will create a folder with the name `self.name`, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path: Path = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use `OperationType.AUTO`."""
    operation_type: OperationType = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms: int = 1000

    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
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
        self.run_table_model = None  # Initialized later

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        technique_factor = FactorModel("technique", ['multithreads', 'multiprocesses', 'ppm', 'mpi'])
        self.run_table_model = RunTableModel(
            factors=[technique_factor],
            repetitions=30,
            data_columns=['total_energy', 'execution_time', 'cpu_user_time', 'cpu_system_time', 'cpu_iowait_time',
                          'mem_usage']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        pass

    def before_run(self) -> None:
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""

        time.sleep(15)  # cooldown period

    def start_run(self, context: RunnerContext) -> None:
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""

        if context.run_variation['technique'] == 'mpi':
            target_file = 'mpi.py'
            self.target = subprocess.Popen(['mpirun', '-np', '4', 'python3', target_file],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR,
                                           )
        else:
            target_file = context.run_variation['technique'] + '.py'
            self.target = subprocess.Popen(['python3', target_file],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR,
                                           )

    def start_measurement(self, context: RunnerContext) -> None:
        """Perform any activity required for starting measurements."""

        if context.run_variation['technique'] != 'multithreads':
            while len(get_all_child_pids(self.target.pid)) != 4:
                time.sleep(0.2)
        self.pids = get_all_child_pids(self.target.pid)
        self.pids.append(self.target.pid)
        print("PIDs: ", self.pids)
        self.profilers = []

        for pid in self.pids:
            profiler_cmd = f'powerjoular -l -p {pid} -f {context.run_dir / "powerjoular.csv"}'
            profiler = subprocess.Popen(shlex.split(profiler_cmd))
            self.profilers.append(profiler)

        self.cpumonitor = subprocess.Popen(['python3', 'cpumonitor.py'] + [str(pid) for pid in self.pids],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR,
                                           )

        self.memmonitor = subprocess.Popen(['python3', 'memmonitor.py'] + [str(pid) for pid in self.pids],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR,
                                           )

    def interact(self, context: RunnerContext) -> None:
        """Perform any interaction with the running target system here, or block here until the target finishes."""

        self.target.wait()

    def stop_measurement(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping measurements."""

        self.cpumonitor.wait()
        self.memmonitor.wait()
        for profiler in self.profilers:
            os.kill(profiler.pid, signal.SIGINT)  # graceful shutdown of powerjoular
            profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""

        pass

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process any measurement data here.
        You can also store the raw measurement data under `context.run_dir`
        Returns a dictionary with keys `self.run_table_model.data_columns` and their values populated"""

        total_energy = 0
        for pid in self.pids:
            df = pd.read_csv(context.run_dir / f"powerjoular.csv-{pid}.csv")
            total_energy += round(df['CPU Power'].sum(), 3)
        execution_time = self.target.stdout.readline().decode('ascii').strip()
        cpu_user_time = self.cpumonitor.stdout.readline().decode('ascii').strip()
        cpu_system_time = self.cpumonitor.stdout.readline().decode('ascii').strip()
        cpu_iowait_time = self.cpumonitor.stdout.readline().decode('ascii').strip()
        mem_usage = self.memmonitor.stdout.readline().decode('ascii').strip()

        run_data = {
            'total_energy': round(total_energy, 3),
            'execution_time': round(float(execution_time), 2),
            'cpu_user_time': round(float(cpu_user_time), 2),
            'cpu_system_time': round(float(cpu_system_time), 2),
            'cpu_iowait_time': round(float(cpu_iowait_time), 2),
            'mem_usage': round(float(mem_usage), 2)
        }

        return run_data

    def after_experiment(self) -> None:
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""

        pass

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path: Path = None
