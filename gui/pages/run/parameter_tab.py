from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QPushButton,
    QLabel,
)

from .run_page_tab import RunPageTab
from gui.model.parameter import MultiParameter, OptionalParameter, Parameter
from gui.model.run_record import RunRecord
from gui.components import (
    VBoxLayout,
    HBoxLayout
)
from gui.components.parameter import ParameterForm
from gui.components.navigation_buttons_holder import NavigationButtonsHolder
from gui.style import constants


class ParameterTab(RunPageTab):
    """
    A tab to input parameters for the run, and to 
    navigate to the next step if the parameters are valid.
    """
    navigate_back = Signal()
    navigate_next = Signal()

    def __init__(self, run_record: RunRecord):
        self._run_record = run_record
        self._section_validity_hints = False
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("parameter_input_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        header_widget = QWidget()
        header_layout = HBoxLayout(header_widget)
        title_label = QLabel("Parameter Input")
        title_label.setProperty("title", "true")

        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        self._all_expanded = False
        self._toggle_all_button = QPushButton("Expand All")
        self._toggle_all_button.setObjectName("toggle_all_button")
        self._toggle_all_button.clicked.connect(self._toggle_all_sections)
        header_layout.addWidget(self._toggle_all_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(header_widget)

        self._parameter_form = ParameterForm(self._run_record, editable=True)
        self._parameter_form.setObjectName("parameter_form")

        parameter_form_scroll = QScrollArea()
        parameter_form_scroll.setObjectName("parameter_form_scroll")
        parameter_form_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        parameter_form_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        parameter_form_scroll.setWidgetResizable(True)
        parameter_form_scroll.setWidget(self._parameter_form)
        layout.addWidget(parameter_form_scroll)

        self._validity_label = QLabel("")
        self._validity_label.setObjectName("validity_label")
        layout.addWidget(self._validity_label)

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.navigate_back.emit)
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(self._next_button_clicked)

        self.update_next_button_state()
        # TODO: make this just connect to a signal on the parameter group list
        self._run_record.run_id_parameter.value_changed.connect(
            self._on_parameter_changed
        )
        for group in self._run_record.parameter_groups:
            for parameter in group.parameters:
                self._connect_parameter_to_update_next_button_state(parameter)
                
        return NavigationButtonsHolder(left_button=self.back_button, right_button=self.next_button)

    def refresh(self) -> None:
        self.reset_touched_section_validity()
        self.update_next_button_state()

    def reset(self) -> None:
        self.reset_touched_section_validity()
        self.update_next_button_state()

    def _connect_parameter_to_update_next_button_state(self, parameter: Parameter) -> None:
        """
        Helper function to connect `value_changed` to `update_next_button_state` on all parameter types.
        """
        if isinstance(parameter, MultiParameter):
            for child in parameter.parameters:
                self._connect_parameter_to_update_next_button_state(child)
        elif isinstance(parameter, OptionalParameter):
            parameter.value_changed.connect(self._on_parameter_changed)
            self._connect_parameter_to_update_next_button_state(parameter.parameter)
        else:
            parameter.value_changed.connect(self._on_parameter_changed)

    def update_next_button_state(self) -> None:
        """
        Helper function to display the error that makes the next_button inactive
        """
        valid = self._run_record.valid
        if valid:
            self._validity_label.setText("")
        else:
            invalid_params = []
            for group in self._run_record.parameter_groups:
                for parameter in group.parameters:
                    if isinstance(parameter, MultiParameter):
                        for child_parameter in parameter.parameters:
                            if not child_parameter.valid and child_parameter.enabled:
                                invalid_params.append(child_parameter.name)
                    else:
                        if not parameter.valid and parameter.enabled:
                            invalid_params.append(parameter.name)
            self._validity_label.setText(
                "Cannot continue. Invalid parameters:" + "".join(f"  - {name}" for name in invalid_params)
            )

    def _next_button_clicked(self) -> None:
        """
        Helper function that decides next buttons function based on parameter validity
        """
        valid = self._run_record.valid
        if valid:
            self._section_validity_hints = False
            self._parameter_form.clear_validity_hints()
            self.navigate_next.emit()
        else:
            self._section_validity_hints = True
            self._parameter_form.update_validity_hints()
            self._parameter_form.touch_all()

    def reset_touched_section_validity(self) -> None:
        """
        Helper function to make touched false for all parameters and validity hints false for all sections
        """
        self._section_validity_hints = False
        self._parameter_form.untouch_all()
        self._parameter_form.clear_validity_hints()

    def _on_parameter_changed(self) -> None:
        """
        Update section borders if validity section hints are active
        """
        self.update_next_button_state()
        if self._section_validity_hints:
            self._parameter_form.update_active_hints()

    def _toggle_all_sections(self) -> None:
        self._all_expanded = not self._all_expanded
        for section in self._parameter_form._parameter_form_sections:
            section._collapsible.collapsed = not self._all_expanded
        if self._all_expanded:
            self._toggle_all_button.setText("Collapse All")
        else:
            self._toggle_all_button.setText("Expand All")