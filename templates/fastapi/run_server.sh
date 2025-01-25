#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
LOGS_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOGS_DIR"

# Set up logging
LOG_FILE="${LOGS_DIR}/server.log"
ERROR_LOG="${LOGS_DIR}/error.log"

# Function to log messages
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i ":${port}" > /dev/null 2>&1; then
        log "ERROR" "Port ${port} is already in use. Killing existing processes..."
        lsof -i ":${port}" | awk 'NR!=1 {print $2}' | xargs kill -9 2>/dev/null
        sleep 2
    fi
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    log "INFO" "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip > /dev/null 2>&1

# Install or upgrade dependencies
log "INFO" "Installing/upgrading dependencies..."
python -m pip install -r requirements.txt > /dev/null 2>&1

# Install waitlist_service in development mode
log "INFO" "Installing waitlist_service in development mode..."
python -m pip install -e "$REPO_ROOT" > /dev/null 2>&1

# Add the parent directory to PYTHONPATH so it can find the waitlist_service module
export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH}"

# Default values
PORT=3030
RELOAD=true
WORKERS=1

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -p|--port)
            PORT="$2"
            shift
            shift
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift
            shift
            ;;
        *)
            log "ERROR" "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set reload flag
RELOAD_FLAG=""
if [ "$RELOAD" = true ]; then
    RELOAD_FLAG="--reload"
fi

# Print debug information
log "INFO" "Current directory: $(pwd)"
log "INFO" "Repository root: ${REPO_ROOT}"
log "INFO" "Python path: $PYTHONPATH"
log "INFO" "Looking for main.py in: $SCRIPT_DIR"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    log "ERROR" "main.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create instance directory for SQLite if it doesn't exist
INSTANCE_DIR="${REPO_ROOT}/instance"
mkdir -p "$INSTANCE_DIR"
log "INFO" "Created instance directory at: ${INSTANCE_DIR}"

# Set default database URL if not set
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="sqlite+aiosqlite:///${INSTANCE_DIR}/waitlist.db"
    log "INFO" "Using default SQLite database at: ${DATABASE_URL}"
fi

# Check if port is already in use
check_port $PORT

# Run the server with log level debug
log "INFO" "Starting FastAPI server on port $PORT with $WORKERS worker(s)"
log "INFO" "Database URL: $DATABASE_URL"
log "INFO" "Logs available at: $LOG_FILE"
log "INFO" "Errors logged to: $ERROR_LOG"

# Start the server with proper logging
python -m uvicorn main:app --host 0.0.0.0 --port $PORT $RELOAD_FLAG --workers $WORKERS --log-level debug 2> >(tee -a "$ERROR_LOG") | tee -a "$LOG_FILE"
