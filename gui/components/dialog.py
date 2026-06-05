from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
)

class ConfirmDialog(QMessageBox):
    """
    A simple confirmation dialog that asks the user to confirm an action.
    """
    def __init__(self, parent: QWidget, title: str, text: str):
        """
        Initialize a `ConfirmDialog` object.
        
        :param parent: the parent of the dialog
        :type parent: QWidget

        :param title: the title of the dialog
        :type title: str

        :param text: the text in the dialog
        :type text: str
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setText(text)
        self.setIcon(QMessageBox.Icon.Warning)
        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        self.setDefaultButton(QMessageBox.StandardButton.Cancel)

class ErrorDialog(QMessageBox):
    """
    A simple dialog that gives the user information about an error.
    """
    def __init__(self, parent:QWidget, title:str, error:str):
        """
        Initialize an `ErrorDialog` object.

        :param parent: the parent of the dialog
        :type parent: QWidget

        :param title: the title of the dialog
        :type title: str

        :param error: the error
        :type error: str
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setText(error)
        self.setIcon(QMessageBox.Icon.Critical)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setDefaultButton(QMessageBox.StandardButton.Ok)