#!/bin/bash

# install_fedora.sh

# Kolory dla lepszej czytelności
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting installation for Fedora...${NC}"

# Sprawdź czy script jest uruchomiony z sudo
if [ "$EUID" -ne 0 ]
  then echo -e "${RED}Please run as root (use sudo)${NC}"
  exit
fi

echo -e "${GREEN}Installing system dependencies...${NC}"
dnf -y install \
    ffmpeg \
    ffmpeg-devel \
    python3-devel \
    python3-pip \
    gcc \
    pkg-config \
    redhat-rpm-config \
    nginx \
    kernel-devel \
    make \
    bzip2-devel \
    openssl-devel \
    libffi-devel \
    zlib-devel \
    wget \
    git

# Instalacja dodatkowych repozytoriów dla FFmpeg
echo -e "${GREEN}Adding RPM Fusion repositories...${NC}"
dnf -y install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
dnf -y install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

# Instalacja dodatkowych pakietów FFmpeg
echo -e "${GREEN}Installing FFmpeg development packages...${NC}"
dnf -y install \
    ffmpeg-libs \
    libavcodec-devel \
    libavdevice-devel \
    libavfilter-devel \
    libavformat-devel \
    libavutil-devel \
    libswscale-devel \
    libswresample-devel

# Tworzenie katalogu projektu
echo -e "${GREEN}Creating project directory...${NC}"
PROJECT_DIR="/opt/video_processor"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Tworzenie virtual environment
echo -e "${GREEN}Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}Upgrading pip...${NC}"
pip install --upgrade pip

# Tworzenie pliku requirements.txt
echo -e "${GREEN}Creating requirements.txt...${NC}"
cat > requirements.txt << EOL
av
python-nginx
m3u8
aiohttp
asyncio
typing
dataclasses
EOL

# Instalacja pakietów Pythona
echo -e "${GREEN}Installing Python packages...${NC}"
pip install -r requirements.txt

# Tworzenie pliku weryfikacyjnego
echo -e "${GREEN}Creating verification script...${NC}"
cat > verify.py << EOL
import sys
import subprocess
import pkg_resources

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        print("✅ FFmpeg installed")
        return True
    except:
        print("❌ FFmpeg not found")
        return False

def check_requirements():
    required = {
        'av': 'PyAV',
        'nginx': 'python-nginx',
        'm3u8': 'm3u8',
        'aiohttp': 'aiohttp',
    }

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = []

    for package, display_name in required.items():
        if package not in installed:
            missing.append(display_name)
        else:
            print(f"✅ {display_name} installed")

    if missing:
        print("\n❌ Missing packages:")
        for package in missing:
            print(f"  - {package}")
        return False
    return True

if __name__ == "__main__":
    print("Checking system requirements...")
    ffmpeg_ok = check_ffmpeg()

    print("\nChecking Python packages...")
    packages_ok = check_requirements()

    if not (ffmpeg_ok and packages_ok):
        print("\n❌ Some requirements are missing. Please install them first.")
        sys.exit(1)
    else:
        print("\n✅ All requirements met!")
EOL

# Konfiguracja NGINX
echo -e "${GREEN}Configuring NGINX...${NC}"
cat > /etc/nginx/nginx.conf << EOL
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    server {
        listen       80;
        server_name  localhost;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }

        location /hls {
            types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }
            root /tmp;
            add_header Cache-Control no-cache;
            add_header Access-Control-Allow-Origin *;
        }
    }
}
EOL

# Tworzenie katalogów dla streamingu
echo -e "${GREEN}Creating streaming directories...${NC}"
mkdir -p /tmp/hls
chmod 777 /tmp/hls

# Uruchamianie usług
echo -e "${GREEN}Starting services...${NC}"
systemctl enable nginx
systemctl start nginx
systemctl status nginx

# Konfiguracja firewall
echo -e "${GREEN}Configuring firewall...${NC}"
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-port=1935/tcp
firewall-cmd --reload

# Weryfikacja instalacji
echo -e "${GREEN}Verifying installation...${NC}"
python verify.py

# Tworzenie pliku z informacjami o środowisku
echo -e "${GREEN}Creating environment info file...${NC}"
cat > environment_info.txt << EOL
Video Processing Environment Info
===============================

FFmpeg version: $(ffmpeg -version | head -n1)
Python version: $(python --version)
NGINX version: $(nginx -v 2>&1)
System: Fedora $(cat /etc/fedora-release)

Installation Directory: $PROJECT_DIR
Virtual Environment: $PROJECT_DIR/venv
HLS Directory: /tmp/hls

Usage:
1. Activate virtual environment: source $PROJECT_DIR/venv/bin/activate
2. Run verification: python verify.py
3. NGINX config location: /etc/nginx/nginx.conf
4. HLS stream directory: /tmp/hls
EOL

echo -e "${GREEN}Installation completed!${NC}"
echo -e "${YELLOW}Please check environment_info.txt for system details and usage instructions.${NC}"