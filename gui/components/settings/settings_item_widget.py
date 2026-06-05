from PySide6.QtCore import (
    Signal
)
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
)

from gui.components import (
    HBoxLayout,
    StylableWidget
)
from gui.style import constants

class SettingsItemWidget(StylableWidget):
    """
    A widget for a single setting. 
    Includes a name, current value and button to set it.
    """

    button_clicked = Signal()

    def __init__(self, name: str, value: str, button: bool = True):
        """
        Initialize the widget for a single setting.
        """
        super().__init__()
        self._name = name
        self._value = value
        self.setObjectName("settings_item_widget")
        layout = HBoxLayout(self, spacing=constants.GAP_TINY)

        # Label to show the workspace folderpath
        self.label = QLabel(self)
        self._update_label(self._value)
        layout.addWidget(self.label, 1)

        # Button to select a new workspace
        if button:
            self.chooser = QPushButton(f"Change {self._name}")
            self.chooser.clicked.connect(self.button_clicked)
            layout.addWidget(self.chooser)

        layout.addSpacing(10)   
        
    def _update_label(self, value: str) -> None:
        """
        Update the label of a setting when the current value changes. 
        """
        self._value = value
        self.label.setText(f"{self._name}: '{self._value}'")