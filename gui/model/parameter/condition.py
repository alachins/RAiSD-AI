from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)


class Condition(QObject):
    """
    An base condition class.

    A condition tracks a certain property and exposes a boolean
    value, emitting a signal when that property changes.
    """

    changed = Signal(bool)

    def __init__(
            self,
            value: bool = False,
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize a `Condition` object.

        :param value: the initial value of the condition
        :type value: bool

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        super().__init__(parent=parent)
        self._value = value

    @property
    def value(self) -> bool:
        """
        The boolean value of the condition.

        Setting this property will emit the `changed` signal.
        """
        return self._value

    @value.setter
    def value(self, new_value: bool) -> None:
        self._value = new_value
        self.changed.emit(self._value)


class AndCondition(Condition):
    """
    A condition whose value is the conjunction of its child conditions'
    values.
    """

    def __init__(
            self,
            conditions: list[Condition] | None = None,
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize an `AndCondition` object.

        :param conditions: the list of child conditions
        :type conditions: list[Condition] | None

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        if conditions is None:
            conditions = []
        super().__init__(
            all([condition.value for condition in conditions]),
            parent,
        )
        self._conditions = conditions

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    def add_condition(
            self,
            condition: Condition,
    ) -> None:
        """
        Add a condition to the list of conditions in the conjunction.

        :param condition: the condition to add
        :type condition: Condition
        """
        self._conditions.append(condition)
        condition.changed.connect(self._condition_changed)
        self._condition_changed(condition.value)

    @Slot(bool)
    def _condition_changed(self, new_value: bool) -> None:
        # If the newly changed condition is now false, the conjunction
        # of all condition must be false.
        if not new_value:
            self.value = False
        else:
            self.value = all(condition.value for condition in self._conditions)


class OrCondition(Condition):
    """
    A condition whose value is the disjunction of its child conditions'
    values.
    """

    def __init__(
            self,
            conditions: list[Condition] | None = None,
            parent: QObject | None = None,
    ) -> None:
        """
        Initialize an `OrCondition` object.

        :param conditions: the list of child conditions
        :type conditions: list[Condition] | None

        :param parent: the parent of this `QObject`
        :type parent: QObject | None
        """
        if conditions is None:
            conditions = []
        super().__init__(
            any([condition.value for condition in conditions]),
            parent=parent,
        )
        self._conditions = conditions

        for condition in self._conditions:
            condition.changed.connect(self._condition_changed)

    def add_condition(
            self,
            condition: Condition,
    ) -> None:
        """
        Add a condition to the list of conditions in the disjunction.

        :param condition: the condition to add
        :type condition: Condition
        """
        self._conditions.append(condition)
        condition.changed.connect(self._condition_changed)
        self._condition_changed(condition.value)

    @Slot(bool)
    def _condition_changed(self, new_value: bool) -> None:
        # If the newly changed condition is now true, the disjunction
        # of all condition must be true.
        if new_value:
            self.value = True
        else:
            self.value = any(condition.value for condition in self._conditions)
