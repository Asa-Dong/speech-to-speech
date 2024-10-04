from datetime import datetime
import requests
import pyaudio

def TtsFishSpeechLocal(text, reference_id="mini_001", url="http://127.0.0.1:11435/v1/invoke"):
    payload = {
        "text": text,
        "reference_id": reference_id,
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    
    begin = datetime.now().timestamp()
    response = requests.post(url, json=payload, headers=headers, stream=True)
    print("tts used:", (datetime.now().timestamp() - begin) * 1000)
    
    p = pyaudio.PyAudio()
    if response.status_code == 200:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        output=True)
        
        first_chunk = True
        for chunk in response.iter_content(chunk_size=9600):
            if chunk:
                if first_chunk:
                    first_chunk = False
                    chunk = chunk[44:] # 跳过wav头
                stream.write(chunk)

        stream.stop_stream()
        stream.close()

    p.terminate()

# 示例用法
if __name__ == "__main__":  # Main entry point
    text_to_speak = "我在"
    TtsFishSpeechLocal(text_to_speak)
  

