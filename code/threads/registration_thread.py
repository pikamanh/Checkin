import os
from PyQt6 import QtCore
import imageio
import os
import pandas as pd
import torch

class RegistrationThread(QtCore.QThread):
    signal_update_text = QtCore.pyqtSignal(str)
    signal_registration_finished = QtCore.pyqtSignal()

    def __init__(self, folder, detect, cap, person_name, parent=None, num_images=5, skip_frame_first=20, frame_skip=30):
        super().__init__(parent)
        self.folder = folder
        self.detect = detect
        self.cap = cap
        self.num_images = num_images
        self.captured_images = []
        self.skip_frame_first = skip_frame_first
        self.frame_skip = frame_skip
        self.name_path = os.path.join(folder,"data", "names.csv")
        self.database_path = os.path.join(folder,"data", "features_database.pt")
        self.person_name = person_name  # Nhận tên người dùng trực tiếp từ constructor

    def run(self):
        self.signal_update_text.emit(f"Capturing images...")
        frame_count = 0
        features_tensor = torch.tensor([]).to("cuda")
        names = []

        if self.person_name:
            while len(self.captured_images) < self.num_images:
                ret, frame = self.cap.read()
                if not ret:
                    break
                frame_count += 1
                if (frame_count > self.skip_frame_first) and (frame_count % self.frame_skip == 0):
                    self.signal_update_text.emit(f"Capturing images... {len(self.captured_images)}/{self.num_images}")
                    img_name = f"{self.person_name}_{len(self.captured_images)+1}.png"
                    contain_image_path = os.path.join(self.folder, "data", self.person_name)
                    if not os.path.exists(contain_image_path):
                        os.makedirs(contain_image_path)
                    self.img_path = os.path.join(contain_image_path, img_name)
                    imageio.imwrite(self.img_path, frame)
                    
                    # Thêm bước analyze_image ở đây:
                    try:
                        response = self.detect.analyze_image(self.img_path)
                        if len(response.faces) != 0:
                            self.captured_images.append(self.img_path)
                            features = response.faces[0].preds['verify'].logits.unsqueeze(0)
                            names.append(self.person_name)
                            features_tensor = torch.concat((features_tensor, features), dim=0)
                    except Exception as e:
                        print(f"Lỗi khi analyze_image: {e}")
                        self.signal_update_text.emit(f"Lỗi khi analyze_image: {e}")
            try:
                db_entries = torch.load(self.database_path)
            except FileNotFoundError:
                db_entries = []

            for i in range(features_tensor.shape[0]):
                db_entries.append({
                    "name": self.person_name,
                    "embedding": features_tensor[i].cpu()
                })

            torch.save(db_entries, self.database_path)

            with open(self.name_path, 'a', newline="", encoding='utf-8-sig') as f:
                pd.DataFrame({'name': [self.person_name]}).to_csv(f, header=f.tell() == 0, index=False)
            print("✅ Registration completed and data saved.")
        else:
            self.signal_update_text.emit("Tên không hợp lệ")
            return

        self.signal_registration_finished.emit()
            # try:
        #         existing_features = torch.load(self.database_path)
        #         features_tensor = torch.concat((existing_features, features_tensor), dim=0)
        #     except FileNotFoundError:
        #         pass  # Nếu file chưa tồn tại, bỏ qua bước này
        #     torch.save(features_tensor, self.database_path)

        #     with open(self.name_path, 'a', newline="") as f:
        #         pd.DataFrame({'name': [self.person_name]}).to_csv(f, header=f.tell() == 0, index=False)
        #     print("Registration completed and data saved.")
        # else:
        #     self.signal_update_text.emit("Tên không hợp lệ")
        #     return

        # self.signal_registration_finished.emit()

    def set_person_name(self, name):
        """Nhận tên từ thread chính."""
        self.person_name = name  # Lưu tên vào biến