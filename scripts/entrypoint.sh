#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Default values
PORT="${PORT:-3030}"
WORKERS="${WORKERS:-1}"
RELOAD="${RELOAD:-false}"
ENVIRONMENT="${ENVIRONMENT:-development}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
APP_DIR="$PROJECT_ROOT/templates/fastapi"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        --reload)
            RELOAD=true
            shift
            ;;
        --no-reload)
            RELOAD=false
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Set up Python path
if [ -z "$PYTHONPATH" ]; then
    export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH}"
fi

# Navigate to the FastAPI app directory
cd "$APP_DIR" || exit 1

# Development environment setup
if [ "$ENVIRONMENT" = "development" ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}Setting up development environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Set reload flag for uvicorn
RELOAD_FLAG=""
if [ "$RELOAD" = "true" ]; then
    RELOAD_FLAG="--reload"
fi

# Print configuration
echo -e "${GREEN}Starting server with:${NC}"
echo -e "  Port: $PORT"
echo -e "  Workers: $WORKERS"
echo -e "  Reload: $RELOAD"
echo -e "  Environment: $ENVIRONMENT"
echo -e "  Python path: $PYTHONPATH"
echo -e "  App directory: $APP_DIR"

# Start the server
exec python -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    $RELOAD_FLAG \
    --log-level debug
