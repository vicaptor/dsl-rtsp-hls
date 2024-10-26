import logging
import time
import av
from pathlib import Path
from fractions import Fraction
import asyncio
from ..config import StreamConfig

logger = logging.getLogger(__name__)

class StreamConverter:
    def __init__(self, config: StreamConfig):
        self.config = config
        self._init_stats()
        Path(config.output_path).mkdir(parents=True, exist_ok=True)
        self.segment_id = 0
        self.current_segment = None
        self.hls_server = None
        logger.info("Stream converter initialized")
        logger.debug(f"Configuration: {vars(config)}")

    def _init_stats(self):
        self.stats = {
            "processed_video_frames": 0,
            "processed_audio_frames": 0,
            "dropped_frames": 0,
            "encoding_errors": 0,
            "start_time": time.time()
        }
        logger.debug("Statistics initialized")

    def set_hls_server(self, server):
        """Set HLS server reference"""
        self.hls_server = server
        server.converter = self
        logger.info("HLS server reference set")

    def _create_new_segment(self):
        """Create a new HLS segment"""
        self.segment_id += 1
        segment_path = Path(self.config.output_path) / f'segment_{self.segment_id}.ts'
        self.current_segment = {
            'id': self.segment_id,
            'path': segment_path,
            'start_time': time.time(),
            'duration': 0
        }
        logger.debug(f"Created new segment: {segment_path}")
        return av.open(str(segment_path), 'w')

    async def start_conversion(self):
        """Start stream conversion process"""
        logger.info(f"Starting conversion from {self.config.input_url}")
        logger.debug(f"Using output path: {self.config.output_path}")
        logger.debug(f"Video settings: {self.config.width}x{self.config.height} @ {self.config.fps}fps")
        logger.debug(f"Video bitrates: {self.config.video_bitrates}")
        logger.debug(f"Audio bitrates: {self.config.audio_bitrates}")
        
        try:
            logger.info("Opening input stream...")
            input_container = av.open(self.config.input_url, options={
                'rtsp_transport': 'tcp',
                'stimeout': '5000000'
            })
            logger.info("Input stream opened successfully")
            
            logger.info("Starting stream processing...")
            await self._process_stream(input_container)
        except Exception as e:
            logger.error(f"Error in conversion: {e}", exc_info=True)
            raise
        finally:
            try:
                input_container.close()
                logger.info("Input stream closed")
            except Exception as e:
                logger.error(f"Error closing input stream: {e}", exc_info=True)

    async def _process_stream(self, input_container):
        """Process input stream"""
        try:
            # Get input streams
            input_streams = input_container.streams
            video_stream = next((s for s in input_streams if s.type == 'video'), None)
            audio_stream = next((s for s in input_streams if s.type == 'audio'), None)

            if not video_stream:
                raise ValueError("No video stream found in input")

            logger.info(f"Input video stream: {video_stream}")
            if audio_stream:
                logger.info(f"Input audio stream: {audio_stream}")

            # Create output segment
            output_container = self._create_new_segment()
            logger.info(f"Created new segment: {self.current_segment['path']}")
            segment_start_time = time.time()

            # Create output streams
            output_video_stream = output_container.add_stream(self.config.video_codec)
            output_video_stream.width = self.config.width
            output_video_stream.height = self.config.height
            output_video_stream.pix_fmt = "yuv420p"
            output_video_stream.bit_rate = self.config.video_bitrates[0]
            output_video_stream.time_base = video_stream.time_base
            if self.config.video_codec == "h264":
                output_video_stream.options = {
                    'preset': 'ultrafast',
                    'tune': 'zerolatency',
                    'profile': 'baseline'
                }

            output_audio_stream = None
            if audio_stream:
                output_audio_stream = output_container.add_stream(self.config.audio_codec)
                output_audio_stream.bit_rate = self.config.audio_bitrates[0]
                output_audio_stream.rate = audio_stream.rate or 44100
                output_audio_stream.layout = audio_stream.layout or "stereo"
                output_audio_stream.time_base = audio_stream.time_base

            logger.info("Streams and codecs initialized successfully")
            frame_count = 0

            # Process frames
            for packet in input_container.demux():
                try:
                    current_time = time.time()
                    if current_time - segment_start_time >= self.config.segment_duration:
                        # Close current segment
                        output_container.close()
                        self.current_segment['duration'] = current_time - self.current_segment['start_time']
                        if self.hls_server:
                            self.hls_server.segments.append(self.current_segment)
                            logger.debug(f"Added segment {self.segment_id} to HLS server")
                        
                        # Create new segment
                        output_container = self._create_new_segment()
                        segment_start_time = current_time
                        
                        # Recreate streams for new segment
                        output_video_stream = output_container.add_stream(self.config.video_codec)
                        output_video_stream.width = self.config.width
                        output_video_stream.height = self.config.height
                        output_video_stream.pix_fmt = "yuv420p"
                        output_video_stream.bit_rate = self.config.video_bitrates[0]
                        output_video_stream.time_base = video_stream.time_base
                        
                        if audio_stream:
                            output_audio_stream = output_container.add_stream(self.config.audio_codec)
                            output_audio_stream.bit_rate = self.config.audio_bitrates[0]
                            output_audio_stream.rate = audio_stream.rate or 44100
                            output_audio_stream.layout = audio_stream.layout or "stereo"
                            output_audio_stream.time_base = audio_stream.time_base

                    for frame in packet.decode():
                        if isinstance(frame, av.VideoFrame):
                            frame_count += 1
                            # Ensure frame has correct format and size
                            if (frame.width != self.config.width or
                                    frame.height != self.config.height or
                                    frame.format.name != "yuv420p"):
                                frame = frame.reformat(
                                    width=self.config.width,
                                    height=self.config.height,
                                    format="yuv420p"
                                )

                            packets = output_video_stream.encode(frame)
                            for out_packet in packets:
                                output_container.mux(out_packet)

                            self.stats["processed_video_frames"] += 1

                            if frame_count % 100 == 0:
                                logger.info(f"Processed {frame_count} video frames")
                                logger.debug(f"Current stats: {self.stats}")

                        elif isinstance(frame, av.AudioFrame) and output_audio_stream:
                            packets = output_audio_stream.encode(frame)
                            for out_packet in packets:
                                output_container.mux(out_packet)

                            self.stats["processed_audio_frames"] += 1

                except Exception as e:
                    logger.error(f"Error processing frame: {e}", exc_info=True)
                    self.stats["encoding_errors"] += 1

            # Flush encoders
            if output_video_stream:
                packets = output_video_stream.encode(None)
                for packet in packets:
                    output_container.mux(packet)

            if output_audio_stream:
                packets = output_audio_stream.encode(None)
                for packet in packets:
                    output_container.mux(packet)

            output_container.close()
            logger.info("Stream processing completed")

        except Exception as e:
            logger.error(f"Error in stream processing: {e}", exc_info=True)
            raise

    async def _log_stats(self):
        """Log processing statistics"""
        while True:
            current_time = time.time()
            elapsed = current_time - self.stats["start_time"]

            if elapsed > 0:
                logger.info(
                    f"Stats: "
                    f"Video frames: {self.stats['processed_video_frames']}, "
                    f"Audio frames: {self.stats['processed_audio_frames']}, "
                    f"Errors: {self.stats['encoding_errors']}, "
                    f"Video FPS: {self.stats['processed_video_frames'] / elapsed:.2f}, "
                    f"Audio FPS: {self.stats['processed_audio_frames'] / elapsed:.2f}"
                )

            await asyncio.sleep(5)
