from PySide6.QtCore import (
    Signal,
    Slot,
    Qt,
)
from PySide6.QtWidgets import (
    QWidget,
    QStackedLayout,
    QLabel,
)

from ..page import Page
from ..run import (
    RunPageTab,
    OperationTab,
    ParameterTab,
    ConfirmationTab,
    ViewTab,
    ResultsTab,
)
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord
from gui.execution.command_executor import CommandExecutor
from gui.components import (
    HBoxLayout,
    VBoxLayout,
)
from gui.components.run import RunEndStatus
from gui.style import constants


class RunPage(Page):
    """
    The page to display all steps of running the RAiSD-AI-GUI application.
    """
    start_run = Signal()
    run_started = Signal(int)  # number of processes
    run_ended = Signal(RunEndStatus)
    run_saved = Signal(HistoryRecord)

    def __init__(self, run_record: RunRecord, command_executor: CommandExecutor):
        """
        Initialize a `RunPage` object.
        """
        super().__init__()
        self._run_record = run_record
        self._command_executor = command_executor
        self._setup_ui()
        self.run_started.connect(self._handle_run_start)
        self.run_ended.connect(self._handle_run_end)

    def _setup_ui(self):
        """
        Set up the general run page.

        Includes the tab bar and the stacked step widget.
        """
        layout = VBoxLayout(self)

        # Step button bar
        tab_bar = QWidget()
        tab_bar.setObjectName("tab_bar")
        tab_bar_layout = HBoxLayout(
            tab_bar,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_SMALL,
            spacing=constants.GAP_TINY,
        )
        layout.addWidget(tab_bar)
        self._setup_tab_bar(tab_bar_layout)

        # Step stacked widget
        stacked_step_widget = QWidget()
        stacked_step_widget.setContentsMargins(
            constants.GAP_MEDIUM,
            constants.GAP_MEDIUM,
            constants.GAP_MEDIUM,
            constants.GAP_MEDIUM,
        )
        self.stacked_step_widget_layout = QStackedLayout(stacked_step_widget)
        self.stacked_step_widget_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(stacked_step_widget, 1)
        self._setup_stacked_step_widget(self.stacked_step_widget_layout)

        self.label_to_tab: dict[QLabel, RunPageTab] = {
            self.operation_selection_label: self.operation_tab,
            self.parameter_input_label: self.parameter_tab,
            self.parameter_confirmation_label: self.confirmation_tab,
            self.execution_view_label: self.view_tab,
            self.results_label: self.results_tab,
        }

        self._set_active_tab(self.operation_tab)

    def _setup_tab_bar(self, layout: HBoxLayout):
        """
        Set up the tab bar.
        """
        self.operation_selection_label = QLabel("Operation Selection", alignment=Qt.AlignmentFlag.AlignCenter)
        self.operation_selection_label.setObjectName("tab_label")
        layout.addWidget(self.operation_selection_label)

        self.parameter_input_label = QLabel("Parameter Input", alignment=Qt.AlignmentFlag.AlignCenter)
        self.parameter_input_label.setObjectName("tab_label")
        layout.addWidget(self.parameter_input_label)

        self.parameter_confirmation_label = QLabel("Parameter Confirmation", alignment=Qt.AlignmentFlag.AlignCenter)
        self.parameter_confirmation_label.setObjectName("tab_label")
        layout.addWidget(self.parameter_confirmation_label)

        self.execution_view_label = QLabel("Run", alignment=Qt.AlignmentFlag.AlignCenter)
        self.execution_view_label.setObjectName("tab_label")
        layout.addWidget(self.execution_view_label)

        self.results_label = QLabel("Results", alignment=Qt.AlignmentFlag.AlignCenter)
        self.results_label.setObjectName("tab_label")
        layout.addWidget(self.results_label)

    def _setup_stacked_step_widget(self, layout: QStackedLayout):
        """
        Set up the stacked step widget.
        """
        # Operation selection tab
        self.operation_tab = OperationTab(run_record=self._run_record)
        self.operation_tab.navigate_next.connect(self._switch_to_parameter_tab)
        layout.addWidget(self.operation_tab)

        # Parameter input tab
        self.parameter_tab = ParameterTab(run_record=self._run_record)
        self.parameter_tab.navigate_back.connect(self._switch_to_operation_tab)
        self.parameter_tab.navigate_next.connect(self._switch_to_confirmation_tab)
        layout.addWidget(self.parameter_tab)

        # Parameter confirmation tab
        self.confirmation_tab = ConfirmationTab(run_record=self._run_record)
        self.confirmation_tab.navigate_back.connect(self._switch_to_parameter_tab)
        self.confirmation_tab.start_run.connect(self.start_run)
        self.run_started.connect(self.confirmation_tab.run_started)
        self.run_ended.connect(self.confirmation_tab.run_ended)
        layout.addWidget(self.confirmation_tab)

        # Run view tab
        self.view_tab = ViewTab(run_record=self._run_record, command_executor=self._command_executor)
        self.view_tab.navigate_next.connect(self._switch_to_results_tab)
        self.view_tab.run_started.connect(self.run_started)
        self.view_tab.run_ended.connect(self.run_ended)
        self.start_run.connect(self.view_tab.start_run)
        layout.addWidget(self.view_tab)

        # Results tab
        self.results_tab = ResultsTab(run_record=self._run_record)
        self.results_tab.navigate_back.connect(self._switch_to_view_tab)
        self.results_tab.new_run_button.clicked.connect(self._new_run)
        self.results_tab.edit_run_button.clicked.connect(self._switch_to_operation_tab)
        self.run_ended.connect(self.results_tab.run_ended)
        layout.addWidget(self.results_tab)

    def _set_active_tab(self, active_tab: RunPageTab) -> None:
        """
        Update the active tab. 
        Both the button styles and the displayed tab are updated.
        """
        for i, (label, tab) in enumerate(self.label_to_tab.items()):
            if tab == active_tab:
                role = "active"
                tab.refresh()
                self.stacked_step_widget_layout.setCurrentWidget(tab)
            elif i < list(self.label_to_tab.values()).index(active_tab):
                role = "past_step"
            else:
                role = "default"
            label.setProperty("step_role", role)
            label.style().unpolish(label) # Required to apply styling dynamically
            label.style().polish(label)

    # ---------- step button bar switch methods ----------
    @Slot()
    def _switch_to_operation_tab(self) -> None:
        self._set_active_tab(self.operation_tab)

    @Slot()
    def _switch_to_parameter_tab(self) -> None:
        self._set_active_tab(self.parameter_tab)

    @Slot()
    def _switch_to_confirmation_tab(self) -> None:
        self._set_active_tab(self.confirmation_tab)

    @Slot()
    def _switch_to_view_tab(self) -> None:
        self._set_active_tab(self.view_tab)

    @Slot()
    def _switch_to_results_tab(self) -> None:
        self._set_active_tab(self.results_tab)

    # ---------- Handle events ----------
    @Slot()
    def _handle_run_start(self) -> None:
        self._switch_to_view_tab()

    @Slot(RunEndStatus)
    def _handle_run_end(self, run_end_status: RunEndStatus) -> None:
        if run_end_status == RunEndStatus.SUCCESS:
            history_record = self._run_record.to_history_record() 
            history_record.save_to_history()     
            self.run_saved.emit(history_record)
        self._switch_to_results_tab()

    @Slot()
    def _new_run(self) -> None:
        self._run_record.reset()
        self._switch_to_operation_tab()

    def reuse_run(self) -> None:
        self._set_active_tab(self.operation_tab)    
        
    @Slot()
    def reset_page(self) -> None:
        self._run_record.reset()
        for tab in self.label_to_tab.values():
            tab.reset()
        self._set_active_tab(self.operation_tab)

