# 使用Edge TTS进行语音合成
import edge_tts
import io
import sounddevice as sd
import soundfile as sf


def TtsEdge(text):
    # 使用Edge TTS生成音频数据
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    
    audio_data = io.BytesIO()
    for chunk in communicate.stream_sync():
        if chunk["type"] == "audio":
           audio_data.write(chunk["data"])
            
    # 将音频数据指针移到开始
    audio_data.seek(0)
    
    # 使用soundfile读取音频数据
    data, samplerate = sf.read(audio_data)
    
    # 使用sounddevice播放音频
    sd.play(data, samplerate)
    sd.wait()  # 等待音频播放完成

if __name__ == "__main__":
    text = "你好，我是小豆子，一个智能助手。"
    TtsEdge(text)