from kokoro import KPipeline
import soundfile as sf
import torch
import epitran
import os
from tqdm import tqdm
import pandas as pd

from huggingface_hub import login
login(token="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")

def text_to_phonemes(name):
    epi = epitran.Epitran('vie-Latn')
    # g2p = en.G2P(trf=False, british=False, fallback=None)
    phonemes_name = epi.trans_list(name)
    phonemes_name = "".join(phonemes_name)
    return phonemes_name

def create_voice(name, mssv, family, output_path):
    pipeline = KPipeline(lang_code='b', repo_id='hexgrad/Kokoro-82M')

    # name='Trần Nguyễn Phương Phi Hùng'
    phonemes_name = f"(/{text_to_phonemes(name)}/)"

    try:
        if int(family) > 0:
            text=f'Welcome, [{name}]{phonemes_name}, and your homies to the Top 100 Outstanding Students Honoring Ceremony, Spring 2025.'
        else:
            text=f'Welcome, [{name}]{phonemes_name}, to the Top 100 Outstanding Students Honoring Ceremony, Spring 2025.'
    except Exception:
        return

    generator = pipeline(text, voice='af_bella')
    output_file = os.path.join(output_path, f'{mssv}_{name}.wav')
    for i, (gs, ps, audio) in enumerate(generator):
        # print(i, gs, ps)
        sf.write(output_file, audio, 24000)

if __name__ == '__main__':
    folder = os.getcwd()
    output_folder = os.path.join(folder, 'data', 'voice')
    data_path = os.path.join(folder, 'data', 'TOP100.csv')
    df = pd.read_csv(data_path)
    df = df[['MSSV', 'HỌ TÊN', 'NGƯỜI THÂN']]
    
    for _, row in tqdm(df.iterrows(), desc='Creating Voice: '):
        mssv = row['MSSV']
        name = row['HỌ TÊN']
        family = row['NGƯỜI THÂN']
        create_voice(name, mssv, family, output_folder)