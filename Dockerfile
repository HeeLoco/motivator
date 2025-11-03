FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for database (will be mounted as volume)
RUN mkdir -p /data

# Set environment variables for container mode
ENV CONTAINER_ENV=true \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
