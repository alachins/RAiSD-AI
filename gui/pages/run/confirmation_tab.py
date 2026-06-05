from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QPushButton,
    QLabel,
    QListWidget,
    QAbstractItemView,
)
from PySide6.QtGui import (
    QGuiApplication,
)

from .run_page_tab import RunPageTab
from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.components import (
    HBoxLayout,
    VBoxLayout,
)
from gui.components.parameter import ParameterForm
from gui.components.dialog import ErrorDialog
from gui.components.label import InfoLabel
from gui.execution.command_executor import default_command_builder
from gui.style import constants
from gui.components.navigation_buttons_holder import NavigationButtonsHolder


class ConfirmationTab(RunPageTab):
    """
    A tab to confirm the parameters and operations 
    selected by the user, and to start the run.
    """
    navigate_back = Signal()
    start_run = Signal()

    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        """
        Set up a ConfirmationTab, including a header,
        a section for the commands to be run, and the ParameterForm,
        in locked form.
        """
        widget = QWidget()
        widget.setObjectName("parameter_confirmation_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_TINY,
        )

        # Header
        title_label = QLabel("Parameter Confirmation")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)

        # Parameters
        header_widget = QWidget()
        header_layout = HBoxLayout(header_widget)

        text_label = QLabel("Given parameters:")

        header_layout.addWidget(text_label)
        header_layout.addStretch(1)

        self._all_expanded = False
        self._toggle_all_button = QPushButton("Expand All")
        self._toggle_all_button.setObjectName("toggle_all_button")
        self._toggle_all_button.clicked.connect(self._toggle_all_sections)
        header_layout.addWidget(self._toggle_all_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(header_widget)

        self._parameter_form = ParameterForm(self._run_record, editable=False)
        self._parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(self._parameter_form)
        layout.addWidget(parameter_form_scroll, 1)

        # Commands
        commands_widget = QWidget()
        commands_layout = VBoxLayout(
            commands_widget,
            spacing=constants.GAP_TINY,
        )

        parameters_header = QWidget()
        parameters_header_layout = HBoxLayout(
            parent=parameters_header,
            spacing=constants.GAP_TINY,
        )

        parameters_label = QLabel("Command-line parameters generated from the input:")
        parameters_header_layout.addWidget(parameters_label)

        self.commands_label = InfoLabel("")
        parameters_header_layout.addWidget(self.commands_label, 1)

        copy_button = QPushButton("Copy as commands")
        copy_button.clicked.connect(self._copy_all)
        parameters_header_layout.addWidget(copy_button)
        commands_layout.addWidget(parameters_header)

        self.parameters_view = QListWidget()
        self.parameters_view.setObjectName("parameters_view")
        self.parameters_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.parameters_view.clicked.connect(self._copy_parameters)
        commands_layout.addWidget(self.parameters_view)

        layout.addWidget(commands_widget)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.navigate_back.emit)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self._run_button_clicked)

        return NavigationButtonsHolder(left_button=self.edit_button, right_button=self.run_button)

    def _toggle_all_sections(self) -> None:
        self._all_expanded = not self._all_expanded
        for section in self._parameter_form._parameter_form_sections:
            section._collapsible.collapsed = not self._all_expanded
        if self._all_expanded:
            self._toggle_all_button.setText("Collapse All")
        else:
            self._toggle_all_button.setText("Expand All")

    def refresh(self) -> None:
        self.update_parameters()
        self.update_command()

    def reset(self) -> None:
        self.update_parameters()
        self.update_command()

    def update_parameters(self) -> None:
        """
        Updates the ParameterConfirmationWidget with the parameters from
        the RunResult.
        """
        self.parameters_view.clear()
        if self._run_record.to_cli():
            self.parameters_view.addItems(
                [command for command in self._run_record.to_cli()]
            )
            self.parameters_view.setMaximumHeight(
                self.parameters_view.sizeHintForRow(0) * 
                (self.parameters_view.count()+1)
            )

    def update_command(self) -> None:
        """
        Updates the command info label in the ConfirmationTab.
        """
        
        self.commands_label.text = "Each line of parameters " \
            "will be run with the following command: " \
            f"'{default_command_builder("<parameters>")}'"

    @Slot(int)
    def _copy_parameters(self, index) -> None:
        """
        Copies a singular line of parameters from the QTreeWidget to the clipboard.
        """
        parameters = self.parameters_view.itemFromIndex(index).text()
        cb = QGuiApplication.clipboard()
        cb.setText(parameters)

    @Slot()
    def _copy_all(self) -> None:
        """
        Copies all commands from the run result to the clipboard.
        """
        if self._run_record.to_cli():
            commands = [default_command_builder(params) for params in self._run_record.to_cli()]
            string = '; '.join(commands)
            cb = QGuiApplication.clipboard()
            cb.setText(string)

    @Slot()
    def _run_button_clicked(self) -> None:
        if self._run_record.valid:
            self.start_run.emit()
        else:
            dialog = ErrorDialog(self, "Invalid input", "Input parameters are invalid")
            dialog.exec()
        pass

    @Slot()
    def run_started(self) -> None:
        self.run_button.setEnabled(False)
        self.run_button.setText("Running")

    @Slot()
    def run_ended(self) -> None:
        self.run_button.setEnabled(True)
        self.run_button.setText("Run")

