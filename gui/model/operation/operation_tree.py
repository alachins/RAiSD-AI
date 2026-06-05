"""
A module for representing operation trees.

RAiSD-AI operations, needing one or more input files which can be
obtained from the output of other operations, are hierarchical in
nature. The `OperationTree` class represents such an operation hierarchy
with a specified operation as the root.

The recommended way to construct operation trees is using the
`OperationTree#build_trees` factory method.
"""

from typing import Any, Callable, Mapping, Sequence

from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    QFileInfo,
    QFileSystemWatcher,
    QDir,
)

from .file_structure import (
    FileStructure,
    SingleFile,
    Directory,
)
from .operation import Operation
from gui.model.parameter import (
    Parameter,
    BoolParameter,
    StringParameter,
)
from gui.model.parameter.condition import (
    Condition,
    OrCondition,
)


class FileProducerNode(QObject):
    """
    An abstract class for nodes that can produce a file.
    """

    class OverwriteCondition(Condition):
        """
        A condition that tracks whether a file producer node's output
        will overwrite existing files.
        """

        def __init__(
                self,
                file_producer_node: "FileProducerNode",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize a `FileProducerNode.OverwriteCondition` object.

            :param file_producer_node: the node to track
            :type file_producer_node: FileProducerNode

            :param target_value: the target value
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(
                value=file_producer_node.overwrite==target_value,
                parent=parent,
            )
            self._file_producer_node = file_producer_node
            self._target_value = target_value

            self._file_producer_node.overwrite_changed.connect(
                self._overwrite_changed,
            )

        @Slot(bool)
        def _overwrite_changed(self, new_overwrite: bool):
            self.value = new_overwrite==self._target_value

    file_changed = Signal(str)
    watched_files_changed = Signal(list[str])
    overwrite_changed = Signal(bool)
    valid_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._watcher = QFileSystemWatcher()
        self.file_changed.connect(self._update_watcher_path)
        self.watched_files_changed.connect(self._update_watcher_path)
        self._watcher.fileChanged.connect(self._watched_file_changed)
        self._watcher.directoryChanged.connect(self._watched_file_changed)

    @property
    def produces(self) -> FileStructure:
        """
        The type of file this node produces.
        """
        raise NotImplementedError()

    @property
    def file(self) -> str | None:
        """
        The path to the file produced by this node, if available.
        """
        raise NotImplementedError()

    @property
    def watched_files(self) -> list[str]:
        """
        The paths to the file this node needs to watch for changes.
        """
        return []

    @property
    def overwrite(self) -> bool:
        """
        Whether the output of this node will overwrite an existing file
        or directory.
        """
        return False

    @property
    def valid(self) -> bool:
        """
        Whether the node is in a valid state.
        """
        raise NotImplementedError()

    def _set_run_id(self, new_run_id: str) -> None:
        raise NotImplementedError()

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        raise NotImplementedError()
    
    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled.

        This property is used in generating commands.
        """
        raise NotImplementedError()

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()
    
    def get_operation_ids(self) -> list[str]:
        raise NotImplementedError()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter[Any]],
    ) -> Sequence[str]:
        """
        Get the terminal commands needed to produce the file.

        :param run_id_paramter: the run ID parameter
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def populate_from_dict(self, values: dict) -> None:
        raise NotImplementedError()

    @Slot()
    def _update_watcher_path(self) -> None:
        # Remove the watched paths, if any.
        paths = self._watcher.files() + self._watcher.directories()
        if paths:
            self._watcher.removePaths(paths)

        # Watch the closest existing ancestor of each watched file.
        for file in self.watched_files:
            added: bool = False
            while file and not added:
                added = self._watcher.addPath(file)
                file = QFileInfo(file).dir().absolutePath()

    @Slot()
    def _watched_file_changed(self) -> None:
        self._update_watcher_path()
        self.overwrite_changed.emit(self.overwrite)


class FileConsumerNode(QObject):
    """
    A node representing an input file required by another node.

    A file consumer node has a list of `FileProducerNode` children that
    produce the required file type, allowing the user to choose between 
    them.
    """

    selected_index_changed = Signal(int)
    valid_changed = Signal(bool)

    def __init__(
            self,
            required_file: Operation.Input,
            enabled: bool = False,
    ) -> None:
        """
        Initialize a `FileConsumerNode` object.

        :param required_file: an object containing the details of the
        required file
        :type required_file: Operation.Input

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._producers = []
        self._selected_index = 0
        self._name = required_file.name
        self._description = required_file.description
        self._cli = required_file.cli
        self._requires = required_file.file
        self._enabled = enabled

    @property
    def requires(self) -> FileStructure:
        """
        The file type the node requires.
        """
        return self._requires

    def add_producer(self, producer: FileProducerNode) -> None:
        """
        Add a `FileProducerNode` as a child of this node.

        :param producer: the child node
        :type producer: FileProducerNode
        """
        self._producers.append(producer)
        producer.valid_changed.connect(self._producer_valid_changed)

    @property
    def producers(self) -> Sequence[FileProducerNode]:
        """
        This node's `FileProducerNode` children.
        """
        return self._producers

    @property
    def name(self) -> str | None:
        """
        The name of the required file to display to the user.
        """
        return self._name

    @property
    def description(self) -> str | None:
        """
        The description of the required file, explaining what it
        represents for the operation that needs it.
        """
        return self._description

    @property
    def cli_parameter(self) -> str:
        """
        The representation of this file as a command-line argument.
        """
        return f"{self._cli}{self.file}"

    @property
    def selected_index(self) -> int:
        """
        The index of the currently selected child node. Setting this
        enables the corresponding child node and disables the previous
        one, if this node is enabled.
        """
        return self._selected_index

    @selected_index.setter
    def selected_index(self, new_selected_index: int) -> None:
        old_valid = self.valid

        if self.selected_producer is not None:
            self.selected_producer.enabled = False

        self._selected_index = new_selected_index
        self.selected_index_changed.emit(new_selected_index)

        if self.selected_producer is not None:
            self.selected_producer.enabled = self.enabled

        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    @property
    def selected_producer(self) -> FileProducerNode | None:
        """
        The currently selected child node.
        """
        if self.producers:
            return self.producers[self.selected_index]
        return None

    def _set_run_id(self, new_run_id: str):
        for producer in self.producers:
            producer.run_id = new_run_id

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str):
        for producer in self.producers:
            producer.base_directory_path = new_base_directory_path

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether this node is currently enabled. Setting this sets the
        enabled status of the selected child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self._enabled = new_enabled
        if self.selected_producer is not None:
            self.selected_producer.enabled = self.enabled

    @property
    def file(self) -> str | None:
        """
        The path to the file produced by the currently selected child 
        node, if available.
        """
        if self.selected_producer is None:
            return None
        return self.selected_producer.file

    @property
    def valid(self) -> bool:
        """
        Whether this node is in a valid state.
        """
        if self.selected_producer is None:
            return False
        return self.selected_producer.valid
    
    def reset(self) -> None:
        self.selected_index = 0
        for producer in self.producers:
            producer.reset()

    def get_operation_ids(self) -> list[str]:
        if self.selected_producer is None:
            return []
        return self.selected_producer.get_operation_ids()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter],
    ) -> Sequence[str]:
        """
        Get the terminal commands needed to produce the file.

        :param run_id_paramter: the run ID parameter
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        if self.selected_producer is None:
            return []
        return self.selected_producer.to_cli(run_id_parameter, parameters)

    def to_dict(self) -> dict:
        return {
            "selected": self.selected_index,
            "file_producers": [
                producer.to_dict() for producer in self.producers
            ]
        }

    def populate_from_dict(self, values: dict) -> None:
        if "selected" not in values:
            raise ValueError("Missing 'selected' in dict.")
        selected_index = values["selected"]
        if not isinstance(selected_index, int):
            raise ValueError(
                f"Invalid 'selected' in dict: {selected_index}. Expected int."
            )
        self.selected_index = selected_index
        
        if "file_producers" not in values:
            raise ValueError("Missing 'file_producers' in dict.")
        file_producer_values_list = values["file_producers"]
        if not isinstance(file_producer_values_list, list):
            raise ValueError(
                "Invalid 'file_producers' in dict: "
                + f"{file_producer_values_list}. Expected a list."
            )
        if len(file_producer_values_list) != len(self.producers):
            raise ValueError("Mismatch in 'file_producers' length: " \
                f"{len(file_producer_values_list)} in dict vs " \
                f"{len(self.producers)} in node."
            )
        for i, file_producer_values in enumerate(file_producer_values_list):
            if not isinstance(file_producer_values, dict):
                raise ValueError(
                    f"Invalid item in 'file_producers': {file_producer_values}"
                    + ". Expected an object."
                )
            self.producers[i].populate_from_dict(file_producer_values)
            

    @Slot(bool)
    def _producer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)


class CommonParentDirectoryNode(FileProducerNode):
    """
    A node which produces a directory of files by producing each file
    individually.

    Implements `FileProducerNode`.
    """

    def __init__(
            self,
            produces: Directory,
            overwrite_parameter_builder: Callable[[], Parameter[Any]],
            enabled: bool = False,
    ) -> None:
        """
        Initialize a `CommonParentDirectoryNode` object.

        The `produces` argument describes the contents of the directory
        this node must produce. For each item in the directory, a child
        `FileConsumerNode` will be instantiated with no label or
        command-line representation.

        :param produces: the file structure to be produced
        :type produces: Directory

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._produces = produces
        self._file_consumers = []
        for file_structure in self._produces.contents:
            file_consumer = FileConsumerNode(
                Operation.Input(
                    name=None,
                    description=None,
                    cli="",
                    file=file_structure,
                )
            )
            self._file_consumers.append(file_consumer)
            file_consumer.valid_changed.connect(self._consumer_valid_changed)

        overwrite_parameter = overwrite_parameter_builder()
        if not isinstance(overwrite_parameter, BoolParameter):
            raise ValueError(
                "Invalid overwrite parameter for common parent directory node:"
                + f" {overwrite_parameter}. Expected a bool parameter."
            )
        self._overwrite_parameter = overwrite_parameter

        self._enabled = enabled

        self._overwrite_parameter.add_condition(
            FileProducerNode.OverwriteCondition(
                file_producer_node=self,
                target_value=True,
                parent=self,
            )
        )

        self._update_watcher_path()

    @property
    def produces(self) -> Directory:
        """
        The file structure this node produces.
        """
        return self._produces

    @property
    def overwrite_parameter(self) -> BoolParameter:
        """
        The overwrite parameter of this node.
        """
        return self._overwrite_parameter

    @property
    def file_consumers(self) -> Sequence[FileConsumerNode]:
        """
        This node's child `FileConsumerNode`s.
        """
        return self._file_consumers

    @property
    def file(self) -> str | None:
        """
        The path to the directory produced by this node's children, if
        available.
        """
        parent_directory_paths: set[str] = set()
        for consumer in self.file_consumers:
            if consumer.file is None:
                return None
            parent_directory_paths.add(
                QFileInfo(consumer.file).dir().absolutePath()
            )
        if len(parent_directory_paths) == 1:
            return list(parent_directory_paths)[0]
        return None

    @property
    def watched_files(self) -> list[str]:
        file = self.file
        if file:
            return [file]
        return []

    @property
    def overwrite(self) -> bool:
        file = self.file
        return file is not None and QFileInfo(file).exists()

    def _set_run_id(self, new_run_id: str) -> None:
        old_file = self.file
        old_overwrite = self.overwrite
        old_valid = self.valid

        for file_consumer in self.file_consumers:
            file_consumer.run_id = new_run_id

        if self.file != old_file:
            self.file_changed.emit(self.file)
        if self.overwrite != old_overwrite:
            self.overwrite_changed.emit(self.overwrite)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        old_file = self.file
        old_overwrite = self.overwrite
        old_valid = self.valid

        for file_consumer in self.file_consumers:
            file_consumer.base_directory_path = new_base_directory_path

        if self.file != old_file:
            self.file_changed.emit(self.file)
        if self.overwrite != old_overwrite:
            self.overwrite_changed.emit(self.overwrite)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether this node is enabled. Setting this property sets the
        enabled state of each child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled

    @property
    def valid(self) -> bool:
        """
        Whether the node is in a valid state.

        A `CommonParentDirectoryNode` is valid if each of its children
        is valid, and they all produce output in the same directory.
        """
        # TODO: hide the node if its children don't have the same output
        # location
        if not all(consumer.valid for consumer in self.file_consumers):
            return False

        if self.file is None:
            return False

        return self.overwrite_parameter.value or not self.overwrite

    def reset(self) -> None:
        for consumer in self.file_consumers:
            consumer.reset()

    def get_operation_ids(self) -> list[str]:
        operation_ids = []

        for file_consumer in self.file_consumers:
            operation_ids.extend(file_consumer.get_operation_ids())

        return operation_ids

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter],
    ) -> Sequence[str]:
        """
        Get the terminal commands needed to produce the directory.

        :param run_id_paramter: the run ID parameter
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        :type parameters: list[Parameter]

        :return: the (possibly empty) list of commands
        :rtype: list[str]
        """
        commands = []
        for i, consumer in enumerate(self.file_consumers):
            child_commands: Sequence[str] = consumer.to_cli(
                run_id_parameter,
                parameters,
            )

            # If this is the first child, add the overwrite parameter
            # to its last command.
            overwrite_parameter_cli = self.overwrite_parameter.to_cli()
            if i == 0 and child_commands and overwrite_parameter_cli:
                child_commands = [
                    *child_commands[:-1],
                    f"{child_commands[-1]} {overwrite_parameter_cli}",
                ]

            commands.extend(child_commands)
        return commands

    def to_dict(self) -> dict:
        return {
            "file_consumers": [
                consumer.to_dict() for consumer in self.file_consumers
            ]
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_consumers" not in values:
            raise ValueError("Missing 'file_consumers' key in dict.")
        file_consumer_values_list = values["file_consumers"]
        if not isinstance(file_consumer_values_list, list):
            raise ValueError(
                f"Invalid 'file_consumers' in dict: {file_consumer_values_list}. "
                + "Expected a list."
            )
        if len(file_consumer_values_list) != len(self.file_consumers):
            raise ValueError(
                "Mismatch in 'file_consumers' length: " \
                f"{len(file_consumer_values_list)} in dict vs " \
                f"{len(self.file_consumers)} in node."
            )
        for i, file_consumer_values in enumerate(file_consumer_values_list):
            if not isinstance(file_consumer_values, dict):
                raise ValueError(
                    f"Invalid item in 'file_consumers': {file_consumer_values}. "
                    + "Expected a dict."
                )
            self.file_consumers[i].populate_from_dict(file_consumer_values)

    @Slot(bool)
    def _consumer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)


class FilePickerNode(FileProducerNode):
    """
    A node which allows the user to select an existing file.

    Implements `FileProducerNode`.
    """

    def __init__(
            self,
            produces: FileStructure,
            enabled: bool = False,
    ) -> None:
        """
        Initialize a `FilePickerNode` object.

        :param produces: the file type the user should choose
        :type produces: FileStructure

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._produces = produces
        self._file: str | None = None
        self._enabled = enabled

        self._update_watcher_path()

    @property
    def produces(self) -> FileStructure:
        """
        The type of file the user is expected to choose.
        """
        return self._produces

    @property
    def file(self) -> str | None:
        """
        The path to the file chosen by the user, if they have done so.
        """
        return self._file

    @file.setter
    def file(self, new_file: str | None) -> None:
        self._file = new_file
        self.file_changed.emit(self._file)
        self.valid_changed.emit(self.valid)

    def _set_run_id(self, new_run_id: str) -> None:
        pass

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        pass

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled) -> None:
        self._enabled = new_enabled

    @property
    def valid(self) -> bool:
        """
        Whether the user has chosen a file matching the required type.
        """
        if self.file is None:
            return False
        return self.produces.matches(self.file)

    def reset(self) -> None:
        self.file = None

    def get_operation_ids(self) -> list[str]:
        return []

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter],
    ) -> Sequence[str]:
        """
        Get the terminal commands needed to produce the file.

        Note: this method always returns an empty list.

        :param run_id_paramter: the run ID parameter (ignored)
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        (ignored)
        :type parameters: list[Parameter]

        :return: the empty list of commands
        :rtype: list[str]
        """
        return []

    def to_dict(self) -> dict:
        return {
            "file_path": self.file
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_path" not in values:
            raise ValueError("Missing 'file_path' key in dict.")
        file_path = values["file_path"]
        if file_path is not None and not isinstance(file_path, str):
            raise ValueError(
                f"Invalid 'file_path' in dict: {file_path}. Expected a string "
                + "or null."
            )
        self.file = file_path


class OperationNode(FileProducerNode):
    """
    A node which allows the user to run an operation.

    Implements `FileProducerNode` by producing the output file of
    the operation.
    """

    class PathFragmentGenerator:
        """
        An abstract class for objects which generate part of a file
        path.

        This class's subclasses should be instantiated using the
        `from_path_fragment` class method.
        """

        @classmethod
        def from_path_fragment(
            cls,
            path_fragment: Operation.PathFragment,
            operation_node: "OperationNode",
        ) -> "OperationNode.PathFragmentGenerator":
            """
            Create the correct `OperationNode.PathFragmentGenerator`
            for a given `Operation.PathFragment`.

            :param path_fragment: the path fragment
            :type path_fragment: Operation.PathFragment

            :param operation_node: the operation node to reference, if
            applicable for the path fragment type
            :type operation_node: OperationNode

            :return: the path fragment generator
            :rtype: PathFragmentGenerator
            """
            if isinstance(path_fragment, Operation.ConstPathFragment):
                return OperationNode.ConstPathFragmentGenerator(
                    value=path_fragment.value,
                )
            if isinstance(path_fragment, Operation.RunIdPathFragment):
                return OperationNode.RunIdPathFragmentGenerator(
                    operation_node=operation_node,
                )
            if isinstance(path_fragment, Operation.SlashPathFragment):
                return OperationNode.SlashPathFragmentGenerator()
            if isinstance(path_fragment, Operation.ParameterValuePathFragment):
                return OperationNode.ParameterValuePathFragmentGenerator(
                    parameter=operation_node.parameters[
                        path_fragment.parameter_id
                    ]
                )
            raise NotImplementedError("Unknown path fragment type!")

        @property
        def value(self) -> str:
            """
            The path fragment generated by this generator.
            """
            raise NotImplementedError()

    class ConstPathFragmentGenerator(PathFragmentGenerator):
        """
        A path fragment generator which always generates the same
        string.
        """

        def __init__(
                self,
                value: str,
        ) -> None:
            """
            Initialize a `ConstPathFragmentGenerator` object.

            :param value: the constant string to generate
            :type value: str
            """
            self._value = value

        @property
        def value(self) -> str:
            return self._value

    class RunIdPathFragmentGenerator(PathFragmentGenerator):
        """
        A path fragment generator which generates a given
        `OperationNode`'s current run ID.
        """

        def __init__(
                self,
                operation_node: "OperationNode",
        ) -> None:
            """
            Initialize a `RunIdPathFragmentGenerator` object.

            :param operation_node: the operation node whose run ID to
            reference
            :type operation_node: OperationNode
            """
            self._operation_node = operation_node

        @property
        def value(self) -> str:
            return self._operation_node.run_id

    class SlashPathFragmentGenerator(PathFragmentGenerator):
        """
        A path fragment generator which always generates a directory
        separator, i.e. a slash.
        """

        @property
        def value(self) -> str:
            return "/"

    class ParameterValuePathFragmentGenerator(PathFragmentGenerator):
        """
        A path fragment generator which generates the value of a given
        parameter.

        The purpose of this class is to be able to include the image
        class label in the output path of an IMG-GEN operation.
        """

        def __init__(
                self,
                parameter: Parameter[Any],
        ) -> None:
            """
            Initialize a `ParameterValuePathFragmentGenerator` object.

            :param parameter: the parameter whose value to reference
            :type parameter: Parameter[Any]
            """
            self._parameter = parameter

        @property
        def value(self) -> str:
            return str(self._parameter.value)

    class EnabledCondition(Condition):
        """
        A condition that tracks whether an operation node is enabled.
        """

        def __init__(
                self,
                operation_node: "OperationNode",
                target_value: bool = True,
                parent: QObject | None = None,
        ) -> None:
            """
            Initialize an `OperationNode.EnabledCondition` object.

            :param operation_node: the operation node to track
            :type operation_node: OperationNode

            :param target_value: the target value
            :type target_value: bool

            :param parent: the parent of this `QObject`
            :type parent: QObject | None
            """
            super().__init__(
                value=operation_node.enabled==target_value,
                parent=parent,
            )
            self._operation_node = operation_node
            self._target_value = target_value

            self._operation_node.enabled_changed.connect(self._enabled_changed)

        @Slot(bool)
        def _enabled_changed(self, new_enabled: bool):
            self.value = new_enabled==self._target_value

    run_id_changed = Signal(str)
    enabled_changed = Signal(bool)

    def __init__(self,
        operation: Operation,
        run_id: str = "",
        base_directory_path: str = "",
        enabled: bool = False,
    ) -> None:
        """
        Initialize an `OperationNode` object.

        For each required file of `operation`, a child
        `FileConsumerNode` is initialized with its details. A
        `FilePickerNode` is added by default.

        :param run_id: the initial run ID
        :type run_id: str

        :param base_directory_path: the initial base directory path for
        constructing the output location

        :param operation: the operation this node represents
        :type operation: Operation

        :param enabled: whether the node is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._id = operation.id
        self._name = operation.name
        self._description = operation.description
        self._cli = operation.cli
        self._produces = operation.produces
        self._file_consumers = []
        for operation_input in operation.requires:
            file_consumer = FileConsumerNode(operation_input)
            file_picker = FilePickerNode(operation_input.file)
            file_consumer.add_producer(file_picker)
            self._file_consumers.append(file_consumer)
            file_consumer.valid_changed.connect(self._consumer_valid_changed)

        overwrite_parameter = operation.overwrite_parameter_builder()
        if not isinstance(overwrite_parameter, BoolParameter):
            raise ValueError(
                f"Invalid overwrite parameter for operation '{self._name}': "
                + f"{overwrite_parameter}. Expected a BoolParameter Instance."
            )
        # Assigned in a roundabout way for type checker purposes.
        self._overwrite_parameter = overwrite_parameter
        self._overwrite_parameter.value_changed.connect(
            self._overwrite_parameter_value_changed,
        )

        self._parameters = {}
        for parameter_id in operation.parameter_builders:
            parameter_builder = operation.parameter_builders[parameter_id]
            parameter = parameter_builder()
            self._parameters[parameter_id] = parameter
            # TODO: consider if there is a way to only connect the
            # used parameters
            parameter.value_changed.connect(self._parameter_value_changed)

        self._output_path = [
            OperationNode.PathFragmentGenerator.from_path_fragment(
                path_fragment=path_fragment,
                operation_node=self,
            )
            for path_fragment in operation.output_path
        ]

        self._overwrite_path = [
            OperationNode.PathFragmentGenerator.from_path_fragment(
                path_fragment=path_fragment,
                operation_node=self,
            )
            for path_fragment in operation.overwrite_path
        ]

        self._run_id = run_id
        self._base_directory_path = base_directory_path
        self._enabled = enabled

        self._overwrite_parameter.add_condition(
            FileProducerNode.OverwriteCondition(
                file_producer_node=self,
                target_value=True,
                parent=self,
            ),
        )

        self._update_watcher_path()

    @property
    def id(self) -> str:
        """
        The string identifier of the operation.
        """
        return self._id

    @property
    def name(self) -> str:
        """
        The name of the operation.
        """
        return self._name

    @property
    def description(self) -> str:
        """
        The description of the operation.
        """
        return self._description

    @property
    def produces(self) -> FileStructure:
        """
        The type of file produced by the operation.
        """
        return self._produces

    @property
    def overwrite_parameter(self) -> BoolParameter:
        """
        The overwrite parameter of this node.
        """
        return self._overwrite_parameter

    @property
    def parameters(self) -> Mapping[str, Parameter[Any]]:
        """
        The parameters of this node's operation.
        """
        return self._parameters

    @property
    def file_consumers(self) -> Sequence[FileConsumerNode]:
        """
        This node's `FileConsumerNode` children.
        """
        return self._file_consumers

    @property
    def run_id(self) -> str:
        """
        The run ID stored in this node.

        When this property is set, the node will append its operation ID
        to the given value.
        """
        return self._run_id

    @run_id.setter
    def run_id(self, new_run_id: str) -> None:
        old_file = self.file
        old_overwrite = self.overwrite
        old_valid = self.valid
        old_run_id = self.run_id

        self._run_id = f"{new_run_id}_{self.id}"
        for file_consumer in self.file_consumers:
            file_consumer.run_id = self.run_id

        if self.file != old_file:
            self.file_changed.emit(self.file)
        if self.overwrite != old_overwrite:
            self.overwrite_changed.emit(self.overwrite)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)
        if self.run_id != old_run_id:
            self.run_id_changed.emit(self.run_id)

    @property
    def base_directory_path(self) -> str:
        return self._base_directory_path
    
    @base_directory_path.setter
    def base_directory_path(self, new_base_directory_path: str) -> None:
        old_file = self.file
        old_overwrite = self.overwrite
        old_valid = self.valid

        self._base_directory_path = new_base_directory_path
        for file_consumer in self.file_consumers:
            file_consumer.base_directory_path = self.base_directory_path

        if self.file != old_file:
            self.file_changed.emit(self.file)
        if self.overwrite != old_overwrite:
            self.overwrite_changed.emit(self.overwrite)
        if self.valid != old_valid:
            self.valid_changed.emit(self.valid)

    @property
    def enabled(self) -> bool:
        """
        Whether the node is enabled. Setting this property sets the
        enabled status of each child node to the same value.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, new_enabled: bool):
        self._enabled = new_enabled
        for file_consumer in self.file_consumers:
            file_consumer.enabled = self.enabled
        self.enabled_changed.emit(self.enabled)

    @property
    def file(self) -> str:
        """
        The path to the output file of the operation.
        """
        return QDir(self.base_directory_path).absoluteFilePath(
            "".join(generator.value for generator in self._output_path)
        )

    @property
    def overwrite_file(self) -> str:
        """
        The path to the file to check for an overwrite.
        """
        return QDir(self.base_directory_path).absoluteFilePath(
            "".join(generator.value for generator in self._overwrite_path)
        )

    @property
    def watched_files(self) -> list[str]:
        return [self.overwrite_file]

    @property
    def overwrite(self) -> bool:
        return QFileInfo(self.overwrite_file).exists()

    @property
    def valid(self) -> bool:
        """
        Whether the operation's inputs are in a valid state.
        """
        return all(
            [self._overwrite_parameter.value or not self.overwrite]
            + [parameter.valid for parameter in self.parameters.values()]
            + [consumer.valid for consumer in self._file_consumers]
        )
    
    def reset(self) -> None:
        for consumer in self.file_consumers:
            consumer.reset()
        for parameter in self.parameters.values():
            parameter.reset_value()

    def get_operation_ids(self) -> list[str]:
        operation_ids = []

        for file_consumer in self.file_consumers:
            operation_ids.extend(file_consumer.get_operation_ids())

        operation_ids.append(self.name)
        return operation_ids

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter[Any]],
    ) -> Sequence[str]:
        """
        Get the terminal commands needed to produce the operation's
        input files, then run the operation.

        The command lists of each child node are concatenated, then this
        node's own command is appended to the list.

        :param run_id_paramter: the run ID parameter
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        :type parameters: Sequence[Parameter[Any]]

        :return: the commands
        :rtype: Sequence[str]
        """
        commands = []
        own_command_pieces = [self._cli]

        for file_consumer in self.file_consumers:
            commands.extend(file_consumer.to_cli(run_id_parameter, parameters))
            own_command_pieces.append(file_consumer.cli_parameter)

        own_command_pieces.append(
            run_id_parameter.to_cli(self.id, self.run_id)
        )

        own_command_pieces.append(self._overwrite_parameter.to_cli(self.id))

        for parameter in self.parameters.values():
            own_command_pieces.append(parameter.to_cli(self.id))

        for parameter in parameters:
            own_command_pieces.append(parameter.to_cli(self.id))

        own_command_pieces = [piece for piece in own_command_pieces if piece]
        own_command = " ".join(own_command_pieces)
        commands.append(own_command)

        return commands

    def to_dict(self) -> dict:
        return {
            "file_consumers": [
                consumer.to_dict() for consumer in self.file_consumers
            ],
            "parameters": {
                parameter.name : parameter.to_dict() for parameter in self.parameters.values()
            }
        }

    def populate_from_dict(self, values: dict) -> None:
        if "file_consumers" not in values:
            raise ValueError("Missing 'file_consumers' key in dict.")
        file_consumer_values_list = values["file_consumers"]
        if not isinstance(file_consumer_values_list, list):
            raise ValueError(
                f"Wrong 'file_consumers': {file_consumer_values_list}. "
                + "Expected a list."
            )
        if len(file_consumer_values_list) != len(self.file_consumers):
            raise ValueError(
                "Mismatched length of 'file_consumers'."
            )
        for i, file_consumer_values in enumerate(file_consumer_values_list):
            if not isinstance(file_consumer_values, dict):
                raise ValueError(
                    f"Wrong item in 'file_consumers': {file_consumer_values}. "
                    + "Expected a dict."
                )
            self.file_consumers[i].populate_from_dict(file_consumer_values)

        if "parameters" not in values:
            raise ValueError("Missing 'parameters' key in dict.")
        parameters_dict = values["parameters"]
        if not isinstance(parameters_dict, dict):
            raise ValueError(
                f"Wrong 'parameters': {parameters_dict}. "
                + "Expected a dictionary."
            )
        for parameter in self.parameters.values():
            if parameter.name in parameters_dict:
                parameter.populate(parameters_dict[parameter.name])

    @Slot(bool)
    def _consumer_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)

    @Slot()
    def _overwrite_parameter_value_changed(self) -> None:
        self.valid_changed.emit(self.valid)

    @Slot()
    def _parameter_value_changed(self) -> None:
        self.file_changed.emit(self.file)
        self.valid_changed.emit(self.valid)
        self.overwrite_changed.emit(self.overwrite)


class OperationTree(QObject):
    """
    An operation tree.

    An `OperationTree` object holds a reference to an `OperationNode` as
    its root.

    The recommended way of creating operation trees is through the
    `build_trees` factory method.
    """

    valid_changed = Signal(bool)

    def __init__(
            self,
            root: OperationNode,
            enabled: bool = False,
    ) -> None:
        """
        Initialize an `OperationTree` object.

        :param root: the operation node at the root of the tree
        :type root: OperationNode

        :param enabled: whether the tree is initially enabled
        :type enabled: bool
        """
        super().__init__()
        self._root = root
        self.root.enabled = enabled
        self.root.valid_changed.connect(self._root_valid_changed)

    @property
    def root(self) -> OperationNode:
        """
        The `OperationNode` at the root of the tree.
        """
        return self._root

    def _set_run_id(self, new_run_id: str) -> None:
        self.root.run_id = new_run_id

    run_id = property(fset=_set_run_id)

    def _set_base_directory_path(self, new_base_directory_path: str) -> None:
        self.root.base_directory_path = new_base_directory_path

    base_directory_path = property(fset=_set_base_directory_path)

    @property
    def enabled(self) -> bool:
        """
        Whether the tree is enabled. Setting this property sets the
        enabled status of the root node to the same value.
        """
        return self.root.enabled

    @enabled.setter
    def enabled(self, new_enabled: bool) -> None:
        self.root.enabled = new_enabled

    @property
    def valid(self) -> bool:
        return self.root.valid

    @classmethod
    def build_trees(
            cls,
            operations: Mapping[str, Operation],
            overwrite_parameter_builder: Callable[[], Parameter[Any]],
            run_id: str = "",
            base_directory_path: str = "",
    ) -> tuple[list["OperationTree"], Mapping[str, OrCondition]]:
        """
        For each operation in a given list, create an operation tree
        with that operation as the root.

        The trees are built by a breadth-first search algorithm. The
        root operation node is explored first. When an operation node is
        visited, the required file of each of its file consumer children
        is compared to the produced file of each operation. If a match
        is found, a node is constructed for that operation and added to
        the tree, as well as to the queue of unexplored operation nodes.

        While constructing the tree, the method creates an
        `OperationNode.EnabledCondition` for each operation node. At the
        end, the conditions for each operation are wrapped in an
        `OrCondition` and returned alongside the constructed trees. The
        conditions can be used to enable parameters when at least one
        instance of the operation they belong to is enabled.

        :param operations: a dictionary from ID to operation
        :type operations: dict[str, Operation]

        :param overwrite_parameter_builder: A function that produces the
        overwrite parameter for common parent directory nodes.
        :type overwrite_parameter_builder: Callable[[], Parameter[Any]]

        :param run_id: the initial run ID
        :type run_id: str

        :param base_directory_path: the initial base file path for the
        output locations of operation nodes
        :type base_directory_path: str

        :return: the list of operation trees and the mapping from
        operation ID to condition
        :rtype: tuple[list[OperationTree], Mapping[str, Condition]]
        """
        trees: list[OperationTree] = []
        # Initialize the dictionary from operation ID to disjunction
        # condition for operation nodes with that operation.
        operation_id_to_condition: Mapping[str, OrCondition] = {
            operation_id: OrCondition() for operation_id in operations
        }
        for root_operation_id in operations:
            root_operation = operations[root_operation_id]
            root_node = OperationNode(
                root_operation,
                run_id=run_id,
                base_directory_path=base_directory_path,
            )
            # Create an EnabledCondition for the root node.
            operation_id_to_condition[root_operation_id].add_condition(
                OperationNode.EnabledCondition(
                    root_node,
                ),
            )

            # Create a queue of unexplored operation nodes for BFS.
            unexplored_nodes: list[OperationNode] = [root_node]
            while unexplored_nodes:
                current_node = unexplored_nodes[0]
                unexplored_nodes = unexplored_nodes[1:]

                for file_consumer in current_node.file_consumers:
                    for candidate_id in operations:
                        candidate_operation = operations[candidate_id]
                        if (candidate_operation.produces
                            == file_consumer.requires):
                            operation_node = OperationNode(
                                candidate_operation,
                                run_id=run_id,
                                base_directory_path=base_directory_path,
                            )
                            file_consumer.add_producer(operation_node)
                            unexplored_nodes.append(operation_node)
                            # Create an EnabledCondition for the node.
                            operation_id_to_condition[
                                candidate_id
                            ].add_condition(
                                OperationNode.EnabledCondition(
                                    operation_node,
                                )
                            )
                    # If the consumer is expecting a directory, try
                    # producing that directory from multiple operations.
                    if (isinstance(file_consumer.requires, Directory)
                        and len(file_consumer.requires.contents) > 1):
                        common_parent_dir = CommonParentDirectoryNode(
                            file_consumer.requires,
                            overwrite_parameter_builder,
                        )
                        # There might not be a suitable operation for
                        # every file in the directory, so keep additions
                        # to the queue and dictionary separate for now.
                        possible_unexplored = []
                        possible_conditions = {
                            operation_id: [] for operation_id in operations
                        }
                        operations_exist: bool = True
                        for sub_consumer in common_parent_dir.file_consumers:
                            operation_exists: bool = False
                            for candidate_id in operations:
                                candidate_operation = operations[candidate_id]
                                if (candidate_operation.produces
                                    == sub_consumer.requires):
                                    operation_exists = True
                                    operation_node = OperationNode(
                                        candidate_operation,
                                        run_id=run_id,
                                        base_directory_path=base_directory_path,
                                    )
                                    possible_conditions[candidate_id].append(
                                        OperationNode.EnabledCondition(
                                            operation_node,
                                        )
                                    )
                                    sub_consumer.add_producer(operation_node)
                                    possible_unexplored.append(operation_node)
                            if not operation_exists:
                                operations_exist = False
                                break
                        # If an operation has been found for every file,
                        # add the node to the tree and extend the queue
                        # and conditions.
                        if operations_exist:
                            file_consumer.add_producer(common_parent_dir)
                            unexplored_nodes.extend(possible_unexplored)
                            for operation_id in possible_conditions:
                                for cond in possible_conditions[operation_id]:
                                    operation_id_to_condition[
                                        operation_id
                                    ].add_condition(cond)

            tree = OperationTree(root_node)
            trees.append(tree)

        return trees, operation_id_to_condition

    def reset(self) -> None:
        self.root.reset()

    def get_operation_ids(self) -> list[str]:
        """
        Get the operation ids corresponding to the commands of `to_cli`.
        """
        return self.root.get_operation_ids()

    def to_cli(
            self,
            run_id_parameter: StringParameter,
            parameters: Sequence[Parameter[Any]],
    ) -> Sequence[str]:
        """
        Get the terminal commands generated by the tree's root node.

        The run ID parameter must be provided so that each operation
        node can inject its own ID.

        :param run_id_paramter: the run ID parameter
        :type run_id_parameter: StringParameter

        :param parameters: the parameters to use in the commands
        :type parameters: Sequence[Parameter[Any]]

        :return: the commands
        :rtype: Sequence[str]
        """
        return self.root.to_cli(run_id_parameter, parameters)

    def to_dict(self) -> dict:
        return self.root.to_dict()

    def populate_from_dict(self, values: dict) -> None:
        self.root.populate_from_dict(values)

    @Slot(bool)
    def _root_valid_changed(self, new_valid: bool) -> None:
        self.valid_changed.emit(self.valid)
