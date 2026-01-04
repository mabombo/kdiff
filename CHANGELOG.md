# Changelog

All notable changes to kdiff will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

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
