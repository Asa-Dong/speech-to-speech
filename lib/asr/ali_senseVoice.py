import re

from funasr import AutoModel


class AsrAliSenseVoice:
    def __init__(self):
        model_dir = "iic/SenseVoiceSmall"

        self.model = AutoModel(
            model=model_dir,
            # trust_remote_code=True,
            # vad_model="fsmn-vad",
            # vad_kwargs={"max_single_segment_time": 30000},
            disable_pbar=True,
            disable_log=True,
            disable_update=True,
        )

    def process(self, audio_in, hotword=""):
        res = self.model.generate(
            input=audio_in,
            cache={},
            language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
            use_itn=True,
            batch_size_s=60,
            merge_vad=True,  #
            merge_length_s=15,
        )
        # [{'key': 'vad_example', 'text': '<|zh|><|ANGRY|><|Speech|><|withitn|>试错的过程很简单。'}]
        if res and len(res) > 0 and len(res[0]["text"]) > 0:
            text = res[0]["text"]
            text = re.sub(r"<\|.*?\|>", "", text)
            return text
        return ""


if __name__ == "__main__":
    text = "<|zh|><|ANGRY|><|Speech|><|withitn|>试错的过程很简单。"
    print("原始文本:", text)
    print("处理后文本:", re.sub(r"<\|.*?\|>", "", text))
