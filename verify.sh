#!/bin/bash

# photographi: Unified Verification Suite
# Runs MCP server tests and integration flows in isolation.
# Simulates a user environment by relying on installed packages.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Isolated Verification Pipeline...${NC}"

# Ensure we are in the photographi root
cd "$(dirname "$0")"
PHOTOGRAPH_ROOT=$(pwd)

# Determine the python path
if [ -f "$PHOTOGRAPH_ROOT/venv/bin/python" ]; then
    VENV_PYTHON="$PHOTOGRAPH_ROOT/venv/bin/python"
elif [ -f "$PHOTOGRAPH_ROOT/venv/Scripts/python.exe" ]; then
    # Windows support
    VENV_PYTHON="$PHOTOGRAPH_ROOT/venv/Scripts/python.exe"
else
    VENV_PYTHON="python3" # Fallback to system python
fi

echo -e "\n${GREEN}🧪 [1/1] Running Unified Test Suite...${NC}"
# Use pytest with verbose output
$VENV_PYTHON -m pytest tests/ -v
STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED SUCCESSFULLY!${NC}"
    echo -e "System verified using pytest."
    exit 0
else
    echo -e "\n${RED}❌ Verification Failed!${NC}"
    exit $STATUS
fi
