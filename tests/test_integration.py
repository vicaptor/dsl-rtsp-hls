import asyncio
import logging
from pathlib import Path
from src.dsl import VideoStreamDSL
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_integration():
    """Test full integration of all components"""
    logger.info("Starting integration test")
    
    try:
        # Create streaming pipeline using DSL
        stream = (VideoStreamDSL()
                .source()  # Will use INPUT_RTSP from environment
                .rtsp()    # Will use default port
                .hls()     # Will use default settings
                .adaptive_bitrate()  # Will use default bitrates
                .output()) # Will use default output path
        
        logger.info("Created streaming pipeline")
        
        # Open web player
        player_url = f"http://localhost:8080/player"
        logger.info(f"Opening web player at {player_url}")
        webbrowser.open(player_url)
        
        # Run the streaming pipeline
        logger.info("Starting streaming pipeline")
        await stream.run()
        
    except Exception as e:
        logger.error(f"Error in integration test: {e}", exc_info=True)
    finally:
        logger.info("Integration test completed")

if __name__ == "__main__":
    try:
        asyncio.run(test_integration())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
