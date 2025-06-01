import imageio
import os
from PyQt6 import QtCore
from Tick_datasheet import checkin_excel
from voice import speak_dual_language

class PostRecognitionThread(QtCore.QThread):
    def __init__(self, name, mssv, checkin_path):
        super().__init__()
        self.name = name
        self.mssv = mssv
        self.checkin_path = checkin_path

    def run(self):
        try:
            checkin_excel(self.checkin_path, self.mssv)
        except Exception as e:
            print(f"Check-in failed: {e}")
        try:
            speak_dual_language(self.name)
        except Exception as e:
            print(f"Voice playback failed: {e}")


class ThreadClass(QtCore.QThread):
    signal_update_text = QtCore.pyqtSignal(str)
    signal_update_button = QtCore.pyqtSignal(bool)
    signal_recognized = QtCore.pyqtSignal(str, float)

    def __init__(self, folder, detect, mutex, parent=None, skip_frame_first=10, frame_skip=10, threshold=0.5):
        super(ThreadClass, self).__init__(parent)
        self.folder = folder
        self.detect = detect
        self.running = True
        self.img_path = os.path.join(self.folder,"img_temp", "my_image.png")
        self.checkin_path = os.path.join(self.folder, "data", "TOP100.csv")
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
                self.signal_update_text.emit("Model đang xử lý.")
                try:
                    name, mssv, acc = self.detect.predict_name(self.img_path)
                    if acc >= self.threshold:
                        self.signal_recognized.emit(name, acc)
                        self.running = False
                        checkin_excel(self.checkin_path, mssv)
                        self.post_thread = PostRecognitionThread(name, mssv, self.checkin_path)
                        self.post_thread.start()
                    elif (name == "notFound"):
                        self.signal_update_text.emit("No faces detected in the camera.")
                    else:
                        self.signal_update_text.emit("No match found.")
                    self.signal_update_button.emit(True) 
                    print(f"Recognize completed with frame {frame_count}")
                except Exception:
                    self.signal_update_text.emit("Please keep your face in the frame.")