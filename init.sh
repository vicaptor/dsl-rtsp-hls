# Install development tools and libraries
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel

# Install dependencies for OpenCV
sudo dnf install gtk3-devel
sudo dnf install qt5-qtbase-devel
sudo dnf install mesa-libGL-devel

# Install FFmpeg dependencies for av
sudo dnf install ffmpeg-devel

# Install dependencies for TensorFlow
sudo dnf install gcc gcc-c++