#import
import logging
logging.disable(logging.CRITICAL)
import warnings
warnings.filterwarnings("ignore")
import torch
torch.cuda.empty_cache()

import cv2
import torchvision.transforms.functional as F
from facetorch import FaceAnalyzer
from omegaconf import OmegaConf
import os
import pandas as pd
import imageio


class faceDetection():
    def __init__(self, folder):
        """
        Initializes the `faceDetection` class with necessary parameters.

        Args:
            folder (str): Path to the folder containing data files, such as names.csv and features_database.pt.
        """
        self.folder = folder
        self.path_config = os.path.join(folder,"data", "gpu.config.yml")
        self.cfg = OmegaConf.load(self.path_config)
        self.analyzer = FaceAnalyzer(self.cfg.analyzer)
        self.name_path = os.path.join(folder,"data", "names.csv")
        self.database_path = os.path.join(folder,"data", "features_database.pt")

    def warmup(self):
        """
        Performs a warm-up routine by analyzing a sample image and predicting its name.
        This helps to initialize the model and improve subsequent performance.
        """
        print("Warming up!")
        path_img_input = os.path.join(self.folder,"img_temp", "persons.jpg")
        path_img_input_2 =  os.path.join(self.folder,"img_temp", "BinhThuongThanh.jpg")
        # warmup
        response = self.analyzer.run(
                path_image=path_img_input,
                batch_size=self.cfg.batch_size,
                fix_img_size=self.cfg.fix_img_size,
                return_img_data=False,
                include_tensors=True
            )
        self.predict_name(path_img_input)
        self.predict_name(path_img_input_2)
        print("Warmup done!")
        
    def analyze_image(self, image_path):
        """
        Analyzes a single image using the face analyzer.

        Args:
            image_path (str): Path to the image to be analyzed.

        Returns:
            Response: A Response object containing the analyzed facial features.
        """
        response = self.analyzer.run(
            path_image=image_path,
            batch_size=self.cfg.batch_size,
            fix_img_size=self.cfg.fix_img_size,
            return_img_data=False,
            include_tensors=True
        )
        return response
    
    def process_images_from_directory(self, directory: str):
        """
        Analyzes images from a directory, extracts features, and saves them to a database.

        Args:
            directory (str): Path to the directory containing the images.
        """
        features_tensor = torch.tensor([]).to("cuda")
        name = []
        for filename in os.listdir(directory):
            print(f"{filename}")
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(directory, filename)
                try:
                    response = self.analyze_image(img_path)
                except:
                    print(f"Don't analysis {filename}")
                    continue
                
                if len(response.faces) == 0:
                    print(f"No faces detected in the image {img_path}.")
                    continue
                
                features = response.faces[0].preds['verify'].logits.unsqueeze(0)
                name.append(filename)
                features_tensor = torch.concat((features_tensor, features), dim = 0)
            print(f"Done {filename}")

        torch.save(features_tensor, self.database_path)  
        df = pd.DataFrame({'name': name})
        df.to_csv(self.name_path, index=False)  
    
    def get_sim_feature_index(self, X, y, eps=torch.tensor(1e-8)):
        """
        Calculates the similarity between a feature vector and a database of feature vectors.
        Returns the index of the most similar vector and its similarity score.

        Args:
            X (torch.Tensor): Database of feature vectors.
            y (torch.Tensor): Input feature vector to compare.
            eps (torch.Tensor, optional): Small value to avoid division by zero. Defaults to torch.tensor(1e-8).

        Returns:
            tuple: Index of the most similar feature vector and its similarity score.
        """
        norm_y = torch.norm(y)
        norm_y = torch.max(norm_y, eps)

        norm_X = torch.norm(X, dim=0)

        eps_vector = eps * torch.ones_like(norm_X.unsqueeze(0))
        norm_X = torch.concat( (norm_X.unsqueeze(0), eps_vector)
                            , dim=0) 
        norm_X = norm_X.max(dim=0).values

        product = norm_X * norm_y
        
        sim = y @ X
        sim = sim / product
        index = sim.argmax(dim=1).item()
        value = sim.max().item()

        return index, value

    def predict_name(self, image_path):
        """
        Predicts the name of a person in the given image by comparing its facial features
        to the database of known faces.

        Args:
            image_path (str): Path to the image to analyze.

        Returns:
            tuple: Name of the predicted person and the similarity score.
        """
        name = pd.read_csv(self.name_path)
        features = torch.load(self.database_path)
        features = features.T

        print("Analyzing")
        response = self.analyze_image(image_path)
        if len(response.faces) == 0:
            return "notFound", 0.0

        print('Analysis completed')
        print(f"Number of face: {len(response.faces)}")
        feature = response.faces[0].preds['verify'].logits
        feature.unsqueeze_(0)

        idx, acc = self.get_sim_feature_index(features, feature)
        return name['name'][idx], acc

    def Recognition(self, img_path, skip_frame_first = 100, frame_skip=80, threshold = 0.5):
        """
        Performs real-time face recognition from a video stream.

        Args:
            img_path (str): Path to the image where the captured frames will be saved.
            skip_frame_first (int, optional): Number of frames to skip at the beginning. Defaults to 100.
            frame_skip (int, optional): Number of frames to skip between predictions. Defaults to 80.
            threshold (float, optional): Minimum similarity score for a positive match. Defaults to 0.5.
        """
        cap = cv2.VideoCapture(0)
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_count += 1
            if (frame_count < skip_frame_first) or (frame_count % frame_skip != 0):
                continue
            
            imageio.imwrite(img_path, frame)
            name, acc = self.predict_name(img_path)
            if acc >= threshold:
                print(f"Best match: {name} with similarity {acc:.2f}")
            else:
                print("No match found.")
            
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    folder = "D:\\FPT\\AI\\9.5 AI\\Check In\\Final1"
    f = faceDetection(folder)
    f.warmup()
    directory = os.path.join(folder, 'img_database')
    f.process_images_from_directory(directory)

    # img_path = os.path.join(folder,"img_temp", "my_image.png")
    # f.Recognition(img_path)
    print("done")
