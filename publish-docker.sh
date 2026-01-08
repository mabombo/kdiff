#!/bin/bash
#
# publish-docker.sh - Automated script to build and publish kdiff to Docker Hub (Multi-platform)
#
# Usage:
#   ./publish-docker.sh [VERSION] [DOCKER_USERNAME]
#
# Examples:
#   ./publish-docker.sh                      # Uses 1.4.0 and DOCKER_USERNAME env var
#   ./publish-docker.sh 1.4.0                # Build and push version 1.4.0
#   ./publish-docker.sh 1.4.0 myusername     # Specify both version and username
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-"1.4.0"}
DOCKER_USERNAME=${2:-${DOCKER_USERNAME:-""}}
IMAGE_NAME="kdiff"
PLATFORMS="linux/amd64,linux/arm64"

# Functions
error() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Validation
if [ -z "$DOCKER_USERNAME" ]; then
    error "Docker username not specified. Use: ./publish-docker.sh VERSION USERNAME or set DOCKER_USERNAME env var"
fi

if [ ! -f "Dockerfile" ]; then
    error "Dockerfile not found. Run this script from the kdiff project root directory"
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    error "Docker is not running. Please start Docker Desktop"
fi

# Check if buildx is available
if ! docker buildx version >/dev/null 2>&1; then
    error "Docker buildx not available. Please update Docker Desktop to a recent version"
fi

# Create and use buildx builder if needed
if ! docker buildx inspect kdiff-builder >/dev/null 2>&1; then
    info "Creating buildx builder instance..."
    docker buildx create --name kdiff-builder --use || error "Failed to create buildx builder"
    success "Buildx builder created"
else
    info "Using existing buildx builder..."
    docker buildx use kdiff-builder
fi

# Check if logged in to Docker Hub
if ! docker info 2>/dev/null | grep -q "Username"; then
    warn "Not logged in to Docker Hub"
    info "Running docker login..."
    docker login || error "Docker login failed"
fi

echo ""
info "Publishing kdiff to Docker Hub (Multi-platform)"
info "Version: $VERSION"
info "Username: $DOCKER_USERNAME"
info "Image: $DOCKER_USERNAME/$IMAGE_NAME"
info "Platforms: $PLATFORMS"
echo ""

# Step 1: Build and Push (combined with buildx)
info "Step 1/2: Building and pushing multi-platform images..."
info "This may take a few minutes as it builds for multiple architectures..."
docker buildx build \
    --platform $PLATFORMS \
    -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION \
    -t $DOCKER_USERNAME/$IMAGE_NAME:latest \
    --push \
    . || error "Multi-platform build and push failed"
success "Multi-platform images built and pushed"
echo ""

# Step 2: Verify
info "Step 2/2: Verifying multi-platform manifest..."
docker buildx imagetools inspect $DOCKER_USERNAME/$IMAGE_NAME:$VERSION || error "Image verification failed"
success "Images successfully pushed to Docker Hub"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Successfully published $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo ""
info "🐳 Docker Hub: https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
info "📦 Pull image: docker pull $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
info "🚀 Run: docker run --rm $DOCKER_USERNAME/$IMAGE_NAME:latest --help"
echo ""
info "Supported platforms:"
docker buildx imagetools inspect $DOCKER_USERNAME/$IMAGE_NAME:$VERSION | grep "Platform:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Optional: Open Docker Hub page
if command -v open >/dev/null 2>&1; then
    read -p "Open Docker Hub page in browser? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
    fi
fi

success "Done! 🎉"
