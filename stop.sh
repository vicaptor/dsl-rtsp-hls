#!/bin/bash
PORT=9000
sudo lsof -i :$PORT | grep LISTEN | awk '{print $2}' | xargs -r kill -9
sudo lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs -r kill -9
