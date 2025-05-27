import logging
logging.disable(logging.CRITICAL)
import warnings
warnings.filterwarnings("ignore")
import torch
torch.cuda.empty_cache()
from facetorch import FaceAnalyzer
from omegaconf import OmegaConf
import os
from tqdm import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def main():
    db = []
    folder = os.getcwd()
    cfg = OmegaConf.load(os.path.join(folder, 'data', 'gpu.yml'))
    analyzer = FaceAnalyzer(cfg.analyzer)

    data_path = os.path.join(folder, 'data', 'data_TOP100')
    image_list = os.listdir(data_path)

    for image in tqdm(image_list, desc="Processing Image: "):
        name = image.split('.')[0]
        response = analyzer.run(
            path_image=os.path.join(data_path, image),
            batch_size=cfg.batch_size,
            fix_img_size=cfg.fix_img_size,
            return_img_data=False,
            include_tensors=True
        )

        if len(response.faces) != 0:
            feature = response.faces[0].preds['verify'].logits.unsqueeze(0)
            db.append({
                'name': name,
                'embedding': feature.T.squeeze(1).cpu()
            })

    torch.save(db, os.path.join(folder, 'data', 'features_database.pt'))

if __name__ == '__main__':
    main()