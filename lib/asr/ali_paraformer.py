from funasr import AutoModel

class AsrAliParaformer:
    def __init__(self):
        self.cache_asr_stream = {}
        self.encoder_chunk_look_back = 4
        self.decoder_chunk_look_back = 1
        self.model = AutoModel(
            model="paraformer-zh",
            model_revision="v2.0.4",
            vad_model="fsmn-vad",
            vad_model_revision="v2.0.4",
            punc_model="ct-punc-c",
            punc_model_revision="v2.0.4",
            # spk_model="cam++", spk_model_revision="v2.0.2",
            disable_pbar=True,
            disable_log=True,
            disable_update=True,
        )

    def process(self, audio_in, hotword=""):
        res = self.model.generate(
            input=audio_in,
            #   batch_size_s=300,
            hotword=hotword,
        )

        # [{'key': 'rand_key_KJq7RcDzUhzwF', 'text': '小云小云，你好呀。', 'timestamp': [[170, 330], [330, 430], [430, 550], [550, 770], [770, 890], [890, 990], [990, 1315]]}]
        if res is not None and len(res) > 0:
            return res[0]
        return ""