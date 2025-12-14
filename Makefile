.PHONY: help install lint test format

help:
@echo "Common commands:"
@echo "  make install   Install dependencies in editable mode"
@echo "  make lint      Run pre-commit hooks on all files"
@echo "  make test      Run unit test suite"
@echo "  make format    Format code with black and isort"

install:
python -m pip install --upgrade pip
python -m pip install -e .
pre-commit install

lint:
pre-commit run --all-files

format:
black src tests tools
isort src tests tools

test:
pytest
