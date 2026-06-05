from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
)
from PySide6.QtWidgets import (
    QWidget,
    QScrollArea,
    QRadioButton,
    QPushButton,
    QLabel,
    QLineEdit
)

from .run_page_tab import RunPageTab
from gui.model.run_record import RunRecord
from gui.components import (
    HBoxLayout,
    ResizableStackedWidget,
    VBoxLayout,
)
from gui.components.operation import OperationTreeWidget
from gui.components.parameter import ParameterWidget
from gui.components.navigation_buttons_holder import NavigationButtonsHolder
from gui.style import constants

class OperationTab(RunPageTab):
    """
    A tab that allows the user to choose a run id and
    to select operations to be run.
    """
    navigate_next = Signal()

    def __init__(self, run_record: RunRecord): 
        self._run_record = run_record
        super().__init__()

    def _setup_widget(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("operation_selection_widget")
        layout = VBoxLayout(
            widget,
            spacing=constants.GAP_MEDIUM,
        )

        title_label = QLabel("Operation Selection")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)

        run_id_parameter_widget = ParameterWidget.from_parameter(
            self._run_record.run_id_parameter,
            editable=True,
        )
        run_id_widget = run_id_parameter_widget.build_form_row()
        
        field = run_id_widget.findChild(QLineEdit)
        if field:
           field.setMinimumWidth(290) 
    
        layout.addWidget(run_id_widget)
            
        self.operation_selector = self.__class__.OperationSelector(
            self._run_record
        )
        self._run_record.selected_operation_tree_index_changed.connect(
            self.operation_selector.operation_selection_changed
        )
        layout.addWidget(self.operation_selector, stretch=1000)

        layout.addStretch(1)

        # Show operation selector only if run ID is valid
        self.operation_selector.setVisible(
            self._run_record.run_id_valid,
        )
        self._run_record.run_id_valid_changed.connect(
            self._run_id_valid_changed,
        )

        return widget

    def _setup_navigation_buttons(self) -> NavigationButtonsHolder:
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("next_button")
        self.next_button.clicked.connect(self.navigate_next.emit)
        self._update_next_button_state()
        self._run_record.run_id_valid_changed.connect(
            self._update_next_button_state,
        )
        self._run_record.operations_valid_changed.connect(
            self._update_next_button_state,
        )

        return NavigationButtonsHolder(right_button=self.next_button)

    def refresh(self) -> None:
        self.operation_selector.refresh()
        self._update_next_button_state()
    
    class OperationSelector(QWidget):
        def __init__(self, run_record: RunRecord):
            super().__init__()

            self._run_record = run_record

            layout = HBoxLayout(
                self,
                spacing=constants.GAP_MEDIUM,
            )

            button_widget = QWidget()
            button_layout = VBoxLayout(button_widget)
            button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            button_layout.setSpacing(constants.GAP_TINY)

            tree_scroll = QScrollArea()
            tree_scroll.setObjectName("tree_scroll")
            tree_scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            tree_scroll.setWidgetResizable(True)

            self.operation_tree_widgets: list[OperationTreeWidget] = []
            self.tree_stacked_widget = ResizableStackedWidget()
            self.tree_stacked_widget.setObjectName("tree_stacked_widget")

            self.tree_selectors: list[tuple[QRadioButton, OperationTreeWidget]] = []
            flat_index = 0
            for mode_name, trees in self._run_record.categorized_operation_trees:
                mode_label = QLabel(mode_name)
                mode_label.setObjectName("mode_label")
                button_layout.addWidget(mode_label)

                for tree in trees:
                    self.button = QRadioButton(tree.root.name)
                    self.button.setChecked(
                        flat_index == self._run_record.selected_operation_tree_index
                    )
                    button_layout.addWidget(self.button)

                    widget = OperationTreeWidget(tree)
                    self.operation_tree_widgets.append(widget)
                    self.tree_stacked_widget.addWidget(widget)

                    idx = flat_index
                    self.button.clicked.connect(lambda _, i=idx: self._button_clicked(i))
                    self.tree_selectors.append((self.button, widget))
                    flat_index += 1

                button_layout.addSpacing(constants.GAP_SMALL)

            tree_scroll.setWidget(self.tree_stacked_widget)

            layout.addWidget(button_widget)
            layout.addWidget(tree_scroll)

        def refresh(self) -> None:
            for tree_widget in self.operation_tree_widgets:
                for i, (button, _) in enumerate(self.tree_selectors):
                    button.setChecked(
                        i == self._run_record.selected_operation_tree_index
                    )
                self.tree_stacked_widget.current_index = (
                    self._run_record.selected_operation_tree_index
                )
                tree_widget.refresh()

        def _button_clicked(self, i: int) -> None:
            self._run_record.selected_operation_tree_index = i
            self.tree_stacked_widget.current_index = i

        def operation_selection_changed(self, index: int) -> None:
            self.tree_stacked_widget.current_index = index
            for i, (button, widget) in enumerate(self.tree_selectors):
                button.setChecked(i == index) 

    @Slot()
    def _run_id_valid_changed(self, new_valid) -> None:
        self.operation_selector.setVisible(new_valid)

    @Slot()
    def _update_next_button_state(self) -> None:
        valid = (
            self._run_record.run_id_valid
            and self._run_record.operations_valid
        )
        self.next_button.setEnabled(valid)
        if valid:
            self.next_button.setProperty("highlight", "true")
        else:
            self.next_button.setProperty("highlight", "false")
        self.next_button.style().unpolish(self.next_button)
        self.next_button.style().polish(self.next_button)
