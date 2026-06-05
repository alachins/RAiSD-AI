from PySide6.QtCore import (
    QSize,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QWidget,
)

from gui.components import (
    HBoxLayout,
    VBoxLayout,
)
from gui.style import constants


class Collapsible(QWidget):
    """
    A collapsible widget.

    The widget is made up of a header and a body, both of which can be
    any `QWidget`.
    """

    collapsed_changed = Signal(bool)

    class Header(QWidget):
        """
        A helper class for the header of a collapsible element.
        """

        clicked = Signal()

        def __init__(
                self,
                widget: QWidget,
                arrows: tuple[str, str],
                collapsed: bool
        ) -> None:
            """
            Initialize a `Header` object.

            The `arrows` tuple contains the two symbols to use for the
            arrow: `arrows[0]` for the collapsed state and `arrows[1]`
            for the expanded state.

            :param widget: the widget that occupies the header
            :type widget: QWidget

            :param arrows: the symbols to use for the arrow
            :type arrows: tuple[str, str]

            :param collapsed: whether the widget should be collapsed in
            its initial state
            :type collapsed: bool
            """
            super().__init__()
            self._arrows = arrows
            self._collapsed = collapsed

            layout = HBoxLayout(
                self,
                left=constants.GAP_SMALL,
                top=constants.GAP_TINY,
                bottom=constants.GAP_TINY,
                spacing=constants.GAP_TINY,
            )
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

            self._arrow = QLabel("")
            self._update_arrow()
            layout.addWidget(self._arrow, alignment=Qt.AlignmentFlag.AlignTop)

            # Set stretch to 1 so that the widget takes up all free
            # space. Otherwise, it gets centered.
            layout.addWidget(widget, stretch=1)

        @property
        def collapsed(self) -> bool:
            """
            Whether the header is collapsed.
            """
            return self._collapsed

        @collapsed.setter
        def collapsed(self, value: bool) -> None:
            self._collapsed = value
            self._update_arrow()

        def _update_arrow(self) -> None:
            new_arrow: str = self._arrows[0 if self._collapsed else 1]
            self._arrow.setText(new_arrow)

        def mousePressEvent(self, event: QMouseEvent) -> None:
            if event.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()


    def __init__(
            self,
            header: QWidget,
            content: QWidget,
            arrows: tuple[str, str] = ("▶", "▼"),
            collapsed: bool = True,
    ) -> None:
        """
        Initialize a `Collapsible` object.

        The `arrows` tuple contains the two symbols to use for the
        arrow: `arrows[0]` for the collapsed state and `arrows[1]`
        for the expanded state.

        :param header: the widget to use for the header
        :type header: QWidget

        :param content: the widget to use for the body
        :type content: QWidget

        :param arrows: the symbols to use for the arrow
        :type arrows: tuple[str, str]

        :param collapsed: whether the widget should be collapsed in its
        initial state
        :type collapsed: bool
        """
        super().__init__()
        self._collapsed = collapsed

        layout = VBoxLayout(self)

        self._header = Collapsible.Header(
            header,
            arrows,
            self._collapsed,
        )
        layout.addWidget(self._header)

        self._content = content
        self._content.setVisible(False)
        layout.addWidget(self._content)

        self._header.clicked.connect(self._header_clicked)

    @property
    def collapsed(self) -> bool:
        """
        Whether the widget is collapsed.
        """
        return self._collapsed

    @collapsed.setter
    def collapsed(self, value: bool) -> None:
        self._collapsed = value
        self._header.collapsed = self._collapsed
        self._content.setVisible(not self._collapsed)

        self.collapsed_changed.emit(self.collapsed)

    @Slot()
    def _header_clicked(self) -> None:
        self.collapsed = not self.collapsed
