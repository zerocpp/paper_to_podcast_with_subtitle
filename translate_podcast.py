'''
端到端翻译播客
'''


import os
import logging
import argparse
import srt
import json
import openai
import json
import ChatTTS
import torch
import torchaudio
from tqdm import tqdm
import soundfile as sf


logging.basicConfig(level=logging.INFO)
openai.api_key = os.getenv("OPENAI_API_KEY")


def srt_to_text(srt_file, save_filename=None):
    # 读取SRT文件
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # 解析SRT内容
    subtitles = list(srt.parse(srt_content))
    
    # 每20个字幕文本拼接一次
    full_text = ""
    for index, subtitle in enumerate(subtitles):
        full_text += subtitle.content + " "
        if (index + 1) % 20 == 0:
            full_text += "\n|===|\n"
    

    # # 提取所有字幕文本并拼接
    # full_text = ""
    # for subtitle in subtitles:
    #     full_text += subtitle.content + " "
    
    # 去除多余空格并返回
    text = full_text.strip()
    
    if save_filename:
        with open(save_filename, "w", encoding="utf-8") as f:
            f.write(text)
    return text



def translate_text(text, save_filename=None):
    translated_text = ""
    for text_part in text.split("\n|===|\n"):
        try:
            # 使用OpenAI的ChatCompletion接口进行翻译
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "我给你一段对话音频的转录文本，对话中有且仅有两个人，一个是“[主持人]”，一个是“[专家]”，请帮我翻译成中文文本，猜测每句话的说话人并标注。例如：[主持人]：“内容”"},
                    {"role": "user", "content": f"请将以下对话文本翻译成中文：\n\n{text_part}"}
                ],
                temperature=0, # 翻译的准确性
                max_tokens=1024
            )
            translation = completion.choices[0].message.content
            translated_text += translation.strip() + "\n\n"
        except Exception as e:
            print(f"翻译时出错：{e}")
            translated_text += "\n\n"
    if save_filename:
        with open(save_filename, "w", encoding="utf-8") as f:
            f.write(translated_text)
    return translated_text

def extract_conversation(text, save_filename=None):
    # 按行分割
    lines = text.split("\n")
    # 去掉空行
    lines = [line for line in lines if line.strip()]
    # 每行的格式是[说话人]：“内容”，分成两部分
    conversation = []
    for line in lines:
        parts = line.split("：")
        speaker = parts[0][1:-1]
        content = parts[1][1:-1]
        conversation.append({"speaker": speaker, "content": content})

    if save_filename:
        # 保存为json
        with open(save_filename, "w", encoding="utf-8") as file:
            json.dump(conversation, file, ensure_ascii=False, indent=4)

    return conversation


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



def parse_args():
    parser = argparse.ArgumentParser(description="Translate subtitle file")
    parser.add_argument("-i", "--input_filename", type=str, default="input/audio.wav", help="输入英文播客音频文件名")
    parser.add_argument("-o", "--output_dir", type=str, default="output", help="输出文件夹")
    parser.add_argument("--generate_srt", default=True, action=argparse.BooleanOptionalAction, help="是否生成字幕")
    parser.add_argument("--src_to_text", default=True, action=argparse.BooleanOptionalAction, help="是否合并字幕")
    parser.add_argument("--translate_text", default=True, action=argparse.BooleanOptionalAction, help="是否翻译对话")
    parser.add_argument("--extract_conversation", default=True, action=argparse.BooleanOptionalAction, help="是否处理对话")
    parser.add_argument("--generate_wav_from_conversation", default=True, action=argparse.BooleanOptionalAction, help="是否生成播客")
    return parser.parse_args()

def main(args):
    input_filename = args.input_filename # 输入的英文字幕文件名
    output_dir = args.output_dir # 输出文件夹

    # 创建输出文件夹
    os.makedirs(output_dir, exist_ok=True)

    if args.generate_srt:   
        logging.info("开始生成字幕")
        os.system(f"whisper --output_format srt --model turbo --language en -o {output_dir} {input_filename}")
        logging.info("字幕生成完毕")

    if args.src_to_text:
        logging.info("开始合并字幕")
        text = srt_to_text(f"{output_dir}/audio.srt", save_filename=f"{output_dir}/audio_en.txt")
        logging.info("字幕合并完毕")
    else:
        logging.info("跳过合并字幕")
        text = open(f"{output_dir}/audio_en.txt", "r", encoding="utf-8").read()

    if args.translate_text:
        logging.info("开始翻译对话")
        text = translate_text(text, save_filename=f"{output_dir}/audio_zh.txt")
        logging.info("对话翻译完毕")
    else:
        logging.info("跳过翻译对话")
        text = open(f"{output_dir}/audio_zh.txt", "r", encoding="utf-8").read()

    if args.extract_conversation:
        logging.info("开始处理对话")
        conversation = extract_conversation(text, save_filename=f"{output_dir}/conversation.json")
        logging.info("对话处理完毕")
    else:
        logging.info("跳过处理对话")
        conversation = open(f"{output_dir}/conversation.json", "r", encoding="utf-8").read()

    if args.generate_wav_from_conversation:
        logging.info("开始生成播客")
        generate_wav_from_conversation(conversation, wav_filename=f"{output_dir}/audio_zh.wav", mp3_filename=f"{output_dir}/audio_zh.mp3")
        logging.info("播客生成完毕")
    else:
        logging.info("跳过生成播客")

if __name__ == "__main__":
    args = parse_args()
    main(args)
    logging.info("DONE!!!")

