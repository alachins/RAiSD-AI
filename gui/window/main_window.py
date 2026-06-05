from PySide6.QtCore import (
    Slot,
    QDir
)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedLayout,
    QPushButton,
    QApplication,
)

from PySide6.QtGui import (
    QCursor, Qt,
)

from gui.model.settings import app_settings
from gui.model.run_record import RunRecord
from gui.model.history_record import HistoryRecord
from gui.execution.command_executor import CommandExecutor
from gui.components import (
    HBoxLayout,
    VBoxLayout,
)
from gui.pages import (
    RunPage,
    HistoryPage,
    SettingsPage
)
from gui.style import constants

class MainWindow(QMainWindow):
    """
    The main window of the RAiSD-AI GUI application.
    """
    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()
        app_settings.config_path_changed.connect(self._init_main_window)
        self._init_main_window()

    def _init_main_window(self) -> None:
        run_record = RunRecord.from_yaml(app_settings.config_path.absoluteFilePath())
        self.run_record = run_record
        self.command_executor = CommandExecutor(run_record)
        QApplication.processEvents() # Necessary for the splash screen to load
        self._setup_ui()
        self.run_page.run_saved.connect(self.history_page.add_completed_run)

    def _setup_ui(self):
        app_settings.workspace_path_changed.connect(self._set_workspace_path_title)
        self._set_workspace_path_title(app_settings.workspace_path)

        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        central_layout = HBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Left sidebar
        left_sidebar = QWidget()
        left_sidebar.setObjectName("left_sidebar")
        left_sidebar_layout = VBoxLayout(
            left_sidebar,
            left=constants.GAP_TINY,
            top=constants.GAP_MEDIUM,
            right=constants.GAP_TINY,
            bottom=constants.GAP_TINY,
            spacing=constants.GAP_TINY,
        )

        central_layout.addWidget(left_sidebar)
        self._setup_left_sidebar(left_sidebar_layout)

        # Main stacked widget
        main_widget = QWidget()
        self.main_widget_layout = QStackedLayout(main_widget)
        central_layout.addWidget(main_widget)
        self._setup_main_widget(self.main_widget_layout)

        # Mapping between sidebar buttons and stack pages
        self.button_page_pairs = {
            self.run_button: self.run_page,
            self.history_button: self.history_page,
            self.settings_button: self.settings_page
        }

        for button in self.findChildren(QPushButton):
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self._set_active_view(self.run_button)

    def _setup_left_sidebar(self, layout: VBoxLayout):
        logo_widget = QWidget()
        logo_widget.setFixedSize(40, 40)
        logo_widget.setObjectName("logo_widget")
        layout.addWidget(logo_widget)

        layout.addSpacing(constants.GAP_TINY)

        # Run Button
        self.run_button = QPushButton()
        self.run_button.clicked.connect(lambda: self._set_active_view(self.run_button))
        self.run_button.setObjectName("run_button")
        self.run_button.setFixedSize(40, 40)
        layout.addWidget(self.run_button)

        # History Button
        self.history_button = QPushButton()
        self.history_button.clicked.connect(lambda: self._set_active_view(self.history_button))
        self.history_button.setObjectName("history_button")
        self.history_button.setFixedSize(40, 40)
        layout.addWidget(self.history_button)

        layout.addStretch()

        # Settings Button
        self.settings_button = QPushButton()
        self.settings_button.clicked.connect(lambda: self._set_active_view(self.settings_button))
        self.settings_button.setObjectName("settings_button")
        self.settings_button.setFixedSize(40, 40)
        layout.addWidget(self.settings_button)


    def _setup_main_widget(self, layout: QStackedLayout):
        self.run_page = RunPage(self.run_record, self.command_executor)
        self.history_page = HistoryPage()
        self.history_page.reuse_run_clicked.connect(self._reuse_run)
        self.settings_page = SettingsPage()

        app_settings.workspace_path_changed.connect(self.run_page.reset_page)
        app_settings.workspace_path_changed.connect(self.history_page.reset_page)

        layout.addWidget(self.run_page)
        layout.addWidget(self.history_page)
        layout.addWidget(self.settings_page)

    @Slot(HistoryRecord)
    def _reuse_run(self, history_record: HistoryRecord) -> None:
        self.run_record.populate(history_record)
        self.run_page.reuse_run()
        self._set_active_view(self.run_button)

    def _set_active_view(self, active_button: QPushButton) -> None:
        for i, (button, page) in enumerate(self.button_page_pairs.items()):
            if button == active_button:
                state = "active"
                self.main_widget_layout.setCurrentWidget(page)
            else:
                state = "default"
            button.setProperty("state", state)
            button.style().unpolish(button)  # Required to apply styling dynamically
            button.style().polish(button)

    def _set_workspace_path_title(self, new_workspace: QDir, max_len: int = 30) -> None:
        """
        Update the window title to reflect the new workspace path.

        Shortens the path if it exceeds a certain length.
        
        :param new_workspace: the new workspace path
        :type new_workspace: QDir

        :param max_len: the maximum length of the path to display
        :type max_len: int
        """
        new_workspace_path = new_workspace.absolutePath()
        if len(new_workspace_path) > max_len:
            self.setWindowTitle(f"RAiSD-AI-GUI - '..{new_workspace_path[-max_len + 2:]}'")
        else:
            self.setWindowTitle(f"RAiSD-AI-GUI - '{new_workspace_path}'")

    