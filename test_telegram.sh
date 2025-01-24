#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists in templates/fastapi
if [ ! -d "templates/fastapi/venv" ]; then
    echo -e "${RED}Virtual environment not found. Please run run_server.sh first.${NC}"
    exit 1
fi

# Activate virtual environment
source templates/fastapi/venv/bin/activate

# Add src to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Run the test script
echo -e "${YELLOW}Testing Telegram notifications...${NC}"
python test_telegram.py
