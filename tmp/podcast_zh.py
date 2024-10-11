'''根据对话生成中文播客'''

import json
import ChatTTS
import torch
import torchaudio
from tqdm import tqdm
import soundfile as sf


def generate_wav(text, spk, chat):
    params_infer_code = ChatTTS.Chat.InferCodeParams(
        spk_emb = spk, # add sampled speaker 
        temperature = .3,   # using custom temperature
        top_P = 0.7,        # top P decode
        top_K = 20,         # top K decode
    )

    # use oral_(0-9), laugh_(0-2), break_(0-7) 
    # to generate special token in text to synthesize.
    params_refine_text = ChatTTS.Chat.RefineTextParams(
        prompt='[oral_2][laugh_0][break_6]',
    )

    wavs = chat.infer(
        [text],
        params_refine_text=params_refine_text,
        params_infer_code=params_infer_code,
    )

    return wavs[0]

def from_numpy_to_tensor(wav):
    try:
        return torch.from_numpy(wav).unsqueeze(0)
    except:
        return torch.from_numpy(wav)

def generate_wav_from_conversation(conversation, wav_filename=None, mp3_filename=None):
    # 对话人列表
    # speakers = list(set([item["speaker"] for item in conversation]))
    spk1 = torch.load("speaker/female_seed_1397_restored_emb.pt", map_location=torch.device('cpu'))
    spk2 = torch.load("speaker/male_seed_402_restored_emb.pt", map_location=torch.device('cpu'))
    spk_dict = {"主持人": spk1, "专家": spk2}


    chat = ChatTTS.Chat()
    chat.load(compile=False) # Set to True for better performance

    # 将对话生成wav并保存
    wavs = []
    for index, item in enumerate(tqdm(conversation)):
        wav = generate_wav(item["content"], spk_dict[item["speaker"]], chat)
        wavs.append(wav)

    # 将wavs拼接成一个音频
    combined_wav = torch.cat([from_numpy_to_tensor(wav) for wav in wavs], dim=1)

    # 保存文件
    if wav_filename:
        sf.write(wav_filename, combined_wav.squeeze().numpy(), 24000)
    if mp3_filename:
        sf.write(mp3_filename, combined_wav.squeeze().numpy(), 24000)
    
    return combined_wav
