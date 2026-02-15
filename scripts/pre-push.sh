#!/bin/bash

# Photographi: Git Pre-Push Hook
# Runs the verification suite before pushing to remote.

echo "🔍 Running pre-push verification..."

# Execute the verification script
./verify.sh

STATUS=$?

if [ $STATUS -ne 0 ]; then
    echo "❌ [ERROR] Pre-push verification failed. Push aborted."
    echo "Please fix the failing tests before pushing."
    exit $STATUS
fi

echo "✅ [SUCCESS] Pre-push verification passed. Proceeding with push..."
exit 0
