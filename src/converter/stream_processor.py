from ..config import StreamConfig

class StreamProcessor:
    def __init__(self, config: StreamConfig):
        self.config = config
        self.running = False
        self._init_codecs()

    def _init_codecs(self):
        """Initialize codec configurations"""
        self.video_codec_options = {
            "h264": {
                "preset": "veryfast",
                "tune": "zerolatency",
                "x264-params": "keyint=60:min-keyint=60"
            }
        }

        self.audio_codec_options = {
            "aac": {
                "b:a": "128k",
                "ar": 44100
            }
        }
