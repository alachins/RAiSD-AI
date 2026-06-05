from typing import Any, Iterator

from PySide6.QtCore import QObject, Signal, Slot

from .parameter import Parameter


class ParameterGroup(QObject):
    """
    A group of `Parameter` objects associated with the same command.
    """

    enabled_changed = Signal(bool)

    def __init__(
            self,
            name: str,
            parameters: list[Parameter[Any]] | None = None,
    ) -> None:
        """
        Initialize a `ParameterGroup` object.

        :param name: the name of the parameter group
        :type name: str

        :param parameters: the list of parameters in the group
        :type parameters: list[Parameter[Any]] | None
        """
        super().__init__()
        self.name = name
        self._parameters = parameters or []
        self._enabled = False
        for parameter in self._parameters:
            parameter.enabled_changed.connect(self._parameter_enabled_changed)
            if parameter.enabled:
                self._enabled = True

    @property
    def parameters(self) -> list[Parameter[Any]]:
        """
        The list of parameters in the group.
        """
        return self._parameters

    def add_parameter(self, parameter: Parameter[Any]) -> None:
        """
        Add a parameter to the group and connect to its enabled_changed signal
        """
        self._parameters.append(parameter)
        parameter.enabled_changed.connect(self._parameter_enabled_changed)

        new_enabled = any(parameter.enabled for parameter in self._parameters)
        if self.enabled != new_enabled:
            self.enabled_changed.emit(new_enabled)
            self._enabled = new_enabled
    
    @property
    def valid(self) -> bool:
        """
        Whether the current parameter values are valid.

        The group is valid if and only if every parameter in the group
        is valid.
        """
        return all([param.valid for param in self])

    @property
    def enabled(self) -> bool:
        """
        Whether the parameter group is enabled.
        """
        return self._enabled

    @Slot(bool)
    def _parameter_enabled_changed(self, new_value: bool) -> None:
        """
        Check if the parameter group is enabled.

        :new_value param: the new value of enabled of the parameter
        :new_value type: bool
        """

        # Check if any children are enabled
        new_enabled = False
        for parameter in self._parameters:
            if parameter.enabled:
                new_enabled = True
                break

        # If enabled changed, emit signal
        if self._enabled != new_enabled:
            self.enabled_changed.emit(new_enabled)
            self._enabled = new_enabled

    def to_cli(self, operation: str) -> str:
        """
        Represent the parameter group for the command line.

        The command-line representation is obtained from the
        representations of the parameters. If the parameter group has
        its own option, it is prepended to the output.

        :return: the command-line representation
        :rtype: str
        """
        cli_params = [p.to_cli(operation) for p in self]
        nonempty_params = [p for p in cli_params if p]
        return " ".join(nonempty_params)

    def __str__(self) -> str:
        return f"ParameterGroup({self.name})"

    def __iter__(self) -> Iterator[Parameter[Any]]:
        return iter(self.parameters)

    def __getitem__(self, i) -> Parameter[Any]:
        return self.parameters[i]
