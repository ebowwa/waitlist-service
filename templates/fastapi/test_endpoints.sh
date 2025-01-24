#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to make HTTP requests
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "\nTesting: ${description}"
    echo "Endpoint: ${method} ${endpoint}"
    if [ -n "$data" ]; then
        echo "Request data: ${data}"
    fi
    echo "Response:"
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "http://localhost:3030${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${data}" \
            -w "\nStatus: %{http_code}")
    else
        response=$(curl -s "http://localhost:3030${endpoint}" \
            -w "\nStatus: %{http_code}")
    fi
    
    echo "$response"
    
    # Check if the status code is in the response
    if [[ $response == *"Status: 2"* ]]; then
        echo -e "${GREEN}✓ Test passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Test failed${NC}"
        return 1
    fi
}

# Check if server is running
echo "Checking if server is running..."
if ! curl -s http://localhost:3030/health > /dev/null; then
    echo -e "${RED}Error: Could not connect to server"
    echo "Please make sure the server is running on http://localhost:3030${NC}"
    exit 1
fi
echo -e "${GREEN}Server is running!${NC}"

# Test health endpoint
make_request "GET" "/health" "" "Health Check"

# Test waitlist endpoint with minimal data
make_request "POST" "/waitlist" \
    '{"email":"test1@example.com"}' \
    "Add to Waitlist (minimal)"

# Test waitlist endpoint with full data
make_request "POST" "/waitlist" \
    '{"email":"test2@example.com","name":"Test User","comment":"Testing waitlist","referral_source":"API Test"}' \
    "Add to Waitlist (full)"

# Test duplicate email (should fail with 409)
echo -e "\nTesting: Add Duplicate Email (should fail)"
echo "Endpoint: POST /waitlist"
response=$(curl -s -X POST "http://localhost:3030/waitlist" \
    -H "Content-Type: application/json" \
    -d '{"email":"test1@example.com"}' \
    -w "\nStatus: %{http_code}")
echo "$response"
if [[ $response == *"Status: 409"* ]]; then
    echo -e "${GREEN}✓ Duplicate check passed${NC}"
else
    echo -e "${RED}✗ Duplicate check failed${NC}"
fi

# Test get all entries
make_request "GET" "/waitlist" "" "Get All Entries"
