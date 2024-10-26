import asyncio
import logging
from typing import List
from ..config import StreamConfig

logger = logging.getLogger(__name__)

class RTSPServer:
    """RTSP Server Implementation"""

    def __init__(self, config: StreamConfig):
        self.config = config
        self.clients = {}
        self.session_counter = 0

    async def start(self):
        """Start RTSP server"""
        server = await asyncio.start_server(
            self._handle_client,
            'localhost',
            8554
        )

        logger.info("RTSP Server started on port 8554")
        await server.serve_forever()

    async def _handle_client(self, reader, writer):
        """Handle RTSP client connection"""
        session_id = self._generate_session_id()
        self.clients[session_id] = {
            'reader': reader,
            'writer': writer,
            'state': 'INIT'
        }

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                response = await self._process_rtsp_request(data, session_id)
                writer.write(response)
                await writer.drain()

        except Exception as e:
            logger.error(f"Error handling RTSP client: {e}")
        finally:
            del self.clients[session_id]
            writer.close()
            await writer.wait_closed()

    def _generate_session_id(self):
        """Generate unique session ID"""
        self.session_counter += 1
        return f"session_{self.session_counter}"

    async def _process_rtsp_request(self, data: bytes, session_id: str) -> bytes:
        """Process RTSP request and generate response"""
        request = data.decode().split('\r\n')
        request_type = request[0].split()[0]

        if request_type == 'OPTIONS':
            return self._handle_options()
        elif request_type == 'DESCRIBE':
            return self._handle_describe(request[0])
        elif request_type == 'SETUP':
            return self._handle_setup(request, session_id)
        elif request_type == 'PLAY':
            return self._handle_play(session_id)

        return b'RTSP/1.0 400 Bad Request\r\n\r\n'

    def _handle_options(self) -> bytes:
        """Handle OPTIONS request"""
        return b'RTSP/1.0 200 OK\r\nPublic: OPTIONS, DESCRIBE, SETUP, PLAY\r\n\r\n'

    def _handle_describe(self, request_line: str) -> bytes:
        """Handle DESCRIBE request"""
        # Basic SDP response
        sdp = (
            "v=0\r\n"
            "o=- 0 0 IN IP4 127.0.0.1\r\n"
            "s=Stream\r\n"
            "c=IN IP4 127.0.0.1\r\n"
            "t=0 0\r\n"
            "m=video 0 RTP/AVP 96\r\n"
            "a=rtpmap:96 H264/90000\r\n"
        ).encode()

        response = (
            b"RTSP/1.0 200 OK\r\n"
            b"Content-Type: application/sdp\r\n"
            b"Content-Length: " + str(len(sdp)).encode() + b"\r\n"
            b"\r\n" + sdp
        )
        return response

    def _handle_setup(self, request: List[str], session_id: str) -> bytes:
        """Handle SETUP request"""
        return (
            b"RTSP/1.0 200 OK\r\n"
            b"Transport: RTP/AVP;unicast;client_port=8000-8001\r\n"
            b"Session: " + session_id.encode() + b"\r\n"
            b"\r\n"
        )

    def _handle_play(self, session_id: str) -> bytes:
        """Handle PLAY request"""
        return (
            b"RTSP/1.0 200 OK\r\n"
            b"Range: npt=0.000-\r\n"
            b"Session: " + session_id.encode() + b"\r\n"
            b"\r\n"
        )
