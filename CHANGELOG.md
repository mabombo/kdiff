# Changelog

All notable changes to kdiff will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-01-04

### Added
- **Side-by-side diff visualization** in HTML reports (VS Code style)
  * New "Side-by-Side" button for each resource with differences
  * Two-pane layout with perfect 50/50 split
  * Integrated **jsdiff library** for robust line-by-line comparison algorithm
  * Synchronized scrolling between left (QA) and right (PROD) panes
  * Color coding:
    - Red background: lines only in QA (removed)
    - Green background: lines only in PROD (added)  
    - Blue background: lines modified between clusters
  * Zoom controls (+, ⟲, -) for adjusting font size with icons matching View Diff
  * Proper handling of embedded newlines (\\n → actual line breaks)
  * Smart block merging: combines removed+added pairs into modified entries
  * Handles diff blocks of different sizes correctly
  * Dark theme matching VS Code interface
  * Line numbers on both sides for easy reference
  * Full JSON content comparison with proper alignment

### Improved
- **Enhanced clickability of "Resources Only in One Cluster" card**
  * Added professional SVG eye icon in top-right corner
  * Improved hover effects: enhanced lift, colored shadow, border expansion
  * Added "Click to view details" hint that changes color on hover
  * Icon scales and brightens on hover for better user feedback
  * Makes it immediately clear the card is interactive

### Changed
- UI consistency: Side-by-side modal buttons now match View Diff modal style

### Fixed
- Nothing yet

## [1.0.0] - 2026-01-03

### Added
- Initial release of kdiff
- Intelligent Kubernetes resource comparison between two clusters
- Smart normalization of volatile fields (uid, resourceVersion, timestamps)
- ConfigMap diff showing only modified lines
- Non-positional environment variable comparison
- Interactive HTML reports with collapsible sections and inline diffs
- JSON and Markdown output formats
- Support for multiple resource types (deployments, configmaps, secrets, etc.)
- Flexible include/exclude filters for resources
- Docker support with Alpine-based image (168MB)
- Installation script for local and system-wide installation
- Comprehensive documentation in English

### Changed
- Complete translation from Italian to English (documentation and code comments)

### Fixed
- Docker container library path resolution
- pyproject.toml email validation issue

### Security
- Docker image runs as non-root user (uid 1000)
- Kubeconfig mounted read-only in containers
- kubectl v1.35.0 included in Docker image

[Unreleased]: https://github.com/YOUR_USERNAME/kdiff/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_USERNAME/kdiff/releases/tag/v1.0.0
