import asyncio
import logging
from pathlib import Path
from src.server import HLSServer
from src.config import StreamConfig
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_hls_server():
    """Test HLS server functionality"""
    logger.info("Starting HLS server test")
    
    # Create test config
    config = StreamConfig(
        input_url=INPUT_RTSP,
        output_path="test_output"
    )
    
    try:
        # Create output directory
        Path(config.output_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {config.output_path}")
        
        # Create HLS server
        server = HLSServer(config)
        logger.info("Created HLS server instance")
        
        # Start server
        await server.start()
        logger.info("HLS server started successfully")
        
        # Test endpoints
        test_urls = [
            "http://localhost:8080/player",
            "http://localhost:8080/stream.m3u8",
            "http://localhost:8080/stats"
        ]
        
        logger.info("Testing server endpoints:")
        for url in test_urls:
            logger.info(f"Opening {url} in browser")
            webbrowser.open(url)
            await asyncio.sleep(2)
        
        # Keep server running
        logger.info("Server is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error in HLS server test: {e}", exc_info=True)
    finally:
        logger.info("HLS server test completed")

if __name__ == "__main__":
    try:
        asyncio.run(test_hls_server())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
