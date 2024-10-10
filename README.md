# 语音交互项目

这是一个Speech To Speech的项目。

## 功能特性
- 唤醒词检测
  - iic/speech_charctc_kws_phone-xiaoyun  该模型使用其它词仅仅可用，要效果好需要训练。
- VAD
- 语音识别 (ASR)
  - senseVoice、 paraformer
- 语音合成 (TTS)
  - fish  https://fish.audio/zh-CN/
  - fish_local  本地自建 https://github.com/fishaudio/fish-speech
  - edge
- LLM 大语言模型
  - ollama
  - deepseek

## 安装

1. 创建并激活虚拟环境:
   ```bash
    uv venv -p 3.12
    uv pip install -r .\requirements.txt
    source .venv/bin/activate  # 在Windows上使用 .venv\Scripts\activate
   ```

4. 配置环境变量:
   复制`.env.example`文件为`.env`，并填写必要的API密钥和配置。

## 使用方法

运行主程序:

```
python main.py
```

