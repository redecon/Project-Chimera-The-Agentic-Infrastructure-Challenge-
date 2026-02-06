# Use official Python slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install only lightweight system dependencies (skip build-essential)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (modern Python package manager)
RUN pip install uv

# Pre-install problematic dependency to avoid network retries
RUN pip install eth-keyfile==0.8.1

RUN pip install pytest

# Sync dependencies from pyproject.toml + uv.lock
RUN uv sync --frozen

# Default command: run tests
CMD ["python", "-m", "pytest", "tests/"]
