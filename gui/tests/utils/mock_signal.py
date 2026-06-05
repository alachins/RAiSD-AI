"""

INSTRUCTION:

# Assert
mock_signal = MockSignal(True)
mocked_object.signal.emit = mock_signal.emit
mocked_object.signal.connect = mock_signal.connect

# Act
mocked_object.signal.emit(True)

"""

from typing import Callable, Any

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtCore import SignalInstance


class MockSignal:
    def __init__(self, *args: Any) -> None:
        self.slots: list = []


    def connect(self, slot: object, /, type: Qt.ConnectionType = Qt.ConnectionType.AutoConnection) -> QMetaObject.Connection:
        self.slots.append(slot)
        return QMetaObject.Connection()

    def emit(self, *args: Any) -> None:
        for slot in self.slots:
            if isinstance(slot, SignalInstance):
                slot.emit(*args)
            elif isinstance(slot, Callable):
                slot(*args)
