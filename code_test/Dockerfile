FROM python:3.9-slim
# Set working directory
WORKDIR /app

# Copy requirements and source code
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY health_check.py .

# Set environment variables (override these at runtime if needed)
ENV HEALTH_ENDPOINT="http://localhost:8000/health"
ENV CHECK_INTERVAL=300
ENV RESPONSE_THRESHOLD=3.0
ENV RETRY_COUNT=3
ENV RETRY_DELAY=2.0

# Run the health check script
CMD ["python", "health_check.py"]
