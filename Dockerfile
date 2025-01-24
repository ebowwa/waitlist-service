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

# Install uvicorn globally first
RUN pip install --no-cache-dir uvicorn[standard] && \
    which uvicorn && \
    uvicorn --version

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Expose port
EXPOSE $PORT

# Run the application with direct uvicorn path
CMD ["uvicorn", "waitlist_service.main:app", "--host", "0.0.0.0", "--port", "3030"]
