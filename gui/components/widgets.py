"""
A module containing base UI classes.

The classes extend default PySide widgets and layouts to make them
stylable and remove margins and spacing.
"""

from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QStyle,
    QStyleOption,
)
from PySide6.QtGui import (
    QPainter,
)

from gui.style import constants


class StylableWidget(QWidget):
    """
    A base class for `QWidget`s that will be targeted by an object name
    selector in QSS.

    `QWidget` subclasses that use the `setObjectName` should instead
    subclass `StylableWidget` to have `paintEvent` automatically
    overriden. This ensures QSS is applied to the widget.
    """

    def paintEvent(self, event) -> None:
        # Override paintEvent so that QSS styling is applied.
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget,
            opt,
            painter,
            self,
        )


class LineEdit(QLineEdit):
    """
    A wrapper around `QLineEdit` with fixed width.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            width: int | None = None
    ) -> None:
        super().__init__(parent)
        if width is None:
            width = constants.LINE_EDIT_WIDTH
        self.setFixedWidth(width)


class GridLayout(QGridLayout):
    """
    A wrapper around `QGridLayout` with no margins or spacing.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            horizontal_spacing: int = 0,
            vertical_spacing: int = 0,
    ) -> None:
        """
        Initialize a `GridLayout` object.

        :param parent: the parent widget of this layout
        :type parent: QWidget

        :param left: the left margin
        :type left: int

        :param top: the top margin
        :type top: int

        :param right: the right margin
        :type right: int

        :param bottom: the bottom margin
        :type bottom: int

        :param horizontal_spacing: the horizontal spacing between
        children
        :type horizontal_spacing: int

        :param vertical_spacing: the vertical spacing between children
        :type vertical_spacing: int
        """
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setHorizontalSpacing(horizontal_spacing)
        self.setVerticalSpacing(vertical_spacing)


class HBoxLayout(QHBoxLayout):
    """
    A wrapper around `QHBoxLayout` with no margins or spacing.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        """
        Initialize an `HBoxLayout` object.

        :param parent: the parent widget of this layout
        :type parent: QWidget

        :param left: the left margin
        :type left: int

        :param top: the top margin
        :type top: int

        :param right: the right margin
        :type right: int

        :param bottom: the bottom margin
        :type bottom: int

        :param spacing: the spacing between children
        :type spacing: int
        """
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class VBoxLayout(QVBoxLayout):
    """
    A wrapper around `QVBoxLayout` with no margins or spacing.
    """

    def __init__(
            self,
            parent: QWidget,
            *,
            left: int = 0,
            top: int = 0,
            right: int = 0,
            bottom: int = 0,
            spacing: int = 0,
    ) -> None:
        """
        Initialize a `VBoxLayout` object.

        :param parent: the parent widget of this layout
        :type parent: QWidget

        :param left: the left margin
        :type left: int

        :param top: the top margin
        :type top: int

        :param right: the right margin
        :type right: int

        :param bottom: the bottom margin
        :type bottom: int

        :param spacing: the spacing between children
        :type spacing: int
        """
        super().__init__(parent)
        self.setContentsMargins(left, top, right, bottom)
        self.setSpacing(spacing)


class ResizableStackedWidget(QWidget):
    """
    A stacked widget that scales to the size of the current widget.
    """

    def __init__(
            self,
    ) -> None:
        """
        Initialize a `ResizableStackedWidget` object.
        """
        super().__init__()

        VBoxLayout(self)
        self._widgets : list[QWidget] = []
        self._current_index = 0

    @property
    def current_index(self) -> int:
        """
        The index of the child widget currently displayed.
        """
        return self._current_index

    @current_index.setter
    def current_index(self, new_index: int) -> None:
        self._current_index = new_index
        self._show_current_widget()

    def addWidget(self, widget: QWidget) -> None:
        layout = self.layout()
        if not layout:
            return
        layout.addWidget(widget)
        self._widgets.append(widget)
        self._show_current_widget()

    def _show_current_widget(self) -> None:
        layout = self.layout()
        if not layout:
            return
        if layout.count() == 0:
            return
        for widget in self._widgets:
            widget.hide()
        self._widgets[self.current_index].show()
        self.updateGeometry()
