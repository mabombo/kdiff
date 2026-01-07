# kdiff v1.4.0 - Custom Resources & Multiple Namespaces

## New Features

### Custom Resources (CR) Comparison
- **Auto-discovery mode**: Automatically detects all Custom Resources available in both clusters
- **Filtered discovery**: Specify API groups to compare (e.g., `--include-cr istio.io,cert-manager.io`)
- **Universal CR support**: Works with any CR type - Elasticsearch, Istio, Cert-Manager, Strimzi, etc.
- **Smart filtering**: Excludes native Kubernetes resources from discovery
- **Dual-cluster merge**: Discovers CRs from both clusters and compares union of resources

#### Usage Examples
```bash
# Auto-discover and compare all CRs
kdiff -c1 prod -c2 staging -n myapp --include-cr

# Compare specific CR groups only
kdiff -c1 prod -c2 staging -n myapp --include-cr istio.io,cert-manager.io

# Compare native resources + CRs
kdiff -c1 prod -c2 staging -n myapp -r deployment,service --include-cr
```

### Multiple Namespace Support
- **Comma-separated namespaces**: Compare resources across multiple namespaces in one run
- **Automatic merging**: Fetches and combines resources from all specified namespaces
- **Backward compatible**: Single namespace usage still works as before
- **Flexible syntax**: Handles spaces gracefully (e.g., `connect, default, kube-system`)

#### Usage Examples
```bash
# Single namespace (classic mode)
kdiff -c1 prod -c2 staging -n myapp

# Multiple namespaces
kdiff -c1 prod -c2 staging -n connect,default,kube-system

# Multiple namespaces with CRs
kdiff -c1 prod -c2 staging -n myapp,monitoring --include-cr
```

### Comprehensive Test Suite
- **14 new test cases**: CR discovery, namespace parsing, error handling
- **Mock testing**: Tests run without real cluster dependencies
- **Coverage improvements**: Auto-discovery, group filtering, multi-cluster merging
- **Namespace tests**: Validates parsing of single, multiple, and space-separated values

## Fixes

### Browser Auto-Open in Tests
- **KDIFF_NO_BROWSER support**: Environment variable now respected in bin/kdiff
- **No sandbox errors**: Tests run cleanly without browser security issues
- **Consistent behavior**: Both entry points (bin/kdiff, kdiff_cli.py) handle flag uniformly

### Test Suite Cleanup
- **Removed pytest check**: Eliminated confusing "pytest not found" message
- **Cleaner output**: Streamlined test execution messages
- **Unified framework**: All tests consistently use unittest

## Technical Improvements

### CR Discovery Architecture
- **kubectl integration**: Uses `kubectl api-resources` for discovery
- **API group filtering**: Intelligent matching on resource group suffixes
- **Error handling**: Graceful fallback when cluster unreachable
- **Resource validation**: Excludes native K8s resources from CR results

### Multiple Namespace Implementation
- **Per-namespace fetching**: Executes kubectl for each namespace independently
- **Result merging**: Combines items[] arrays from all namespace responses
- **Unified processing**: Merged resources processed identically to single-namespace mode
- **No duplicate fetching**: Efficient resource retrieval across namespaces

## Upgrade Notes

- No breaking changes to existing CLI interface
- New `--include-cr` flag is optional and backward compatible
- Multiple namespace feature works with existing `-n` parameter
- All previous features remain fully functional
- Requires kubectl access to target clusters for CR discovery

---

# kdiff v1.3.0 - Enhanced Diff Visualization & Professional Output

## New Features

### Inline Character-Level Highlighting
- **Precise diff visualization**: Modified lines now highlight only the specific characters that changed
- **Yellow highlighting**: Changed characters marked with bright yellow background for easy identification
- **Dual-pane highlighting**: Left pane shows removed characters, right pane shows added characters
- **jsdiff integration**: Uses industry-standard diffChars() algorithm for accurate comparison
- **Secure rendering**: HTML escaping prevents XSS vulnerabilities

### Interactive Filter System
- **Clickable filter boxes**: Click on Added, Removed, Modified, or Unchanged to filter visible lines
- **Visual indicators**: Active filters show checkmark (\u2713) for clear state tracking
- **OR logic**: Multiple filters combine to show all matching line types
- **Reset button**: One-click to clear all filters and restore full view
- **Default off**: All filters disabled initially, showing complete diff

### Smart Filter Management
- **Auto-detection**: System analyzes each file to detect available line types
- **Auto-disable**: Filters for non-existent line types are automatically disabled
- **Visual feedback**: Disabled filters shown with reduced opacity and disabled cursor
- **Empty line control**: Placeholder lines only shown when needed (Added/Removed filters active)

### Professional Console Output
- **No emojis**: All console output uses clean text markers
- **Clear status**: [OK], [ERROR], [WARNING] for unambiguous messaging
- **Professional suggestions**: Simple "Suggestion:" prompts without decoration
- **Enterprise-ready**: Suitable for corporate and CI/CD environments

## Documentation & Standards

### Updated Documentation
- **Professional README**: Concise, clear, emoji-free documentation
- **Clean markdown**: All docs updated to professional style
- **Python 3.10+**: Minimum version requirement updated throughout
- **Repository cleanup**: Internal docs excluded from tracking

### Repository Organization
- **Renamed images folder**: loghi/ renamed to images/ for clarity
- **Logo consolidation**: Kept only active logo file
- **Updated references**: All paths updated across codebase
- **Cleaner .gitignore**: Organized exclusions for better maintenance

## Technical Improvements

### Filter System Architecture
- **State management**: JavaScript object tracks filter state
- **Event handling**: Clean onclick handlers with proper propagation
- **CSS transitions**: Smooth hover effects and visual feedback
- **DOM manipulation**: Efficient show/hide logic for filtered lines

### Code Quality
- **Python 3.10+**: Modern Python features and type hints
- **Security**: HTML escaping in all user-facing content
- **Performance**: Optimized filter application and line rendering
- **Maintainability**: Clear code structure and documentation

## Upgrade Notes

- Minimum Python version is now 3.10 (previously 3.8)
- No breaking changes to CLI interface
- All existing features remain functional
- HTML reports fully backward compatible

---

# kdiff v1.2.0 - Enhanced Search & UI Improvements

## New Features

### Real-time Resource Search
- **Live filtering**: Search resources by name with instant results while typing
- **Visual feedback**: Matching text highlighted in bright yellow
- **Auto-expand**: Groups automatically expand when matches are found
- **Smart reset**: Clear button restores initial collapsed state
- **Info icon**: Added tooltip explaining search filters by name only

### UI/UX Enhancements
- **Info icons**: Added info icons with tooltips for better user guidance
  - Next to "changes" badge: explains count represents JSON fields modified
  - Next to search box: clarifies search works on resource names only
- **Improved search box visibility**: Enhanced borders, shadows, and sizing
- **Compact action buttons**: Redesigned +/− buttons with consistent sizing
- **Removed Legend section**: Cleaner interface by removing redundant legend cards

### Button Improvements
- **Unified toggle buttons**: Changed from "⇅ Toggle" to "+/−" symbols
- **Consistent sizing**: All collapse/expand buttons now proportionally sized
- **Group controls**: Small "+/−" buttons for individual resource groups
- **Global control**: "+/− All" button for expanding/collapsing everything

## Design Updates
- Enhanced search input with gray border (#9ca3af) and subtle shadow
- Info icons with hover effect (black → blue transition with scale)
- Yellow highlight (#ffeb3b) for search matches
- Improved button hierarchy and visual consistency

## Bug Fixes
- Fixed search state restoration when clearing filters
- Improved keyboard interaction with search field
- Better tooltip positioning and visibility

---

# kdiff v1.1.1 - Docker Experience Improvements

## Docker Enhancements

### Smart Browser Detection
- **Automatic Docker environment detection**: Prevents browser open failures in containers
- **Graceful fallback**: Shows helpful manual open instructions instead of errors
- Improved user experience when running kdiff in Docker

### OS-Specific Open Commands
- **Platform-aware suggestions**: Shows the right command for your operating system
  - macOS: `open <file>`
  - Linux: `xdg-open <file>`
  - Windows: `start <file>`
- **Relative paths**: Uses relative paths for easy copy-paste from any directory
- **User-friendly messages**: Clear instructions when browser auto-open is not available

## Technical Improvements
- Added `is_running_in_docker()` detection function
- Checks for `/.dockerenv` file and Docker cgroup
- Prevents unnecessary error messages in containerized environments

---

# kdiff v1.1.0 - Enhanced User Experience & Reporting

## New Features

### Improved CLI Help System
- **Comprehensive parameter documentation** with detailed descriptions
- **Practical usage examples** covering common scenarios
- **Clear parameter explanations** for all command-line options
- Better understanding of `-c1`, `-c2`, `-r`, `-n`, `-o`, `-f` parameters

### Auto-Open HTML Report
- **Automatic browser launch** after comparison completion
- **Multi-platform support** (macOS, Linux, Windows)
- **Fallback message** with file path if auto-open fails
- Seamless workflow from command line to visual report

### Enhanced HTML Report
- **Improved collapse/expand behavior**: Groups collapsed by default, resources expanded
- **Per-group toggle buttons**: Expand/collapse all resources within a specific type
- **Unified "Toggle All" button**: Single button replacing Expand All/Collapse All
- **Color legends** in View Diff and Side-by-Side modals explaining change types
- **Simplified legends**: Removed redundant cluster references
- **Tooltip on changes count**: Explains it shows JSON fields modified, not diff lines
- **Sorted missing resources**: Alphabetically ordered by resource type (A-Z)
- Removed "(Grouped by Type)" text for cleaner interface

### Redesigned Console Report
- **Professional layout** with clear sections and separators
- **Summary overview** with intuitive metrics display
- **Top resource types** showing detailed breakdown
- **Detailed table** with actual cluster names (not C1/C2)
- **Preview of modifications** with addition/deletion counts
- **Fixed metric inversion**: Correctly displays resources in each cluster
- **Better color coding** for different change types
- **Cleaner formatting** without Unicode alignment issues

### Side-by-Side Diff Viewer
- **VS Code-style two-pane layout** for comparing resources
- **Integrated jsdiff library** for robust line-by-line comparison
- **Color-coded differences**:
  - 🔴 Red: Lines only in first cluster (removed)
  - 🟢 Green: Lines only in second cluster (added)
  - 🔵 Blue: Modified lines (correct color in legend)
- **Synchronized scrolling** between panes
- **Zoom controls** (+, ⟲, -) for adjusting font size
- **Smart block merging**: Automatically combines removed+added pairs into modified entries
- Dark theme matching VS Code interface
- Line numbers on both sides for easy reference

### Enhanced UI/UX
- **Improved "Resources Only in One Cluster" card**
  - Professional SVG eye icon
  - Enhanced hover effects with lift and colored shadow
  - "Click to view details" hint that changes color on hover
  - Makes it immediately clear the card is interactive and clickable

## 🔧 Improvements
- UI consistency: All toggle buttons use same style (⇅ icon)
- Better visual feedback for interactive elements
- More intuitive report organization
- Fixed alignment issues in console output
- Corrected cluster name display throughout reports

## 📦 Installation

```bash
pip install kdiff==1.1.0
```

Or with Docker:
```bash
docker pull mabombo/kdiff:1.1.0
```

See [CHANGELOG.md](./CHANGELOG.md) for complete details.
