from PySide6.QtWidgets import (
    QWidget,
)

from gui.components import (
    StylableWidget,
    VBoxLayout,
)
from gui.style import constants
from gui.components.navigation_buttons_holder import NavigationButtonsHolder


class RunPageTab(StylableWidget):
    """
    An abstract base class for tabs in the run page.
     
    Which includes a widget for the main content of the tab and 
    a NavigationButtonsHolder for the navigation buttons. 
    
    Subclasses should implement the `_setup_widget` and
    `_setup_navigation_buttons` methods.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("run_tab")
        widget = self._setup_widget()
        navigation = self._setup_navigation_buttons()
        self._setup_layout(widget, navigation)

    def _setup_layout(self, widget: QWidget, navigation: QWidget) -> None:
        layout = VBoxLayout(
            self,
            spacing=constants.GAP_MEDIUM,
        )
        layout.addWidget(widget, 1)
        layout.addWidget(navigation)
        pass

    def _setup_widget(self) -> QWidget:
        """
        Set up the main content widget for the tab.
        
        This method should be implemented by each subclass.

        :return: the main content widget for the tab
        :rtype: QWidget
        """
        raise NotImplementedError()

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        """
        Set up the navigation buttons for the tab.

        This method should be implemented by each subclass.

        :return: a NavigationButtonsHolder 
        :rtype: NavigationButtonsHolder
        """
        raise NotImplementedError()

    def refresh(self) -> None:
        """
        Refresh the UI elements of the tab when it is shown.
        """
        pass
    
    def reset(self) -> None:
        """
        Reset the UI elements of the tab when the run page is reset.
        """
        pass
