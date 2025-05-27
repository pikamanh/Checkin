# This Python file uses the following encoding: utf-8
import sys
import os
import cv2
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool, QRunnable, QObject
from PyQt6.QtGui import QImage, QPixmap, QColor
from PyQt6.QtWidgets import QDialog, QApplication, QStackedWidget, QDockWidget, QInputDialog
from PyQt6.uic import loadUi
from detection import faceDetection
import imageio
import threading

class WarmupTaskSignals(QObject):
    finished = QtCore.pyqtSignal()  # Tạo tín hiệu thông báo khi khởi động hoàn tất

class WarmupTask(QRunnable):
    def __init__(self, detect):
        super(WarmupTask, self).__init__()
        self.detect = detect
        self.signals = WarmupTaskSignals()  # Tạo instance của lớp tín hiệu

    def run(self):
        self.detect.warmup()
        self.signals.finished.emit()  # Phát tín hiệu khi khởi động hoàn tất

class ThreadClass(QtCore.QThread):
    signal_update_text = QtCore.pyqtSignal(str)
    signal_update_button = QtCore.pyqtSignal(bool)
    signal_recognized = QtCore.pyqtSignal(str, float)

    def __init__(self, folder, detect, mutex, parent=None, skip_frame_first = 30, frame_skip = 30, threshold = 0.5):
        super(ThreadClass, self).__init__(parent)
        self.folder = folder
        self.detect = detect
        self.running = True
        self.img_path = os.path.join(self.folder,"img_temp", "my_image.png")
        self.mutex = mutex

        self.skip_frame_first = skip_frame_first
        self.frame_skip = frame_skip
        self.threshold = threshold
        self.cap = None

    def run(self):
        self.running = True
        frame_count = 0
        while self.running:
            if self.cap is not None:  # Kiểm tra self.cap khác None trước khi sử dụng
                ret, frame = self.cap.read()
            else:
                ret = False
                frame = None
            
            if not ret:
                break
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_count += 1
            if (frame_count < self.skip_frame_first) or (frame_count % self.frame_skip != 0):
                continue
            
            with self.mutex:
                self.signal_update_button.emit(False)
                imageio.imwrite(self.img_path, frame)
                print(f"\n\nRecognizing with frame {frame_count}")
                name, acc = self.detect.predict_name(self.img_path)
                if acc >= self.threshold:
                    self.signal_recognized.emit(name, acc)
                    self.running = False
                elif (name == "notFound"):
                    self.signal_update_text.emit("No faces detected in the camera.")
                else:
                    self.signal_update_text.emit("No match found.")
                self.signal_update_button.emit(True) 
                print(f"Recognize completed with frame {frame_count}")
    
class WelcomeScreen(QDockWidget):
    def __init__(self, folder, parent=None):
        super(WelcomeScreen, self).__init__(parent)
        ui_path = os.path.join(folder, "UI", 'welcome.ui')
        loadUi(ui_path, self)
        
        self.backButton.clicked.connect(self.goBack)

    def update_text(self, name, acc):
        self.TEXT.setText(f"Welcome, {name} (Accuracy: {acc:.2f})!")
    
    def goBack(self):
        self.parent().setCurrentIndex(0)

class MainScreen(QDialog):
    signal_update_buttons = QtCore.pyqtSignal(bool)
    def __init__(self, folder, parent=None, skip_frame_first=30, frame_skip=30, threshold=0.5):
        super(MainScreen, self).__init__(parent)
        ui_path = os.path.join(folder,"UI", 'form.ui')
        loadUi(ui_path, self)
        self.folder = folder
        self.detect = faceDetection(self.folder)

        self.SHOW.clicked.connect(self.onClicked)
        self.TEXT.setText('Findly Press')
        self.Break.clicked.connect(self.breakClicked)
        self.warmup.clicked.connect(self.WarmUp)
        self.inputButton.clicked.connect(self.getInputName)

        self.cap = None
        self.thread_pool = QThreadPool()
        self.signal_update_buttons.connect(self.update_buttons)
        self.warmup_active = False
        
        self.running = True
        self.mutex = threading.Lock()
        self.thread = ThreadClass(self.folder, self.detect, self.mutex, parent, skip_frame_first, frame_skip, threshold)

        self.thread.signal_update_text.connect(self.update_text)
        self.thread.signal_update_button.connect(self.update_button_state)
        self.thread.signal_recognized.connect(self.onRecognized)
        self.predicting = False
        self.WarmUp()

    def WarmUp(self):
        if not self.warmup_active:
            self.signal_update_buttons.emit(False)
            self.TEXT.setText("Warming up...")
            self.warmup_active = True

            def warmup_finished():
                self.signal_update_buttons.emit(True)
                self.TEXT.setText("Warmup complete!")
                self.warmup_active = False

            warmup_task = WarmupTask(self.detect)
            warmup_task.signals.finished.connect(warmup_finished)  # Kết nối tín hiệu finished với khe cắm warmup_finished
            self.thread_pool.start(warmup_task)
         

    @pyqtSlot()
    def onClicked(self):
        if not self.predicting:
            print("Button show click!")
            self.TEXT.setText("Camera starting...")
            self.warmup.setEnabled(False)
            self.SHOW.setEnabled(False)
            self.inputButton.setEnabled(False)
            self.cap = cv2.VideoCapture(0)

            # Tạo và kết nối luồng xử lý nhận diện
            self.thread.cap = self.cap
            self.thread.signal_update_text.connect(self.update_text)
            self.thread.start()

            # Bắt đầu vòng lặp hiển thị camera trong luồng chính
            while (self.cap != None):
                ret, frame = self.cap.read()
                frame = cv2.flip(frame, 1)

                if not ret:
                    break
                self.displayImage(frame)
                cv2.waitKey(1)


    def breakClicked(self):
        if not self.predicting:
            self.TEXT.setText("Don't Click any button!")
            if self.cap != None:
                self.thread.running = False
                self.thread.wait() # Đợi luồng kết thúc

                self.cap.release()
                cv2.destroyAllWindows()
            self.TEXT.setText("Camera stopped")
            self.cap = None
            self.warmup.setEnabled(True)
            self.inputButton.setEnabled(True)
            self.SHOW.setEnabled(True)
            self.predicting = False

            # Tạo QPixmap trắng trơn
            white_pixmap = QPixmap(self.imgLabel.size())
            white_pixmap.fill(QColor("white"))

            # Đặt QPixmap trắng vào imgLabel
            self.imgLabel.setPixmap(white_pixmap)

    def update_button_state(self, enabled):
        self.Break.setEnabled(enabled)
        self.predicting = not enabled

    @pyqtSlot(bool)
    def update_buttons(self, enabled):
        self.SHOW.setEnabled(enabled)
        self.Break.setEnabled(enabled)
        self.inputButton.setEnabled(enabled) 
        self.warmup.setEnabled(enabled)

    def update_text(self, text):
        self.TEXT.setText(text)
    
    def displayImage(self, img):
        qformat = QImage.Format.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format.Format_RGB888
            else:
                qformat = QImage.Format.Format_RGB888
        
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.imgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def onRecognized(self, name, acc):
        self.predicting = False
        self.breakClicked() 
        self.stacked_widget.setCurrentIndex(1)  
        self.welcome_screen.update_text(name, acc) 
    
    def getInputName(self):
        name, ok = QInputDialog.getText(self, "Nhập tên", "Nhập tên:")
        if ok and name:
            self.goToWelcomeScreen(name)

    def goToWelcomeScreen(self, name):
        self.stacked_widget.setCurrentIndex(1)
        self.welcome_screen.update_text(name, 100)
    
    def closeEvent(self, event):
        if (self.cap != None) or self.warmup_active:
            # Nếu predict_name đang chạy, chặn sự kiện đóng và thông báo cho người dùng
            event.ignore()
            self.TEXT.setText("Chương trình đang xử lý, hãy thử lại sau...")
        else:
            # Nếu predict_name đã hoàn thành, cho phép đóng ứng dụng
            self.breakClicked()
            event.accept()


if __name__ == "__main__":
    folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
    app = QApplication(sys.argv)
    
    # Create stacked widget and add screens
    stacked_widget = QStackedWidget()
    main_screen = MainScreen(folder=folder)
    welcome_screen = WelcomeScreen(folder=folder)
    stacked_widget.addWidget(main_screen)
    stacked_widget.addWidget(welcome_screen)
    # stacked_widget.showMaximized()
    stacked_widget.show()
    stacked_widget.adjustSize()
    stacked_widget.resize(stacked_widget.width() + 100, stacked_widget.height() + 50)

    # Store stacked widget reference in main screen
    main_screen.stacked_widget = stacked_widget
    main_screen.welcome_screen = welcome_screen

    welcome_screen.setParent(stacked_widget)

    # Ghi đè closeEvent của stacked_widget, không phải app
    stacked_widget.closeEvent = main_screen.closeEvent  
    app.exec()
    # sys.exit(app.exec())