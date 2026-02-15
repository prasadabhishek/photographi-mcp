#!/bin/bash

# photographi-mcp: Automated Release Utility

if [ -z "$1" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.1.0"
    exit 1
fi

VERSION=$1
TAG="v$VERSION"

echo "🚀 Preparing release $VERSION..."

# 1. Update server.py version
sed -i '' "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" server.py

# 2. Update pyproject.toml version
sed -i '' "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml

echo "✅ Updated version strings in server.py and pyproject.toml"

# 3. Check if CHANGELOG.md has entry for this version
if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
    echo "⚠️ Warning: No entry for [$VERSION] found in CHANGELOG.md"
    echo "Please add release notes before tagging."
    exit 1
fi

# 4. Commit and Tag
git add server.py pyproject.toml CHANGELOG.md
git commit -m "chore: release $VERSION"
git tag -a "$TAG" -m "Release $VERSION"

echo "✅ Release $VERSION committed and tagged locally."
echo "➡️  Next steps:"
echo "   1. git push origin mainline"
echo "   2. git push origin $TAG"
echo "   3. GitHub Actions will handle the rest (GitHub Release + PyPI)!"
