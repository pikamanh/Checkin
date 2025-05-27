from PyQt6 import QtCore
from PyQt6.QtCore import QRunnable, QObject

class WarmupTaskSignals(QObject):
    finished = QtCore.pyqtSignal()

class WarmupTask(QRunnable):
    def __init__(self, detect):
        super(WarmupTask, self).__init__()
        self.detect = detect
        self.signals = WarmupTaskSignals()  # Tạo instance của lớp tín hiệu

    def run(self):
        self.detect.warmup()
        self.signals.finished.emit()