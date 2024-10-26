from typing import List
from dataclasses import dataclass, field
from enum import Enum
import os


class StreamType(Enum):
    RTSP = "rtsp"
    HLS = "hls"
    BOTH = "both"


def _parse_int_list(value: str) -> List[int]:
    """Parse comma-separated string of integers into a list"""
    if not value:
        return []
    return [int(x.strip()) for x in value.split(',')]


@dataclass
class StreamConfig:
    input_url: str = os.getenv('INPUT_RTSP', '')
    output_path: str = os.getenv('OUTPUT_HLS', '/app/hls_output')
    
    # HLS Configuration
    segment_duration: int = int(os.getenv('HLS_SEGMENT_DURATION', '4'))
    playlist_size: int = int(os.getenv('HLS_PLAYLIST_SIZE', '5'))
    
    # Video Configuration
    video_bitrates: List[int] = field(default_factory=lambda: _parse_int_list(
        os.getenv('VIDEO_BITRATES', '2000000,1000000,500000')
    ))
    video_codec: str = os.getenv('VIDEO_CODEC', 'h264')
    video_preset: str = os.getenv('VIDEO_PRESET', 'ultrafast')
    width: int = int(os.getenv('VIDEO_WIDTH', '1280'))
    height: int = int(os.getenv('VIDEO_HEIGHT', '720'))
    fps: int = int(os.getenv('VIDEO_FPS', '30'))
    keyframe_interval: int = int(os.getenv('VIDEO_KEYFRAME_INTERVAL', '60'))
    
    # Audio Configuration
    audio_bitrates: List[int] = field(default_factory=lambda: _parse_int_list(
        os.getenv('AUDIO_BITRATES', '128000,64000')
    ))
    audio_codec: str = os.getenv('AUDIO_CODEC', 'aac')
    audio_sample_rate: int = int(os.getenv('AUDIO_SAMPLE_RATE', '44100'))
    audio_channels: int = int(os.getenv('AUDIO_CHANNELS', '2'))
    
    # Buffer Configuration
    max_buffer_size: int = int(os.getenv('MAX_BUFFER_SIZE', '60'))
    
    # RTSP Configuration
    rtsp_transport: str = os.getenv('RTSP_TRANSPORT', 'tcp')
    rtsp_timeout: int = int(os.getenv('RTSP_TIMEOUT', '5000000'))
    
    # Server Configuration
    rtsp_server_port: int = int(os.getenv('RTSP_SERVER_PORT', '8554'))
    hls_server_port: int = int(os.getenv('HLS_SERVER_PORT', '8080'))
    
    # Feature Flags
    enable_stats: bool = os.getenv('ENABLE_STATS', 'true').lower() == 'true'
    enable_debug: bool = os.getenv('ENABLE_DEBUG', 'false').lower() == 'true'

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.input_url:
            raise ValueError("INPUT_RTSP environment variable is required")
        
        if not self.video_bitrates:
            raise ValueError("At least one video bitrate must be specified")
            
        if not self.audio_bitrates:
            raise ValueError("At least one audio bitrate must be specified")
            
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Invalid video dimensions")
            
        if self.fps <= 0:
            raise ValueError("Invalid FPS value")
            
        if self.segment_duration <= 0:
            raise ValueError("Invalid segment duration")
            
        if self.playlist_size <= 0:
            raise ValueError("Invalid playlist size")

    def get_rtsp_options(self) -> dict:
        """Get RTSP-specific options"""
        return {
            'rtsp_transport': self.rtsp_transport,
            'stimeout': str(self.rtsp_timeout)
        }

    def get_video_options(self) -> dict:
        """Get video codec options"""
        return {
            'preset': self.video_preset,
            'tune': 'zerolatency',
            'profile': 'baseline',
            'x264opts': f'keyint={self.keyframe_interval}:min-keyint={self.keyframe_interval}'
        }

    def get_audio_options(self) -> dict:
        """Get audio codec options"""
        return {
            'b:a': f'{self.audio_bitrates[0]}',
            'ar': str(self.audio_sample_rate),
            'ac': str(self.audio_channels)
        }
