import os
import openai
import srt
import argparse
from tqdm import tqdm

# 设置OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def translate_text(text):
    try:
        # 使用OpenAI的ChatCompletion接口进行翻译
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个翻译助手。"},
                {"role": "user", "content": f"请将以下英文文本翻译成中文：\n\n{text}"}
            ],
            temperature=0, # 翻译的准确性
            max_tokens=1024
        )
        translation = completion.choices[0].message.content
        return translation.strip()
    except Exception as e:
        print(f"翻译时出错：{e}")
        return ""
    
def create_bilingual_srt(subtitles):
    bilingual_subtitles = []
    for subtitle in tqdm(subtitles):
        original_text = subtitle.content
        translation = translate_text(original_text)
        combined_text = f"{original_text}\n{translation}"
        subtitle.content = combined_text
        bilingual_subtitles.append(subtitle)
    return bilingual_subtitles


def main(args):
    input_filename = args.input_filename # 输入的英文字幕文件名
    output_filename = args.output_filename # 输出的中英双语字幕文件名
    with open(input_filename, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    subtitles = list(srt.parse(srt_content))
    bilingual_subtitles = create_bilingual_srt(subtitles)
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(srt.compose(bilingual_subtitles))
    print(f"中英双语字幕文件已保存为 {output_filename}")


def parse_args():
    parser = argparse.ArgumentParser(description="Translate subtitle file")
    parser.add_argument("-i", "--input_filename", type=str, default="subtitle.srt", help="输入字幕文件名")
    parser.add_argument("-o", "--output_filename", type=str, default="bilingual_subtitle.srt", help="输出双语字幕文件名")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    main(args)

