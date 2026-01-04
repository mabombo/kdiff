#!/bin/bash
#
# version-bump.sh - Simple version bumping utility
#
# Usage:
#   ./version-bump.sh [major|minor|patch|VERSION]
#
# Examples:
#   ./version-bump.sh patch      # 1.0.0 -> 1.0.1
#   ./version-bump.sh minor      # 1.0.0 -> 1.1.0
#   ./version-bump.sh major      # 1.0.0 -> 2.0.0
#   ./version-bump.sh 1.5.2      # Set to 1.5.2
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get current version
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/v//' || echo "1.0.0")

echo -e "${BLUE}Current version: v$CURRENT_VERSION${NC}"

# Parse input
TYPE=$1

if [ -z "$TYPE" ]; then
    echo "Usage: $0 [major|minor|patch|VERSION]"
    exit 1
fi

# Calculate new version
if [[ $TYPE =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    NEW_VERSION=$TYPE
else
    IFS='.' read -r -a parts <<< "$CURRENT_VERSION"
    major=${parts[0]}
    minor=${parts[1]}
    patch=${parts[2]}
    
    case $TYPE in
        major)
            NEW_VERSION="$((major + 1)).0.0"
            ;;
        minor)
            NEW_VERSION="$major.$((minor + 1)).0"
            ;;
        patch)
            NEW_VERSION="$major.$minor.$((patch + 1))"
            ;;
        *)
            echo "Invalid type: $TYPE"
            echo "Use: major, minor, patch, or a version number (e.g., 1.2.3)"
            exit 1
            ;;
    esac
fi

echo -e "${BLUE}New version: v$NEW_VERSION${NC}"
echo ""

# Update files
echo "Updating files..."

# pyproject.toml
if [ -f pyproject.toml ]; then
    sed -i.bak "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
    rm pyproject.toml.bak 2>/dev/null || true
    echo "  ✓ pyproject.toml"
fi

# setup.py
if [ -f setup.py ]; then
    sed -i.bak "s/version=\"[^\"]*\"/version=\"$NEW_VERSION\"/" setup.py
    rm setup.py.bak 2>/dev/null || true
    echo "  ✓ setup.py"
fi

# Dockerfile
if [ -f Dockerfile ]; then
    sed -i.bak "s/LABEL version=\"[^\"]*\"/LABEL version=\"$NEW_VERSION\"/" Dockerfile
    rm Dockerfile.bak 2>/dev/null || true
    echo "  ✓ Dockerfile"
fi

echo ""
echo -e "${GREEN}✅ Version bumped to $NEW_VERSION${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review changes: git diff"
echo "  2. Update CHANGELOG.md with changes"
echo "  3. Commit: git add -A && git commit -m 'chore: Bump version to $NEW_VERSION'"
echo "  4. Or run: ./release.sh $NEW_VERSION"
