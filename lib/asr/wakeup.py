import pyaudio
import numpy as np
from funasr import AutoModel
from datetime import datetime

from funasr.models.fsmn_kws.model import FsmnKWS, DatadirWriter


import time
import torch

from funasr.utils.load_utils import load_audio_text_image_video, extract_fbank


## 修复必须配置
def custom_inference(
    self,
    data_in,
    data_lengths=None,
    key: list = None,
    tokenizer=None,
    frontend=None,
    **kwargs,
):
    keywords = kwargs.get("keywords")
    from funasr.utils.kws_utils import KwsCtcPrefixDecoder

    self.kws_decoder = KwsCtcPrefixDecoder(
        ctc=self.ctc,
        keywords=keywords,
        token_list=tokenizer.token_list,
        seg_dict=tokenizer.seg_dict,
    )

    meta_data = {}
    if (
        isinstance(data_in, torch.Tensor)
        and kwargs.get("data_type", "sound") == "fbank"
    ):  # fbank
        speech, speech_lengths = data_in, data_lengths
        if len(speech.shape) < 3:
            speech = speech[None, :, :]
        if speech_lengths is not None:
            speech_lengths = speech_lengths.squeeze(-1)
        else:
            speech_lengths = speech.shape[1]
    else:
        # extract fbank feats
        time1 = time.perf_counter()
        audio_sample_list = load_audio_text_image_video(
            data_in,
            fs=frontend.fs,
            audio_fs=kwargs.get("fs", 16000),
            data_type=kwargs.get("data_type", "sound"),
            tokenizer=tokenizer,
        )
        time2 = time.perf_counter()
        meta_data["load_data"] = f"{time2 - time1:0.3f}"
        speech, speech_lengths = extract_fbank(
            audio_sample_list,
            data_type=kwargs.get("data_type", "sound"),
            frontend=frontend,
        )
        time3 = time.perf_counter()
        meta_data["extract_feat"] = f"{time3 - time2:0.3f}"
        meta_data["batch_data_time"] = (
            speech_lengths.sum().item() * frontend.frame_shift * frontend.lfr_n / 1000
        )

    speech = speech.to(device=kwargs["device"])
    speech_lengths = speech_lengths.to(device=kwargs["device"])

    # Encoder
    encoder_out, encoder_out_lens = self.encode(speech, speech_lengths)
    if isinstance(encoder_out, tuple):
        encoder_out = encoder_out[0]

    results = []
    if kwargs.get("output_dir") is not None:
        if not hasattr(self, "writer"):
            self.writer = DatadirWriter(kwargs.get("output_dir"))

    for i in range(encoder_out.size(0)):
        x = encoder_out[i, : encoder_out_lens[i], :]
        detect_result = self.kws_decoder.decode(x)
        is_deted, det_keyword, det_score = (
            detect_result[0],
            detect_result[1],
            detect_result[2],
        )

        if is_deted:
            det_info = "detected " + det_keyword + " " + str(det_score)
        else:
            det_info = "rejected"

        result_i = {"key": key[i], "text": det_info}
        results.append(result_i)

    return results, meta_data


# 将自定义的 inference 方法绑定到 FsmnKWS 类
FsmnKWS.inference = custom_inference

class WakeupModel:
    def __init__(self, keywords: str):

        self.model = AutoModel(
            model="iic/speech_charctc_kws_phone-xiaoyun",
            keywords=keywords,
            disable_pbar=True,
            disable_log=True,
            disable_update=True,
        )
        self.frames = []
        self.wait_size = 2

    def generate(self, input):
        # [{'key': 'rand_key_ILtky5j8iZouG', 'text': 'detected 小豆子 0.19719722207401819'}]
        # [{'key': 'rand_key_HAGt8hjB5KB7f', 'text': 'rejected'}]
        
        self.frames.append(input)
        if len(self.frames) > self.wait_size:
            self.frames = self.frames[-self.wait_size:]
            res = self.model.generate(input=b"".join(self.frames))
            if res is not None and res[0] is not None and res[0]["text"].find("detected") != -1:
                return True, self.frames
        return False, None


if __name__ == "__main__":
    model = WakeupModel("小云小云")
    
   # # 音频流参数
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    num_frames = 9600

    # 初始化pyaudio
    audio = pyaudio.PyAudio()

    # 打开音频流
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=num_frames)

    print("Listening...")

    try:
        while True:
            frame = stream.read(num_frames)
            
            begin = datetime.now().timestamp()
            res, _ = model.generate(frame)
            if res:
                print(res, (datetime.now().timestamp() - begin) * 1000)
    finally:
        # 关闭音频流
        stream.stop_stream()
        stream.close()
        audio.terminate()

