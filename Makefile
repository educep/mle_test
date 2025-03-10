# Makefile for managing the pharmaceutical data pipeline project

# Variables
VENV_NAME = mle_test
PYTHON_FILES = src tests

# install uv
install_uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment
venv:
	uv venv
	@echo "Virtual environment created."

# Activate the virtual environment
activate:
	@source venv/bin/activate
	@echo "Virtual environment activated."

# Install dependencies using uv
install:
	uv pip install --system -r requirements.txt
	@echo "Dependencies installed."


# Pre-commit hooks
pre_commit:
	pre-commit install
	@echo "Pre-commit hooks installed."

# Clean up
clean:
	rm -rf venv
	@echo "Cleaned up the environment."


# Tests
test:
	python -m unittest tests/test_integration.py
	python -m unittest tests/test_graph_comparison.py
	python -m unittest tests/test_sql.py
	@echo "Tests executed."

# Build the Docker image
build:
	docker build -t mle_test .
	@echo "Docker image built."

# Run the Docker container : docker run -it --rm mle_test ls -la venv
run:
	docker run -it --rm --entrypoint /bin/bash mle_test
	@echo "Docker container running with interactive shell."

# Linting and formatting
.PHONY: format
format:
	black $(PYTHON_FILES)
	isort $(PYTHON_FILES)
	@echo "Formatting completed."

.PHONY: check-format
check-format:
	black --check $(PYTHON_FILES)
	isort --check --diff $(PYTHON_FILES)
	@echo "Format check completed."

.PHONY: lint
lint: format
	flake8 $(PYTHON_FILES)
	mypy $(PYTHON_FILES)
	@echo "Linting completed."

# Help
help:
	@echo "Makefile for managing the pharmaceutical data pipeline project"
	@echo "Usage:"
	@echo "  make venv         - Create a virtual environment"
	@echo "  make activate     - Activate the virtual environment"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make pre_commit   - Install pre-commit hooks"
	@echo "  make lint         - Check code style with flake8, isort, black, and mypy"
	@echo "  make format       - Format code with isort and black"
	@echo "  make clean        - Clean up the environment"
	@echo "  make build        - Build the Docker image"
	@echo "  make run          - Run the Docker container"
	@echo "  make help         - Display this help message"
