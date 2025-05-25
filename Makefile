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


# Project variables
PROJECT_NAME = $(shell basename $(CURDIR))
PYTHON = python3
PIP = pip3
VENV = venv
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Default target
all: help

## help: Show this help message
help:
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@fgrep -h "##" $$(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\$$//' | sed -e 's/##//' | awk 'BEGIN {FS = ":"}; {printf "  \033[36m%-20s\033[0m %s\n", $$$$1, $$$$2}'

## setup: Set up development environment
setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt

## install: Install dependencies
install:
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt

## test: Run tests
test:
	. $(VENV)/bin/activate && python -m pytest tests/

## lint: Run linters
lint:
	. $(VENV)/bin/activate && flake8 .

## format: Format code
format:
	. $(VENV)/bin/activate && black .
	. $(VENV)/bin/activate && isort .

## clean: Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ .mypy_cache/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete

## docker-build: Build Docker image
docker-build:
	$(DOCKER) build -t $(PROJECT_NAME) .

## docker-run: Run Docker container
docker-run:
	$(DOCKER) run -p 8000:8000 $(PROJECT_NAME)

## docker-compose-up: Start services with docker-compose
docker-compose-up:
	$(DOCKER_COMPOSE) up -d

## docker-compose-down: Stop and remove services
docker-compose-down:
	$(DOCKER_COMPOSE) down

.PHONY: all help setup install test lint format clean docker-build docker-run docker-compose-up docker-compose-down
