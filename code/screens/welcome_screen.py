from PyQt6.QtWidgets import QMainWindow, QLabel, QTextEdit
from PyQt6.uic import loadUi
from PyQt6 import QtCore, QtGui
import os

class WelcomeScreen(QMainWindow):
    def __init__(self, folder, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        ui_path = os.path.join(folder, "UI", 'back.ui')
        loadUi(ui_path, self)
        
        self.backButton.clicked.connect(self.goBack)
        # self.TEXT = self.findChild(QtCore.QObject, "TEXT")
        self.TEXT = self.findChild(QTextEdit, "TEXT")
        self.TEXT.setReadOnly(True)
        # self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # self.TEXT.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)


    def update_text(self, name, acc):
        # self.TEXT.setText(f"Welcome, {name} (Accuracy: {acc:.2f})!")
        self.TEXT.setHtml(f"""
            <div align='center' style="font-family: Arial; font-size: 70px; font-weight: bold; color: white;">
                Chào mừng<br>{name}<br>đã đến với TOP 100!
            </div>
        """
        )
    
    def goBack(self):
        pass
        # self.parent().setCurrentIndex(0)