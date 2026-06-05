"""
A module containing the `Operation` class.
"""

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .file_structure import FileStructure
from gui.model.parameter import Parameter


@dataclass
class Operation():
    """
    A data class which holds the details of an operation.

    This class is used to hold intermediate information about operations
    between parsing and building the operation tree.
    """

    @dataclass
    class Input:
        name: str | None
        description: str | None
        cli: str
        file: FileStructure

    class PathFragment:
        pass

    @dataclass
    class ConstPathFragment(PathFragment):
        value: str

    class RunIdPathFragment(PathFragment):
        pass

    class SlashPathFragment(PathFragment):
        pass

    @dataclass
    class ParameterValuePathFragment(PathFragment):
        parameter_id: str

    id: str
    name: str
    description: str
    cli: str
    requires: Sequence[Input]
    produces: FileStructure
    output_path: Sequence[PathFragment]
    overwrite_parameter_builder: Callable[[], Parameter[Any]]
    overwrite_path: Sequence[PathFragment]
    parameter_builders: Mapping[str, Callable[[], Parameter[Any]]]
