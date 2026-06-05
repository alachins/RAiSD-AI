from PySide6.QtCore import (
    QDir,
    QFileInfo,
    Slot
)
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QLineEdit
)

from gui.model.settings import app_settings
from gui.components import VBoxLayout
from gui.style import constants


def set_workspace_folder() -> None:
    """
    Open a file dialog to select a new workspace folder and update the workspace path.

    If the user selects a new workspace folder, 
    the workspace path is updated and the `workspace_path_changed` signal is emitted.

    If the user cancels the dialog, the workspace path remains unchanged.
    If the the selected path is invalid, the workspace path remains unchanged.
    """
    new_workspace_folder_str = QFileDialog.getExistingDirectory(
        None,
        "Select Workspace Folder",
        app_settings.workspace_path.absolutePath(),
        QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks
    )
    if not new_workspace_folder_str:  # Check for empty string (canceled)
        return  
    try:
        app_settings.workspace_path = QDir(new_workspace_folder_str)
    except Exception as e:
        print(f"Error setting workspace: {e}")

def set_executable_path() -> None:
    """
    Open a file dialog to select a new executable file.
    # TODO: check that the file is a (RAiSD) executable?
    """
    new_executable_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            app_settings.executable_file_path.absolutePath(),
        )
    if not new_executable_path:  # Check for empty string (canceled)
        return  
    try:
        app_settings.executable_file_path = QFileInfo(new_executable_path)
    except Exception as e:
        print(f"Error setting workspace: {e}")

def set_environment_manager() -> None:
    """
    Open a dialog to select a new environment manager.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Choose environment manager")
    dialog.setModal(True)
    dialog.resize(300, 200)

    layout = VBoxLayout(dialog, spacing=constants.GAP_TINY)

    combo_box = QComboBox()
    combo_box.addItems(app_settings.environment_managers)
    combo_box.setCurrentIndex(app_settings.environment_manager)
    layout.addWidget(combo_box)

    buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    buttonbox.setCenterButtons(True)
    buttonbox.accepted.connect(
        lambda : _on_environment_manager_select(combo_box.currentIndex()))
    layout.addWidget(buttonbox)

    @Slot(int)
    def _on_environment_manager_select(index: int) -> None:
        """
        Set the environment manager to the new value and close the dialog.
        # TODO: check that the environment manager is installed?

        :param index: the index of the new environment manager
        :type index: int
        """
        app_settings.environment_manager = index
        dialog.close()

    dialog.exec()

def set_environment_name() -> None:
    """
    Open a dialog to choose a new environment name.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Choose environment name")
    dialog.setModal(True)
    dialog.resize(300, 200)

    layout = VBoxLayout(dialog, spacing=constants.GAP_TINY)

    line_edit = QLineEdit()
    line_edit.setText(app_settings.environment_name)
    layout.addWidget(line_edit)

    buttonbox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    buttonbox.setCenterButtons(True)
    buttonbox.accepted.connect(
        lambda : _on_environment_name_select(line_edit.text()))
    layout.addWidget(buttonbox)

    @Slot(str)
    def _on_environment_name_select(name: str) -> None:
        """
        Set the environment name to the new value and close the dialog.
        # TODO: check that the environment exists?

        :param name: the name of the environment
        :type name: str
        """
        app_settings.environment_name = name
        dialog.close()

    dialog.exec()

def set_config_path() -> None:
    """
    Open a file dialog to select a new config file.
    # TODO: check the contents of the file?
    """
    new_config_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            app_settings.config_path.absolutePath(),
        )
    if not new_config_path:  # Check for empty string (canceled)
        return  
    try:
        app_settings.config_path = QFileInfo(new_config_path)
    except Exception as e:
        print(f"Error setting workspace: {e}")