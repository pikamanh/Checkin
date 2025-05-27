# This Python file uses the following encoding: utf-8
import sys
import os
import cv2
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QDialog, QApplication
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
from detection import faceDetection
import imageio

folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
detect = faceDetection(folder)
detect.warmup()

class tehSeencode(QDialog):
    def __init__(self):
        super(tehSeencode, self).__init__()
        ui_path = os.path.join(folder, 'form.ui')
        loadUi(ui_path, self)
        self.thread = {}
        self.SHOW.clicked.connect(self.camera)
        self.TEXT.setText('Findly Press')
        self.Break.clicked.connect(self.breakClicked)
        self.cap = None

    @pyqtSlot()
    def onClicked(self):
        self.TEXT.setText("on clicked")
        skip_frame_first = 100
        frame_skip=80
        threshold = 0.5
        img_path = os.path.join(folder, "my_image.png")

        self.cap = cv2.VideoCapture(0)
        frame_count = 0
        while (self.cap != None):
            ret, frame = self.cap.read()
            if not ret:
                break
            # cv2.imshow('Video', frame)
            self.displayImage(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1
            if (frame_count < skip_frame_first) or (frame_count % frame_skip != 0):
                continue

            imageio.imwrite(img_path, frame)
            name, acc = detect.predict_name(img_path)
            if acc >= threshold:
                self.TEXT.setText(f"Name: {name} with acc {acc:.2f}")
                # print(f"Best match: {name} with similarity {acc:.2f}")
            else:
                self.TEXT.setText("No match found.")
                # print("No match found.")


    def breakClicked(self):
        if self.cap is not None:
            self.cap.release()  # Release the camera
            cv2.destroyAllWindows()
            self.TEXT.setText("Camera stopped")
            self.cap = None  # Set the capture object to None
    
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

if __name__ == "__main__":

    # img_path = os.path.join(folder, "my_image.png")
    # detect.Recognition(img_path)
    # print("Done!")

    app = QApplication(sys.argv)
    widget = tehSeencode()
    widget.show()
    sys.exit(app.exec())

