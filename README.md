# paper_to_podcast_with_subtitle
论文->播客+双语字幕

## 使用方法1（推荐）
- 首先通过Google的NotebookLM将论文转换成播客音频([NotebookLM](https://notebooklm.google))
- 然后通过`translate_podcast.py`将播客音频转换成中文播客
```shell
python translate_podcast.py -i input/2402.18048.wav -o output/2402.18048
```
- 如果需要屏蔽某些步骤，可以参考如下命令：
```shell
python translate_podcast.py -i input/2402.18048.wav -o output/2402.18048 --no-generate_srt --no-src_to_text --no-translate_text --no-extract_conversation --no-generate_wav_from_conversation
```



## 使用方法2
- 首先通过Google的NotebookLM将论文转换成播客音频([NotebookLM](https://notebooklm.google))
- 然后通过ffmpeg将音频(`audio.wav`)和图片(`image.png`)合并成视频(`video.mp4`)
```shell
ffmpeg -loop 1 -i image.png -i audio.wav -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest video.mp4
```
- 接着通过OpenAI的Whisper将音频转换成字幕([Whisper](https://github.com/openai/whisper))
```shell
whisper --output_format srt --model turbo --language en -o OUTPUT_DIR audio.wav
```
- 最后通过OpenAI的GPT-4o-mini翻译字幕，并生成双语字幕(`translate_subtitle.py`)
**注：需要配置环境变量OPENAI_API_KEY**
```shell
python translate_subtitle.py -i subtitle.srt -o bilingual_subtitle.srt
```

- 直接将whisper生成的srt文件转换成文本(`subtitle_to_text.py`)
```shell
python subtitle_to_text.py -i subtitle.srt -o subtitle_text.txt
```

- 将文本直接输入到GTP-o1中去，提示词如下：
```text
给你一段对话音频的转录文本，对话中有且仅有两个人，请帮我翻译成中文，猜测每句话的说话人并标注。对话文本如下：
<SUBTITLE_TEXT>
</SUBTITLE_TEXT>
```

- 将对话提取到json中
```python
python extract_conversation.py
```

- 讲话人: https://github.com/6drf21e/ChatTTS_Speaker?tab=readme-ov-file

- 中文播客生成
```python
python podcast_zh.py
```
