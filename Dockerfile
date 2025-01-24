# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=3030 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the package in development mode
RUN pip install -e .

# Expose port
EXPOSE $PORT

# Run the application with the correct module path
CMD ["sh", "-c", "python -m uvicorn src.waitlist_service.main:app --host 0.0.0.0 --port $PORT"]
