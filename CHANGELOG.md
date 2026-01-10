# Changelog

All notable changes to kdiff will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.4] - 2026-01-10

### Added
- **Cluster connectivity testing**: Tests cluster connectivity before attempting to fetch resources
  * Executes `kubectl cluster-info` with 10s timeout for each cluster
  * Tests connectivity after context validation, before resource fetch
  * Provides specific error messages for common issues:
    - DNS resolution failures
    - Connection timeouts
    - Authentication errors (Unauthorized)
    - Permission errors (Forbidden)
  * Includes helpful suggestions (VPN check, network connectivity, firewall rules, credentials)
  * Exit code 2 for connectivity failures (distinguishable from comparison differences)
  * Saves significant time by failing fast on unreachable clusters

### Fixed
- **Docker user home directory**: Set kdiff user home directory to `/home/kdiff` (was `/`)
  * Fixes issues with tools expecting a valid home directory
  * Creates `/home/kdiff/.kube` directory with correct permissions
  * Improves compatibility when running as current user with `--user` flag

### Changed
- **docker-entrypoint.sh**: Simplified to not attempt automatic kubeconfig copy
  * Removed automatic permission handling (was unreliable on some Linux systems)
  * Now provides clear guidance on manual solutions
  * Updated DOCKER_README.md with three solutions ordered by preference:
    1. `chmod 644 ~/.kube/config` (simplest)
    2. `--user $(id -u):$(id -g)` (most reliable)
    3. Temporary copy method (for shared systems)

### Technical
- Added `test_cluster_connectivity()` function in kdiff_cli.py
- Added `get_available_contexts()` function to retrieve kubectl contexts
- Integrated connectivity check into main execution flow
- Comprehensive error parsing for various kubectl failure modes
- Enhanced error messages with actionable troubleshooting steps

## [1.5.3] - 2026-01-10

### Added
- **Automatic kubeconfig permission handling in Docker**: No more manual fixes required on Linux!
  * New `docker-entrypoint.sh` script automatically detects permission issues
  * Creates temporary copy of kubeconfig with correct permissions inside container
  * Transparent to the user - works automatically
  * Falls back to clear error messages if automatic fix fails
  * Eliminates the need for `chmod 777` or other manual permission changes

### Changed
- **Dockerfile**: Updated to use custom entrypoint for automatic permission handling
- **DOCKER_README.md**: Updated to reflect automatic permission handling (v1.5.2+)
  * Moved manual solutions to "For older versions" section
  * Highlighted automatic handling as default behavior

### Technical
- Added `docker-entrypoint.sh` wrapper script
- Entrypoint checks kubeconfig readability before execution
- Creates `/tmp/kubeconfig` copy if permission issues detected
- Sets KUBECONFIG environment variable to temporary location
- Maintains security by keeping temporary copy inside container only

## [1.5.2] - 2026-01-09

### Added
- **Context validation**: Validates that specified Kubernetes contexts exist before attempting to fetch resources
  * Checks contexts using `kubectl config get-contexts`
  * Displays clear error message if context doesn't exist
  * Lists all available contexts to help user choose correct one
  * Provides suggestion to run `kubectl config get-contexts`
  * Prevents wasted time attempting to connect to non-existent clusters
  * Exit code 2 for invalid contexts (distinguishable from comparison differences)

### Fixed
- **Docker permission issues on Linux**: Added comprehensive troubleshooting section in DOCKER_README.md
  * Solution 1: Adjust kubeconfig file permissions to 644
  * Solution 2: Use temporary copy with appropriate permissions
  * Solution 3: Run container as current user (--user flag)
  * Documented why permission issues occur on Linux
  * Clear step-by-step solutions for each approach

### Documentation
- Enhanced DOCKER_README.md with troubleshooting section
- Added examples for handling permission issues on Linux
- Added examples for context validation errors
- Improved error messages for better user experience

### Testing
- Added 6 new tests for context validation
- All tests pass: invalid contexts rejected, valid contexts accepted
- Error messages and suggestions verified

## [1.5.1] - 2026-01-08

### Changed
- **Unified namespace parameter**: Merged `-n` and `--namespaces` into single parameter
  * `-n NAMESPACE` now accepts both single namespace and comma-separated list
  * `--namespaces` remains as long-form alias
  * Simpler, more intuitive interface
  * Works seamlessly with both single-cluster and two-cluster modes
  * Reduces confusion about which parameter to use

### Documentation
- Updated all examples to use unified `-n` parameter
- Clarified parameter usage in help text
- Updated README with simplified syntax examples

## [1.5.0] - 2026-01-08

### Added
- **Single-Cluster Multi-Namespace Comparison Mode**
  * New `-c CONTEXT` option for comparing namespaces within the same cluster
  * Requires `--namespaces` with at least 2 namespaces
  * Pairwise comparison: automatically generates comparisons for all namespace pairs
  * Example: `-c prod --namespaces ns1,ns2,ns3` creates 3 comparisons (ns1 vs ns2, ns1 vs ns3, ns2 vs ns3)
  * Each comparison gets its own subdirectory with complete reports
- **Intelligent Resource Matching**
  * Single-cluster mode: resources matched by kind+name (namespace excluded from filename)
  * Two-cluster mode: resources matched by kind+namespace+name (maintains existing behavior)
  * Prevents same resources in different namespaces from being marked as "missing"
  * Correctly detects modified resources across namespaces
- **Context-Aware Report Generation**
  * Reports automatically detect namespace vs cluster comparison context
  * Dynamic UI labels: "Namespace 1/2" vs "Cluster 1/2"
  * Dynamic comparison type labels: "Only in One Namespace" vs "Only in One Cluster"
  * Accurate resource path resolution with separate directory names and display labels
- **Comprehensive Test Coverage**
  * 6 new test cases for single-cluster and two-cluster modes
  * Tests for filename logic, pairwise comparison, argument validation
  * Total test suite: 39 tests - all passing
  * Validates backward compatibility with two-cluster mode

### Changed
- **Output Directory Structure**
  * Single-cluster mode: organized by namespace pairs (e.g., `latest/ns1_vs_ns2/`)
  * Two-cluster mode: unchanged (maintains existing structure)
  * Cleaner separation between different comparison types
- **Documentation Updates**
  * README.md updated with single-cluster mode usage examples
  * Added comprehensive parameter documentation for both modes
  * Updated output structure documentation
  * Enhanced CLI help text with mode-specific examples

### Fixed
- **Resource Path Resolution**
  * Fixed "Unable to read resource details" error in namespace comparisons
  * Separated directory names from display labels in report generation
  * Correct file paths used for reading resource details

### Technical
- Extended `fetch_resources()` with `single_cluster_mode` parameter
- Modified `diff_details.py` to accept separate cluster names and labels
- Enhanced comparison logic to support namespace-aware matching
- Maintained full backward compatibility with existing two-cluster workflows

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
