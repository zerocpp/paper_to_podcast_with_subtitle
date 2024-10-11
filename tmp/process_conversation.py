import json

# 读取翻译文本
with open("翻译文本.txt", "r", encoding="utf-8") as file:
    text = file.read()
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

# 保存为json
with open("conversation.json", "w", encoding="utf-8") as file:
    json.dump(conversation, file, ensure_ascii=False, indent=4)
