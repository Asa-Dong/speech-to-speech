import io
import os
import sounddevice as sd
import soundfile as sf

from fish_audio_sdk import Session, TTSRequest

class TtsFishSpeech:    
    def __init__(self, api_key, reference_id):
        self.session = Session(api_key)
        self.reference_id = reference_id
        
    def speak(self, text):
        audio_data = io.BytesIO()

        for chunk in self.session.tts(TTSRequest(
            reference_id=self.reference_id,
            text=text
        )):
            audio_data.write(chunk)
            
        audio_data.seek(0)
        data, samplerate = sf.read(audio_data)
        sd.play(data, samplerate)
        sd.wait()

# 示例用法
if __name__ == "__main__":  # Main entry point
    text_to_speak = "我在"
    api_key = os.getenv("FISH_API_KEY")
    reference_id = os.getenv("FISH_REFERENCE_ID")
    tts = TtsFishSpeech(api_key, reference_id)
    tts.speak(text_to_speak)
  

