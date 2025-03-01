FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install Flask
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code
COPY health.py .

# Expose port 8000
EXPOSE 8000

CMD ["python", "health.py"]
