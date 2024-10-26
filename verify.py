import av
import nginx
import m3u8

# Check FFmpeg version
print(av.version())

# Check nginx configuration
with open('/etc/nginx/nginx.conf', 'r') as f:
    print(nginx.loads(f.read()))