import sys
import sass

from PySide6.QtWidgets import (
    QApplication,
)


from gui.model.settings import app_settings
from gui.window import (
    MainWindow,
    SplashScreen,
    SettingsSetup,
)


def main():
    app = QApplication(sys.argv)

    # Set styling
    with open("gui/style/variables.scss", "r") as f:
        variables = f.read()

    with open("gui/style/style.qss", "r") as f:
        stylesheet = f.read()

    final_stylesheet = variables + stylesheet
    final_stylesheet = sass.compile(string=final_stylesheet)

    app.setStyleSheet(final_stylesheet)

    splash_screen = SplashScreen()
    splash_screen.show()
    app.processEvents()

    splash_screen.showMessage("Select Workspace...")
    app.processEvents()

    SettingsSetup.initialize_settings()

    splash_screen.showMessage("Loading GUI...")
    app.processEvents()

    # Set main window
    window = MainWindow()

    window.resize(1200,800)
    window.show()

    splash_screen.finish(window)

    app.exec()
    print("App closed")


if __name__ == "__main__":
    main()
