from setuptools import setup, find_packages

setup(
    name="rtsp-hls",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'av>=9.0.0',
        'aiohttp>=3.8.0',
        'aiohttp-jinja2>=1.5.0',
        'jinja2>=3.0.0',
        'm3u8>=3.0.0',
        'python-dotenv==1.0.1',
        'python-nginx==1.5.7'
    ]
)
