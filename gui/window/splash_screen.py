from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSplashScreen,
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QColor,
    QRgba64,
)

from gui.style import constants


class SplashScreen(QSplashScreen):
    """
    A splash screen that displays the RAiSD-AI GUI splash image with
    support for showing messages in the bottom-left corner.
    """

    def __init__(
            self, 
            text_color: QColor = QColor(10,13,79), 
            alignment : int =  Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        ) -> None:
        """
        Initialize a `SplashScreen` object.
        """
        self._message = ""
        self._text_color = text_color
        self._alignment = alignment

        pixmap = QPixmap("gui/style/resources/Raisd_ai_splash_screen.png")
        super().__init__(pixmap)
        self.setWindowFlag(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)

    def drawContents(self, painter: QPainter) -> None:
        """
        Override drawContents to render the message with a margin.
        """
        painter.setPen(self._text_color)
        rect = self.rect().adjusted(
            constants.GAP_TINY,   # left
            0,   # top
            0,  # right
            -constants.GAP_TINY,  # bottom
        )
        painter.drawText(
            rect,
            self._alignment,
            self._message,
        )

    def showMessage(
            self, 
            message: str, 
            /, 
            alignment: int = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            color = QColor(10,13,79)
        ) -> None:
        """
        Show a message in the bottom-left corner of the splash screen.

        :param message: the message to display
        :type message: str

        :param alignment: the alignment of the message
        :type alignment: int

        :param color: the text color
        :type color: QColor
        """
        self._message = message
        self._alignment = alignment
        self._text_color = color
        self.repaint()
