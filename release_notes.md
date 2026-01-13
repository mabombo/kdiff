# Release Notes

All notable release notes for kdiff will be documented in this file.

## [1.7.3] - 2026-01-13

### Added
- **Enhanced Namespace Context in HTML Reports**: Comprehensive namespace information display
  * Two-cluster comparison: namespace list in header for better context
  * Namespace comparison: cluster name prominently displayed in header
  * Multiple namespace badges for resources spanning different namespaces
  * Color-coded namespace badges for visual distinction
  * Cluster/namespace information in tooltips and side-by-side modal headers
  * Unified header layout for both comparison modes (cluster vs namespace)

### Fixed
- **F-String Syntax Error**: Corrected nested f-string in metadata header generation
  * Fixed Python syntax error that prevented proper HTML report generation
  * Separated metadata header construction from main template
  * Improved code maintainability and readability

### Changed
- **HTML Report Header Structure**: Streamlined metadata display
  * Consistent layout between cluster and namespace comparison modes
  * Better visual hierarchy for cluster and namespace information
  * Enhanced context visibility for resource differences

## [1.7.2] - 2026-01-13

### Added
- **Text Search in Side-by-Side View**: Interactive search functionality in side-by-side diff modal
  * Search input field in modal toolbar
  * Real-time search with highlighting of matching text
  * Case-insensitive search across both panes
  * Match counter showing current match and total matches
  * Previous/Next navigation buttons to jump between search results
  * Automatic scroll to center matched text in viewport
  * Keyboard shortcuts support (Enter for next, Shift+Enter for previous)
  * Clear button to reset search and remove highlights

### Fixed
- **Search Input Selector**: Corrected querySelector to properly target search input element
  * Improved error handling for search-related DOM operations

### Changed
- **Search UX**: Enhanced user experience for text search
  * Search results persist during diff navigation
  * Smooth scrolling to matched text
  * Search state maintained across filter changes

## [1.7.1] - 2026-01-11

### Added
- **Side-by-Side Modal Auto-Navigation**: Modal now automatically navigates to first difference on open
  * Uses 100ms delay to ensure proper layout rendering before scroll

### Fixed
- **Diff Counter Minimum Value**: Counter now always shows minimum value of 1 instead of 0
- **First Diff Centering**: First difference now properly centered in viewport when modal opens

### Changed
- **Navigation Highlight Color**: Reverted to original yellow color after user feedback

## [1.7.0] - 2026-01-10

### Added
- **Parallel Execution**: Multi-threaded kubectl calls for dramatically improved performance
  * Parallel resource fetching using ThreadPoolExecutor (up to 10 concurrent threads by default)
  * Clusters queried simultaneously in two-cluster mode
  * Namespaces queried simultaneously in single-cluster mode
  * Thread-safe console output with Lock synchronization
  * New --max-workers N option to control parallelization (default: 10)
  * 5.7x performance improvement - execution time reduced from 18.3s to 3.2s (82.5% faster)

### Changed
- **Resource Fetching Architecture**: Refactored from sequential to parallel execution

### Fixed
- Performance bottleneck in resource fetching eliminated through parallelization

## [1.6.0] - 2026-01-10

### Added
- **Diff Navigation in Side-by-Side View**: Interactive navigation between differences
  * Previous/Next navigation buttons in side-by-side modal header
  * Editable diff counter showing "X / Y" for direct navigation
  * Smooth scrolling that centers target difference in viewport
  * Visual highlight animation for 1.5 seconds when navigating
  * Synchronized scrolling between left and right panes
  * Wraparound support with optimized scrolling

## [1.5.0] - 2025-12-15

### Added
- **Custom Resource Discovery**: Automatic detection of Custom Resources in clusters
  * Auto-discovery of all CRDs in target cluster
  * Support for filtering by API groups
  * Namespace-scoped custom resource discovery

### Fixed
- Improved kubectl error handling for missing resources

## [1.4.0] - 2025-10-15

### Added
- **Multiple Namespace Support**: Compare resources across multiple namespaces
  * Comma-separated namespace list support
  * Pairwise namespace comparisons
  * Namespace filtering in reports

### Changed
- Enhanced report organization for multiple namespaces

## [1.3.0] - 2025-09-10

### Added
- **ConfigMap Line-by-Line Diff**: Detailed ConfigMap comparison
- **Metadata Filtering**: --show-metadata flag to include/exclude metadata
- **Performance Improvements**: Faster diff computation

## [1.2.0] - 2025-08-05

### Added
- **HTML Reports**: Interactive visual reports with color-coded changes
- **JSON Export**: Machine-readable output format
- **Diff Highlighting**: Color-coded changes in reports

## [1.1.0] - 2025-07-01

### Added
- **Two-Cluster Comparison**: Compare resources across different clusters
- **Resource Type Filtering**: Select specific resource types to compare

## [1.0.0] - 2025-06-01

### Added
- Initial release of kdiff
- Basic Kubernetes resource comparison
- Namespace-to-namespace comparison within same cluster
- Command-line interface
- JSON diff output

---

**Last Updated**: January 13, 2026
