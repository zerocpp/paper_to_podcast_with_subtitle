import srt
import argparse

def srt_to_text(srt_file):
    # 读取SRT文件
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # 解析SRT内容
    subtitles = list(srt.parse(srt_content))
    
    # 提取所有字幕文本并拼接
    full_text = ""
    for subtitle in subtitles:
        full_text += subtitle.content + " "
    
    # 去除多余空格并返回
    return full_text.strip()

def main():
    parser = argparse.ArgumentParser(description="Extract subtitle text from SRT file")
    parser.add_argument("-i", "--input_filename", type=str, default="subtitle.srt", help="输入字幕文件名")
    parser.add_argument("-o", "--output_filename", type=str, default="subtitle_text.txt", help="输出文本文件名")
    args = parser.parse_args()
    
    input_file = args.input_filename  # 输入的SRT文件名
    output_file = args.output_filename  # 输出的文本文件名
    
    # 将SRT转换为文本
    text = srt_to_text(input_file)
    
    # 将文本写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"字幕文本已保存到 {output_file}")

if __name__ == "__main__":
    main()
