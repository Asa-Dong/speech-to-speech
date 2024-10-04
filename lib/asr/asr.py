from datetime import datetime
import sys
import pyaudio
import logging

from funasr import AutoModel
from lib.asr.ali_senseVoice import AsrAliSenseVoice
from lib.asr.wakeup import WakeupModel

from modelscope.utils.logger import get_logger

logger = get_logger(log_level=logging.CRITICAL)
logger.setLevel(logging.CRITICAL)


class VAD:
    def __init__(self):
        self.model = AutoModel(
            model="fsmn-vad",
            model_revision="v2.0.4",
            disable_pbar=True,
            # disable_log=True,
            disable_update=True,
        )
        self.cache_vad = {}

    # chunk_ms x ms
    def process(self, audio_in, chunk_ms=2048):
        segments_result = self.model.generate(
            input=audio_in, cache=self.cache_vad, is_final=False, chunk_size=chunk_ms
        )
        speech_start = False
        speech_end = False

        if len(segments_result) == 0 or len(segments_result[0]["value"]) == 0:
            return speech_start, speech_end

        r = segments_result[0]["value"][0]
        if r[0] != -1:
            speech_start = True
        if r[1] != -1:
            speech_end = True
        return speech_start, speech_end


class AudioStream:
    def __init__(self, sample_rate: int, num_frames: int):
        self.sample_rate = sample_rate
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=num_frames,
        )

    def read(self, num_frames: int):
        return self.stream.read(num_frames)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class WakeupAndASR:
    def __init__(self, keywords="小云小云"):
        self.keywords = keywords
        self.wakeup = WakeupModel(keywords=self.keywords)
        self.vad = VAD()
        self.asr = AsrAliSenseVoice()

        # self.asrStream = ASRStreamProcessor()

        sample_rate = 16000  # base
        chunk_size = [0, 8, 4]  # base
        chunk_size_ms = [0, chunk_size[1] * 60, chunk_size[1] * 60]
        num_frames = int(sample_rate * chunk_size_ms[1] / 1000)

        config = {
            "sample_rate": sample_rate,
            "num_frames": num_frames,
            "chunk_size": chunk_size,
            "chunk_size_ms": chunk_size_ms,
        }
        self.config = config
        self.stream = AudioStream(config["sample_rate"], config["num_frames"])

    def processAsr(self, wakeup_chunks, is_exit):
        speak_start = False
        speak_end = False
        chunks = []
        speak_lose_count = 0

        while True:
            if is_exit:
                return
            try:
                chunk = self.stream.read(self.config["num_frames"])
            except Exception as e:
                print(e)
                continue

            chunks.append(chunk)

            # begin = datetime.now().timestamp()
            start, end = self.vad.process(
                chunk, chunk_ms=self.config["chunk_size_ms"][1]
            )
            # print("vad", (datetime.now().timestamp() - begin) * 1000, start, end)

            if not speak_start and start:
                speak_start = True
                print("speak_start")
            if not speak_end and end:
                speak_end = True
                print("speak_end")

            if not speak_start:
                speak_lose_count += 1
            if speak_lose_count > 10:
                return

            # begin = datetime.now().timestamp()
            # txt2 = asrStream.process_audio(chunk, chunk_size=chunk_size, is_final=speak_end)
            # print(txt2, speak_end, (datetime.now().timestamp() - begin) * 1000)

            if speak_end:
                if len(chunks) < 2:
                    speak_start = False
                    speak_end = False
                    continue

                chunks = wakeup_chunks + chunks
                res = self.asr.process(b"".join(chunks), hotword=self.keywords)
                if res:
                    return res

    def waitOne(self, is_exit=False):
        while True:
            if is_exit:
                return
            try:
                chunk = self.stream.read(self.config["num_frames"])
            except Exception as e:
                print(e)
                continue

            res, wakeup_chunks = self.wakeup.generate(chunk)
            sys.stdout.write(
                "\r"
                + "["
                + datetime.now().strftime("%H:%M:%S")
                + "] waiting..."
            )
            sys.stdout.flush()

            if not res:
                continue
            print("\nwakeup")

            res = self.processAsr(wakeup_chunks, is_exit)
            if res:
                return res


if __name__ == "__main__":
    w = WakeupAndASR()
    while True:
        w.waitOne()
