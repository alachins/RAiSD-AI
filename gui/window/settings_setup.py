from PySide6.QtCore import (
    QDir,
    Slot
)
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QLabel,
    QPushButton,
    QDialogButtonBox,
)

from gui.style import constants
from gui.components import VBoxLayout, StylableWidget
from gui.model.settings import app_settings
from gui.components.settings import SettingsItemWidget, set_settings


class SettingsSetup():
     
    class SetupDialog(QDialog):
        """
        A dialog for displaying and setting the application settings.
        """

        def __init__(
                self, 
                parent=None, 
                ):
            super().__init__(parent)
            self.setObjectName("settings_dialog")
            self.setWindowTitle("Complete setup")
            self.setModal(True)
            # self.resize(500, 300)

            layout = VBoxLayout(
                self,
                left=constants.GAP_SMALL,
                right=constants.GAP_SMALL,
                top=constants.GAP_TINY,
                bottom=constants.GAP_TINY,
                spacing=constants.GAP_TINY,
            )

            # workspace
            workspace_widget = StylableWidget()
            workspace_widget.setObjectName("container_widget")
            workspace_layout = VBoxLayout(
                workspace_widget,
                left=constants.GAP_SMALL,
                right=constants.GAP_SMALL,
                top=constants.GAP_TINY,
                bottom=constants.GAP_MEDIUM,
                spacing=constants.GAP_TINY,
            )
            workspace_header = QLabel("Select a workspace to use")
            workspace_layout.addWidget(workspace_header)

            self._file_browse = QPushButton('Browse')
            self._file_browse.setObjectName("file_button")
            self._file_browse.clicked.connect(lambda _, i=self._file_browse: self._open_file_dialog_folder(i))
            workspace_layout.addWidget(self._file_browse)
            layout.addWidget(workspace_widget)

            settings_widget = StylableWidget()
            settings_widget.setObjectName("container_widget")
            settings_layout = VBoxLayout(
                settings_widget,
                left=constants.GAP_SMALL,
                right=constants.GAP_TINY,
                top=constants.GAP_TINY,
                bottom=constants.GAP_MEDIUM,
                spacing=constants.GAP_TINY,
            )

            # Executable
            executable_widget = SettingsItemWidget("Executable", app_settings.executable_file_path.absoluteFilePath())
            app_settings.executable_file_path_changed.connect(
                lambda p : executable_widget._update_label(p.absoluteFilePath()))
            executable_widget.button_clicked.connect(set_settings.set_executable_path)
            settings_layout.addWidget(executable_widget)

            # Environment manager
            environment_manager_widget = SettingsItemWidget("Environment manager", app_settings.environment_manager_name)
            app_settings.environment_manager_changed.connect(
                lambda _ : environment_manager_widget._update_label(app_settings.environment_manager_name))
            environment_manager_widget.button_clicked.connect(set_settings.set_environment_manager)
            settings_layout.addWidget(environment_manager_widget)

            # Environment name
            environment_name_widget = SettingsItemWidget("Environment name", app_settings.environment_name)
            app_settings.environment_name_changed.connect(
                lambda _ : environment_name_widget._update_label(app_settings.environment_name)
            )
            environment_name_widget.button_clicked.connect(set_settings.set_environment_name)
            settings_layout.addWidget(environment_name_widget)
            layout.addWidget(settings_widget)

            # OK button
            self.buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            self.buttonbox.setCenterButtons(True)
            self.buttonbox.accepted.connect(self._close_clicked)
            for button in self.buttonbox.buttons():
                button.setObjectName("file_button")
            layout.addWidget(self.buttonbox)
            

        @Slot()
        def _close_clicked(self) -> None:
            """
            Close the dialog if a valid workspace path has been selected. 
            """
            if app_settings._workspace_path:
                self.close()
    
        @Slot(QPushButton)
        def _open_file_dialog_folder(self, button : QPushButton) -> None:
            """
            Helper function that opens the OS file picker. If `multiple`
            is `True`, it uses `getOpenFileNames` to allow for multiple
            file selection. Otherwise, it uses `getOpenFileName` to allow
            only a single file.
            """
            new_path = QFileDialog.getExistingDirectory(
                None,
                "Select Directory",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            if not new_path:  # Check for empty string (canceled)
                return  
            try:
                app_settings.workspace_path = QDir(new_path)
                button.setText(new_path)
            except Exception as e:
                print(f"Error setting workspace: {e}")

    @classmethod
    def initialize_settings(cls) -> None:
        """
        Initialize a settings object by filling it.
        """
        app_settings.from_yaml(app_settings.settings_file_path)
        if not app_settings._workspace_path:
            dialog = cls.SetupDialog()
            dialog.exec()
            
            if app_settings._workspace_path:
                print(f"Workspace path set to: {app_settings._workspace_path.absolutePath()}")
            else:
                app_settings.workspace_path = QDir("./")
                if app_settings._workspace_path:
                    print(f"No workspace path selected. Using default workspace path: {app_settings._workspace_path.absolutePath()}")
