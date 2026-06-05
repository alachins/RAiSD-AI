from PySide6.QtCore import (
    Qt,
    QProcess,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QTextEdit,
    QMessageBox,
    QSplitter
)

from .run_page_tab import RunPageTab
from gui.model.run_record import RunRecord
from gui.execution.command_executor import CommandExecutor
from gui.components import (
    HBoxLayout,
    VBoxLayout,
)
from gui.components.dialog import ConfirmDialog, ErrorDialog
from gui.components.run import ProcessIndicator, IndicatorState, RunEndStatus
from gui.style import constants
from gui.components.navigation_buttons_holder import NavigationButtonsHolder


class ViewTab(RunPageTab):
    navigate_next = Signal()
    run_started = Signal(int)  # Number of processes
    run_ended = Signal(RunEndStatus)

    def __init__(self, run_record: RunRecord, command_executor: CommandExecutor):
        self._run_record = run_record
        self._command_executor = command_executor

        self.confirm_stop_execution_dialog = None
        self.execution_still_running_dialog = None
        super().__init__()

        self.run_started.connect(self._run_started)
        self.run_ended.connect(self._run_ended)

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("run_view_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        title_label = QLabel("Run View")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop)

        step_widget = QWidget()
        step_widget.setObjectName("step_widget")
        self.step_layout = HBoxLayout(step_widget)
        self.run_indicators: list[ProcessIndicator] = []
        layout.addWidget(step_widget,1)

        self.output_widget = QSplitter()

        self.standard_output_widget = QWidget()
        self.standard_output_widget_layout = VBoxLayout(
            self.standard_output_widget,
            spacing=constants.GAP_TINY
        )

        self.standard_output_label = QLabel("Standard Output:")
        self.standard_output_widget_layout.addWidget(self.standard_output_label)

        self.standard_output = QTextEdit(readOnly=True)
        self.standard_output.setObjectName("execution_output")
        self.standard_output_widget_layout.addWidget(self.standard_output, 1)

        self.output_widget.addWidget(self.standard_output_widget)

        self.error_output_widget = QWidget()
        self.error_output_widget_layout = VBoxLayout(
            self.error_output_widget,
            spacing=constants.GAP_TINY,
        )

        self.error_output_label = QLabel("Error Output:")
        self.error_output_widget_layout.addWidget(self.error_output_label)

        self.error_output = QTextEdit(readOnly=True)
        self.error_output.setObjectName("error_output")
        self.error_output_widget_layout.addWidget(self.error_output, 1)

        self.output_widget.addWidget(self.error_output_widget)

        self.output_widget.setVisible(False)

        layout.addWidget(self.output_widget,1)

        self._command_executor.output.connect(self._command_executor_output)
        self._command_executor.err_output.connect(self._command_executor_err_output)
        self._command_executor.execution_started.connect(self._execution_started)
        self._command_executor.execution_finished.connect(self._execution_finished)
        self._command_executor.execution_stopped.connect(self._execution_stopped)
        self._command_executor.execution_failed.connect(self._execution_failed)
        # process_started and process_finished are connected to the indicator widgets
        self._command_executor.process_failed.connect(self._process_failed)
        self._command_executor.process_stopped.connect(self._process_stopped)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.stop_run_button = QPushButton("Stop Run")
        self.stop_run_button.setEnabled(False)
        self.stop_run_button.setProperty("highlight", "false")
        self.stop_run_button.clicked.connect(self._stop_run_button_clicked)

        self.toggle_console_button = QPushButton("Toggle Console")
        self.toggle_console_button.setEnabled(True)
        self.toggle_console_button.clicked.connect(self._toggle_console_button_clicked)

        self.results_button = QPushButton("Results")
        self.results_button.setEnabled(False)
        self.results_button.setProperty("highlight", "false")
        self.results_button.clicked.connect(self.navigate_next.emit)

        return NavigationButtonsHolder(left_button=self.stop_run_button, middle_button=self.toggle_console_button, right_button=self.results_button)

    def refresh(self) -> None:
        pass

    def reset(self) -> None:
        self.clear_outputs()
        self.run_indicators = []

    def _stop_run_button_clicked(self) -> None:
        self._stop_execution()

    def _toggle_console_button_clicked(self) -> None:
        console_visible = not self.output_widget.isHidden()
        if console_visible:
            self.output_widget.hide()
            new_size = 160
            new_stretch = 1
        else:
            self.output_widget.show()
            new_size = 80
            new_stretch = 0

        layout = self.output_widget.parent().layout() # type: ignore
        step_widget_index = 1
        layout.setStretch(step_widget_index, new_stretch)

        for indicator in self.run_indicators:
            indicator.set_indicator_size(new_size)

    # methods
    @Slot()
    def start_run(self):
        self.clear_outputs()
        self._start_execution()

    @Slot(int)
    def _run_started(self, number_of_processes: int) -> None:
        self.results_button.setEnabled(False)
        self.results_button.setProperty("highlight", "false")
        self.results_button.style().unpolish(self.results_button)
        self.results_button.style().polish(self.results_button)

        self.setup_execution_indicators(number_of_processes)
        self.stop_run_button.setEnabled(True)

        self.stop_run_button.setProperty("highlight", "true")
        self.stop_run_button.style().unpolish(self.stop_run_button)
        self.stop_run_button.style().polish(self.stop_run_button)

    @Slot()
    def _run_ended(self) -> None:
        """
        Update the execution buttons and close an open confirm dialog.
        """
        self.results_button.setEnabled(True)
        self.results_button.setProperty("highlight", "true")
        self.results_button.style().unpolish(self.results_button)
        self.results_button.style().polish(self.results_button)
        self.stop_run_button.setEnabled(False)
        self.stop_run_button.setProperty("highlight", "false")
        self.stop_run_button.style().unpolish(self.stop_run_button)
        self.stop_run_button.style().polish(self.stop_run_button)
        if self.confirm_stop_execution_dialog is not None:
            self.confirm_stop_execution_dialog.close()
        if self.execution_still_running_dialog is not None:
            self.execution_still_running_dialog.close()

    def _start_execution(self):
        commands = self._run_record.to_cli()
        try:
            self._command_executor.start_execution(commands)
        except Exception:
            self.execution_still_running_dialog = ErrorDialog(self, "Execution still running", "A process is still running, try again later.")
            self.execution_still_running_dialog.exec()

    @Slot()
    def _stop_execution(self):
        """
        Stop the current execution after confirmation.
        """
        self.confirm_stop_execution_dialog = ConfirmDialog(self, "Stop Execution", "You are about to stop the current execution. Are you sure?")
        button = self.confirm_stop_execution_dialog.exec()
        if button == QMessageBox.StandardButton.Yes:
            self._command_executor.stop_execution()

    @Slot(str)
    def _command_executor_output(self, output: str) -> None:
        """
        Append the output from the command_executor to execution_output.
        """
        self.standard_output.append(output)

    @Slot(str)
    def _command_executor_err_output(self, output: str) -> None:
        """
        Append the error output from the command_executor to error_output.
        """
        self.error_output.append(output)

    def setup_execution_indicators(self, number_of_processes: int) -> None:
        """
        Set the execution indicators.

        reset current ones and add more or hide when needed.
        """
        operation_ids = self._run_record.selected_operation_tree.get_operation_ids()
        number_of_indicators = len(self.run_indicators)
        size = 160 if self.output_widget.isHidden() else 80

        for idx in range(max([number_of_indicators, number_of_processes])):
            if idx < number_of_indicators:
                indicator = self.run_indicators[idx]
                if idx < number_of_processes:
                    indicator.text = operation_ids[idx]
                    indicator.state = IndicatorState.PENDING
                    indicator.set_indicator_size(size)
                    indicator.setVisible(True)
                elif idx >= number_of_processes:
                    self.run_indicators[idx].setVisible(False)
            else:
                self.add_indicator_widget(idx, operation_ids[idx])

            

    def add_indicator_widget(self, index: int, text: str) -> None:
        """
        Add an indicator widget to self.step_layout.
        """
        size = 160 if self.output_widget.isHidden() else 80
        indicator = ProcessIndicator(text=text, size=size)
        self._command_executor.process_started.connect(lambda idx=index: self._process_started(idx))
        self._command_executor.process_finished.connect(lambda idx=index: self._process_finished(idx))
        self.step_layout.addWidget(indicator)
        self.run_indicators.append(indicator)

    def set_execution_view_indicator(self, index: int, state: IndicatorState) -> None:
        """
        Set the indicator to the given state.

        :param index: the index of the indicator
        :type index: int

        :param state: the new state of the indicator
        :type state: str
        """
        self.run_indicators[index].state = state

    def clear_outputs(self) -> None:
        """
        Clear the output fields.
        """
        self.standard_output.clear()
        self.error_output.clear()

    # SLOTS
    @Slot(int)
    def _execution_started(self, number_of_processes: int) -> None:
        """
        Handle CommandExecutor.execution_started.
        """
        print("Execution started")
        self.run_started.emit(number_of_processes)

    @Slot()
    def _execution_finished(self) -> None:
        """
        Handle CommandExecutor.execution_finshed.
        """
        print("Execution finished")
        self.run_ended.emit(RunEndStatus.SUCCESS)

    @Slot(int, QProcess.ProcessError)
    def _execution_failed(self, exit_code: int, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.execution_failed.
        """
        print(f"Execution failed with exit code '{exit_code}'")

        self.run_ended.emit(RunEndStatus.FAILED)        

        if process_error is None: # otherwise _process_failed will show an error dialog:
            self.standard_output.append(f"Execution failed with exit code '{exit_code}'")
            self.execution_error_dialog = ErrorDialog(self, f"Execution Failed ({exit_code})", f"Execution failed with exit code '{exit_code}'")
            self.execution_error_dialog.exec()
    
    @Slot()
    def _execution_stopped(self) -> None:
        """
        Handle CommandExecutor.execution_stopped.
        """
        print("Execution stopped.")
        self.run_ended.emit(RunEndStatus.STOPPED)

    @Slot(int)
    def _process_started(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_started.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.RUNNING)
    @Slot(int)
    def _process_finished(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_finished.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.FINISHED)

    @Slot(int, QProcess.ProcessError)
    def _process_failed(self, process_index: int, process_error: QProcess.ProcessError) -> None:
        """
        Handle CommandExecutor.process_failed.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.FAILED)

        if process_error is not None:
            print(f"Process '{process_index}' failed with process error '{process_error}'")
            self.standard_output.append(f"Process '{process_index}' failed with process error '{process_error}'")
            process_error_dialog = ErrorDialog(self, f"Process Failed ({process_error})", f"Process '{process_index}' failed with process error '{process_error}'")
            process_error_dialog.exec()

    @Slot(int)
    def _process_stopped(self, process_index: int) -> None:
        """
        Handle CommandExecutor.process_stopped.
        """
        self.set_execution_view_indicator(process_index, IndicatorState.STOPPED)
