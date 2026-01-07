# Changelog

All notable changes to kdiff will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-01-07

### Added
- **Custom Resources (CR) Comparison**
  * New `--include-cr` flag for comparing Kubernetes Custom Resources
  * Auto-discovery mode: automatically detects all CRs in both clusters
  * Filtered mode: specify API groups (e.g., `--include-cr istio.io,cert-manager.io`)
  * Seamless integration with existing resource fetching logic
  * Discovers CRs from both clusters and compares union of resources
  * Supports any CR type: Elasticsearch, Istio VirtualServices, Cert-Manager Certificates, etc.
- **Multiple Namespace Support**
  * Comma-separated namespace values in `-n` parameter
  * Example: `-n connect,default,kube-system`
  * Fetches and merges resources from all specified namespaces
  * Maintains backward compatibility with single namespace
- **Comprehensive Test Suite**
  * New test_cr_discovery.py with 14 test cases
  * Mock kubectl api-resources for testing without real clusters
  * Tests for auto-discovery, group filtering, error handling
  * Tests for namespace parsing (single, multiple, with spaces)
  * Verification of CR union from both clusters

### Fixed
- **Browser Auto-Open During Tests**
  * Added `KDIFF_NO_BROWSER` environment variable support in bin/kdiff
  * Prevents sandbox errors when running test suite
  * Browser opening properly disabled during test execution
  * Aligns bin/kdiff behavior with kdiff_cli.py

### Changed
- **Test Suite Improvements**
  * Removed obsolete pytest check from run_tests.sh
  * Cleaner test output without confusing messages
  * All tests use unittest framework consistently

## [1.3.0] - 2026-01-07

### Added
- **Inline Character-Level Highlighting** in side-by-side diff view
  * Uses jsdiff library's diffChars() for precise character-level comparison
  * Yellow highlighting for modified characters within changed lines
  * Separate highlighting for left (removed) and right (added) panes
  * HTML escaping for security
- **Interactive Filter System** for side-by-side view
  * Clickable filter boxes for Added, Removed, Modified, and Unchanged lines
  * Visual checkmarks (✓) indicate active filters
  * OR logic for multiple filter combinations
  * Reset Filters button to clear all selections
  * All filters disabled by default (show all lines)
- **Smart Empty Line Handling**
  * Empty placeholder lines only shown when Added or Removed filters are active
  * Hidden when viewing Modified or Unchanged lines alone
  * Maintains proper alignment in side-by-side view
- **Auto-Disable Unavailable Filters**
  * Automatically detects which line types exist in each file
  * Disables and grays out filters for non-existent line types
  * Visual indication with reduced opacity and disabled cursor
  * Prevents confusion with inapplicable filters

### Changed
- **Professional Console Output**
  * Removed all emoji from error, warning, and success messages
  * Replaced with text markers: [OK], [ERROR], [WARNING]
  * Cleaner "Suggestion:" prompts without decoration
  * Professional appearance suitable for enterprise environments
- **Documentation Overhaul**
  * Completely rewritten README.md: concise, professional, no emojis
  * Removed visual clutter from all markdown files
  * Updated to professional tone throughout
  * Excluded internal documentation from repository
- **Python Version Requirement**
  * Minimum Python version updated from 3.8 to 3.10
  * Updated in all configuration files and documentation
  * Removed Python 3.8 and 3.9 from classifiers
- **Repository Organization**
  * Renamed loghi/ folder to images/
  * Kept only the active logo file
  * Updated all references throughout codebase
  * Excluded internal docs from git tracking

### Improved
- **Side-by-Side Diff UX**
  * Filter state management with JavaScript object
  * Hover effects on filter boxes
  * Smooth transitions and visual feedback
  * Better organization of filter controls
- **HTML Report Quality**
  * Removed emojis from button labels and titles
  * Professional button text: "Side-by-Side", "View Diff"
  * Cleaner search input placeholder
  * Consistent styling across all UI elements

## [1.2.0] - 2026-01-07

### Added
- **Real-time Resource Search** in HTML reports
  * Live search filter to instantly find resources by name
  * Yellow highlighting (`#ffeb3b`) on matched text
  * Automatic expansion of groups containing matches
  * Smart state restoration when clearing search
  * Data preservation using `data-original-text` attribute
- **Info icons** with helpful tooltips
  * Next to "changes" badge explaining counter meaning
  * Next to search box clarifying "filters by name only"
  * Interactive hover effects (blue color, scale animation)

### Changed
- **Enhanced search box visibility**
  * Increased font size to 15px
  * Added 2.5px gray border
  * Added subtle shadow effects for prominence
- **Compact button design**
  * Reduced button size by 50% (0.75em font-size, 3px/6px padding)
  * Unified all toggle buttons to use +/− symbols
  * Changed "⇅ Toggle Resources" → "+/−"
  * Changed "⇅ Toggle All" → "+/− All"
  * Consistent styling across all action buttons

### Removed
- **Legend section** from HTML reports
  * Removed redundant cards (Changed, Added, Removed)
  * Kept legends only in detail view modals where they provide context

## [1.1.1] - 2026-01-06

### Added
- **Smart Docker environment detection** to prevent browser open failures
  * Automatic detection via `/.dockerenv` file and Docker cgroups
  * `is_running_in_docker()` function for reliable container detection
- **OS-specific manual open suggestions** when browser auto-open fails
  * macOS: `open <file>`
  * Linux: `xdg-open <file>`
  * Windows: `start <file>`
  * Uses relative paths for easy copy-paste

### Improved
- **Better Docker user experience**: No more error messages when running in containers
- **Clearer instructions**: Shows the exact command to run based on detected OS

### Fixed
- Browser auto-open errors in Docker containerized environments
- Missing `os` module import for Docker detection

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

[Unreleased]: https://github.com/mabombo/kdiff/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mabombo/kdiff/releases/tag/v1.0.0
