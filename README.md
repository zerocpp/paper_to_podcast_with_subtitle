# paper_to_podcast_with_subtitle
论文->播客+双语字幕

## 使用方法
- 首先通过Google的NotebookLM将论文转换成播客音频
- 然后通过ffmpeg将音频(`audio.wav`)和图片(`image.png`)合并成视频(`video.mp4`)
```shell
ffmpeg -loop 1 -i image.png -i audio.wav -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest video.mp4
```
- 接着通过OpenAI的Whisper将音频转换成字幕
```shell
whisper --output_format srt --model turbo --language en audio.wav
```
- 最后通过OpenAI的GPT-4o-mini翻译字幕，并生成双语字幕(`translate_subtitle.py`)
**注：需要配置环境变量OPENAI_API_KEY**
```shell
python translate_subtitle.py -i subtitle.srt -o bilingual_subtitle.srt
```

