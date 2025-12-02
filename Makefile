.PHONY: test install clean build help

help:
	@echo "Available commands:"
	@echo "  make install    - Install the package in development mode"
	@echo "  make test       - Run tests"
	@echo "  make build      - Build distribution packages"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make lint       - Run code linting (if flake8 installed)"

install:
	pip install -e .

test:
	python -m pytest tests/

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

lint:
	@which flake8 > /dev/null && flake8 whisper_cleaner/ || echo "flake8 not installed, skipping lint"
