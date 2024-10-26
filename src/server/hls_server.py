import logging
from pathlib import Path
import m3u8
from aiohttp import web
import jinja2
import aiohttp_jinja2
import time
from ..config import StreamConfig

logger = logging.getLogger(__name__)

class HLSServer:
    """HLS Server Implementation"""

    def __init__(self, config: StreamConfig):
        self.config = config
        self.segments = []
        self.app = web.Application()
        self._setup_routes()
        self._setup_templates()
        self.converter = None  # Will be set by the DSL
        logger.info("HLS Server initialized")

    def _setup_templates(self):
        """Setup Jinja2 templates"""
        template_dir = Path(__file__).parent.parent / 'templates'
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(str(template_dir)))
        logger.debug(f"Templates directory set to: {template_dir}")

    def _setup_routes(self):
        """Setup HLS server routes"""
        # API routes
        self.app.router.add_get('/stream.m3u8', self._handle_master_playlist)
        self.app.router.add_get('/stream_{bitrate}.m3u8', self._handle_playlist)
        self.app.router.add_get('/segment_{id}.ts', self._handle_segment)
        self.app.router.add_get('/player', self._handle_player)
        self.app.router.add_get('/stats', self._handle_stats)
        
        # Add CORS middleware
        self.app.middlewares.append(self._cors_middleware)
        logger.debug("Routes and middleware configured")

    @web.middleware
    async def _cors_middleware(self, request, handler):
        """Handle CORS"""
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)
            
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
        return response

    async def start(self):
        """Start HLS server"""
        logger.info("Starting HLS server...")
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.config.hls_server_port)
        await site.start()
        logger.info(f"HLS Server started on port {self.config.hls_server_port}")
        logger.debug(f"Server configuration: {vars(self.config)}")

    @aiohttp_jinja2.template('player.html')
    async def _handle_player(self, request):
        """Handle player page request"""
        logger.debug(f"Player page requested from {request.remote}")
        return {
            'stream_url': '/stream.m3u8',
            'server_url': f'http://{request.host}'
        }

    async def _handle_stats(self, request):
        """Handle stats request"""
        logger.debug(f"Stats requested from {request.remote}")
        if hasattr(self, 'converter') and self.converter:
            current_time = time.time()
            elapsed = current_time - self.converter.stats['start_time']
            stats = {
                'processed_video_frames': self.converter.stats['processed_video_frames'],
                'processed_audio_frames': self.converter.stats['processed_audio_frames'],
                'video_fps': self.converter.stats['processed_video_frames'] / elapsed if elapsed > 0 else 0,
                'audio_fps': self.converter.stats['processed_audio_frames'] / elapsed if elapsed > 0 else 0,
                'encoding_errors': self.converter.stats['encoding_errors']
            }
            logger.debug(f"Returning stats: {stats}")
            return web.json_response(stats)
        return web.json_response({
            'processed_video_frames': 0,
            'processed_audio_frames': 0,
            'video_fps': 0,
            'audio_fps': 0,
            'encoding_errors': 0
        })

    async def _handle_master_playlist(self, request):
        """Handle master playlist request"""
        logger.debug("Master playlist requested")
        playlist = m3u8.M3U8()
        playlist.is_endlist = False
        playlist.is_live = True

        # Add different quality variants
        for bitrate in self.config.video_bitrates:
            playlist.add_playlist(
                uri=f'/stream_{bitrate}.m3u8',
                stream_info={
                    'bandwidth': bitrate,
                    'resolution': f"{self.config.width}x{self.config.height}",
                    'codecs': 'avc1.42E01E,mp4a.40.2'
                }
            )

        logger.debug(f"Generated master playlist with {len(self.config.video_bitrates)} variants")
        return web.Response(
            text=playlist.dumps(),
            content_type='application/vnd.apple.mpegurl'
        )

    async def _handle_playlist(self, request):
        """Handle media playlist request"""
        bitrate = request.match_info['bitrate']
        logger.debug(f"Media playlist requested for bitrate {bitrate}")
        
        playlist = m3u8.M3U8()
        playlist.target_duration = self.config.segment_duration
        playlist.is_endlist = False
        playlist.is_live = True

        # Add segments
        for segment in self.segments[-self.config.playlist_size:]:
            playlist.add_segment(
                uri=f'/segment_{segment["id"]}.ts',
                duration=segment["duration"]
            )

        logger.debug(f"Generated media playlist with {len(self.segments[-self.config.playlist_size:])} segments")
        return web.Response(
            text=playlist.dumps(),
            content_type='application/vnd.apple.mpegurl'
        )

    async def _handle_segment(self, request):
        """Handle segment request"""
        segment_id = request.match_info['id']
        logger.debug(f"Segment requested: {segment_id}")
        
        segment_path = Path(self.config.output_path) / f'segment_{segment_id}.ts'

        if not segment_path.exists():
            logger.warning(f"Segment not found: {segment_path}")
            raise web.HTTPNotFound()

        logger.debug(f"Serving segment: {segment_path}")
        return web.FileResponse(segment_path)
