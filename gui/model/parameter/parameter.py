from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from re import Pattern, compile
from pathlib import Path
import os

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from gui.model.parameter.condition import (
    AndCondition,
    Condition,
)
from .constraint import Constraint, IntervalConstraint

T = TypeVar("T")


class Parameter(QObject, Generic[T]):
    """
    A base class for parameters to be filled in using the GUI.

    The class inherits from `QObject` to use the signal mechanism and
    from `Generic` to add type hints based on the type of value that
    the parameter stores.

    By default, a parameter is always enabled. Use the `add_condition`
    method to add a condition that governs the parameter's enabled
    state. If multiple conditions are added, the parameter is only
    enabled when all of the conditions are true.
    """

    class EnabledCondition(Condition):
        """
        A condition that tracks whether a parameter is enabled.
        """

        def __init__(
                self,
                parameter: "Parameter[Any]",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize a `Parameter.EnabledCondition` object.

            :param parameter: the parameter to track
            :type parameter: "Parameter[Any]"

            :param target_value: the target value
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            self._parameter = parameter
            self._target_value = target_value
            super().__init__(
                value=self._parameter.enabled == self._target_value,
                parent=parent,
            )

            self._parameter.enabled_changed.connect(
                self._parameter_enabled_changed
            )
        
        @Slot(bool)
        def _parameter_enabled_changed(
            self,
            new_enabled: bool,
        ) -> None:
            self.value = new_enabled == self._target_value

    value_changed: Signal
    value_reset = Signal()
    valid_changed = Signal(bool)
    constraint_added = Signal(Constraint)
    enabled_changed = Signal(bool)

    def __init__(
            self,
            name: str, 
            description: str, 
            flag: str,
            operations: set[str],
            default_value: T,
            constraints: list[Constraint[T]] | None = None,
    ) -> None:
        """
        Initialize a `Parameter` object.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param default_value: the default value of the parameter
        :type default_value: T
        """
        super().__init__()
        self.name = name
        self.description = description
        self.flag = flag
        self.operations = operations
        self.default_value = default_value
        self._value = default_value
        self._condition = AndCondition()
        self._condition.changed.connect(self.enabled_changed)
        self._constraints: list[Constraint] = []
        self._hidden_constraints: list[Constraint] = []
        for constraint in constraints or []:
            self.add_constraint(constraint)

    @property
    def value(self) -> T:
        """
        The current value of the parameter.

        Setting this property emits the `value_changed` and 
        `valid_changed` signals if applicable.
        """
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        old_value = self._value
        old_valid = self.valid

        self._value = new_value
        for constraint in self._constraints:
            constraint.value = self.value
        for constraint in self._hidden_constraints:
            constraint.value = self.value

        if self.value != old_value:
            self.value_changed.emit(self.value, self.valid)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    def add_condition(
            self,
            condition: Condition,
    ) -> None:
        """
        Add a condition that determines this parameter's enabled state.

        :param condition: the condition to add
        :type condition: Condition
        """
        self._condition.add_condition(condition)

    @property
    def enabled(self) -> bool:
        """
        Whether the parameter is enabled.

        The value of this property is determined solely by the
        conditions which have been added to the parameter using the
        `add_condition` method.
        """
        return self._condition.value

    def reset_value(self) -> None:
        """
        Reset the value of the parameter to the default value.

        The `value_changed` and `valid_changed` signals are emitted if
        applicable.
        """
        self.value = self.default_value
        self.value_reset.emit()

    def add_constraint(
            self,
            constraint: Constraint[T],
            hidden: bool = False,
    ) -> None:
        """
        Add a new constraint to the parameter.

        If `hidden` is `True`, the constraint will not be exposed
        through the `constraint` property, but will nonetheless be
        checked for validity.

        The `valid_changed` signal is emitted if the newly added
        constraint makes the parameter's value invalid.

        The `hint_added` signal is emitted if `hidden` is `False`.

        :param constraint: the constraint to add
        :type constraint: Constraint[T]

        :param hidden: whether to add the constraint as hidden
        :type hidden: bool
        """
        old_valid = self.valid

        if not hidden:
            self._constraints.append(constraint)
            self.constraint_added.emit(constraint)
        else:
            self._hidden_constraints.append(constraint)
        constraint.value = self.value

        constraint.valid_changed.connect(self._emit_valid_changed)
        constraint.enabled_changed.connect(self._emit_valid_changed)

        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    def to_dict(self) -> str | dict:
        return self.value

    def populate(self, value: dict | str) -> None:
        self.value = value

    @property
    def valid(self) -> bool:
        """
        Whether the current value of the parameter is valid.
        """
        if not self.enabled:
            return True
        return (
            all(
                constraint.valid or not constraint.enabled
                for constraint in self._constraints
            )
            and all(
                constraint.valid or not constraint.enabled
                for constraint in self._hidden_constraints
            )
        )

    @property
    def constraints(self) -> list[Constraint]:
        """
        This parameter's (non-hidden) constraints.

        :return: the constraints
        :rtype: list[str]
        """
        return self._constraints

    def in_cli(self, operation: str) -> bool:
        """
        Check if the parameter should be represented in a cli representation
        based on a mode and whether it is enabled.
        """
        return operation in self.operations and self.enabled

    def _to_cli(
            self,
            operation: str | None = None,
            value: T | None = None,
        ) -> str:
        """
        Helper method to represent the parameter for the command line,
        taking into account its current value but not the operation or
        whether the parameter is enabled.

        The operation is nonetheless passed as an argument, in case it
        needs to be passed down recursively.

        :param operation: the ID of the operation
        :type operation: str | None

        :param value: the value to use in place of this parameter's
        value
        :type value: T | None

        :return: the command-line representation
        :rtype: str
        """
        raise NotImplementedError()

    def to_cli(
            self,
            operation: str | None = None,
            value: T | None = None
        ) -> str:
        """
        Represent the parameter for the command line, taking into
        account its current value, whether it is enabled and which
        operation the representation is for.

        If no operation is given, only the enabled status is considered.

        :param operation: the ID of the operation to represent the
        parameter for
        :type operation: str | None

        :return: the command-line representation
        :rtype: str
        """
        if not self.enabled:
            return ""
        if operation is not None and operation not in self.operations:
            return ""
        return self._to_cli(
            operation=operation,
            value=value,
        )

    @Slot()
    def _emit_valid_changed(self) -> None:
        self.valid_changed.emit(self.valid)


class OptionalParameter(Parameter[bool]):
    """
    An optional parameter in the GUI.

    The class acts as a wrapper around a parameter of any type, making it
    optional.

    The resulting parameter belongs to the same operations as the inner
    parameter.
    """

    class Condition(Condition):
        """
        A condition that tracks whether an optional parameter is used.
        """

        def __init__(
                self,
                parameter: "OptionalParameter",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize an `OptionalParameter.Condition` object.

            :param parameter: the optional parameter to track
            :type parameter: OptionalParameter

            :param target_value: the target value of the optional
            parameter
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(
                value=parameter.value==target_value,
                parent=parent,
            )
            self._parameter = parameter
            self._target_value = target_value

            self._parameter.value_changed.connect(self._parameter_value_changed)

        @Slot(bool, bool)
        def _parameter_value_changed(
            self,
            new_value: bool,
        ) -> None:
            self.value = new_value == self._target_value

    value_changed = Signal(bool, bool)

    def __init__(
            self,
            name: str, description: str,
            operations: set[str],
            default_value: bool,
            parameter: Parameter[Any],
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            flag="",
            operations=operations,
            default_value=default_value,
        )
        self._parameter = parameter

        # The inner parameter can only be enabled if the optional
        # parameter is enabled and its value is set.
        condition = AndCondition(
            conditions=[
                Parameter.EnabledCondition(
                    parameter=self,
                    target_value=True,
                    parent=self,
                ),
                self.__class__.Condition(
                    parameter=self,
                    target_value=True,
                    parent=self,
                ),
            ],
            parent=self,
        )
        self._parameter.add_condition(condition)

    @property
    def parameter(self) -> Parameter[Any]:
        return self._parameter

    @property
    def valid(self) -> bool:
        if not self.value:
            return True
        return self.parameter.valid
    
    def to_dict(self) -> str | dict:
        value = {}
        value["enabled"] = self.value
        value[self.parameter.name] = self.parameter.to_dict()
        return value
    
    def populate(self, value: dict | str) -> None:
        if isinstance(value, dict) and 'enabled' not in value:
            raise ValueError(
                f"Incorrect format for {self.name}: {value}"
                + "Optional parameter must have 'enabled' value."
            )
            
        if isinstance(value, dict) and isinstance(value["enabled"], bool):
            self.value = value["enabled"]
            if self.parameter in value:
                self.parameter.populate(
                    value[self.parameter.name]
                )

    def reset_value(self) -> None:
        self.parameter.reset_value()
        super().reset_value()

    def _to_cli(
            self,
            operation: str | None = None,
            value: bool | None = None,
    ) -> str:
        if value is None:
            value = self.value
        if value:
            return self.parameter.to_cli(operation)
        return ""


class MultiParameter(Parameter[tuple[()]]):
    """
    A multi-value parameter in the GUI.
    """

    value_changed = Signal(tuple[()], bool)

    def __init__(
            self,
            name: str,
            description: str,
            flag: str,
            operations: set[str],
            parameters: list[Parameter[Any]],
    ) -> None:
        super().__init__(
            name,
            description,
            flag,
            operations,
            (),
        )
        self._parameters = parameters

        # The inner parameters can only be enabled if the multi-value
        # parameter is enabled.
        condition = Parameter.EnabledCondition(
            parameter=self,
            target_value=True,
            parent=self,
        )
        for parameter in self._parameters:
            parameter.add_condition(condition)

    @property
    def parameters(self) -> list[Parameter[Any]]:
        return self._parameters

    def reset_value(self) -> None:
        for parameter in self.parameters:
            parameter.reset_value()

    @property
    def valid(self) -> bool:
        if not self.enabled:
            return True
        return all([parameter.valid for parameter in self.parameters])

    def to_dict(self) -> str | dict:
        parameters = {}
        for param in self.parameters:
            parameters[param.name] = param.to_dict()
        return parameters

    def populate(self, value: dict | str) -> None:
        for param in self.parameters:
            if isinstance(value, dict) and param.name in value and value[param.name] is not None:
                param.populate(value[param.name])

    def _to_cli(
            self,
            operation: str | None = None,
            value: tuple[()] | None = None,
    ) -> str:
        cli_params = [p.to_cli(operation) for p in self.parameters]
        nonempty_params = [p for p in cli_params if p]
        return f"{self.flag}{" ".join(nonempty_params)}"


class CountedMultiParameter(MultiParameter):
    """
    A multi-value parameter which includes the number of values in its
    command-line representation.
    """

    def _to_cli(
            self,
            operation: str | None = None,
            value: tuple[()] | None = None,
        ) -> str:
        inner_parameters = [p.to_cli(operation) for p in self.parameters]
        nonempty_inner_parameters = [p for p in inner_parameters if p]
        if not nonempty_inner_parameters:
            return ""
        cli_pieces: list[str] = [
            f"{self.flag}{str(len(nonempty_inner_parameters))}",
            *nonempty_inner_parameters,
        ]
        return " ".join(cli_pieces)


class BoolParameter(Parameter[bool]):
    """
    A boolean parameter in the GUI.

    The value of a boolean parameter is always valid.
    """

    class Condition(Condition):
        """
        A condition that tracks whether a bool parameter has a given
        value.
        """

        def __init__(
                self,
                parameter: "BoolParameter",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize a `BoolParameter.Condition` object.

            :param parameter: the bool parameter to track
            :type parameter: BoolParameter

            :param target_value: the target value of the bool parameter
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(
                value=parameter.value==target_value,
                parent=parent,
            )
            self._parameter = parameter
            self._target_value = target_value

            self._parameter.value_changed.connect(self._parameter_value_changed)

        @Slot(bool, bool)
        def _parameter_value_changed(
            self,
            new_value: bool,
            _: bool,
        ) -> None:
            self.value = new_value == self._target_value

    value_changed = Signal(bool, bool)

    def _to_cli(
            self,
            operation: str | None = None,
            value: bool | None = None,
    ) -> str:
        if value is None:
            value = self.value
        # A boolean parameter is represented in the command line by the
        # presence or absence of its flag.
        return self.flag if value else ""
    
    def __str__(self) -> str:
        return (
            f'BoolParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


X = TypeVar("X", bound=float)


class NumberParameter(Parameter[X]):
    """
    A numeric parameter in the GUI.

    The value of a numeric parameter is valid if it is greater than or equal to the
    lower bound and lower than or equal to the upper bound, when provided.
    """

    def _to_cli(
            self,
            operation: str | None = None,
            value: X | None = None,
    ) -> str:
        if value is None:
            value = self.value
        # A numeric parameter is represented in the command line by
        # its flag and its value.
        return f"{self.flag}{self.value}"


class IntParameter(NumberParameter[int]):
    """
    An integer parameter in the GUI.
    """

    value_changed = Signal(int, bool)

    def __str__(self) -> str:
        return (
            f'IntParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


class FloatParameter(NumberParameter[float]):
    """
    A floating-point parameter in the GUI.
    """

    value_changed = Signal(float, bool)

    def __str__(self) -> str:
        return (
            f'FloatParameter('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


class EnumParameter(Parameter[int]):
    """
    A parameter with enumerated values in the GUI.
    """

    class Condition(Condition):
        """
        A condition that tracks whether an enum parameter's value is in
        a given set of values.
        """

        def __init__(
                self,
                parameter: "EnumParameter",
                target_values: list[int],
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize an `EnumParameter.Condition` object.

            :param parameter: the enum parameter to track
            :type parameter: EnumParameter

            :param target_values: the set of target values
            :type target_values: list[int]

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            self._parameter = parameter
            self._target_values = target_values
            super().__init__(
                value=self._parameter.value in self._target_values,
                parent=parent,
            )

            self._parameter.value_changed.connect(self._parameter_value_changed)

        @Slot(int, bool)
        def _parameter_value_changed(
            self,
            new_value: int,
            _: bool,
        ) -> None:
            self.value = new_value in self._target_values

    value_changed = Signal(int, bool)

    def __init__(
            self,
            name: str, 
            description: str, 
            flag: str,
            operations: set[str],
            options: list[tuple[str, str]],
            default_value: int,
            constraints: list[Constraint[int]] | None = None,
    ) -> None:
        """
        Initialize an `EnumParameter` object.

        The `options` argument is a list of the options offered by the
        enum parameter. Each option is a 2-tuple where the first element
        is the name to be displayed to the user, and the second is the
        form to be used in the command-line representation.

        :param name: the name of the parameter
        :type name: str

        :param description: a longer description of the parameter
        :type description: str

        :param flag: the command-line flag of the parameter
        :type flag: str

        :param options: the options of the parameter
        :type options: list[tuple[str, str]]

        :param default_value: the index of the default option
        :type default_value: int
        """
        super().__init__(
            name=name,
            description=description,
            flag=flag,
            operations=operations,
            default_value=default_value,
            constraints=constraints,
        )
        self._options = options

        self.add_constraint(
            IntervalConstraint(
                lower_bound=0,
                lower_bound_inclusive=True,
                upper_bound=len(self._options),
                upper_bound_inclusive=False,
            ),
            hidden=True,
        )

    @property
    def options(self) -> list[str]:
        return [option[0] for option in self._options]

    @property
    def option(self) -> str | None:
        try:
            return self.options[self.value]
        except IndexError:
            return None

    def _to_cli(
            self,
            operation: str | None = None,
            value: int | None = None,
    ) -> str:
        if value is not None:
            value = self.value
        return f"{self.flag}{self._options[self.value][1]}"

    def __str__(self) -> str:
        return (
            "EnumParameter"
            + f'name: "{self.name}", '
            + f'description: "{self.description}", '
            + f'options: {self.options}, '
            + f'selected option: {self.option})'
        )


class StringParameter(Parameter[str]):
    """
    A string parameter in the GUI.

    The parameter may optionally contain a maximum length and/or a
    regex pattern the input must match.

    The value is considered valid when both of the following hold:
    - If a maximum length was specified, the value does not exceed it.
    - If a regex pattern was specified, the value matches it.

    If neither constraint is given, the value is always valid.
    """

    value_changed = Signal(str, bool)

    def _to_cli(
            self,
            operation: str | None = None,
            value: str | None = None,
    ) -> str:
        """
        Represent the parameter for the command line.

        A value can optionally be provided as an argument. If not
        provided, the current value of the parameter is used.

        :return: the command-line representation
        :rtype: str
        """
        if value is None:
            value = self.value
        return f"{self.flag}{value}"

    def __str__(self) -> str:
        return (
            f'String('
            + f'name: "{self.name}", '
            + f'description: "{self.description})", '
            + f'value: {self.value}, '
            + f'valid: {self.valid})'
        )


class StringTableParameter(Parameter[tuple[()]]):
    """
    A parameter for entering a table of strings.
    """

    value_changed = Signal(int, bool)
    row_count_index_changed = Signal(int)
    row_count_changed = Signal(int)

    def __init__(
            self,
            name: str, 
            description: str,
            flag: str,
            operations: set[str],
            columns: list[tuple[str, str, list[Constraint[str]]]],
            allowed_row_counts: list[int],
            separator: str,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            flag=flag,
            operations=operations,
            default_value=(),
        )

        if not columns:
            raise ValueError("Empty column list.")
        self._column_names = [name for name, _, _ in columns]

        if not allowed_row_counts:
            raise ValueError("Empty list of allowed row counts.")
        self._allowed_row_counts = list(allowed_row_counts)
        self._allowed_row_counts.sort()
        self._row_count_index = 0

        max_allowed_row_count = max(allowed_row_counts)
        self._parameters: list[list[StringParameter]] = []
        for _ in range(max_allowed_row_count):
            row = []
            for _, default_value, constraints in columns:
                parameter = StringParameter(
                    name="",
                    description="",
                    flag="",
                    operations=operations,
                    default_value=default_value,
                )
                for constraint in constraints:
                    parameter.add_constraint(constraint.copy())
                parameter.value_changed.connect(self._inner_value_changed)
                row.append(parameter)
            self._parameters.append(row)

        self._separator = separator

    @Slot()
    def _inner_value_changed(self) -> None:
        self.value_changed.emit(self.row_count_index, self.valid)

    def reset_value(self) -> None:
        super().reset_value()
        for row in self.parameters:
            for parameter in row:
                parameter.reset_value()

    def to_dict(self) -> str | dict:
        result = {"parameters": []}
        for row in self.parameters:
            result_row: list[str] = []
            for parameter in row:
                result_row.append(parameter.to_dict())
            result["parameters"].append(result_row)
        return result

    def populate(self, value: dict | str) -> None:
        for row_index, row in enumerate(self.parameters):
            for column_index, parameter in enumerate(row):
                parameter.populate(
                    value["parameters"][row_index][column_index]
                )

    @property
    def allowed_row_counts(self) -> list[int]:
        return self._allowed_row_counts

    @property
    def row_count_index(self) -> int:
        return self._row_count_index

    @row_count_index.setter
    def row_count_index(self, new_row_count_index: int) -> None:
        old_row_count_index = self.row_count_index
        old_row_count = self.row_count

        self._row_count_index = new_row_count_index

        if self.row_count_index != old_row_count_index:
            self.row_count_index_changed.emit(self.row_count_index)
        if self.row_count != old_row_count:
            self.row_count_changed.emit(self.row_count)

    @property
    def row_count(self) -> int:
        return self.allowed_row_counts[self.row_count_index]

    @property
    def column_count(self) -> int:
        return len(self._column_names)

    @property
    def column_names(self) -> list[str]:
        return self._column_names

    @property
    def parameters(self) -> list[list[StringParameter]]:
        return self._parameters

    @property
    def valid(self) -> bool:
        if not self.enabled:
            return True
        return all(
            parameter.valid
            for row in self.parameters[:self.row_count]
            for parameter in row
        )

    def _to_cli(
            self,
            operation: str | None = None,
            value: tuple[()] | None = None,
    ) -> str:
        pieces = [f"{self.flag}{self.row_count}"]
        for row in self.parameters[:self.row_count]:
            pieces.append(
                self._separator.join(
                    parameter.value for parameter in row
                )
            )
        return " ".join(pieces)


class FileParameter(Parameter[list[str]]):
    """
    A file path parameter in the GUI

    Stores the list of file paths selected by the user. The file
    parameter accepts a list of file parameters, and it has the option
    to allow single or multiple file inputs.

    The value is valid when all the following holds:
    - The value list is not empty.
    - If it is not a multiple-file parameter, (`multiple` = False),
    there should only be a single file in the list.
    - Every file in the list exists and readable, and their file
    extension is in `accepted_formats`.

    There are three different levels of strictness for file types:

    1. If `accepted_formats` is given and `strict` is `True`, the user
    is only able to select files that match the types in
    `accepted_formats`.
    2. If `accepted_formats` is given and `strict` is `False`, the user
    can select any file, but a warning is displayed if the file type
    does not match the ones in `accepted_formats`.
    3. If `accepted_formats` is `None`, the user can select any file.
    The value of `strict` is expected to be `False`.
    """

    value_changed = Signal(list, bool)

    def __init__(
        self,
        name: str,
        description: str,
        flag: str,
        operations: set[str],
        accepted_formats: list[str] | None = None,
        strict: bool = False,
        multiple: bool = False,
        default_value: list[str] | None = None,
    ) -> None:
        self.strict = strict
        if strict:
            self.accepted_formats = (
                [ext if ext.startswith(".") else f".{ext}"
                    for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.expected_formats = None
        if not strict:
            self.expected_formats = (
                [ext if ext.startswith(".") else f".{ext}"
                    for ext in accepted_formats]
                if accepted_formats is not None else None
            )
            self.accepted_formats = None
        self.multiple = multiple
        super().__init__(
            name,
            description,
            flag,
            operations,
            default_value or []
        )

    @property
    def valid(self) -> bool:
        if not self.enabled:
            return True
        if not self.value:
            return False
        if not self.multiple and len(self.value) > 1:
            return False
        return all(
            Path(f).is_file()
            and os.access(Path(f), os.R_OK)
            and (
                    not self.strict
                    or self.accepted_formats is None
                    or Path(f).suffix.lower() in self.accepted_formats
            )
            for f in self.value
        )

    @property
    def file_extensions(self) -> list[str]:
        return [Path(f).suffix.lower() for f in self.value if f]

    @property
    def matches_expected(self) -> bool:
        if not self.value or self.expected_formats is None:
            return True
        return all(
            Path(f).suffix.lower() in self.expected_formats
            for f in self.value
        )

    @property
    def value(self) -> list[str]:
        return super().value

    @value.setter
    def value(self, new_value: list[str]) -> None:
        self._value = new_value
        self.value_changed.emit(self.value, self.valid)

    def __str__(self) -> str:
        return (
            f'FileParameter('
            f'name: "{self.name}", '
            f'description: "{self.description}", '
            f'accepted_formats: {self.accepted_formats}, '
            f'value: "{self.value}", '
            f'valid: {self.valid})'
        )

    def _to_cli(
            self,
            operation: str | None = None,
            value: list[str] | None = None,
    ) -> str:
        if value is None:
            value = self.value
        return " ".join(f"{self.flag}{f}" for f in value)
