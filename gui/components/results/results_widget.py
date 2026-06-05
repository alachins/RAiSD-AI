from PySide6.QtCore import (
    Qt,
    QDir,
    Slot,
    QUrl,
)
from PySide6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QLabel,
    QFileSystemModel,
    QTreeView,
    QHeaderView,
    QPushButton,
    QSizePolicy,
)
from PySide6.QtGui import QDesktopServices

from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.components import (
    StylableWidget,
    VBoxLayout,
    HBoxLayout,
)
from gui.components.parameter import ParameterForm
from gui.components.collapsible import Collapsible
from gui.style import constants


class ResultsWidget(StylableWidget):
    """
    The results of a completed execution shown.
    """
    def __init__(self, run_record: RunRecord):
        """
        Initialize a `ResultsWidget` object.

        :param run_record: the result to display
        :type run_record: RunResult
        """
        super().__init__()
        self._run_record = run_record
        self.setObjectName('results_widget')
        layout = VBoxLayout(
            self,
            spacing=constants.GAP_TINY,
        )

        self.files_widget_stack = QStackedWidget()
        self.files_widget_stack.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Folder widget
        self.files_widget = QWidget()
        files_layout = VBoxLayout(
            self.files_widget,
            spacing=constants.GAP_TINY,
        )

        header_widget = QWidget()
        header_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        header_layout = HBoxLayout(
            header_widget,
        )

        self.files_label = QLabel("Files in the generated directory")
        header_layout.addWidget(self.files_label, 1)

        self.path = ""
        self.file_browser_button = QPushButton("Open Directory")
        self.file_browser_button.setObjectName("file_browser_button")
        self.file_browser_button.clicked.connect(self._file_browser_button_clicked)
        header_layout.addWidget(self.file_browser_button)

        files_layout.addWidget(header_widget)

        self.folder_structure = QFileSystemModel()
        self.folder_widget = QTreeView()

        self.folder_widget.horizontalScrollBar().setEnabled(True)
        self.folder_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.folder_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.folder_widget.setObjectName("folder_widget")
        self.folder_widget.doubleClicked.connect(self._on_double_click)
        self.folder_widget.setMinimumHeight(int(self.height()))
        self.folder_widget.setMaximumHeight(int(self.height()))
        files_layout.addWidget(self.folder_widget, 1)


        self.files_widget_stack.addWidget(self.files_widget)

        self.no_files_label = QLabel(
            "The output directory does not exist anymore.", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.files_widget_stack.addWidget(self.no_files_label)

        #layout.addWidget(self.files_widget_stack, 1)
        layout.addWidget(self.files_widget_stack) 

        # Parameter widget
        parameters_header = QLabel("Parameters used")
        parameter_form = ParameterForm(self._run_record, editable=False)
        parameters_collapsible = Collapsible(parameters_header, parameter_form)
        layout.addWidget(parameters_collapsible)

        layout.addStretch()  

    def show_results(self) -> None:
        """
        Updates the ResultWidget with results in the RunRecord.
        """
        # Set folder widget to right folder
        self.path = app_settings.workspace_path.filePath(self._run_record.run_id)
        if not QDir(self.path).exists():
            self.files_widget_stack.setCurrentWidget(self.no_files_label)
        else:
            self.files_label.setText(f"Files in the output directory '{app_settings.workspace_path.dirName()}/{self._run_record.run_id}':")
            self.folder_structure.setRootPath(self.path)
            self.folder_widget.setModel(self.folder_structure)
            self.folder_widget.setRootIndex(self.folder_structure.index(self.path))
            # self.folder_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header = self.folder_widget.header()
            #header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) #Stretch)  # Name
            #header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Size
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Date ResizeToContents
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Date ResizeToContents
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Date ResizeToContents
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Date ResizeToContents
            self.folder_widget.setColumnWidth(0, 600)  # Name
            self.folder_widget.setColumnWidth(1, 100)  # Size
            self.folder_widget.setColumnWidth(2, 200)  # Type
            self.folder_widget.setColumnWidth(3, 150)  # Date
            self.files_widget_stack.setCurrentWidget(self.files_widget)

    @Slot(int)
    def _on_double_click(self, index) -> None:
        if not self.folder_structure.isDir(index):
            path = self.folder_structure.filePath(index)
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @Slot()
    def _file_browser_button_clicked(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.path))
