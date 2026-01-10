# kdiff v1.5.5 - Version Flag and Docker HOME Fix

## Quick Fixes

### 📌 Version Flag
Added command-line options to check kdiff version:

```bash
# Check version
kdiff -v
kdiff --version

# Output: kdiff 1.5.5
```

Useful for:
- Troubleshooting issues
- Verifying installed version
- Checking Docker image version
- Documentation and support requests

### 🐳 Docker HOME Directory Fix

**Problem:** When using `--user $(id -u):$(id -g)` flag with Docker, the HOME environment variable was set to `/` instead of `/home/kdiff`, causing kubeconfig path resolution issues.

**Solution:** The entrypoint script now automatically detects and fixes HOME directory:

```bash
# Now works correctly with --user flag
docker run --rm -it \
  --user $(id -u):$(id -g) \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp
```

**What changed:**
- Entrypoint checks if `HOME=/` or is empty
- Automatically sets `HOME=/home/kdiff`
- Ensures `$HOME/.kube/config` resolves correctly
- Fixes compatibility with tools expecting valid home directory

**Before (v1.5.4):**
```bash
$ docker run --user $(id -u):$(id -g) ... --entrypoint /bin/bash mabombo/kdiff:latest
$ echo $HOME
/  # Wrong!
```

**After (v1.5.5):**
```bash
$ docker run --user $(id -u):$(id -g) ... --entrypoint /bin/bash mabombo/kdiff:latest
$ echo $HOME
/home/kdiff  # Correct!
```

## Technical Details

### Version Implementation
- Added `__version__` variable in kdiff_cli.py
- Added `-v, --version` argument to ArgumentParser
- Uses argparse `action='version'` for automatic handling
- Version synchronized across all files (pyproject.toml, setup.py, Dockerfile)

### HOME Directory Fix
The docker-entrypoint.sh now includes:
```bash
# Set HOME to /home/kdiff if it's not already set correctly
if [ "$HOME" = "/" ] || [ -z "$HOME" ]; then
    export HOME=/home/kdiff
fi
```

This ensures consistent behavior regardless of how the container is launched.

## Upgrade Notes

### Breaking Changes
None. All changes are backward compatible.

### Recommended Actions
1. **Pull new image:** `docker pull mabombo/kdiff:1.5.5`
2. **Test version flag:** `docker run --rm mabombo/kdiff:latest -v`
3. **No changes needed** to existing scripts or configurations

### For --user Flag Users
If you were experiencing issues with kubeconfig not being found when using `--user $(id -u):$(id -g)`, this release fixes that problem. Simply update to v1.5.5.

## Compatibility

- ✅ Works with all previous kubeconfig mount methods
- ✅ Compatible with `--user` flag on Linux/macOS
- ✅ No changes to command-line interface (except new -v flag)
- ✅ All previous features and fixes retained

---

# kdiff v1.5.4 - Cluster Connectivity Testing

## Major Features

### 🚀 Cluster Connectivity Testing
**Fail fast, save time!** kdiff now tests cluster connectivity before attempting to fetch resources, providing immediate feedback on connection issues.

#### What Changed
- **Pre-flight connectivity check**: Tests each cluster's reachability using `kubectl cluster-info`
- **Fast failure**: 10-second timeout per cluster, 15-second total limit
- **Intelligent error detection**: Specific messages for DNS, timeout, auth, and permission issues
- **Actionable guidance**: Helpful suggestions for VPN, network, firewall, and credential problems

#### How It Works
```bash
# If cluster is unreachable, you'll know immediately
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 unreachable-cluster -n myapp

# Output:
# [ERROR] CONNECTIVITY ERROR: Connection timeout to cluster 'unreachable-cluster' (exceeded 15 seconds)
# 
# Suggestions:
#   - Check that clusters are running and accessible
#   - Verify VPN connection if required
#   - Check network connectivity and firewall rules
#   - Verify kubeconfig credentials are valid
```

#### Error Detection
The connectivity check identifies and provides specific guidance for:
- **DNS failures**: "unable to resolve host" or "no such host"
- **Connection timeouts**: Exceeded timeout waiting for cluster response
- **Unauthorized**: Invalid or expired credentials
- **Forbidden**: Valid credentials but insufficient permissions
- **Generic errors**: Other connection issues with full error details

#### Execution Flow
1. ✅ Validate contexts exist (v1.5.2)
2. ✅ **Test cluster connectivity (v1.5.4)** ← NEW
3. ✅ Clean output directory
4. ✅ Fetch and compare resources

This "fail fast" approach saves significant time by detecting problems before expensive fetch operations begin.

### 🐳 Docker Improvements

#### Fixed: User Home Directory
- kdiff user home directory now properly set to `/home/kdiff` (was `/`)
- Fixes compatibility issues with tools expecting a valid home directory
- Creates `/home/kdiff/.kube` directory automatically with correct permissions
- Improves experience when running with `--user $(id -u):$(id -g)` flag

#### Updated: Permission Handling
After testing on various Linux distributions, we've updated the approach:
- **Removed**: Automatic permission copying (unreliable on some systems)
- **Added**: Clear documentation with three manual solutions, ordered by preference

**Recommended solutions:**

**Option 1: Simple permissions (best for single-user systems)**
```bash
chmod 644 ~/.kube/config
docker run ... mabombo/kdiff:latest -c1 prod -c2 staging -n myapp
```

**Option 2: Run as current user (most reliable)**
```bash
docker run --rm -it \
  --user $(id -u):$(id -g) \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp
```

**Option 3: Temporary copy (for shared systems)**
```bash
cp ~/.kube/config /tmp/kube-config-kdiff
chmod 644 /tmp/kube-config-kdiff
docker run -v /tmp/kube-config-kdiff:/home/kdiff/.kube/config:ro ...
rm /tmp/kube-config-kdiff
```

## Technical Details

### Connectivity Testing Function
```python
def test_cluster_connectivity(context: str) -> tuple[bool, str]:
    """Test if cluster is reachable using kubectl cluster-info"""
    # - Uses 'kubectl cluster-info --request-timeout=10s'
    # - 15-second total timeout via subprocess
    # - Parses stderr for specific error patterns
    # - Returns (success: bool, error_message: str)
```

### Error Parsing
Comprehensive detection of common kubectl failures:
- DNS resolution issues
- Connection timeouts
- Authentication failures (Unauthorized)
- Permission issues (Forbidden)
- Generic connection errors

### Integration Points
- Runs after context validation (`validate_context()`)
- Tests all specified clusters in parallel logic
- Exits with code 2 on connectivity failure
- Provides detailed suggestions based on error type

## Upgrade Notes

### Breaking Changes
None. All changes are backward compatible.

### Behavioral Changes
1. **New exit code**: Program now exits with code 2 on connectivity failures
2. **Additional startup time**: ~10-15 seconds per unreachable cluster (but saves much more time later)
3. **Earlier error detection**: Connection issues now caught before fetch operations

### Docker Users
- **Home directory change**: If scripts relied on `/` as home, update to `/home/kdiff`
- **Permission handling**: Review DOCKER_README.md for updated guidance
- **No action required**: If your setup already works, continue as before

## Migration Guide

### From v1.5.3
No migration needed. Simply pull the new image:
```bash
docker pull mabombo/kdiff:1.5.4
```

### From v1.5.2 or earlier
Update your kubeconfig mount if needed (see Docker Improvements section above).

## What's Next

Possible future enhancements:
- Parallel resource fetching for faster comparisons
- Additional resource type support
- Web UI for report viewing
- CI/CD integration templates

---

# kdiff v1.5.3 - Automatic Docker Permission Handling

## Major Improvement

### Automatic Kubeconfig Permission Handling
**Problem solved!** No more manual permission fixes required when using Docker on Linux.

#### What Changed
- **New entrypoint script**: Automatically detects and fixes kubeconfig permission issues
- **Zero configuration**: Works transparently without user intervention
- **Secure**: Temporary copy created only inside container, original file untouched

#### How It Works
```bash
# Just run normally - permissions handled automatically!
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp
```

The entrypoint script:
1. ✅ Detects if kubeconfig is readable
2. ✅ If not, creates temporary copy with correct permissions
3. ✅ Uses temporary copy for kubectl operations
4. ✅ Cleans up automatically when container exits

#### Before vs After

**Before (v1.5.2 and earlier):**
```bash
# Required manual permission changes
chmod 644 ~/.kube/config  # or
cp ~/.kube/config /tmp/kube-config
chmod 644 /tmp/kube-config
# Then run docker...
```

**After (v1.5.3+):**
```bash
# Just works! No manual steps needed
docker run ... mabombo/kdiff:latest -c1 prod -c2 staging -n myapp
```

## Technical Details

### Entrypoint Script
- New `docker-entrypoint.sh` wraps kdiff execution
- Checks `KUBECONFIG` environment variable (defaults to `/home/kdiff/.kube/config`)
- Attempts to read kubeconfig file
- If permission denied:
  * Creates `/tmp/kubeconfig` with copy of content
  * Sets `KUBECONFIG=/tmp/kubeconfig`
  * Proceeds with kdiff execution
- If unable to fix, shows clear error with manual solutions

### Security
- Temporary file created inside container only
- Original kubeconfig remains untouched
- Temporary file deleted when container exits
- No security compromise

## Compatibility

- ✅ Works on Linux (primary target)
- ✅ Works on macOS (no changes needed, already worked)
- ✅ Works on Windows (no changes needed, already worked)
- ✅ Backward compatible with all previous usage patterns

---

# kdiff v1.5.2 - Context Validation & Docker Fixes

## New Features

### Context Validation
- **Early validation**: Checks that specified Kubernetes contexts exist before starting
- **Clear error messages**: Shows exactly which context is invalid
- **Helpful output**: Lists all available contexts when validation fails
- **Time saver**: Prevents wasted time attempting to connect to non-existent clusters

#### Example Error Output
```
[ERROR] CRITICAL ERROR: Context 'my-typo-cluster' does not exist

Available contexts:
  - prod-cluster
  - staging-cluster
  - dev-cluster

Suggestion: Use 'kubectl config get-contexts' to see all available contexts
```

## Bug Fixes

### Docker Permission Issues on Linux
Added comprehensive troubleshooting documentation for permission issues when running on Linux.

**Problem**: Linux users encountered "permission denied" errors when mounting kubeconfig

**Solutions documented**:
1. **Adjust file permissions** (Recommended)
   ```bash
   chmod 644 ~/.kube/config
   ```

2. **Use temporary copy**
   ```bash
   cp ~/.kube/config /tmp/kube-config-kdiff
   chmod 644 /tmp/kube-config-kdiff
   # Mount /tmp/kube-config-kdiff instead
   ```

3. **Run as current user**
   ```bash
   docker run --user $(id -u):$(id -g) ...
   ```

## Improvements

### Error Handling
- Exit code 2 for context validation failures (distinguishable from comparison differences)
- Consistent error formatting across all validation failures
- Actionable suggestions in all error messages

### Documentation
- New "Troubleshooting" section in DOCKER_README.md
- Step-by-step solutions for common Linux issues
- Examples for both permission and context errors

## Testing
- 6 new tests for context validation
- Validates error messages, exit codes, and suggestions
- All 45 tests passing (39 existing + 6 new)

---

# kdiff v1.5.1 - Unified Namespace Parameter

## Improvements

### Simplified Parameter Interface
- **Unified `-n` parameter**: Now accepts both single namespace and comma-separated list
  * Single namespace: `-n prod`
  * Multiple namespaces: `-n ns1,ns2,ns3`
  * Long form alias: `--namespaces` still available
- **Clearer usage**: No more confusion between `-n` and `--namespaces`
- **Same behavior, simpler syntax**: Works identically in both single-cluster and two-cluster modes

### Updated Examples
```bash
# Single-cluster mode (was: --namespaces)
kdiff -c prod-cluster -n ns1,ns2

# Two-cluster mode - single namespace
kdiff -c1 prod -c2 staging -n myapp

# Two-cluster mode - multiple namespaces  
kdiff -c1 prod -c2 staging -n ns1,ns2,ns3
```

### Documentation
- All examples updated to use unified `-n` syntax
- Help text clarified
- README simplified with consistent parameter usage

---

# kdiff v1.5.0 - Single-Cluster Namespace Comparison

## Major Features

### Single-Cluster Multi-Namespace Comparison
- **New comparison mode**: Compare resources across multiple namespaces within the same cluster
- **Pairwise comparison**: Automatically generates comparisons for all namespace pairs
- **Intelligent filename matching**: Resources matched by kind+name, namespace excluded from matching logic
- **Separate comparison directories**: Each namespace pair gets its own subdirectory with complete reports
- **Dual-mode support**: Maintains full backward compatibility with two-cluster comparison mode

#### Usage Examples
```bash
# Compare two namespaces in the same cluster
kdiff -c prod-cluster --namespaces ns1,ns2

# Compare three namespaces (generates 3 pairwise comparisons: ns1 vs ns2, ns1 vs ns3, ns2 vs ns3)
kdiff -c prod-cluster --namespaces dev,staging,prod

# Single-cluster comparison with specific resources
kdiff -c prod-cluster --namespaces ns1,ns2 -r configmap,deployment

# Include services and ingress
kdiff -c prod-cluster --namespaces ns1,ns2 --include-services-ingress
```

### Enhanced Report Generation
- **Context-aware labels**: Reports automatically detect namespace vs cluster comparison
- **Dynamic UI text**: "Namespace 1/2" instead of "Cluster 1/2" in single-cluster mode
- **Proper resource paths**: Separate directory names from display labels for accurate file reading
- **Organized output structure**: Each comparison in its own subdirectory (e.g., `ns1_vs_ns2/`)

### Output Structure
**Single-cluster mode:**
```
kdiff_output/
└── latest/
    ├── ns1_vs_ns2/              # Comparison between ns1 and ns2
    │   ├── summary.json
    │   ├── diff-details.html
    │   ├── diff-details.json
    │   ├── diffs/
    │   ├── CLUSTER_ns1/
    │   └── CLUSTER_ns2/
    └── ns1_vs_ns3/              # Comparison between ns1 and ns3
```

## Enhancements

### CLI Improvements
- Added `-c CONTEXT` option for single-cluster mode
- Extended `--namespaces` to work with both modes (single-cluster and two-cluster)
- Enhanced help text with examples for both comparison modes
- Improved argument validation with clear error messages

### Testing
- **6 new test cases** covering:
  * Single-cluster filename logic (namespace exclusion)
  * Two-cluster filename logic (namespace inclusion)
  * Pairwise comparison generation
  * Argument validation for both modes
- Total test suite: **39 tests** - all passing

### Documentation
- Updated README.md with single-cluster mode documentation
- Added comprehensive examples for both comparison modes
- Documented output structure for both modes
- Updated CLI help text with mode-specific examples

## Technical Details

### Comparison Logic
- **Two-cluster mode**: Resources identified by `kind__namespace__name` (namespace part of identity)
- **Single-cluster mode**: Resources identified by `kind__name` (namespace ignored for matching)
- **Smart matching**: Same resource in different namespaces correctly detected as "different" not "missing"

### Backward Compatibility
- ✅ All existing two-cluster functionality preserved
- ✅ Existing scripts and workflows continue to work
- ✅ No breaking changes to command-line interface
- ✅ Maintains same output format for two-cluster mode

---

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
