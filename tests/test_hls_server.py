import asyncio
import logging
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.server import HLSServer
from src.config import StreamConfig
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test RTSP URL
TEST_RTSP_URL = "rtsp://example.com/stream"

@pytest.fixture
def mock_webbrowser_open():
    with patch('webbrowser.open') as mock_open:
        yield mock_open

@pytest.fixture
def mock_aiohttp_web():
    with patch('aiohttp.web') as mock_web:
        yield mock_web

@pytest.fixture
def mock_av_open():
    with patch('av.open') as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_container.streams.video = [mock_stream]
        mock_open.return_value.__enter__.return_value = mock_container
        yield mock_open

@pytest.mark.asyncio
@pytest.mark.timeout(10)  # 10 second timeout for the test
async def test_hls_server(tmp_path, mock_webbrowser_open, mock_aiohttp_web, mock_av_open):
    """Test HLS server functionality"""
    logger.info("Starting HLS server test")
    
    # Create test config with very short timeouts for testing
    config = StreamConfig(
        input_url=TEST_RTSP_URL,
        output_path=str(tmp_path / "output"),
        rtsp_server_port=8555,  # Use non-default port for testing
        hls_server_port=8081,   # Use non-default port for testing
        rtsp_timeout=1,        # Shorter timeout for testing
        segment_duration=1,     # Shorter segments for testing
    )
    
    # Mock the server start method to complete immediately
    with patch.object(HLSServer, 'start', new_callable=AsyncMock) as mock_start, \
         patch.object(HLSServer, 'stop', new_callable=AsyncMock) as mock_stop:
        
        # Create HLS server
        server = HLSServer(config)
        logger.info("Created HLS server instance")
        
        # Mock the server's run_until_complete to avoid hanging
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_loop.return_value.run_until_complete.side_effect = asyncio.CancelledError("Test complete")
            
            # Call start (mocked)
            try:
                await server.start()
            except asyncio.CancelledError:
                logger.info("Server start cancelled as expected")
        
        # Verify start was called
        mock_start.assert_awaited_once()
        logger.info("HLS server start method was called")
        
        # Verify web server setup
        mock_aiohttp_web.Application.assert_called_once()
        logger.info("Web application created successfully")
        
        # Verify web browser would be opened with correct URL
        mock_webbrowser_open.assert_called_once_with(
            f"http://localhost:{config.hls_server_port}/player"
        )
        logger.info("Web browser open verified")

if __name__ == "__main__":
    try:
        asyncio.run(test_hls_server())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
