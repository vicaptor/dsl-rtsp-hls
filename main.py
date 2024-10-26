import asyncio
import logging
import os
from dotenv import load_dotenv
from src.dsl import VideoStreamDSL
import webbrowser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create streaming pipeline using DSL
    stream = (VideoStreamDSL()
             .source()  # Will use INPUT_RTSP from environment
             .rtsp()    # Will use default port
             .hls()     # Will use default settings
             .adaptive_bitrate()  # Will use default bitrates
             .output()) # Will use default output path

    try:
        # Open web player in browser
        webbrowser.open(f"http://localhost:{os.getenv('HLS_SERVER_PORT', '8080')}/player")
        
        # Run the streaming pipeline
        await stream.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
    finally:
        logger.info("Conversion stopped")


if __name__ == "__main__":
    asyncio.run(main())
