#!/bin/bash
#
# rebuild-all-versions.sh - Rebuild all versions with multi-platform support
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

error() { echo -e "${RED}❌ Error: $1${NC}" >&2; exit 1; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# Configuration
DOCKER_USERNAME="mabombo"
IMAGE_NAME="kdiff"
PLATFORMS="linux/amd64,linux/arm64"
VERSIONS=("1.1.0" "1.1.1" "1.2.0" "1.3.0")

# Check Docker and buildx
if ! docker info >/dev/null 2>&1; then
    error "Docker is not running"
fi

if ! docker buildx version >/dev/null 2>&1; then
    error "Docker buildx not available"
fi

# Ensure builder exists
if ! docker buildx inspect kdiff-builder >/dev/null 2>&1; then
    info "Creating buildx builder instance..."
    docker buildx create --name kdiff-builder --use || error "Failed to create buildx builder"
else
    docker buildx use kdiff-builder
fi

# Check login
if ! docker info 2>/dev/null | grep -q "Username"; then
    warn "Not logged in to Docker Hub"
    docker login || error "Docker login failed"
fi

echo ""
info "Rebuilding all versions with multi-platform support"
info "Platforms: $PLATFORMS"
info "Versions: ${VERSIONS[*]}"
echo ""

# Save current Dockerfile and publish-docker.sh
TEMP_DIR=$(mktemp -d)
cp Dockerfile "$TEMP_DIR/Dockerfile.new"
cp publish-docker.sh "$TEMP_DIR/publish-docker.sh.new"

info "Saved multi-platform configurations to temp directory"
echo ""

# Process each version
for VERSION in "${VERSIONS[@]}"; do
    info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    info "Processing version $VERSION"
    info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Checkout version
    git checkout "v$VERSION" 2>/dev/null || error "Failed to checkout v$VERSION"
    
    # Apply multi-platform patches
    info "Applying multi-platform patches..."
    
    # Patch Dockerfile - add TARGETARCH and update kubectl download
    if grep -q "linux/amd64/kubectl" Dockerfile; then
        info "Patching Dockerfile for multi-arch support..."
        sed -i.bak 's|RUN apk add|ARG TARGETARCH\nRUN apk add|' Dockerfile
        sed -i.bak 's|linux/amd64/kubectl|linux/${TARGETARCH}/kubectl|' Dockerfile
        rm -f Dockerfile.bak
    fi
    
    # Update label version if exists
    if grep -q 'LABEL version=' Dockerfile; then
        sed -i.bak "s|LABEL version=.*|LABEL version=\"$VERSION\"|" Dockerfile
        rm -f Dockerfile.bak
    fi
    
    # Build and push with buildx
    info "Building and pushing multi-platform image..."
    docker buildx build \
        --platform $PLATFORMS \
        -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION \
        --push \
        . || error "Multi-platform build failed for $VERSION"
    
    success "Version $VERSION published successfully"
    echo ""
done

# Return to main
git checkout main

# Restore modified files
git checkout Dockerfile publish-docker.sh 2>/dev/null || true

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "All versions rebuilt with multi-platform support!"
echo ""
info "Verifying images on Docker Hub..."
echo ""

for VERSION in "${VERSIONS[@]}"; do
    info "Version $VERSION:"
    docker buildx imagetools inspect $DOCKER_USERNAME/$IMAGE_NAME:$VERSION | grep "Platform:" | head -2
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Done!"
