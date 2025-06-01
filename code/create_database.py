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

import torchvision

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def main():
    db = []
    folder = os.getcwd()
    cfg = OmegaConf.load(os.path.join(folder, 'data', 'gpu.yml'))
    analyzer = FaceAnalyzer(cfg.analyzer)

    data_path = os.path.join(folder, 'data', 'image_test')
    image_list = os.listdir(data_path)

    for image in tqdm(image_list, desc="Processing Image: "):
        name_mssv = image.split('.')[0]
        name = name_mssv.split('_')[0]
        mssv = name_mssv.split('_')[1]
        response = analyzer.run(
            path_image=os.path.join(data_path, image),
            batch_size=cfg.batch_size,
            fix_img_size=cfg.fix_img_size,
            return_img_data=True,
            include_tensors=True
        )

        pil_image = torchvision.transforms.functional.to_pil_image(response.img)
        pil_image.save(os.path.join(folder, 'data', 'output_analyzer_test', image))

        if len(response.faces) != 0:
            feature = response.faces[0].preds['verify'].logits.unsqueeze(0)
            db.append({
                'name': name,
                'mssv': mssv,
                'embedding': feature.T.squeeze(1).cpu()
            })

    torch.save(db, os.path.join(folder, 'data', 'features_database_test.pt'))

if __name__ == '__main__':
    main()