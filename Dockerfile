# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3030

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Make the script executable
RUN chmod +x /app/templates/fastapi/run_server.sh

# Create a wrapper script to handle environment and execution
RUN echo '#!/bin/bash\n\
export PYTHONPATH=/app/src:$PYTHONPATH\n\
cd /app/templates/fastapi\n\
exec ./run_server.sh --port 3030 --no-reload --workers 1\n\
' > /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh

# Run the wrapper script
CMD ["/app/docker-entrypoint.sh"]

# docker compose down && docker compose up --build