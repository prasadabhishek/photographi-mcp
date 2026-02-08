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
VENV_PYTHON="$PHOTOGRAPH_ROOT/venv/bin/python"

# Check for venv
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found at $VENV_PYTHON${NC}"
    echo -e "Please run 'python -m venv venv && source venv/bin/activate && pip install -e .' first."
    exit 1
fi

echo -e "\n${GREEN}🔌 [1/2] Running MCP Server Unit Tests...${NC}"
# No PYTHONPATH override: tests the instance installed in the environment
$VENV_PYTHON -m unittest discover -v -s "$PHOTOGRAPH_ROOT/tests" -p 'test_*.py'
MCP_STATUS=$?

if [ $MCP_STATUS -ne 0 ]; then
    echo -e "${RED}❌ MCP Server Tests Failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}🔗 [2/2] Running Master Integration Suite...${NC}"
export PYTHONPATH="$PHOTOGRAPH_ROOT"
$VENV_PYTHON "$PHOTOGRAPH_ROOT/tests/integration/master_test_suite.py"
INT_STATUS=$?

if [ $INT_STATUS -ne 0 ]; then
    echo -e "${RED}❌ Integration Suite Failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ ALL TESTS PASSED SUCCESSFULLY!${NC}"
echo -e "System verified in isolation using environment-installed packages."
exit 0
