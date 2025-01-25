# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory and environment variables
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3030 \
    ENVIRONMENT=production \
    PYTHONPATH=/app/src

# Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application
COPY . .

# Use the new entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--workers", "1", "--no-reload"]