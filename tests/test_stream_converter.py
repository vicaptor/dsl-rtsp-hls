import os
import asyncio
import logging
from pathlib import Path
from src.converter import StreamConverter
from src.config import StreamConfig

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

INPUT_RTSP=os.getenv('INPUT_RTSP', '')

async def test_stream_converter():
    """Test stream converter functionality"""
    logger.info("Starting stream converter test")
    
    # Create test config
    config = StreamConfig(
        input_url=INPUT_RTSP,
        output_path="test_output"
    )
    
    try:
        # Create output directory
        Path(config.output_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {config.output_path}")
        
        # Create converter
        converter = StreamConverter(config)
        logger.info("Created stream converter instance")
        
        # Start conversion
        logger.info("Starting stream conversion")
        await asyncio.gather(
            converter.start_conversion(),
            converter._log_stats()
        )
        
    except Exception as e:
        logger.error(f"Error in stream converter test: {e}", exc_info=True)
    finally:
        logger.info("Stream converter test completed")

if __name__ == "__main__":
    try:
        asyncio.run(test_stream_converter())
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
