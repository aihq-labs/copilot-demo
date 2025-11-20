# Microsoft Copilot Agent SDK - Python 3.12
# Copyright 2025 AIHQ.ie
# Licensed under the Apache License, Version 2.0
#
# Note: Python 3.13+ not yet supported by microsoft-agents-* packages

FROM python:3.12-slim

# Metadata labels
LABEL maintainer="AIHQ.ie <info@aihq.ie>"
LABEL org.opencontainers.image.title="Copilot Studio Agent SDK"
LABEL org.opencontainers.image.description="Python SDK for Microsoft Copilot Studio agents"
LABEL org.opencontainers.image.vendor="AIHQ.ie"
LABEL org.opencontainers.image.licenses="Apache-2.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose API port (default: 8000)
EXPOSE 8000

# Health check for API server (using curl if available, otherwise skip)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Default command: Run API server
# Override with: docker run ... python cli.py [args]
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Usage Examples:
#
# 1. Run API server (default):
#    docker build -t copilot-agent-sdk .
#    docker run -p 8000:8000 --env-file .env copilot-agent-sdk
#
# 2. Run CLI interactively:
#    docker run -it --rm --env-file .env copilot-agent-sdk python cli.py
#
# 3. Send a message via CLI:
#    docker run --rm --env-file .env copilot-agent-sdk python cli.py --message "Hello"
#
# 4. View configuration:
#    docker run --rm --env-file .env copilot-agent-sdk python cli.py --config
#
# Note: Make sure your .env file is in the current directory or specify the path
