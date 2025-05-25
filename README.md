# HLS Video Streaming Service

## License

```
#
# Copyright 2025 Tom Sapletta <info@softreck.dev>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```

## Author
- Tom Sapletta <info@softreck.dev>


A Python-based service that converts RTSP video streams to HLS format with support for adaptive bitrate streaming.

## Features

- RTSP to HLS conversion
- Adaptive bitrate streaming
- Video transcoding with configurable parameters
- Audio stream handling
- Docker support
- Real-time statistics monitoring
- Web-based player interface
- Comprehensive logging
- Unit and integration tests

## Project Structure

```
hls/
├── src/                    # Source code
│   ├── config/            # Configuration related modules
│   │   ├── __init__.py
│   │   └── stream_config.py
│   ├── converter/         # Stream conversion modules
│   │   ├── __init__.py
│   │   ├── stream_converter.py
│   │   └── stream_processor.py
│   ├── dsl/              # Domain Specific Language
│   │   ├── __init__.py
│   │   └── video_stream_dsl.py
│   ├── server/           # Server implementations
│   │   ├── __init__.py
│   │   ├── hls_server.py
│   │   └── rtsp_server.py
│   └── templates/        # HTML templates
│       └── player.html
├── tests/                # Test suite
│   ├── test_hls_server.py
│   ├── test_stream_converter.py
│   └── test_integration.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── setup.py
└── main.py
```

## Prerequisites

- Python 3.12+
- FFmpeg
- Docker and Docker Compose (optional)

## Installation

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hls
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install in development mode:
```bash
pip install -e .
```

4. Create a `.env` file with your configuration:
```env
# RTSP Stream Configuration
INPUT_RTSP=rtsp://your-camera-url
RTSP_TRANSPORT=tcp
RTSP_TIMEOUT=5000000

# HLS Output Configuration
OUTPUT_HLS=/app/hls_output
HLS_SEGMENT_DURATION=4
HLS_PLAYLIST_SIZE=5

# Video Configuration
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_FPS=30
VIDEO_CODEC=h264
VIDEO_PRESET=ultrafast
VIDEO_BITRATES=2000000,1000000,500000
VIDEO_KEYFRAME_INTERVAL=60

# Audio Configuration
AUDIO_CODEC=aac
AUDIO_SAMPLE_RATE=44100
AUDIO_BITRATES=128000,64000
AUDIO_CHANNELS=2

# Server Configuration
RTSP_SERVER_PORT=8554
HLS_SERVER_PORT=8080
ENABLE_STATS=true
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Usage

### Running the Service

1. Start the service:
```bash
# Local development
python main.py

# or with Docker
docker-compose up
```

2. Access the web player:
```
http://localhost:8080/player
```

### Running Tests

The project includes three types of tests:

1. HLS Server Tests:
```bash
python tests/test_hls_server.py
```

2. Stream Converter Tests:
```bash
python tests/test_stream_converter.py
```

3. Integration Tests:
```bash
python tests/test_integration.py
```

## Development

### Logging

The service uses Python's logging module with different levels:
- DEBUG: Detailed information for debugging
- INFO: General operational information
- WARNING: Warning messages for potential issues
- ERROR: Error messages with stack traces

Example log output:
```
2024-01-20 10:00:00,000 - INFO - HLS Server started on port 8080
2024-01-20 10:00:01,000 - INFO - Starting conversion from rtsp://example.com/stream
2024-01-20 10:00:02,000 - DEBUG - Created new segment: segment_1.ts
```

### Adding New Features

1. Create new modules in the appropriate directory:
   - `src/config/` for configuration-related code
   - `src/converter/` for stream processing code
   - `src/server/` for server implementations
   - `src/dsl/` for DSL extensions

2. Add corresponding test files in `tests/`

3. Update documentation as needed

## Monitoring

The service provides real-time statistics through:

1. Web Interface:
   - Access statistics at http://localhost:8080/player
   - View processed frames, FPS, and errors

2. Logs:
   - Monitor detailed operation in the console
   - Track performance metrics and errors

## Troubleshooting

Common issues and solutions:

1. Module Not Found Errors:
   - Ensure you've installed the package in development mode
   - Check that all __init__.py files exist
   - Verify PYTHONPATH includes the project root

2. RTSP Connection Issues:
   - Verify the RTSP URL is accessible
   - Check network connectivity
   - Ensure proper authentication credentials

3. HLS Playback Issues:
   - Check segment generation in output directory
   - Verify HLS server is running
   - Check browser console for errors

4. Performance Issues:
   - Monitor system resources
   - Adjust buffer sizes
   - Check network bandwidth

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new features
4. Update documentation
5. Submit a pull request


