#!/bin/bash

# Exit on error
set -e

# Check for uncommitted changes (excluding the version file we are about to change is hard, so just warn)
if [[ -n $(git status --porcelain) ]]; then
    echo "WARNING: You have uncommitted changes."
    git status --short
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Function to extract version
get_current_version() {
    if [ -f "app/core/version.py" ]; then
        grep 'VERSION = ' app/core/version.py | cut -d '"' -f 2
    else
        echo "Unknown"
    fi
}

CURRENT_VERSION=$(get_current_version)
echo "------------------------------------------------"
echo "Current Version: $CURRENT_VERSION"
echo "------------------------------------------------"

read -p "Enter NEW version number (e.g., 0.0.2): " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    echo "Error: Version cannot be empty."
    exit 1
fi

# Regex check for version format (simple check)
if [[ ! $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Warning: Version '$NEW_VERSION' usually looks like 'x.y.z'"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

TAG_NAME="v$NEW_VERSION"

echo "Preparing to release: $TAG_NAME"
echo "1. Update app/core/version.py"
echo "2. Commit change"
echo "3. Create git tag: $TAG_NAME"
echo "4. Push to origin (branch + tag)"

read -p "Proceed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Update version file
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/VERSION = ".*"/VERSION = \"$NEW_VERSION\"/" app/core/version.py
else
    sed -i "s/VERSION = ".*"/VERSION = \"$NEW_VERSION\"/" app/core/version.py
fi

# Stage and Commit
git add app/core/version.py
git commit -m "Bump version to $TAG_NAME"

# Tag
git tag "$TAG_NAME"

# Push
CURRENT_BRANCH=$(git branch --show-current)
echo "Pushing changes to remote (branch: $CURRENT_BRANCH)..."
git push origin "$CURRENT_BRANCH"
git push origin "$TAG_NAME"

echo "------------------------------------------------"
echo "Success! Release $TAG_NAME has been pushed."
echo "GitHub Actions should now start building the release."
echo "------------------------------------------------"
