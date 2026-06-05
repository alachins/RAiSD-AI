from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Signal, Slot

from .parameter_widget import ParameterWidget
from gui.model.parameter import ParameterGroup
from gui.components import (
    StylableWidget,
    VBoxLayout,
)
from gui.components.collapsible import Collapsible
from gui.style import constants


class ParameterFormSection(StylableWidget):
    """
    A section of the parameter form.

    Every section corresponds to a `ParameterGroup` object.
    """

    def __init__(
            self,
            parameter_group: ParameterGroup,
            editable: bool
    ) -> None:
        """
        Initialize a `ParameterFormSection` object.

        The method creates a `ParameterWidget` object for each
        parameter in the group by calling the `from_parameter` factory
        method. The widgets are placed in a form layout along with their
        labels.

        :param parameter_group: the parameter group to reference
        :type parameter_group: ParameterGroup
        """
        super().__init__()
        self.setObjectName("parameter_form_section")

        self._parameter_group = parameter_group
        self._parameter_group.enabled_changed.connect(self._parameter_group_enabled_changed)
        self._editable = editable
        self._invalid = False
        self._parameter_widgets: list[ParameterWidget] = []

        # Make parameter widgets
        heading = QLabel(self._parameter_group.name)
        heading.setObjectName("heading")

        row_widget = QWidget()
        row_layout = VBoxLayout(
            row_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_SMALL,
            spacing=constants.GAP_SMALL,
        )
        for parameter in parameter_group:
            widget = ParameterWidget.from_parameter(
                parameter,
                editable=self._editable,
            )
            self._parameter_widgets.append(widget)
            row_layout.addWidget(widget.build_form_row())

        layout = VBoxLayout(
            self,
        )
        self._collapsible = Collapsible(heading, row_widget)
        layout.addWidget(self._collapsible)

        self.setVisible(self._parameter_group.enabled)

    @property
    def parameter_group(self) -> ParameterGroup:
        """
        The ParameterGroup of the ParameterFormSection.
        """
        return self._parameter_group

    @Slot(bool)
    def _parameter_group_enabled_changed(self, new_value: bool) -> None:
        """
        Handle an enabled_changed from the ParameterGroup by setting 
        visibility accordingly.
        
        :new_value param: the new value of enabled of the ParameterGroup
        :new_value type: bool
        """
        self.setVisible(new_value)

    def touch_all(self) -> None:
        for widget in self._parameter_widgets:
            widget.touched = True

    def untouch_all(self) -> None:
        for widget in self._parameter_widgets:
            widget.touched = False

    @property
    def invalid(self) -> bool:
        """
        Get invalid property on the parameter_form_section
        """
        return self._invalid

    @invalid.setter
    def invalid(self, value: bool) -> None:
        """
        Set invalid property on the parameter_form_section
        """
        self._invalid = value
        self.setProperty("invalid", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)