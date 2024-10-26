#!/bin/bash
sudo lsof -i :9000 | grep LISTEN | awk '{print $2}' | xargs -r kill -9
sudo lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs -r kill -9
source venv/bin/activate
pip install -e .
python main.py
