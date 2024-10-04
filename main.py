from datetime import datetime
import os
from lib.asr.asr import WakeupAndASR
from lib.llama.llama_deepseek import LlamaDeepseek
from lib.llama.llama_ollama import LlamaOllama
from lib.tts.tts_edge import TtsEdge
from lib.tts.tts_fish_speech import TtsFishSpeech
from dotenv import load_dotenv

from lib.tts.tts_fish_speech_local import TtsFishSpeechLocal

load_dotenv()

def create_tts():
    tts_fish = None
    
    def tts(text):
        nonlocal tts_fish
        provider = os.getenv("TTS_PROVIDER")
        if provider == "fish":
            if not tts_fish:
                tts_fish = TtsFishSpeech(os.getenv("TTS_FISH_API_KEY"), os.getenv("TTS_FISH_REFERENCE_ID"))
            tts_fish.speak(text)
        elif provider == "fish_local":
            TtsFishSpeechLocal(text)
        elif provider == "edge":
            TtsEdge(text)
        else:
            raise Exception(f"Unknown TTS provider: {provider}")
    return tts

def create_llama():
    def llama(text):
        provider = os.getenv("LLAMA_PROVIDER")
        prompt = os.getenv("LLAMA_PROMPT")
        if provider == "deepseek":
            return LlamaDeepseek(text, prompt.format(role_name=role_name))
        elif provider == "ollama":
            return LlamaOllama(text, prompt.format(role_name=role_name))
        else:
            raise Exception(f"Unknown LLAMA provider: {provider}")
    return llama


if __name__ == "__main__":
    role_name = os.getenv("ROLE_NAME")
    tts = create_tts()
    w = WakeupAndASR(role_name)
    llama = create_llama()
    while True:
        try:
            text = w.waitOne()
        except KeyboardInterrupt as e:
            print("exit")
            exit(0)
        if not text:
            continue

        print("asr question:", text)

        begin = datetime.now().timestamp()
        res = llama(text)
        if not res:
            continue
        print(f"answer: {res}  {(datetime.now().timestamp() - begin) * 1000:.2f}ms")

        begin = datetime.now().timestamp()
        tts(res)
        print(f"tts: {(datetime.now().timestamp() - begin) * 1000:.2f}ms")


