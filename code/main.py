import os
import sys
from PyQt6.QtWidgets import QApplication
from screens.main_screen import MainScreen
from screens.welcome_screen import WelcomeScreen

if __name__ == "__main__":
    folder = os.getcwd()
    app = QApplication(sys.argv)

    main_screen = MainScreen(folder=folder)
    welcome_screen = WelcomeScreen(folder=folder)

    main_screen.welcome_screen = welcome_screen 

    main_screen.showMaximized()
    welcome_screen.show() # Không cần maximized

    app.exec()