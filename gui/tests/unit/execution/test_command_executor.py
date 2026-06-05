import pytest
import re

from PySide6.QtCore import (
    Slot, 
    QProcess, 
    QDir,
    QFileInfo
)

from gui.model.settings import Settings, app_settings
from gui.execution.command_executor import CommandExecutor, default_command_builder


def test_default_command_builder(mocker):
    # Arrange
    # Set values
    environment_manager_name = "raise"
    environment_name = "utwente"
    executable_file_path = "/home/raisd/raisdai"

    parameters = "-a -m 10 -f 1 1"
    goal_command = (f"{environment_manager_name} run -n {environment_name} "
                    f"{executable_file_path} {parameters}")

    # Set mock
    environment_manager_name_mock = mocker.PropertyMock(
        return_value=environment_manager_name
    )
    environment_name_mock = mocker.PropertyMock(
        return_value=environment_name
    )
    executable_file_path_mock = mocker.PropertyMock(
        return_value=QFileInfo(executable_file_path)
    )

    # Apply mock
    mocker.patch.object(
        Settings, 
        'environment_manager_name', 
        environment_manager_name_mock
    )
    mocker.patch.object(
        Settings,
        'environment_name',
        environment_name_mock
    )
    mocker.patch.object(
        Settings,
        'executable_file_path',
        executable_file_path_mock
    )

    # Act
    command = default_command_builder(parameters=parameters)

    # Assert
    assert command
    assert command == goal_command

class TestCommandExecutor:
    """Tests for CommandExecutor class."""

    @pytest.fixture(autouse=True)
    def set_command_executor(self, tmp_path, qtbot, mocker):
        # Create a real temp dir
        qdir = QDir(str(tmp_path))

        # Patch app_settings.workspace_path to return the real QDir        
        workspace_path_mock = mocker.PropertyMock(return_value=qdir)
        mocker.patch.object(Settings, 'workspace_path', workspace_path_mock)

        mock_run_record = mocker.Mock()
        mock_run_record.run_id = "test-command-executor"

        self.command_executor = CommandExecutor(mock_run_record)
        self.command_executor.command_builder = (lambda cmd: cmd)
        self.command_executor.output.connect(self.output_signal)
        self.command_executor.err_output.connect(self.err_output_signal)
        self.command_executor.execution_started.connect(self.execution_started_signal)
        self.command_executor.execution_finished.connect(self.execution_finished_signal)
        self.command_executor.execution_failed.connect(self.execution_failed_signal)
        self.command_executor.execution_stopped.connect(self.execution_stopped_signal)
        self.command_executor.process_started.connect(self.process_started_signal)
        self.command_executor.process_finished.connect(self.process_finished_signal)
        self.command_executor.process_failed.connect(self.process_failed_signal)
        self.command_executor.process_stopped.connect(self.process_stopped_signal)

        self.output = ""
        self.err_output = ""
        self.execution_started = []
        self.execution_finished = []
        self.execution_failed = []
        self.execution_stopped = []
        self.process_started = []
        self.process_finished = []
        self.process_failed = []
        self.process_stopped = []

        yield   # everything after this will be run after the test methods.

        print("teardown")
        self.command_executor.stop_execution()
        self.command_executor._process.waitForFinished(3000)

    # ---------- test slots(+ signals) ----------
    # test start_execution / execution_started
    def test_start_execution_emit_execution_started_empty(self, qtbot):
        # arrange
        commands = []

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 0
        assert len(self.process_finished) == 0
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0

    def test_start_execution_emit_execution_started_commands(self, qtbot):
        # arrange
        commands = ["echo test1", "echo test2"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 2
        assert self.process_started == [0, 1]
        assert len(self.process_finished) == 2
        assert self.process_finished == [0, 1]
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0

    def test_start_execution_while_running_exception(self):
        # arrange
        commands = ["ping -c 4"]

        # act
        self.command_executor.start_execution(commands)

        # assert
        with pytest.raises(Exception):
            self.command_executor.start_execution(commands)

    # test stop_execution / execution_stopped
    def test_stop_execution(self, qtbot):
        # arrange
        commands = ["exit 15"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)
        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 0
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 1
        assert len(self.process_started) == 1
        assert self.process_started == [0]
        assert len(self.process_finished) == 0
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 1
        assert self.process_stopped == [0]

    # ---------- test signals ----------
    # test execution_finished
    def test_execution_finished(self, qtbot):
        # arrange
        commands = ["echo test1", "echo test2"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 2
        assert self.process_started == [0, 1]
        assert len(self.process_finished) == 2
        assert self.process_finished == [0, 1]
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0

    # test execution_failed / process_failed
    def test_execution_failed_first_command(self, qtbot):
        # arrange
        commands = ["pwd -rt", "echo test1"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 0
        assert len(self.execution_failed) == 1
        assert self.execution_failed[0] != 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 1
        assert self.process_started == [0]
        assert len(self.process_finished) == 0
        assert len(self.process_failed) == 1
        assert self.process_failed == [(0, QProcess.ProcessError.FailedToStart)]
        assert len(self.process_stopped) == 0

    def test_execution_failed_second_command(self, qtbot):
        # arrange
        commands = ["echo test1", "pwd -rt"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 0
        assert len(self.execution_failed) == 1
        assert self.execution_failed[0] != 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 2
        assert self.process_started == [0, 1]
        assert len(self.process_finished) == 1
        assert self.process_finished == [0]
        assert len(self.process_failed) == 1
        assert self.process_failed == [(1, QProcess.ProcessError.FailedToStart)]
        assert len(self.process_stopped) == 0

    # test process_started / process_finished
    def test_process_started_zero_commands(self, qtbot):
        # arrange
        commands = []

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 0
        assert len(self.process_finished) == 0
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0

    def test_process_started_one_commands(self, qtbot):
        # arrange
        commands = ["echo test1"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 1
        assert self.process_started == [0]
        assert len(self.process_finished) == 1
        assert self.process_finished == [0]
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0

    def test_process_started_two_commands(self, qtbot):
        # arrange
        commands = ["echo test1", "echo test2"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert len(self.execution_started) == 1
        assert self.execution_started == [len(commands)]
        assert len(self.execution_finished) == 1
        assert len(self.execution_failed) == 0
        assert len(self.execution_stopped) == 0
        assert len(self.process_started) == 2
        assert self.process_started == [0, 1]
        assert len(self.process_finished) == 2
        assert self.process_finished == [0, 1]
        assert len(self.process_failed) == 0
        assert len(self.process_stopped) == 0        

    # test output
    def test_output(self, qtbot):
        # arrange
        commands = ["echo test1", "echo test2"]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert self.output == "\ntest1\ntest2"
        assert self.err_output == ""

    # test err output
    def test_output_and_err_output(self, qtbot):
        # arrange
        commands = ["echo test1", "pwd -rt", ]

        # act
        self.command_executor.start_execution(commands)
        qtbot.wait(500)

        # assert
        assert self.output == "\ntest1"
        assert re.search(r"invalid option", self.err_output) is not None

    # test killing process
    def test_stop_process_calls_kill_after_timeout(self, qtbot, mocker):
        # arrange
        # Mock the process to return Running state, and make terminate/waitForFinished fail
        mocker.patch.object(self.command_executor._process, 'state',
                            return_value=QProcess.ProcessState.Running)
        mocker.patch.object(self.command_executor._process, 'terminate')
        mocker.patch.object(self.command_executor._process, 'waitForFinished',
                            return_value=False)
        kill_mock = mocker.patch.object(self.command_executor._process, 'kill')

        # act
        self.command_executor._stop_process()

        # assert
        self.command_executor._process.terminate.assert_called_once() # type: ignore
        self.command_executor._process.waitForFinished.assert_called_once_with(2000) # type: ignore
        kill_mock.assert_called_once()

    # Helper methods
    @Slot(str)
    def output_signal(self, output: str) -> None:
        """Helper method to register output signal"""
        self.output += "\n" + output

    @Slot(str)
    def err_output_signal(self, err_output: str) -> None:
        """Helper method to register error output signal"""
        self.err_output += "\n" + err_output

    @Slot(int)
    def execution_started_signal(self, number_of_processes: int) -> None:
        """Helper method to register execution started signal"""
        self.execution_started.append(number_of_processes)

    @Slot()
    def execution_finished_signal(self) -> None:
        self.execution_finished.append(True)

    @Slot(int)
    def execution_failed_signal(self, exit_code: int) -> None:
        self.execution_failed.append(exit_code)

    @Slot()
    def execution_stopped_signal(self) -> None:
        self.execution_stopped.append(True)

    @Slot(int)
    def process_started_signal(self, process_index: int) -> None:
        self.process_started.append(process_index)

    @Slot(int)
    def process_finished_signal(self, process_index: int) -> None:
        self.process_finished.append(process_index)

    @Slot(int, QProcess.ProcessError)
    def process_failed_signal(self, process_index: int, process_error: QProcess.ProcessError) -> None:
        self.process_failed.append((process_index, process_error))

    @Slot(int)
    def process_stopped_signal(self, process_index: int) -> None:
        self.process_stopped.append(process_index)
