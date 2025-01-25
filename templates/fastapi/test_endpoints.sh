#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Generate unique timestamp for email addresses
TIMESTAMP=$(date +%s)

# Function to make HTTP requests
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo "Endpoint: ${method} ${endpoint}"
    if [ -n "$data" ]; then
        echo "Request data: ${data}"
    fi
    echo "Response:"
    
    if [ "$method" = "POST" ]; then
        echo -e "${YELLOW}Sending POST request...${NC}"
        response=$(curl -v -s -X POST "http://localhost:3030${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${data}" \
            -m 10 \
            -w "\nStatus: %{http_code}")
    else
        echo -e "${YELLOW}Sending GET request...${NC}"
        response=$(curl -v -s "http://localhost:3030${endpoint}" \
            -m 10 \
            -w "\nStatus: %{http_code}")
    fi
    
    # Check if curl timed out
    if [ $? -eq 28 ]; then
        echo -e "${RED}Request timed out after 10 seconds${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Raw response:${NC}"
    echo "$response"
    
    # Check if the status code is in the response
    if [[ $response == *"Status: 2"* ]]; then
        echo -e "${GREEN}✓ Test passed${NC}"
        return 0
    elif [[ $response == *"Status: 409"* && "$description" == *"(should fail)"* ]]; then
        echo -e "${GREEN}✓ Test passed (expected failure)${NC}"
        return 0
    else
        echo -e "${RED}✗ Test failed${NC}"
        echo -e "${RED}Response did not contain expected status code${NC}"
        return 1
    fi
}

# Check if server is running
echo -e "${YELLOW}Checking if server is running...${NC}"
if ! curl -s -m 5 http://localhost:3030/health > /dev/null; then
    echo -e "${RED}Error: Could not connect to server"
    echo "Please make sure the server is running on http://localhost:3030${NC}"
    exit 1
fi
echo -e "${GREEN}Server is running!${NC}"

# Test health endpoint
make_request "GET" "/health" "" "Health Check"

# Test waitlist endpoint with minimal data
make_request "POST" "/waitlist" \
    "{\"email\":\"test1_${TIMESTAMP}@example.com\",\"name\":\"Test User 1\"}" \
    "Add to Waitlist (minimal)"

# Test waitlist endpoint with full data
make_request "POST" "/waitlist" \
    "{\"email\":\"test2_${TIMESTAMP}@example.com\",\"name\":\"Test User 2\",\"comment\":\"Testing waitlist\",\"referral_source\":\"API Test\"}" \
    "Add to Waitlist (full)"

# Test duplicate email (should fail with 409)
echo -e "\n${YELLOW}Testing: Add Duplicate Email (should fail)${NC}"
echo "Endpoint: POST /waitlist"
response=$(curl -v -s -X POST "http://localhost:3030/waitlist" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test1_${TIMESTAMP}@example.com\",\"name\":\"Test User 3\"}" \
    -m 10 \
    -w "\nStatus: %{http_code}")
echo -e "${YELLOW}Raw response:${NC}"
echo "$response"
if [[ $response == *"Status: 409"* ]]; then
    echo -e "${GREEN}✓ Duplicate check passed${NC}"
else
    echo -e "${RED}✗ Duplicate check failed${NC}"
fi

# Test get all entries
make_request "GET" "/waitlist" "" "Get All Entries"
