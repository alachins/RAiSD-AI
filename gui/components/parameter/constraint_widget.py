from PySide6.QtCore import (
    Slot,
)
from PySide6.QtWidgets import QLabel

from gui.model.parameter import Constraint
from gui.components.utils import set_bool_property


class ConstraintWidget(QLabel):
    def __init__(self, constraint: Constraint) -> None:
        super().__init__(text=constraint.hint)
        self.setObjectName("constraint")
        self._constraint = constraint
        self._touched = False

        self.setVisible(self._constraint.enabled)

        self._constraint.hint_changed.connect(self._hint_changed)
        self._constraint.enabled_changed.connect(self._enabled_changed)
        self._constraint.valid_changed.connect(self.show_validity)

    @property
    def touched(self) -> bool:
        return self._touched

    @touched.setter
    def touched(self, new_touched: bool) -> None:
        self._touched = new_touched
        self.show_validity()

    @Slot(str)
    def _hint_changed(self, new_hint: str) -> None:
        self.setText(new_hint)

    @Slot(bool)
    def _enabled_changed(self, new_enabled: bool) -> None:
        self.setVisible(new_enabled)

    def show_validity(self) -> None:
        if self.touched:
            set_bool_property(self, "valid", self._constraint.valid)
        else:
            set_bool_property(self, "valid", None)
