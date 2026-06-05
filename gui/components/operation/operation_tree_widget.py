"""
A module defining the widgets that allow the user to visualize and
interact with an operation tree.

Other modules only need to import `OperationTreeWidget`.
"""

from PySide6.QtCore import (
    Qt,
    Slot,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QPushButton,
    QRadioButton,
    QWidget,
)

from gui.model.settings import app_settings
from gui.model.operation import (
    FileProducerNode,
    FileConsumerNode,
    CommonParentDirectoryNode,
    FilePickerNode,
    OperationNode,
    OperationTree,
    SingleFile,
    Directory,
)
from gui.components.label import (
    InfoLabel,
    WarningLabel,
)
from gui.components import (
    HBoxLayout,
    ResizableStackedWidget,
    StylableWidget,
    VBoxLayout,
)
from gui.components.parameter import ParameterWidget
from gui.style import constants


class FileProducerNodeWidget(StylableWidget):
    """
    An abstract widget class to display a `FileProducerNode`.

    Use the `from_file_producer` class method to construct the suitable
    widget for a `FileProducerNode` instance based on its class.
    """

    @classmethod
    def from_file_producer(
            cls,
            file_producer: FileProducerNode
    ) -> "FileProducerNodeWidget":
        """
        Construct the suitable widget for a file producer node.

        :param file_producer: the file producer node
        :type file_producer: FileProducerNode
        """
        match file_producer:
            case FilePickerNode():
                return FilePickerNodeWidget(file_producer)
            case OperationNode():
                return OperationNodeWidget(file_producer)
            case CommonParentDirectoryNode():
                return CommonParentDirectoryNodeWidget(file_producer)
            case _:
                raise NotImplementedError(
                    "Cannot create widget for unknown file producer node."
                )

    @property
    def button_text(self) -> str:
        """
        The text to be displayed on the button that selects this widget.
        """
        raise NotImplementedError()

    def refresh(self) -> None:
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()


class FileConsumerNodeWidget(StylableWidget):
    """
    A widget to display a `FileConsumerNode`.

    The widget explains to the user what purpose a file is needed for,
    and presents the options for obtaining that file, i.e. the child
    `FileProducerNode`s. If there are multiple such options, the user
    can select one of them by a menu of radio buttons. The widget for
    the currently selected option is displayed.
    """

    def __init__(self, file_consumer_node: FileConsumerNode):
        """
        Initialize a `FileConsumerNodeWidget` object.

        :param file_consumer_node: the file consumer node to display
        :type file_consumer_node: FileConsumerNode
        """
        super().__init__()
        self.setObjectName("file_consumer_node")
        self._file_consumer_node = file_consumer_node
        self._file_consumer_node.selected_index_changed.connect(self._selected_index_changed)

        layout = VBoxLayout(
            self,
            left=constants.GAP_SMALL,
            top=constants.GAP_TINY,
            bottom=constants.GAP_TINY,
            spacing=constants.GAP_TINY,
        )

        if self._file_consumer_node.name:
            heading = QLabel(self._file_consumer_node.name)
            layout.addWidget(heading)
            heading.setObjectName("heading")

        if self._file_consumer_node.description:
            description = QLabel(self._file_consumer_node.description)
            description.setWordWrap(True)
            layout.addWidget(description)
            description.setObjectName("description")

        self._buttons: list[QRadioButton] = []
        self._file_producer_widgets: list[FileProducerNodeWidget] = []
        self.file_producer_stack = ResizableStackedWidget()
        self.file_selectors : list[tuple[QRadioButton | None, FileProducerNodeWidget]] = []
        if len(self._file_consumer_node.producers) == 1:
            # There is only one way to produce the required file, so
            # simply display that to the user.
            producer = self._file_consumer_node.producers[0]
            producer_widget = FileProducerNodeWidget.from_file_producer(
                producer,
            )
            self._file_producer_widgets.append(producer_widget)
            self.file_producer_stack.addWidget(producer_widget)
            self.file_selectors.append((None, producer_widget))
        else:
            # There are multiple options for obtaining the file, so
            # present the user with a choice through radio buttons.
            button_widget = QWidget()
            button_layout = VBoxLayout(button_widget)

            for i, producer in enumerate(self._file_consumer_node.producers):
                producer_widget = FileProducerNodeWidget.from_file_producer(
                    producer,
                    )
                button = QRadioButton(producer_widget.button_text)
                button.setChecked(i == self._file_consumer_node.selected_index)
                self._buttons.append(button)
                button_layout.addWidget(button)

                self._file_producer_widgets.append(producer_widget)
                self.file_producer_stack.addWidget(producer_widget)
                self.file_selectors.append((button, producer_widget))

                button.clicked.connect(lambda _, i=i: self._button_clicked(i))
            layout.addWidget(button_widget)
        layout.addWidget(self.file_producer_stack)

    def _button_clicked(self, i: int) -> None:
        self._file_consumer_node.selected_index = i
        self.file_producer_stack.current_index = i

    def refresh(self) -> None:
        for i, button in enumerate(self._buttons):
            button.setChecked(i == self._file_consumer_node.selected_index)

        for file_consumer_widget in self._file_producer_widgets:
            file_consumer_widget.refresh()

    @Slot(int)
    def _selected_index_changed(self, index: int) -> None:
        self.file_producer_stack.current_index = index
        for (i, (button, _)) in enumerate(self.file_selectors):
            if button:
                button.setChecked(i == index)

class CommonParentDirectoryNodeWidget(FileProducerNodeWidget):
    """
    A widget to display a `CommonParentDirectoryNode`.

    The widget displays all files that produce the necessary directory
    in a vertical layout.
    """

    def __init__(self, common_parent_directory: CommonParentDirectoryNode):
        """
        Initialize a `CommonParentDirectoryNodeWidget` object.

        :param common_parent_directory: the common parent directory node to
        display
        :type common_parent_directory: CommonParentDirectoryNode
        """
        super().__init__()
        self.setObjectName("common_parent_directory_node")
        self._common_parent_directory_node = common_parent_directory

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_SMALL,
        )

        heading = QLabel(
            "You can run the operations below "
            + "to generate the necessary input files:"
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        self._overwrite_warning_label = WarningLabel(
            "You are about to overwrite existing data!"
        )
        self._overwrite_warning_label.setVisible(
            self._common_parent_directory_node.overwrite,
        )
        layout.addWidget(self._overwrite_warning_label)

        self._overwrite_parameter_row = ParameterWidget.from_parameter(
            self._common_parent_directory_node.overwrite_parameter,
            editable=True,
        ).build_form_row()
        layout.addWidget(self._overwrite_parameter_row)

        self.file_consumer_widgets : list[FileConsumerNodeWidget]= []
        for file_consumer in self._common_parent_directory_node.file_consumers:
            file_consumer_widget = FileConsumerNodeWidget(file_consumer)
            layout.addWidget(file_consumer_widget)
            self.file_consumer_widgets.append(file_consumer_widget)

        self._common_parent_directory_node.overwrite_changed.connect(
            self._overwrite_changed,
        )

    def refresh(self) -> None:
        self._overwrite_warning_label.setVisible(
            self._common_parent_directory_node.overwrite,
        )
        self._common_parent_directory_node.overwrite_parameter.value = False

        for file_consumer_widget in self.file_consumer_widgets:
            file_consumer_widget.refresh()

    @property
    def button_text(self) -> str:
        return "Run multiple operations to generate the input files."

    @Slot(bool)
    def _overwrite_changed(self, new_overwrite: bool) -> None:
        self._overwrite_warning_label.setVisible(new_overwrite)


class FilePickerNodeWidget(FileProducerNodeWidget):
    """
    A widget to display a `FilePickerNode`.

    The widget explains to the user the type of file that is needed, and allows
    the user to browse their files and select a suitable file or directory.
    """

    def __init__(self, file_picker: FilePickerNode):
        """
        Initialize a `FilePickerNodeWidget` object.

        :param file_picker: the file picker node to display
        :type file_picker: FilePickerNode
        """
        super().__init__()
        self._file_picker = file_picker

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        self._is_directory = isinstance(self._file_picker.produces, Directory)

        self.button = QPushButton("Browse")
        self.button.setObjectName("file_selector_button")
        self.button.clicked.connect(self._browse_button_clicked) 
        layout.addWidget(self.button)

        self._file_picker.file_changed.connect(self._file_picker_file_changed)

    def refresh(self) -> None:
        pass

    def reset(self) -> None:
        pass

    @property
    def button_text(self) -> str:
        if self._is_directory:
            return "Choose a directory on your computer."
        return "Choose a file on your computer."

    def _browse_button_clicked(self):
        if self._is_directory:
            new_path = QFileDialog.getExistingDirectory(
                None,
                "Select Directory",
                app_settings.workspace_path.absolutePath(),
                QFileDialog.Option.ShowDirsOnly
            )
        else:
            new_path, _ = QFileDialog.getOpenFileName(
                None,
                "Select File",
                app_settings.workspace_path.absolutePath(),
            )
        if not new_path:  # Check for empty string (canceled)
            return  
        else:
            self._file_picker.file = new_path

    def _file_picker_file_changed(self, new_file: str):
        if new_file == "":
            self.button.setText("Browse")
        else:
            self.button.setText(new_file)


class OperationNodeWidget(FileProducerNodeWidget):
    """
    A widget to display an `OperationNode`.

    The widget displays the name and description of the operation. The
    necessary input files are displayed side by side below.
    """

    def __init__(self, operation_node: OperationNode):
        """
        Initialize an `OperationNodeWidget` object.

        :param operation_node: the operation node to display
        :type operation_node: OperationNode
        """
        super().__init__()
        self._operation_node = operation_node
        self.setObjectName("operation_node")

        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        name_info = QWidget()
        name_info_layout = HBoxLayout(
            name_info,
            spacing=constants.GAP_TINY,
        )
        name = QLabel(operation_node.name)
        name.setObjectName("heading")
        name.setWordWrap(True)
        name.setAlignment(Qt.AlignmentFlag.AlignTop)
        name_info_layout.addWidget(name)
        self._info_label = InfoLabel(self.info_label_text)
        name_info_layout.addWidget(self._info_label)
        layout.addWidget(name_info)

        description = QLabel(operation_node.description)
        description.setWordWrap(True)
        layout.addWidget(description)

        self.parameter_widgets: list[ParameterWidget] = []
        if self._operation_node.parameters:
            parameter_rows_widget = QWidget()
            parameter_rows_layout = VBoxLayout(parameter_rows_widget)

            for parameter in self._operation_node.parameters.values():
                parameter_widget = ParameterWidget.from_parameter(
                    parameter=parameter,
                    editable=True,
                )
                self.parameter_widgets.append(parameter_widget)
                parameter_row = parameter_widget.build_form_row()
                parameter_rows_layout.addWidget(parameter_row)
            layout.addWidget(parameter_rows_widget)

        self._overwrite_warning_label = WarningLabel(
            "You are about to overwrite existing data!"
        )
        self._overwrite_warning_label.setVisible(
            self._operation_node.overwrite,
        )
        layout.addWidget(self._overwrite_warning_label)

        self._overwrite_parameter_row = ParameterWidget.from_parameter(
            self._operation_node.overwrite_parameter,
            editable=True,
        ).build_form_row()
        layout.addWidget(self._overwrite_parameter_row)

        self.file_consumer_widgets: list[FileConsumerNodeWidget] = []
        if operation_node.file_consumers:
            input_files_widget = QWidget()
            input_files_layout = HBoxLayout(
                input_files_widget,
                spacing=constants.GAP_MEDIUM,
            )
            for file_consumer in operation_node.file_consumers:
                file_consumer_widget = FileConsumerNodeWidget(file_consumer)
                self.file_consumer_widgets.append(file_consumer_widget)
                input_files_layout.addWidget(
                    file_consumer_widget,
                    alignment=Qt.AlignmentFlag.AlignTop,
                    stretch=1,
                )
            layout.addWidget(input_files_widget)

        self._operation_node.file_changed.connect(self._refresh_info_label)
        self._operation_node.overwrite_changed.connect(self._overwrite_changed)
        self._operation_node.run_id_changed.connect(self._refresh_info_label)

    def refresh(self) -> None:
        self._refresh_info_label()
        self._overwrite_warning_label.setVisible(
            self._operation_node.overwrite,
        )
        self._operation_node.overwrite_parameter.value = False

        for file_consumer_widget in self.file_consumer_widgets:
            file_consumer_widget.refresh()

    @property
    def button_text(self) -> str:
        return (
            f"Run {self._operation_node.name} to generate the input file or "
            + "directory."
        )

    @property
    def info_label_text(self) -> str:
        return (
            "The following run ID will be given to RAiSD-AI: "
            + f"{self._operation_node.run_id}\nThe output of the operation "
            + f"will be stored at: {self._operation_node.file}"
        )

    @Slot()
    def _refresh_info_label(self) -> None:
        self._info_label.text = self.info_label_text

    @Slot(bool)
    def _overwrite_changed(self, new_overwrite: bool) -> None:
        self._overwrite_warning_label.setVisible(new_overwrite)


class OperationTreeWidget(StylableWidget):
    """
    A widget to display an `OperationTree`.

    A widget is created for the root operation, which hierarchically
    creates widgets for the other nodes in the tree.
    """

    def __init__(self, operation_tree: OperationTree):
        """
        Initialize an `OperationTreeWidget` object.

        :param operation_tree: the operation tree to display
        :type operation_tree: OperationTree
        """
        super().__init__()
        self.setObjectName("operation_tree")
        self._operation_tree = operation_tree

        layout = HBoxLayout(
            self,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_SMALL,
        )

        self.body = OperationNodeWidget(self._operation_tree.root)
        layout.addWidget(
            self.body,
            alignment=Qt.AlignmentFlag.AlignTop,
        )

    def refresh(self) -> None:
        self.body.refresh()
