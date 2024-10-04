# 语音交互项目

这是一个Speech To Speech的项目。

## 功能特性
- 唤醒词检测
- 语音识别 (ASR)
- 语音合成 (TTS)
- 支持多种ASR和TTS引擎

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

