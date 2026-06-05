from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QLabel,
)

from .history_record_widget import HistoryRecordWidget
from gui.model.history_record import HistoryRecord
from gui.components import (
    StylableWidget,
    VBoxLayout,
)
from gui.style import constants


class HistoryListWidget(StylableWidget):
    """
    The widget that holds the all operation records to display in history_widget
    """
    run_selected = Signal(HistoryRecord)

    def __init__(
            self,
            history_records: list[HistoryRecord] | None = None,
    ) -> None:
        super().__init__()
        self._history_records = history_records or []
        self._history_widgets: list[HistoryRecordWidget] = []
        self.setObjectName('history_list_widget')

        layout = VBoxLayout(self)
        layout.setSpacing(constants.GAP_SMALL)

        title = QLabel("History")
        title.setProperty("title", "true")
        layout.addWidget(title)

        # The list of history widgets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(
            scroll_area.verticalScrollBarPolicy().ScrollBarAlwaysOff
        )
        layout.addWidget(scroll_area)

        self._list_container = QWidget()
        self._list_container.setObjectName("history_list_container")
        self._list_layout = VBoxLayout(self._list_container)
        self._list_layout.setSpacing(constants.GAP_TINY)
        self._list_layout.addStretch()
        scroll_area.setWidget(self._list_container)

        # Add the widgets to the list
        for record in self._history_records:
            widget = self._add_record_widget(record)
            self._history_widgets.append(widget)

    def clear(self) -> None:
        """
        Clears the history list.
        """
        for widget in self._history_widgets:
            widget.setParent(None)
        self._history_widgets.clear()
        self._history_records.clear()

    def add_record(self, history_record: HistoryRecord) -> None:
        """
        Adds a history record to the HistoryList.
        """
        self._history_records.insert(0, history_record)
        widget = self._add_record_widget(history_record, at_top = True)
        self._history_widgets.append(widget)

    def _add_record_widget(self, history_record: HistoryRecord, at_top: bool = False) -> HistoryRecordWidget:
        """
        Adds a history record by creating it and setting its size and 
        interactivity.
        """
        widget = HistoryRecordWidget(history_record)
        widget.setMinimumHeight(widget.minimumSizeHint().height())
        widget.mousePressEvent = lambda _: self.run_selected.emit(history_record)
        if at_top:
            self._list_layout.insertWidget(0, widget)
        else:
            count = self._list_layout.count()
            self._list_layout.insertWidget(count - 1, widget)
        return widget

    def update_time(self) -> None:
        """
        Updates the time label of all the history widgets.
        """
        for widget in self._history_widgets:
            widget.update_time()
