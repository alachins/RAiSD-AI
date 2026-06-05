"""
Utility classes for displaying text with an icon, e.g. as a warning.

Clicking the icon toggles the text and background visibility.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import(
    QLabel,
    QStyle,
)

from gui.components import (
    HBoxLayout,
    StylableWidget,
)
from gui.style import constants


class IconLabel(StylableWidget):
    """
    Base class for icon labels.

    An `IconLabel` combines the provided icon and text in a horizontal
    layout. Visibility of the text and the background are determined by expanded parameter.
    """

    def __init__(
            self,
            pixmapi: QStyle.StandardPixmap,
            text: str,
            expanded: bool,
    ) -> None:
        """
        Initialize an `IconLabel` object.

        :param pixmapi: the standard pixmap enum value
        :type pixmapi: QStyle.StandardPixmap

        :param text: the text to display
        :type text: str

        :param expanded: whether the text is expanded
        :type expanded: bool
        """
        super().__init__()
        layout = HBoxLayout(
            self,
            left=constants.GAP_TINY,
            top=constants.GAP_TINY,
            right=constants.GAP_TINY,
            bottom=constants.GAP_TINY,
            spacing=constants.GAP_TINY,
        )

        self._icon_label = QLabel()
        self._icon_label.setCursor(Qt.CursorShape.PointingHandCursor)
        pixmap = self.style().standardPixmap(pixmapi)
        self._icon_label.setPixmap(pixmap)
        self._icon_label.setToolTip("Click to see more")
        layout.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignTop)

        self.text_label = QLabel(text)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label, stretch=1)

        self.expanded = expanded

    @property
    def text(self) -> str:
        return self.text_label.text()

    @text.setter
    def text(self, new_text: str) -> None:
        self.text_label.setText(new_text)

    @property
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, value: bool) -> None:
        self._expanded = value
        self.text_label.setVisible(value)
        if value:
            self._icon_label.setToolTip("Click to hide")
        else:
            self._icon_label.setToolTip("Click to see more")
        self.setProperty("expanded", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.updateGeometry()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.expanded = not self.expanded
        else:
            super().mousePressEvent(event)


class InfoLabel(IconLabel):
    """
    A label with an 'i' (info) icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize an `InfoLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxInformation,
            text=text,
            expanded=False,
        )
        self.setObjectName("info_label")


class WarningLabel(IconLabel):
    """
    A label with a warning sign icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize a `WarningLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxWarning,
            text=text,
            expanded=True,
        )
        self.setObjectName("warning_label")


class ErrorLabel(IconLabel):
    """
    A label with an error icon.
    """

    def __init__(self, text: str) -> None:
        """
        Initialize an `ErrorLabel` object.

        :param text: the text to display
        :type text: str
        """
        super().__init__(
            pixmapi=QStyle.StandardPixmap.SP_MessageBoxCritical,
            text=text,
            expanded=True,
        )
        self.setObjectName("error_label")
