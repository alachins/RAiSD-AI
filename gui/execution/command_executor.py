import queue
from collections.abc import (
    Callable,
)

from PySide6.QtCore import (
        QObject, 
        QProcess, 
        Signal, 
        Slot,
        QDir,
)

from gui.model.run_record import RunRecord
from gui.model.settings import app_settings

def default_command_builder(parameters: str) -> str:
        """
        Builds a command using the given parameters.

        :param parameters: the parameters to use
        :type parameters: str
        """
        return (
            f"{app_settings.environment_manager_name} run "
            f"-n {app_settings.environment_name} "
            f"{app_settings.executable_file_path.absoluteFilePath()} {parameters}"
        )


class CommandExecutor(QObject):
    """
    A class that manages the execution of shell commands in QProcesses.
        
    Use `start_execution` to start the execution.
    Use `stop_execution` to stop the execution.
    """

    output = Signal(str)                            # line of stdout output
    err_output = Signal(str)                        # line of stderr output
    execution_started = Signal(int)                 # number of processes to run
    execution_finished = Signal()   
    execution_failed = Signal(int, QProcess.ProcessError)   # exit_code, process_error
    execution_stopped = Signal()
    process_started = Signal(int)                   # process_index
    process_finished = Signal(int)                  # process_index
    process_failed = Signal(int, QProcess.ProcessError)     # process_index, process_error
    process_stopped = Signal(int)                   # process_index

    def __init__(self, run_record: RunRecord, command_builder: Callable[[str], str] | None = None):
        """
        Initialize a `CommandExecutor` object.
        """
        super().__init__()
        self.run_record = run_record
        self.command_builder = command_builder or default_command_builder

        self._process = QProcess()
        self._process.started.connect(self._process_started)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.readyReadStandardError.connect(self._read_error)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._error_occurred)
        
        self._commands = []
        self._command_queue = queue.Queue()

    @Slot(list)
    def start_execution(self, commands:list[str]=[]) -> None:
        """
        Starts exectution of a list of commands. Puts all the commands
        in the command queue and starts the first process.

        :param commands: the list of commands to be executed
        :type command: list[str]
        """
        if (not self._command_queue.empty or
            self._process.state() == QProcess.ProcessState.Starting or 
            self._process.state() == QProcess.ProcessState.Running):
            raise Exception("Execution is still running")
        
        self.execution_started.emit(len(commands))
        
        run_id = self.run_record.run_id
        if not app_settings.workspace_path.exists(run_id):
            if not app_settings.workspace_path.mkdir(run_id):
                raise RuntimeError(f"Creating run folder: '{run_id}' failed.")

        self.run_folder = QDir(app_settings.workspace_path)
        if not self.run_folder.cd(run_id):
            raise RuntimeError(f"Failed to move to run folder: '{self.run_folder.absolutePath()}' + '{run_id}'.")

        self._commands = commands
        self._command_queue = queue.Queue()
        for command in self._commands:
            self._command_queue.put(command)
        self._next_process()   

    @Slot()
    def stop_execution(self) -> None:
        """
        Stops the execution of the current process.
        """
        self._stop_process()

    @Slot()
    def _next_process(self) -> None:
        """
        Starts the next process with the next command from the queue.

        If the queue is empty then the `execution_finished` signal is emitted.
        """
        try:
            command = self._command_queue.get(block=False)
            self._start_process(command)
        except queue.Empty:
            self.execution_finished.emit()

    @Slot()
    def _start_process(self, command:str) -> None:
        """
        Starts a process with the given command.

        :param command: the command to be executed in the process
        :type command: str
        """
        print(f"Starting process in folder:{self.run_folder.absolutePath()}")
        self._process.setWorkingDirectory(self.run_folder.absolutePath())
        self._process.setProgram("bash")

        full_command = self.command_builder(command)
        self._process.setArguments(["-c", full_command])
        self._process.start()

    @Slot()
    def _stop_process(self) -> None:
        """
        Stops the current running process.
        """
        if self._process.state() == QProcess.ProcessState.Running or self._process.state() == QProcess.ProcessState.Starting:
            self._process.terminate()
            if not self._process.waitForFinished(2000):
                self._process.kill()

    @Slot()
    def _process_started(self) -> None:
        """
        Emits `process_started` with the process_index.
        """
        self.process_started.emit(self.get_process_index())

    @Slot()
    def _error_occurred(self, process_error:QProcess.ProcessError) -> None:
        """
        Emits `error_occurred` with the error message.
        """
        self.process_failed.emit(self.get_process_index(), process_error)
        self.execution_failed.emit(1, process_error) # general error exit code + process_error

    @Slot()
    def _process_finished(self, exit_code:int, exit_status:QProcess.ExitStatus) -> None:
        """
        Starts the next process and signals the completion of the previous process
        or signals the end of the execution.

        If the process finished with exit code 9 or 15, `execution_stopped` is emitted.
        Otherwise `execution_failed` is emitted with the exit code of the process.
        """
        print(f"PROCESS FINISHED: ({exit_code}.{exit_status})")
        if exit_status is QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.process_finished.emit(self.get_process_index())
            self._next_process()
        else:
            if exit_code == 4 or exit_code == 252 or exit_code == 9 or exit_code == 15:
                self.process_stopped.emit(self.get_process_index())
                self.execution_stopped.emit()
            else:
                self.process_failed.emit(self.get_process_index(), None)
                self.execution_failed.emit(exit_code, None)

    @Slot()
    def _read_output(self) -> None:
        """
        Reads the stdout of the process and emits the data.
        """
        data = bytes(self._process.readAllStandardOutput().data()).decode(errors="ignore")
        self.output.emit(data.strip())
        print(f"stdout:{data.strip()}")
        # TODO: filter output for substeps (self.sub_step_finished)

    @Slot()
    def _read_error(self) -> None:
        """
        Reads the stderr of the process and compiles the error message.
        """
        data = bytes(self._process.readAllStandardError().data()).decode(errors="ignore")
        self.err_output.emit(data.strip())
        print(f"stderr:{data.strip()}")

    def get_process_index(self) -> int:
        """
        The index of the current process.
        """
        process_index = len(self._commands) - self._command_queue.qsize() - 1
        return process_index
