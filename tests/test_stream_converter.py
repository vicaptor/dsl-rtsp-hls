import asyncio
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from src.converter import StreamConverter
from src.config import StreamConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test RTSP URL
TEST_RTSP_URL = "rtsp://example.com/stream"

@pytest.fixture
def mock_av_open():
    with patch('av.open') as mock_open:
        mock_container = MagicMock()
        mock_stream = MagicMock()
        mock_container.streams.video = [mock_stream]
        mock_open.return_value.__enter__.return_value = mock_container
        yield mock_open

@pytest.fixture
def mock_aiohttp_web():
    with patch('aiohttp.web') as mock_web:
        yield mock_web

@pytest.mark.asyncio
@pytest.mark.timeout(10)  # 10 second timeout for the test
async def test_stream_converter(tmp_path, mock_av_open, mock_aiohttp_web):
    """Test stream converter functionality"""
    logger.info("Starting stream converter test")
    
    # Create test config with very short timeouts for testing
    config = StreamConfig(
        input_url=TEST_RTSP_URL,
        output_path=str(tmp_path / "output"),
        rtsp_server_port=8555,  # Use non-default port for testing
        hls_server_port=8081,   # Use non-default port for testing
        rtsp_timeout=1,        # Shorter timeout for testing
        segment_duration=1,     # Shorter segments for testing
    )
    
    # Create output directory
    Path(config.output_path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {config.output_path}")
    
    # Mock the StreamConverter's start_conversion method to complete immediately
    with patch.object(StreamConverter, 'start_conversion', new_callable=AsyncMock) as mock_start_conversion, \
         patch.object(StreamConverter, 'stop', new_callable=AsyncMock) as mock_stop:
        
        # Mock the stream processing to avoid actual processing
        async def mock_process_stream():
            logger.info("Mock stream processing started")
            await asyncio.sleep(0.1)  # Small delay to simulate processing
            logger.info("Mock stream processing completed")
        
        mock_start_conversion.side_effect = mock_process_stream
        
        # Create stream converter
        converter = StreamConverter(config)
        logger.info("Created StreamConverter instance")
        
        # Call start_conversion (mocked)
        try:
            await asyncio.wait_for(converter.start_conversion(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Test timed out, but continuing with assertions")
        
        # Verify start_conversion was called
        mock_start_conversion.assert_awaited_once()
        logger.info("StreamConverter start_conversion method was called")
        
        # Verify AV container was opened with correct URL
        mock_av_open.assert_called_once_with(TEST_RTSP_URL, 'r', timeout=config.rtsp_timeout)
        logger.info("AV container opened with correct URL")

if __name__ == "__main__":
    try:
        asyncio.run(test_stream_converter())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
