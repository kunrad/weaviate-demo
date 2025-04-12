# Use a more complete base image that includes build tools
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY health.py .
COPY health_check.py .

# Environment variables
ENV HEALTH_ENDPOINT=http://localhost:8000/health
ENV CHECK_INTERVAL=60
ENV RESPONSE_THRESHOLD=3.0
ENV RETRY_COUNT=3
ENV RETRY_DELAY=2.0

CMD ["python", "health.py"]