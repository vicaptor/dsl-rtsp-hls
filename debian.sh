#!/bin/bash

# install.sh
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    ffmpeg \
    python3-dev \
    python3-pip \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
pip install av
pip install python-nginx
pip install m3u8
pip install aiohttp

echo "Verifying installation..."
python verify.py