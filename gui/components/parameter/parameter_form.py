from PySide6.QtWidgets import (
    QWidget,
    QLabel,
)

from .parameter_form_section import ParameterFormSection
from gui.model.run_record import RunRecord
from gui.components import VBoxLayout
from gui.style import constants


class ParameterForm(QWidget):
    """
    A form of parameters to be filled in by the user.
    """

    def __init__(self, run_record: RunRecord, editable: bool):
        """
        Initialize a `ParameterForm` object.

        :param run_record: the `RunRecord` holding the parameters to be filled in by
        the user
        :type run_record: RunRecord
        """
        super().__init__()
        self._editable = editable
        self._run_record = run_record
        self._parameter_form_sections: list[ParameterFormSection] = []
        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        for parameter_group in self._run_record.parameter_groups:
            parameter_form_section = ParameterFormSection(parameter_group, editable=self._editable)
            layout.addWidget(parameter_form_section)
            self._parameter_form_sections.append(parameter_form_section)

        layout.addStretch()

    def touch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.touch_all()

    def untouch_all(self) -> None:
        for section in self._parameter_form_sections:
            section.untouch_all()

    def update_validity_hints(self) -> None:
        """
        Update each section's border based on whether it contains any invalid enabled parameters.
        """
        for section in self._parameter_form_sections:
            section.invalid = self._section_with_invalid_parameters(section)

    def update_active_hints(self) -> None:
        """
        Change invalid(red) sections to valid sections
        when the respective invalid parameters are changed to valid
        """
        for section in self._parameter_form_sections:
            if section.invalid and not self._section_with_invalid_parameters(section):
                section.invalid = False

    def clear_validity_hints(self) -> None:
        """
        Clear red border from all sections when navigating
        """
        for section in self._parameter_form_sections:
            section.invalid = False

    def _section_with_invalid_parameters(self, section) -> bool:
        """
        Helper function that returns true for a section with an invalid parameters
        Otherwise, returns false
        """
        for parameter in section.parameter_group.parameters:
            if parameter.enabled and not parameter.valid:
                return True
        return False