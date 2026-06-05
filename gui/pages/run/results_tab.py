from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QTimer,
)
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QPushButton,
    QLabel,
)

from .run_page_tab import RunPageTab
from gui.model.run_record import RunRecord
from gui.components import (
    VBoxLayout,
)
from gui.components.label import ErrorLabel, WarningLabel
from gui.components.results import ResultsWidget
from gui.components.navigation_buttons_holder import NavigationButtonsHolder
from gui.components.run import RunEndStatus
from gui.components.utils import set_bool_property
from gui.style import constants


class ResultsTab(RunPageTab):
    """
    A tab to display the results of a run, and to allow the user
    to start a new run or edit the current run.
    """
    navigate_back = Signal()
    new_run = Signal()
    edit_run = Signal()
    
    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("run_results_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        self.title_label = QLabel("Run Results")
        self.title_label.setProperty("title", "true")
        layout.addWidget(self.title_label)

        self.run_failed_label = ErrorLabel(
            "Running RAiSD-AI failed. " \
            "The files shown below may be incomplete. " \
            "Go back to the 'Run' tab to see the error output. " \
            "The results won't be listed in the 'History' page. "
        )
        
        self.run_failed_label.hide()
        layout.addWidget(self.run_failed_label)

        self.run_stopped_label = WarningLabel(
            "RAiSD-AI was manually stopped. " \
            "The files shown below may be incomplete. " \
            "Go back to the 'Run' tab to see the output. " \
            "The results won't be listed in the 'History' page. "
        )
        
        self.run_stopped_label.hide()
        layout.addWidget(self.run_stopped_label)

        self.results_widget = ResultsWidget(self._run_record)

        results_scroll = QScrollArea()
        results_scroll.setObjectName("results_scroll")
        results_scroll.setWidgetResizable(True)
        results_scroll.setWidget(self.results_widget)
        layout.addWidget(results_scroll, 1)
        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.navigate_back_button = QPushButton("Back")
        self.navigate_back_button.clicked.connect(self.navigate_back.emit)
        self.new_run_button = QPushButton("New Run")
        self.new_run_button.clicked.connect(self.new_run.emit)
        self.edit_run_button = QPushButton("Edit Run")
        self.edit_run_button.clicked.connect(self.edit_run.emit)
        self.buttons = [self.navigate_back_button, 
                   self.new_run_button,
                   self.edit_run_button]
        self.enable_buttons(False)

        return NavigationButtonsHolder(
            left_button=self.navigate_back_button, 
            right_button=self.new_run_button, 
            middle_button=self.edit_run_button
        )

    def refresh(self) -> None:
        self.enable_buttons(False)
        QTimer.singleShot(500, lambda: self.enable_buttons(True))

    @Slot(RunEndStatus)
    def run_ended(self, run_end_status: RunEndStatus) -> None:
        match run_end_status:
            case RunEndStatus.SUCCESS:
                self.run_failed_label.hide()
                self.run_stopped_label.hide()
            case RunEndStatus.FAILED:
                self.run_failed_label.show()
                self.run_stopped_label.hide()
            case RunEndStatus.STOPPED:
                self.run_failed_label.hide()
                self.run_stopped_label.show()
        self.results_widget.show_results()

    @Slot(bool)
    def enable_buttons(self, enable) -> None:
        for button in self.buttons:
            button.setEnabled(enable)
            set_bool_property(button, "highlight", enable)
