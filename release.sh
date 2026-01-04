#!/bin/bash
#
# release.sh - Automated release script for kdiff
#
# Usage:
#   ./release.sh [VERSION] [TYPE]
#
# VERSION: Version number (e.g., 1.1.0, 1.0.1) - optional, will prompt if not provided
# TYPE: Release type - major, minor, patch (optional, will prompt if not provided)
#
# Examples:
#   ./release.sh 1.1.0        # Create release v1.1.0
#   ./release.sh 1.1.0 minor  # Create release v1.1.0 as minor release
#   ./release.sh              # Interactive mode
#

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DOCKER_USERNAME=${DOCKER_USERNAME:-"mabombo"}
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/v//' || echo "1.0.0")

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

header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Calculate next version based on type
calculate_version() {
    local current=$1
    local type=$2
    
    IFS='.' read -r -a parts <<< "$current"
    local major=${parts[0]}
    local minor=${parts[1]}
    local patch=${parts[2]}
    
    case $type in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "$major.$((minor + 1)).0"
            ;;
        patch)
            echo "$major.$minor.$((patch + 1))"
            ;;
        *)
            echo "$current"
            ;;
    esac
}

# Pre-flight checks
preflight_checks() {
    info "Running pre-flight checks..."
    
    # Check if on main branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$current_branch" != "main" ]; then
        warn "You are not on 'main' branch (current: $current_branch)"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Aborted. Switch to main branch first: git checkout main"
        fi
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        error "Uncommitted changes detected. Commit or stash them first."
    fi
    
    # Check for unpushed commits
    if [ -n "$(git log origin/$current_branch..$current_branch 2>/dev/null)" ]; then
        warn "You have unpushed commits"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Aborted. Push your commits first: git push"
        fi
    fi
    
    # Check CHANGELOG
    if ! grep -q "\[Unreleased\]" CHANGELOG.md; then
        warn "CHANGELOG.md doesn't have [Unreleased] section"
    fi
    
    success "Pre-flight checks passed"
}

# Update CHANGELOG
update_changelog() {
    local version=$1
    local date=$(date +%Y-%m-%d)
    
    info "Updating CHANGELOG.md..."
    
    # Replace [Unreleased] with version and date
    sed -i.bak "s/## \[Unreleased\]/## [Unreleased]\n\n### Added\n- Nothing yet\n\n### Changed\n- Nothing yet\n\n### Fixed\n- Nothing yet\n\n## [$version] - $date/" CHANGELOG.md
    rm CHANGELOG.md.bak 2>/dev/null || true
    
    success "CHANGELOG.md updated"
}

# Update version in files
update_version_files() {
    local version=$1
    
    info "Updating version in project files..."
    
    # Update pyproject.toml
    if [ -f pyproject.toml ]; then
        sed -i.bak "s/^version = .*/version = \"$version\"/" pyproject.toml
        rm pyproject.toml.bak 2>/dev/null || true
        success "Updated pyproject.toml"
    fi
    
    # Update setup.py
    if [ -f setup.py ]; then
        sed -i.bak "s/version=\"[^\"]*\"/version=\"$version\"/" setup.py
        rm setup.py.bak 2>/dev/null || true
        success "Updated setup.py"
    fi
    
    # Update Dockerfile
    if [ -f Dockerfile ]; then
        sed -i.bak "s/LABEL version=\"[^\"]*\"/LABEL version=\"$version\"/" Dockerfile
        rm Dockerfile.bak 2>/dev/null || true
        success "Updated Dockerfile"
    fi
}

# Create release notes
create_release_notes() {
    local version=$1
    local notes_file="release-notes-v$version.md"
    
    info "Extracting release notes..."
    
    # Extract section for this version from CHANGELOG
    awk "/## \[$version\]/,/## \[/" CHANGELOG.md | grep -v "^## \[" | sed '/^$/d' > "$notes_file"
    
    if [ -s "$notes_file" ]; then
        success "Release notes created: $notes_file"
        return 0
    else
        warn "No release notes found in CHANGELOG"
        echo "Release v$version" > "$notes_file"
        return 1
    fi
}

# Main release process
main() {
    header "🚀 kdiff Release Process"
    
    # Get version
    local version=$1
    local type=$2
    
    if [ -z "$version" ]; then
        info "Current version: v$CURRENT_VERSION"
        echo ""
        echo "Release type:"
        echo "  1) major - Breaking changes (e.g., $CURRENT_VERSION -> $(calculate_version $CURRENT_VERSION major))"
        echo "  2) minor - New features (e.g., $CURRENT_VERSION -> $(calculate_version $CURRENT_VERSION minor))"
        echo "  3) patch - Bug fixes (e.g., $CURRENT_VERSION -> $(calculate_version $CURRENT_VERSION patch))"
        echo "  4) custom - Specify version manually"
        echo ""
        read -p "Select release type (1-4): " choice
        
        case $choice in
            1) type="major" ;;
            2) type="minor" ;;
            3) type="patch" ;;
            4) type="custom" ;;
            *) error "Invalid choice" ;;
        esac
        
        if [ "$type" = "custom" ]; then
            read -p "Enter version number (e.g., 1.2.0): " version
        else
            version=$(calculate_version $CURRENT_VERSION $type)
        fi
    fi
    
    # Validate version format
    if ! [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        error "Invalid version format. Use semantic versioning (e.g., 1.2.3)"
    fi
    
    info "Preparing release v$version"
    echo ""
    
    # Confirm
    read -p "Create release v$version? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
    
    # Run checks
    preflight_checks
    
    # Update files
    header "📝 Updating Files"
    update_changelog "$version"
    update_version_files "$version"
    
    # Commit changes
    info "Committing version bump..."
    git add CHANGELOG.md pyproject.toml setup.py Dockerfile 2>/dev/null || true
    git commit -m "chore: Bump version to $version" || warn "No changes to commit"
    success "Changes committed"
    
    # Create tag
    header "🏷️  Creating Git Tag"
    create_release_notes "$version"
    
    info "Creating tag v$version..."
    git tag -a "v$version" -F "release-notes-v$version.md"
    success "Tag v$version created"
    
    # Push to remote
    header "📤 Pushing to Remote"
    info "Pushing commits and tags..."
    git push origin main
    git push origin "v$version"
    success "Pushed to remote"
    
    # Build and push Docker image
    header "🐳 Building and Publishing Docker Image"
    if [ -f "./publish-docker.sh" ]; then
        info "Running Docker publish script..."
        ./publish-docker.sh "$version" "$DOCKER_USERNAME"
        success "Docker image published"
    else
        warn "publish-docker.sh not found, skipping Docker publish"
    fi
    
    # Summary
    header "🎉 Release v$version Complete!"
    echo ""
    info "📋 Summary:"
    echo "  • Version: v$version"
    echo "  • Git tag: v$version"
    echo "  • Docker image: $DOCKER_USERNAME/kdiff:$version"
    echo "  • Docker image: $DOCKER_USERNAME/kdiff:latest"
    echo ""
    info "🔗 Next steps:"
    echo "  • Create GitHub release: https://github.com/mabombo/kdiff/releases/new?tag=v$version"
    echo "  • Update Docker Hub description if needed"
    echo "  • Announce the release"
    echo ""
    
    # Cleanup
    rm -f "release-notes-v$version.md"
    
    success "Done! 🎊"
}

# Run main
main "$@"
