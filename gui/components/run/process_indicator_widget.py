from enum import Enum

from PySide6.QtCore import (
    Qt, 
    Property, 
    QMargins,
)
from PySide6.QtGui import (
    QPainter, 
    QColor, 
    QFont, 
    QPen,
)
from PySide6.QtWidgets import (
    QWidget, 
    QSizePolicy,
)


class IndicatorState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    STOPPED = "stopped"


class ProcessIndicator(QWidget):
    """
    A rectangular indicator widget that displays text.
    """

    def __init__(self, text: str, size: int = 200):
        super().__init__()
        self._text = text
        self._indicator_size = size
        self._fill_color = QColor()
        self._border_color = QColor()
        self._text_color = QColor()
        self._state = IndicatorState.PENDING

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setObjectName("process_indicator")
        self.setProperty("indicator_state", self._state.value)
        self._apply_size()

    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    # Size

    def set_indicator_size(self, size: int) -> None:
        self._indicator_size = size
        self._apply_size()
        self.update()

    def _apply_size(self) -> None:
        self.setFixedSize(self._indicator_size, self._indicator_size)

    # Color properties
    
    def get_fill_color(self) -> QColor:
        return self._fill_color

    def set_fill_color(self, color: QColor) -> None:
        self._fill_color = QColor(color)
        self.update()

    def get_border_color(self) -> QColor:
        return self._border_color

    def set_border_color(self, color: QColor) -> None:
        self._border_color = QColor(color)
        self.update()

    def get_text_color(self) -> QColor:
        return self._text_color

    def set_text_color(self, color: QColor) -> None:
        self._text_color = QColor(color)
        self.update()

    fillColor = Property(QColor, get_fill_color, set_fill_color)
    borderColor = Property(QColor, get_border_color, set_border_color)
    textColor = Property(QColor, get_text_color, set_text_color)

    # State management

    @property
    def state(self) -> IndicatorState:
        return self._state

    @state.setter
    def state(self, new_state: IndicatorState) -> None:
        self._state = new_state
        self.setProperty("indicator_state", new_state.value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # Painting

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = self._indicator_size
        margin = 3
        rect_size = size - 2 * margin

        # Fill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._fill_color)
        # Calculate vertical offset to center the rectangle
        rect_height = int(rect_size * 0.7)
        vertical_offset = (rect_size - rect_height) // 2
        
        painter.drawRect(margin, margin + vertical_offset, rect_size, rect_height)

        # Border
        pen = QPen(self._border_color, 3)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(margin, margin + vertical_offset, rect_size, rect_height)

        # Text
        font = QFont()
        font.setPixelSize(int(size * 0.15))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(self._text_color)
        rect = self.rect()
        rect = rect.marginsRemoved(QMargins(2, 2, 2, 2))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, str(self._text))

        painter.end()
