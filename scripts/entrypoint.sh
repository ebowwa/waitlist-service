#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        echo -e "${YELLOW}Please install $1 using:${NC}"
        case $1 in
            python3)
                echo "sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
                ;;
            *)
                echo "sudo apt update && sudo apt install -y $1"
                ;;
        esac
        exit 1
    fi
}

# Check for required commands
check_command python3
check_command pip3

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
cd "$APP_DIR" || {
    echo -e "${RED}Error: Could not navigate to $APP_DIR${NC}"
    exit 1
}

# Development environment setup
if [ "$ENVIRONMENT" = "development" ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}Setting up development environment...${NC}"
    python3 -m venv venv || {
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        exit 1
    }
    source venv/bin/activate || {
        echo -e "${RED}Error: Failed to activate virtual environment${NC}"
        exit 1
    }
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt || {
        echo -e "${RED}Error: Failed to install requirements${NC}"
        exit 1
    }
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate || {
        echo -e "${RED}Error: Failed to activate virtual environment${NC}"
        exit 1
    }
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
exec python3 -m uvicorn main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    $RELOAD_FLAG \
    --log-level debug
