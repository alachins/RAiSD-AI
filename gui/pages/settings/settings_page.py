from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QScrollArea,
)

from ..page import Page
from gui.model.settings import app_settings
from gui.components.settings import set_settings, SettingsItemWidget
from gui.components import (
    VBoxLayout,
)
from gui.style import constants


class SettingsPage(Page):
    """
    The settings page of the RAiSD-AI GUI application.
    """
    def __init__(self):
        """
        Initialize the `SettingsPage`.
        """
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):

        outer_layout = VBoxLayout(
            self,
        )

        scroll_area = QScrollArea()
        scroll_area.setObjectName("settings_scroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner_widget = QWidget()
        inner_widget.setObjectName("settings_inner")
        layout = VBoxLayout(
            inner_widget,
            left=constants.GAP_MEDIUM,
            top=constants.GAP_MEDIUM,
            right=constants.GAP_MEDIUM,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_TINY,
        )

        scroll_area.setWidget(inner_widget)
        outer_layout.addWidget(scroll_area)

        title_label = QLabel("Settings")
        title_label.setProperty("title", "true")
        layout.addWidget(title_label)

        container_widget = QWidget()
        container_widget.setObjectName("container_widget")
        container_layout = VBoxLayout(
            container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

        # Workspace
        workspace_widget = SettingsItemWidget("Workspace", app_settings.workspace_path.absolutePath())
        app_settings.workspace_path_changed.connect(
            lambda p : workspace_widget._update_label(p.absolutePath()))
        workspace_widget.button_clicked.connect(set_settings.set_workspace_folder)
        container_layout.addWidget(workspace_widget)

        # Executable
        executable_widget = SettingsItemWidget("Executable", app_settings.executable_file_path.absoluteFilePath())
        app_settings.executable_file_path_changed.connect(
            lambda p : executable_widget._update_label(p.absoluteFilePath()))
        executable_widget.button_clicked.connect(set_settings.set_executable_path)
        container_layout.addWidget(executable_widget)

        # Environment manager
        environment_manager_widget = SettingsItemWidget("Environment manager", app_settings.environment_manager_name)
        app_settings.environment_manager_changed.connect(
            lambda _ : environment_manager_widget._update_label(app_settings.environment_manager_name))
        environment_manager_widget.button_clicked.connect(set_settings.set_environment_manager)
        container_layout.addWidget(environment_manager_widget)

        # Environment name
        environment_name_widget = SettingsItemWidget("Environment name", app_settings.environment_name)
        app_settings.environment_name_changed.connect(
            lambda _ : environment_name_widget._update_label(app_settings.environment_name)
        )
        environment_name_widget.button_clicked.connect(set_settings.set_environment_name)
        container_layout.addWidget(environment_name_widget)

        layout.addWidget(container_widget)

        info_label = QLabel("General Information")
        info_label.setProperty("title", "true")
        layout.addWidget(info_label)

        info_container_widget = QWidget()
        info_container_widget.setObjectName("container_widget")
        info_container_layout = VBoxLayout(
            info_container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

        raisd_ai_label = QLabel(
            """<a href='https://www.nature.com/articles/s42003-018-0085-8'>
            RAiSD-AI</a> (Raised Accuracy in Sweep Detection using AI) is a
            command-line tool for detecting selective sweeps in genomic data
            developed by <b>Nikolaos Alachiotis</b> & <b>Pavlos Pavlidis</b>
            (<a href='https://github.com/alachins/RAiSD-AI'>GitHub</a>).
            """
        )
        raisd_ai_label.setWordWrap(True)
        raisd_ai_label.setOpenExternalLinks(True)
        info_container_layout.addWidget(raisd_ai_label)

        raisd_ai_gui_label = QLabel(
            """<a href='https://github.com/RAiSD-AI-GUI-Project-Team/RAiSD-AI-GUI'>RAiSD-AI 
            GUI</a> developed by <b>Loes Baart de la Faille</b>, <b>Steef 
            Broeder</b>, <b>Taylan Kıncır</b>, <b>Alphan Mete</b>, <b>Vlad 
            Negară</b> and <b>Giulia Tălău</b>."""
        )
        raisd_ai_gui_label.setWordWrap(True)
        raisd_ai_gui_label.setOpenExternalLinks(True)
        info_container_layout.addWidget(raisd_ai_gui_label)

        raisd_description_label = QLabel(
            """<b>What is RAiSD?</b> RAiSD (Raised Accuracy in Sweep Detection) is a stand-alone software implementation 
            of the μ statistic for selective sweep detection. Unlike existing implementations, including our previously 
            released tools (SweeD and OmegaPlus), RAiSD scans whole-genome SNP data based on a composite evaluation 
            scheme that captures multiple sweep signatures at once."""
        )
        raisd_description_label.setWordWrap(True)
        info_container_layout.addWidget(raisd_description_label)

        raisd_ai_description_label = QLabel(
            """<b>What is RAiSD-AI?</b> RAiSD-AI (RAiSD using AI) includes all the features of the latest RAiSD version 
            and introduces support for the practical deployment of Convolutional Neural Networks (CNN) in population 
            genetics research. In addition to using the μ statistic for selective sweep detection, RAiSD-AI can also 
            a) extract training data from standard file formats like FASTA and VCF, b) use TensorFlow or PyTorch to 
            train a network and generate a CNN model, c) test the CNN model and report various classification metrics, 
            and d) deploy the CNN model to scan standard file formats (and optionally report detection metrics). 
            RAiSD-AI is primarily designed and optimized for selective sweep detection, but can also be used to identify 
            other regions of interest (e.g., recombination hotspots, negative selection), provided that the CNN 
            is appropriately trained."""
        )
        raisd_ai_description_label.setWordWrap(True)
        info_container_layout.addWidget(raisd_ai_description_label)

        raisd_ai_gui_description_label = QLabel(
            """<b>What is RAiSD-AI GUI?</b> RAiSD-AI GUI is an intuitive graphical user interface that allows 
            biologists without a programming background to use the μ statistic for selective sweep detection using RAiSD and 
            train, evaluate and run a selective sweep detection model using RAiSD-AI."""
        )
        raisd_ai_gui_description_label.setWordWrap(True)
        info_container_layout.addWidget(raisd_ai_gui_description_label)

        # TODO: add a link to the user manual

        layout.addWidget(info_container_widget)

        contact_label = QLabel("Contact information")
        contact_label.setProperty("title", "true")
        layout.addWidget(contact_label)

        contact_container_widget = QWidget()
        contact_container_widget.setObjectName("container_widget")
        contact_container_layout = VBoxLayout(
            contact_container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

        contact_text_label = QLabel(
            "You can request support or report a bug by opening an issue "
            "on Github via <a href='https://github.com/RAiSD-AI-GUI-Project-Team/RAiSD-AI-GUI/issues/new'>this link</a> or by "
            "contacting RAiSD-AI developers Nikolaos Alachiotis ("
            "<a href='mailto:n.alachiotis@gmail.com'>n.alachiotis@gmail.com</a>) "
            "and Pavlos Pavlidis (<a href='mailto:pavlidisp@gmail.com'>pavlidisp@gmail.com</a>)."
        )
        contact_text_label.setWordWrap(True)
        contact_text_label.setOpenExternalLinks(True)
        contact_container_layout.addWidget(contact_text_label)

        layout.addWidget(contact_container_widget)

        license_label = QLabel("Licensing")
        license_label.setProperty("title", "true")
        layout.addWidget(license_label)

        license_container_widget = QWidget()
        license_container_widget.setObjectName("container_widget")
        license_container_layout = VBoxLayout(
            license_container_widget,
            left=constants.GAP_SMALL,
            top=constants.GAP_SMALL,
            right=constants.GAP_SMALL,
            bottom=constants.GAP_MEDIUM,
            spacing=constants.GAP_SMALL,
        )

        license_text_label = QLabel(
            """Copyright April 2026 by <b>Nikolaos Alachiotis</b>, <b>Loes Baart de la Faille</b>, <b>Steef Broeder</b>, 
            <b>Taylan Kıncır</b>, <b>Alphan Mete</b>, <b>Vlad Negară</b> and <b>Giulia Tălău</b>.<br>
            
            <br>This program is free software, you may redistribute it and/or modify it under the terms of the 
             GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or 
            (at your option) any later version.<br>

            <br>This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without 
            even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
            <a href='https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html'>GNU General Public License</a>   
            for more details."""
        )
        license_text_label.setWordWrap(True)
        license_text_label.setOpenExternalLinks(True)
        license_container_layout.addWidget(license_text_label)

        layout.addWidget(license_container_widget)

        layout.addStretch()
