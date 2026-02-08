#!/bin/bash

# photographi-mcp: Release Guard
# Ensures version consistency and test stability before push.

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🛡️ Running Release Guard for photographi-mcp...${NC}"

# 1. Extract Versions
PYPROJECT_VERSION=$(grep -m 1 "version = " pyproject.toml | cut -d '"' -f 2)
SERVER_VERSION=$(grep "__version__ = " server.py | cut -d '"' -f 2)

echo -e "pyproject.toml: $PYPROJECT_VERSION"
echo -e "server.py:      $SERVER_VERSION"

# 2. Compare Versions
if [ "$PYPROJECT_VERSION" != "$SERVER_VERSION" ]; then
    echo -e "${RED}❌ Error: Version mismatch detected!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Versions are synchronized.${NC}"

# 3. Running Verification Suite
echo -e "\n${GREEN}🧪 Executing Full Test Suite...${NC}"
./verify.sh
VERIFY_STATUS=$?

if [ $VERIFY_STATUS -ne 0 ]; then
    echo -e "${RED}❌ Verification failed. Aborting release.${NC}"
    exit 1
fi

echo -e "\n${GREEN}🚀 RELEASE GUARD PASSED!${NC}"
echo -e "You are clear to: git push origin mainline && git tag v$PYPROJECT_VERSION && git push origin v$PYPROJECT_VERSION"
exit 0
