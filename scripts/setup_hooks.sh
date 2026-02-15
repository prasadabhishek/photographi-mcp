#!/bin/bash

# Photographi: Git Hook Setup Utility
# Links scripts in ops/ to .git/hooks/

HOOK_DIR=".git/hooks"
PRE_PUSH_SRC="ops/pre-push.sh"
PRE_PUSH_DEST="$HOOK_DIR/pre-push"

if [ ! -d ".git" ]; then
    echo "❌ Error: This script must be run from the root of the photographi repository."
    exit 1
fi

echo "🏗️  Setting up git hooks..."

# Ensure source is executable
chmod +x "$PRE_PUSH_SRC"

# Link pre-push hook
if [ -L "$PRE_PUSH_DEST" ] || [ -f "$PRE_PUSH_DEST" ]; then
    echo "⚠️  Existing pre-push hook found. Backing up to $PRE_PUSH_DEST.bak"
    mv "$PRE_PUSH_DEST" "$PRE_PUSH_DEST".bak
fi

ln -sf "../../$PRE_PUSH_SRC" "$PRE_PUSH_DEST"
chmod +x "$PRE_PUSH_DEST"

echo "✅ Git hooks linked successfully."
echo "   - $PRE_PUSH_DEST -> $PRE_PUSH_SRC"
