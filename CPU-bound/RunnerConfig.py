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
import shlex
import pandas as pd

class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))
    name: str = "cpu_bound_experiment"
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
        self.run_table_model = None  # To be initialized in create_run_table_model
        output.console_log("Custom CPU-bound config loaded")

    def create_run_table_model(self) -> RunTableModel:
        technique_factor = FactorModel("technique", ['multithreads', 'multiprocesses', 'mpi','ppm'])
        self.run_table_model = RunTableModel(
            factors=[technique_factor],
            repetitions=1,
            data_columns=['total_energy', 'execution_time']
        )
        return self.run_table_model

    def before_experiment(self) -> None:
        output.console_log("Preparing to start the CPU-bound experiment.")
        pass

    def before_run(self) -> None:
        output.console_log("Configuring environment before each run.")
        pass

    def start_run(self, context: RunnerContext) -> None:
        if context.run_variation['technique'] == 'mpi':
            target_file = 'mpi.py'
            cmd = ['mpirun', '-np', '4', 'python3', target_file]
        else:
            target_file = f"{context.run_variation['technique']}.py"
            cmd = ['python3', target_file]
        self.target = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.ROOT_DIR
        )

    def start_measurement(self, context: RunnerContext) -> None:
        profiler_cmd = f'powerjoular -l -p {self.target.pid} -f {context.run_dir / "powerjoular.csv"}'
        time.sleep(0.2)  # Allow some runtime before measurement
        self.profiler = subprocess.Popen(shlex.split(profiler_cmd))

    def interact(self, context: RunnerContext) -> None:
        output.console_log("Waiting for the process to complete.")
        self.target.wait()

    def stop_measurement(self, context: RunnerContext) -> None:
        os.kill(self.profiler.pid, signal.SIGINT)
        self.profiler.wait()

    def stop_run(self, context: RunnerContext) -> None:
        output.console_log("Run completed. Cleaning up...")
        pass

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        df = pd.read_csv(context.run_dir / f"powerjoular.csv-{self.target.pid}.csv")
        execution_time = float(self.target.stdout.readline().decode('utf-8').strip())
        run_data = {
            'total_energy': str(round(df['CPU Power'].sum(), 3)),
            'execution_time': str(round(execution_time, 2))
        }
        return run_data

    def after_experiment(self) -> None:
        output.console_log("Experiment completed successfully.")
        pass

    experiment_path: Path = None
