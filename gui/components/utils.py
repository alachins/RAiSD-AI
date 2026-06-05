"""
A module containing helper functions for manipulating UI components.
"""

from PySide6.QtWidgets import QWidget


def set_bool_property(widget: QWidget, name: str, value: bool | None):
    """
    Utility function to set a boolean property on a `QWidget`.

    The function sets the property `name` to:
    - "true" if `value == True`
    - "false" if `value == False`
    - "" (the empty string) if `value is None`

    The widget is then unpolished and polished to refresh its styling.

    :param widget: the widget to set the property on
    :type widget: QWidget

    :param name: the name of the property
    :type name: str

    :param value: the value to set
    :type value: bool | None
    """
    if value is None:
        widget.setProperty(name, "")
    elif value:
        widget.setProperty(name, "true")
    else:
        widget.setProperty(name, "false")

    widget.style().unpolish(widget)
    widget.style().polish(widget)
