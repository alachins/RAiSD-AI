import datetime as dt
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel

from gui.model.settings import app_settings
from gui.model.history_record import HistoryRecord
from gui.components import (
    StylableWidget,
)

class HistoryRecordWidget(StylableWidget):
    """
    A widget for single operation record to be put in the history_list
    """
    def __init__(self, history_record: HistoryRecord):
        super().__init__()
        self._history_record = history_record
        self.setObjectName('history_record_widget')

        layout = QGridLayout(self)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

        # top left: the name of the operation record
        name_label = QLabel(self._history_record.name)
        layout.addWidget(name_label, 0, 0, Qt.AlignmentFlag.AlignLeft)

        # top right: indication of the completion time/date
        self.time_label = QLabel(self._format_time_ago(self._history_record.time_completed))
        layout.addWidget(self.time_label, 0, 1, Qt.AlignmentFlag.AlignRight)

        # TODO add icons for operations. Alphan's code below:
        # operations_widget = QWidget()
        # operations_layout = QHBoxLayout(operations_widget)
        # operations_layout.setContentsMargins(0, 0, 0, 0)
        # operations_layout.setSpacing(0)
        # for operation in run_result.operations:
        #     icon_widget = QWidget()
        #     icon_widget.setFixedSize(28, 28)
        #     icon_widget.setToolTip(operation)
        #     icon_widget.setObjectName("operation_icon")
        #     icon_widget.setProperty("operation", operation)
        #     operations_layout.addWidget(icon_widget)
        # operations_layout.addStretch()
        # layout.addWidget(operations_widget, 2, 1, Qt.AlignmentFlag.AlignRight)

    @staticmethod
    def _format_time_ago(date: dt.datetime) -> str:

        delta = dt.datetime.now() - date
        total_seconds = int(delta.total_seconds())
        minutes = total_seconds // 60
        hours = minutes // 60
        days = delta.days
        weeks = days // 7
        months = days // 30
        years = days // 365

        if minutes < 60:
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        elif hours < 24:
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif days < 7:
            return f"{days} {'day' if days == 1 else 'days'} ago"
        elif days < 30:
            return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
        elif days < 365:
            return f"{months} {'month' if months == 1 else 'months'} ago"
        else:
            return f"{years} {'year' if years == 1 else 'years'} ago"
        
    def update_time(self) -> None:
        """
        Re-sets the time label of the widget.
        """
        self.time_label.setText(self._format_time_ago(self._history_record.time_completed))
