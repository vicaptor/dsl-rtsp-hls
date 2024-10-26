from typing import List, Optional
from ..config import StreamConfig, StreamType
from ..converter import StreamConverter
from ..server import HLSServer
import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoStreamDSL:
    """DSL for video streaming configuration"""

    def __init__(self):
        # Use local output directory when not in Docker
        default_output = '/app/hls_output' if os.path.exists('/.dockerenv') else 'hls_output'
        
        # Create output directory if it doesn't exist
        output_path = os.getenv('OUTPUT_HLS', default_output)
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize with empty values, they will be set through DSL methods
        self.config = StreamConfig(
            input_url=os.getenv('INPUT_RTSP', ''),
            output_path=output_path
        )
        self.stream_type = StreamType.BOTH
        self.rtsp_port = int(os.getenv('RTSP_SERVER_PORT', '8554'))
        self.hls_port = int(os.getenv('HLS_SERVER_PORT', '8080'))
        self.hls_server = None
        self.converter = None

    def source(self, url: str = None) -> 'VideoStreamDSL':
        """Define stream source"""
        if url:
            self.config.input_url = url
        elif not self.config.input_url:
            raise ValueError("Stream source URL is required")
        return self

    def rtsp(self, port: int = None) -> 'VideoStreamDSL':
        """Configure RTSP output"""
        self.stream_type = StreamType.RTSP
        if port:
            self.rtsp_port = port
        return self

    def hls(self, segment_duration: int = None,
            playlist_size: int = None,
            port: int = None) -> 'VideoStreamDSL':
        """Configure HLS output"""
        self.stream_type = StreamType.HLS
        if segment_duration:
            self.config.segment_duration = segment_duration
        if playlist_size:
            self.config.playlist_size = playlist_size
        if port:
            self.hls_port = port
        return self

    def adaptive_bitrate(self, video_bitrates: List[int] = None,
                        audio_bitrates: List[int] = None) -> 'VideoStreamDSL':
        """Configure adaptive bitrate streaming"""
        if video_bitrates:
            self.config.video_bitrates = video_bitrates
        if audio_bitrates:
            self.config.audio_bitrates = audio_bitrates
        return self

    def output(self, path: str = None) -> 'VideoStreamDSL':
        """Define output path"""
        if path:
            self.config.output_path = path
            Path(path).mkdir(parents=True, exist_ok=True)
        return self

    async def start_hls_server(self):
        """Start HLS server"""
        if self.stream_type in [StreamType.HLS, StreamType.BOTH]:
            self.hls_server = HLSServer(self.config)
            await self.hls_server.start()
            logger.info(f"HLS server started on port {self.hls_port}")
            
            # Generate web player URL
            player_url = f"http://localhost:{self.hls_port}/player"
            logger.info(f"Web player available at: {player_url}")

    async def build(self) -> StreamConverter:
        """Build and return stream converter"""
        self.converter = StreamConverter(self.config)
        if self.hls_server:
            self.converter.set_hls_server(self.hls_server)
        return self.converter

    async def run(self):
        """Run the complete streaming pipeline"""
        try:
            # Start HLS server
            await self.start_hls_server()
            
            # Build and start converter
            self.converter = await self.build()
            await asyncio.gather(
                self.converter.start_conversion(),
                self.converter._log_stats() if self.config.enable_stats else asyncio.sleep(0)
            )
        except Exception as e:
            logger.error(f"Error running streaming pipeline: {e}")
            raise
