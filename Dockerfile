# AidMind Docker Image
# Production-ready container for humanitarian needs assessment

FROM python:3.11-slim

# Set metadata
LABEL maintainer="support@aidmind.org"
LABEL description="AidMind - Unsupervised ML for humanitarian needs assessment"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY aidmind.py .
COPY setup.py .
COPY README.md .
COPY LICENSE .

# Install aidmind package
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/data /app/output /app/cache

# Set proper permissions
RUN chmod +x /app/aidmind.py

# Volume mounts for data, output, and cache
VOLUME ["/app/data", "/app/output", "/app/cache"]

# Default command shows help
CMD ["python", "-m", "aidmind", "--help"]

# Health check (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import aidmind; print('OK')" || exit 1

# Usage examples:
# 
# Build:
#   docker build -t aidmind:1.0.0 .
#
# Run with local data:
#   docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output \
#     aidmind:1.0.0 python -m aidmind /app/data/dataset.csv "Afghanistan"
#
# Interactive shell:
#   docker run -it -v $(pwd):/app/data aidmind:1.0.0 /bin/bash
#
# With cache persistence:
#   docker run -v $(pwd)/data:/app/data \
#     -v $(pwd)/output:/app/output \
#     -v $(pwd)/cache:/app/cache \
#     aidmind:1.0.0 python -m aidmind /app/data/dataset.csv "Kenya"
