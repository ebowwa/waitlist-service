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

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
python -m pip install --upgrade pip

# Install or upgrade dependencies
echo -e "${YELLOW}Installing/upgrading dependencies...${NC}"
python -m pip install -r requirements.txt

# Install waitlist_service in development mode
echo -e "${YELLOW}Installing waitlist_service in development mode...${NC}"
python -m pip install -e "$REPO_ROOT"

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
            echo "Unknown option: $1"
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
echo -e "${GREEN}Current directory: $(pwd)${NC}"
echo -e "${GREEN}Repository root: ${REPO_ROOT}${NC}"
echo -e "${GREEN}Python path: $PYTHONPATH${NC}"
echo -e "${GREEN}Looking for main.py in: $SCRIPT_DIR${NC}"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Run the server with log level debug
echo -e "${GREEN}Starting FastAPI server on port $PORT with $WORKERS worker(s)${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port $PORT $RELOAD_FLAG --workers $WORKERS --log-level debug
