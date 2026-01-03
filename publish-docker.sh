#!/bin/bash
#
# publish-docker.sh - Automated script to build and publish kdiff to Docker Hub
#
# Usage:
#   ./publish-docker.sh [VERSION] [DOCKER_USERNAME]
#
# Examples:
#   ./publish-docker.sh                      # Uses 1.0.0 and DOCKER_USERNAME env var
#   ./publish-docker.sh 1.1.0                # Build and push version 1.1.0
#   ./publish-docker.sh 1.2.0 myusername     # Specify both version and username
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-"1.0.0"}
DOCKER_USERNAME=${2:-${DOCKER_USERNAME:-""}}
IMAGE_NAME="kdiff"

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

# Check if logged in to Docker Hub
if ! docker info 2>/dev/null | grep -q "Username"; then
    warn "Not logged in to Docker Hub"
    info "Running docker login..."
    docker login || error "Docker login failed"
fi

echo ""
info "Publishing kdiff to Docker Hub"
info "Version: $VERSION"
info "Username: $DOCKER_USERNAME"
info "Image: $DOCKER_USERNAME/$IMAGE_NAME"
echo ""

# Step 1: Build
info "Step 1/4: Building Docker image..."
docker build \
    -t $IMAGE_NAME:$VERSION \
    -t $IMAGE_NAME:latest \
    . || error "Docker build failed"
success "Build completed"
echo ""

# Step 2: Tag
info "Step 2/4: Tagging images..."
docker tag $IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:$VERSION || error "Tagging version failed"
docker tag $IMAGE_NAME:latest $DOCKER_USERNAME/$IMAGE_NAME:latest || error "Tagging latest failed"
success "Images tagged"
echo ""

# Step 3: Test
info "Step 3/4: Testing image..."
docker run --rm $IMAGE_NAME:$VERSION --help > /dev/null || error "Image test failed"
success "Image test passed"
echo ""

# Step 4: Push
info "Step 4/4: Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION || error "Push version failed"
docker push $DOCKER_USERNAME/$IMAGE_NAME:latest || error "Push latest failed"
success "Images pushed to Docker Hub"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "Successfully published $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo ""
info "🐳 Docker Hub: https://hub.docker.com/r/$DOCKER_USERNAME/$IMAGE_NAME"
info "📦 Pull image: docker pull $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
info "🚀 Run: docker run --rm $DOCKER_USERNAME/$IMAGE_NAME:latest --help"
echo ""

# Display image info
info "Image information:"
docker images $DOCKER_USERNAME/$IMAGE_NAME --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
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
