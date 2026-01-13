# kdiff v1.7.3 - Enhanced Namespace Context in HTML Reports

## Overview

Version 1.7.3 significantly improves namespace and cluster context visibility in HTML reports. Whether you're comparing two clusters or multiple namespaces within a single cluster, the enhanced reports now provide comprehensive context information that makes it easier to understand where differences occur.

## New Features

### Enhanced Namespace Context Display

#### Two-Cluster Comparison Mode
When comparing resources across two different clusters:
- **Namespace List in Header**: All compared namespaces are now listed in the report header
- **Cluster/Namespace in Tooltips**: Hover tooltips show both cluster and namespace information
- **Side-by-Side Modal Headers**: Modal windows display cluster/namespace for each pane
- **Better Context Tracking**: Easy to see which namespaces are being compared

#### Namespace Comparison Mode
When comparing multiple namespaces within a single cluster:
- **Cluster Name in Header**: Cluster name prominently displayed for context
- **Multiple Namespace Badges**: Resources show all namespaces where they exist
- **Color-Coded Badges**: Visual distinction between different namespaces
- **Enhanced Resource Context**: Clear indication of namespace scope for each resource

### Unified Header Layout
- **Consistent Design**: Same header structure for both comparison modes
- **Improved Visual Hierarchy**: Better organization of cluster and namespace information
- **Enhanced Readability**: Clearer presentation of context metadata

## Bug Fixes

### F-String Syntax Error
- **Fixed**: Corrected nested f-string syntax error in metadata header generation
- **Impact**: Resolved Python syntax error that prevented HTML report generation
- **Improvement**: Better code structure with separated metadata construction

## Technical Details

### Implementation
- Refactored metadata header generation to avoid nested f-strings
- Added namespace collection logic for both comparison modes
- Enhanced data attributes for proper context passing to modals
- Improved badge generation with namespace-specific styling

### Testing
- All 49 existing tests passing
- Syntax validation confirmed
- Manual testing across both comparison modes

## Usage Example

### Two-Cluster Comparison
```bash
kdiff -c1 prod-cluster -c2 staging-cluster -ns production,staging
```
The report will now show:
- Header: "Comparing: prod-cluster vs staging-cluster"
- "ns: production, staging" in metadata
- Cluster/namespace in all tooltips and modals

### Namespace Comparison
```bash
kdiff -c prod-cluster --namespaces ns1,ns2,ns3
```
The report will now show:
- Header: "Cluster: prod-cluster"
- "ns: ns1, ns2" in metadata
- Multiple namespace badges for resources in different namespaces

## Installation

### Update to v1.7.3

```bash
git pull origin main
git checkout v1.7.3
```

**Docker:**
```bash
docker pull mabombo/kdiff:1.7.3
```

## Migration Notes

- No breaking changes
- Existing reports remain functional
- New context features automatically applied
- No configuration changes required

## Release Information

**Version:** 1.7.3  
**Release Date:** January 13, 2026  
**Git Tag:** v1.7.3  
**Tests:** 49 passing  

---

# kdiff v1.7.2 - Text Search in Side-by-Side View

## Overview

Version 1.7.2 introduces powerful text search functionality in the side-by-side diff modal, enabling users to quickly locate specific content across both panes with real-time highlighting and navigation.

## New Features

### Text Search in Side-by-Side View

**Interactive Search Functionality:**
- Search input field integrated in modal toolbar
- Real-time search with instant highlighting of matching text
- Case-insensitive search across both left and right panes
- Search works on all visible content in the diff view
- Clear button to reset search and remove all highlights

**Match Counter & Navigation:**
- Visual counter showing current match and total matches (e.g., "1/5")
- Previous/Next navigation buttons to jump between search results
- Keyboard shortcuts support:
  - `Enter` key for next match
  - `Shift+Enter` for previous match
- Automatic scroll to center matched text in viewport
- Smooth navigation with visual feedback

**Visual Highlighting:**
- Active match highlighted with yellow background
- All matches visible but dimmed
- Clear visual distinction between current and other matches
- Highlights persist during diff navigation
- Search state maintained across filter changes

**Integration with Existing Features:**
- Works seamlessly with diff navigation (Previous/Next diff buttons)
- Compatible with filter system (Added/Removed/Modified filters)
- Maintains zoom level during search
- Synchronized scrolling preserved while searching

## Bug Fixes

### Search Input Selector
- **Fixed:** Corrected querySelector to properly target search input element
- **Impact:** Search functionality now initializes correctly on modal open
- **Details:** Improved error handling for search-related DOM operations

## Use Cases

**Finding Specific Configuration Values:**
```
Scenario: You need to find all occurrences of "DB_PASSWORD" in a large ConfigMap
Action: Open side-by-side view, type "DB_PASSWORD" in search box
Result: All 3 matches highlighted, counter shows "1/3", navigate with arrows
```

**Locating Environment Variables:**
```
Scenario: Check if "JAVA_OPTS" is set differently between clusters
Action: Search for "JAVA_OPTS" in the diff
Result: Jump directly to the line with the environment variable
```

**Reviewing API Endpoints:**
```
Scenario: Find all references to "/api/v2" in service configuration
Action: Use search to highlight all endpoint references
Result: Quickly navigate through all API paths in both versions
```

## Tips & Tricks

**Efficient Searching:**
1. Start search while modal is loading for instant results
2. Use partial matches (e.g., "replicas" finds "spec.replicas")
3. Combine with filters to search within specific change types
4. Clear search to see full diff context again

**Keyboard Workflow:**
```
1. Open side-by-side modal (click button)
2. Focus search input (automatically focused or Tab key)
3. Type search term
4. Press Enter repeatedly to cycle through matches
5. Use Shift+Enter to go backwards
6. Press Esc or click X to clear search
```

**Best Practices:**
- Search is case-insensitive - "password" matches "PASSWORD"
- Use specific terms to reduce number of matches
- Combine search with zoom for detailed inspection
- Clear search between different lookups for clarity

## Technical Details

**Search Implementation:**
- JavaScript-based client-side search
- No server communication required
- Efficient text matching algorithm
- DOM manipulation for highlighting
- State management for active match tracking

**Performance:**
- Real-time search with no lag on large files
- Efficient highlight rendering
- Smooth scrolling animations
- Minimal memory footprint

## Comparison with v1.7.1

| Feature | v1.7.1 | v1.7.2 |
|---------|--------|--------|
| Text Search | ❌ No | ✅ Yes |
| Match Counter | ❌ No | ✅ Yes |
| Search Navigation | ❌ No | ✅ Yes |
| Keyboard Shortcuts | Diff nav only | Diff + Search |
| Visual Highlighting | Diffs only | Diffs + Search |

## Getting Started

**Installation:**
```bash
# Update to v1.7.2
cd kdiff
git pull
git checkout v1.7.2

# Or pull Docker image
docker pull mabombo/kdiff:1.7.2
```

**Using Text Search:**
```bash
# Generate diff report
kdiff -c1 prod-cluster -c2 staging-cluster -n myapp

# Open diff-details.html in browser
# Click "Side-by-Side" on any resource
# Use search box at top of modal
```

## Release Notes

**Version:** 1.7.2  
**Release Date:** January 13, 2026  
**Git Tag:** v1.7.2  
**Changes:** 1 new feature, 1 bug fix  
**Backward Compatibility:** Fully compatible with v1.7.x

## 🔗 Resources

- **Documentation:** README.md
- **Changelog:** CHANGELOG.md  
- **Source Code:** https://github.com/mabombo/kdiff
- **Docker Hub:** https://hub.docker.com/r/mabombo/kdiff

---

# kdiff v1.7.1 - Side-by-Side Navigation UX Improvements

## Overview

Version 1.7.1 enhances the side-by-side diff modal with improved navigation user experience. The modal now automatically shows the first difference and maintains consistent counter display behavior.

## User Experience Improvements

### Auto-Navigation to First Diff

**Immediate Context on Modal Open:**
- Modal automatically navigates to the first difference when opened
- No need to manually click "Next" to see the first change
- 100ms delay ensures proper layout rendering before navigation
- Improves workflow efficiency for reviewing diffs

**Before v1.7.1:**
```
1. Click "View Side-by-Side"
2. Modal opens at top of file (counter shows 0/X)
3. Click "Next" to see first diff
```

**After v1.7.1:**
```
1. Click "View Side-by-Side"
2. Modal opens directly at first diff (counter shows 1/X)
3. Immediately see the change
```

### Counter Display Consistency

**Minimum Value Always 1:**
- Counter now always displays minimum value of 1 instead of 0
- Consistent behavior when filtering differences
- More intuitive for users (diffs numbered 1 to N, not 0 to N-1)
- Better alignment with user expectations

### Improved First Diff Centering

**Proper Viewport Positioning:**
- First difference properly centered when modal opens
- Fixed issue where first diff appeared at bottom of viewport
- Better visual presentation of initial change location
- Improved alignment between left and right panes

### Navigation Highlight Color

**Visual Feedback Optimization:**
- Reverted to original yellow highlight color after user testing
- Tested alternatives (cyan, blue) for improved visibility
- Yellow provides best contrast with existing diff colors:
  * Green: Added lines
  * Red: Removed lines
  * Yellow: Modified lines (inline diffs)
  * Yellow highlight: Current navigation position

## Technical Implementation

### JavaScript Enhancements

**initializeDiffNavigation() Updates:**
```javascript
function initializeDiffNavigation() {
    currentDiffIndex = -1;
    allDiffs = [];
    collectAllDiffs();
    
    // Auto-navigate to first diff if available
    if (allDiffs.length > 0) {
        setTimeout(() => {
            navigateToNextDiff();
        }, 100);
    }
}
```

**updateDiffCounter() Fix:**
```javascript
function updateDiffCounter() {
    const current = currentDiffIndex >= 0 ? currentDiffIndex + 1 : 1;
    // Now always shows 1 as minimum, not 0
}
```

## Installation & Upgrade

### PyPI
```bash
pip install --upgrade kdiff
```

### Docker
```bash
docker pull mabombo/kdiff:1.7.1
# or use latest tag
docker pull mabombo/kdiff:latest
```

## Bug Fixes

- Fixed diff counter showing 0 as minimum value
- Fixed first diff not being centered on modal open
- Improved layout rendering timing for auto-navigation

## Use Cases

### Quick Diff Review Workflow

**Scenario:** DevOps engineer reviewing differences between prod and staging

**Improved Experience:**
1. Open side-by-side modal
2. **Automatically positioned at first difference** (NEW)
3. Review change in context
4. Click "Next" to move through remaining diffs
5. Counter shows 1/15, 2/15, ... N/15 (not 0/15)

### Filtered Diff Navigation

**Scenario:** Focusing only on specific resource types

**Improved Experience:**
- Apply filters to show only ConfigMap diffs
- Counter consistently shows 1/5 even with filters active
- No confusion from 0-based indexing

## Migration Notes

### From v1.7.0

No breaking changes. All existing functionality preserved.

**New Behaviors:**
- Side-by-side modal auto-scrolls to first diff
- Counter minimum value is 1 (was 0)
- These are enhancements only - no API changes

### Compatibility

- Python: 3.10+
- Kubernetes: 1.20+
- kubectl: Must be installed and configured

## Summary

Version 1.7.1 is a focused UX improvement release that makes the side-by-side diff navigation more intuitive and efficient. Combined with the 5.7x performance improvement from v1.7.0, kdiff now offers both speed and excellent user experience for Kubernetes cluster comparisons.

---

# kdiff v1.7.0 - Parallel Execution Performance Boost

## Overview

Version 1.7.0 introduces parallel execution of kubectl calls, delivering a **5.7x performance improvement** over the previous version. This major optimization makes kdiff significantly faster for comparing large clusters and multiple namespaces.

## Major Features

### Parallel Execution Engine

**Multi-threaded Resource Fetching:**
- Utilizes Python's `ThreadPoolExecutor` for concurrent kubectl calls
- Up to 10 parallel threads by default (configurable with `--max-workers`)
- Clusters queried simultaneously in two-cluster mode
- Namespaces queried simultaneously in single-cluster mode
- Thread-safe console output with Lock synchronization

**Measured Performance Improvement:**

Real-world benchmark (two clusters, namespace with 12 resource types):

| Metric | v1.6.0 (Sequential) | v1.7.0 (Parallel) | Improvement |
|--------|---------------------|-------------------|-------------|
| Execution Time | 18.3 seconds | 3.2 seconds | **5.7x faster** |
| Time Saved | - | 15.1 seconds | **82.5% reduction** |

### New Command-Line Option

**`--max-workers N`** - Control parallelization level
```bash
# Use default parallelization (10 workers)
kdiff -c1 prod -c2 staging -n myapp

# Increase for large clusters
kdiff -c1 prod -c2 staging -n myapp --max-workers 20

# Decrease if hitting API rate limits
kdiff -c1 prod -c2 staging -n myapp --max-workers 5
```

## Technical Implementation

### Architecture Changes

**Refactored Resource Fetching:**
- New `fetch_single_resource()` function for thread-safe operations
- Enhanced error handling in multi-threaded context
- Critical errors properly terminate all threads
- Non-critical errors don't block other resource fetches

**Thread Safety:**
- Lock-based synchronization for console output
- Safe concurrent file writes
- Proper error propagation across threads

## Performance Analysis

### Scalability Benefits

The performance improvement scales with:
- **Number of resource types**: More resources = greater benefit
- **Number of clusters/namespaces**: Parallel cluster queries
- **Network latency**: Higher latency = more time saved

**Example scenarios:**
- Small comparison (1 namespace, 5 resources): ~3x faster
- Medium comparison (1 namespace, 12 resources): ~5.7x faster
- Large comparison (3 namespaces, 12 resources): ~8-10x faster

### When to Tune `--max-workers`

**Increase workers (15-20):**
- Large clusters with many resources
- Stable, high-bandwidth network
- No API rate limiting concerns

**Decrease workers (3-5):**
- Hitting Kubernetes API rate limits
- Shared cluster with many users
- Limited network bandwidth

**Keep default (10):**
- Most production scenarios
- Good balance between speed and API load

## 🧪 Testing

### Comprehensive Test Suite

Added 10 new tests specifically for parallel execution:
- `test_parallel_fetch_creates_all_resources`
- `test_max_workers_parameter_is_used`
- `test_thread_safe_console_output`
- `test_error_in_one_thread_does_not_block_others`
- `test_parallel_produces_same_results_as_sequential`
- `test_critical_error_terminates_all_threads`
- `test_fetch_single_resource_success`
- `test_fetch_single_resource_permission_error`
- `test_fetch_single_resource_context_not_found`
- `test_concurrent_file_writes_are_safe`

**Total: 49 tests (39 existing + 10 new) - All passing ✅**

## Migration Notes

- No breaking changes
- Parallel execution enabled by default
- Sequential behavior available with `--max-workers 1` if needed
- All existing commands work without modification
- Configuration files and scripts require no updates

## Use Cases

**CI/CD Pipelines:**
```bash
# Faster pre-deployment checks
kdiff -c1 staging -c2 prod -n myapp --max-workers 15
```

**Large-Scale Comparisons:**
```bash
# Compare multiple namespaces efficiently
kdiff -c prod-cluster -n ns1,ns2,ns3,ns4,ns5 --max-workers 20
```

**Iterative Development:**
```bash
# Rapid feedback during configuration changes
kdiff -c1 dev -c2 staging -n myapp
# Now completes in seconds instead of ~20 seconds
```

## Docker Image

```bash
# Pull latest version
docker pull mabombo/kdiff:1.7.0
docker pull mabombo/kdiff:latest

# Run with parallel execution
docker run --rm -v ~/.kube:/root/.kube \
  mabombo/kdiff:1.7.0 \
  -c1 prod-cluster -c2 staging-cluster \
  -n default --max-workers 15
```

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## What's Next

Future optimizations being considered:
- Async I/O for even better performance
- Caching layer for repeated comparisons
- Incremental comparison mode
- Real-time cluster monitoring

---

# kdiff v1.6.0 - Enhanced Diff Navigation and Filter Improvements

## Overview

Version 1.6.0 introduces a powerful navigation system for the side-by-side diff viewer, making it significantly easier to review and navigate through differences in large Kubernetes resource comparisons.

## Major Features

### Interactive Diff Navigation

**New Navigation Controls:** Side-by-side diff modal now includes intuitive navigation buttons:
- **Previous/Next Buttons:** Navigate sequentially through all differences
- **Editable Counter:** Jump directly to any specific difference by typing its number
- **Current Position Display:** Shows "X / Y" format (e.g., "5 / 23")
- **Wraparound Support:** Seamlessly cycles from last to first difference

**Smart Scrolling Behavior:**
- Smooth scrolling for nearby differences (enhanced UX)
- Instant scrolling for large jumps (e.g., wraparound from diff 50 to diff 1)
- Automatic centering of target difference in viewport
- Synchronized scrolling between left and right panes
- Visual highlight (yellow glow animation) for 1.5 seconds on navigation

**Filter Integration:**
- Navigation respects active filters (Added, Removed, Modified)
- Counter dynamically updates when filters are toggled
- Only navigates through visible differences
- Maintains alignment between left and right panes

### Keyboard Support

**Editable Counter Field:**
- Click counter to type any difference number (1 to total)
- Press Enter to jump to specified difference
- Numeric input validation (only accepts digits)
- Arrow keys for easy editing

### Filter UI Improvements

**Streamlined Interface:**
- Removed "Unchanged" filter (rarely used in practice)
- Renamed "Reset Filters" → "Clear Filters" for clarity
- Cleaner, more focused filter options

## 📋 Technical Details

### Navigation Implementation
- Collects diffs by line index for perfect alignment
- Uses `getComputedStyle()` for reliable visibility checking
- Tracks both left and right pane differences independently
- Re-collects diffs when filters change

### Performance Optimizations
- Instant scroll for jumps > 2 viewports
- Smooth scroll with fine-tuning for nearby navigation
- Efficient diff collection (excludes hidden/placeholder elements)

## Bug Fixes

- Fixed diff counter not updating when filters changed
- Fixed alignment issues between left and right panes
- Fixed navigation breaking after manual scrolling
- Improved wraparound centering accuracy
- Fixed counter visibility (better contrast)

## Use Cases

**Large Resource Comparisons:**
```bash
# Compare production vs staging namespaces with many differences
kdiff -c prod-cluster,staging-cluster -n app-namespace

# Open side-by-side view for any resource
# Use Previous/Next to review each difference
# Filter by type (Added/Removed/Modified)
# Jump to specific diff using counter
```

**Multi-Namespace Reviews:**
```bash
# Review differences across multiple namespaces
kdiff -c REEVO-BMW-PROD -n connect,default,kube-system

# Navigate through hundreds of differences efficiently
# Focus on specific change types with filters
```

## Migration Notes

- No breaking changes
- Navigation feature automatically available in all HTML reports
- Existing reports remain functional
- No configuration changes required

## Docker Image

```bash
# Pull latest version
docker pull mabombo/kdiff:1.6.0
docker pull mabombo/kdiff:latest

# Run with navigation features
docker run --rm -v ~/.kube:/root/.kube \
  mabombo/kdiff:1.6.0 \
  -c prod-cluster,staging-cluster \
  -n default -o /data/output
```

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

# kdiff v1.5.6 - Namespace-Scoped Connectivity Fix

## Critical Fix

### 🔧 Namespace-Scoped Permissions Support

**Problem:** Users with namespace-only RBAC permissions were getting "Insufficient permissions" errors during connectivity testing, even when they had full access to the specified namespaces.

**Root Cause:** The connectivity test used `kubectl cluster-info` which requires cluster-level permissions. Many Kubernetes users only have namespace-scoped access.

**Solution:** Smart connectivity testing that adapts to your permission level:

```bash
# Now works correctly with namespace-scoped permissions
kdiff -c REEVO-BMW-PROD -n connect,default

# Output:
# Validating Kubernetes contexts...
# Testing cluster connectivity...
# ✓ All clusters are reachable
# Mode: Single-cluster multi-namespace comparison
# Cluster: REEVO-BMW-PROD
# Namespaces: connect, default
```

### How It Works

**When namespaces are specified:**
- Tests connectivity using `kubectl get pods -n <first-namespace>`
- Only requires namespace-scoped permissions
- Perfect for users with limited RBAC access

**When no namespaces specified:**
- Falls back to `kubectl cluster-info`
- Requires cluster-level permissions
- Used for cluster-wide comparisons

**Error Messages:**
- Clearly distinguishes between namespace and cluster-level permission issues
- Provides specific guidance based on your permission scope

### Before vs After

**Before (v1.5.5):**
```bash
$ kdiff -c REEVO-BMW-PROD -n connect,default
Validating Kubernetes contexts...
Testing cluster connectivity...

[ERROR] CONNECTIVITY ERROR: Insufficient permissions to access cluster 'REEVO-BMW-PROD'
# ❌ Failed even with namespace permissions
```

**After (v1.5.6):**
```bash
$ kdiff -c REEVO-BMW-PROD -n connect,default
Validating Kubernetes contexts...
Testing cluster connectivity...
✓ All clusters are reachable
# ✅ Works with namespace-scoped permissions!
```

## Technical Details

### Implementation
```python
def test_cluster_connectivity(context: str, namespaces: list[str] | None = None):
    """Test connectivity with appropriate permissions level"""
    if namespaces:
        # Namespace-scoped test: kubectl get pods -n <namespace>
        test_ns = namespaces[0]
        kubectl('get', 'pods', '-n', test_ns, ...)
    else:
        # Cluster-scoped test: kubectl cluster-info
        kubectl('cluster-info', ...)
```

### Permission Requirements

**Namespace-Scoped Mode** (when `-n` specified):
- ✅ Read access to specified namespaces
- ✅ `pods` resource read permission
- ❌ No cluster-level access needed

**Cluster-Scoped Mode** (no `-n` specified):
- ❌ Cluster-level permissions required
- ❌ Access to cluster info APIs

### Error Message Improvements

**Namespace permission error:**
```
[ERROR] Access denied to namespace 'myapp' in cluster 'prod-cluster'
Check RBAC permissions for namespace-scoped resources
```

**Cluster permission error:**
```
[ERROR] Insufficient cluster-level permissions for 'prod-cluster'
This may be normal if you have only namespace-scoped access
```

## Who Benefits

- ✅ Developers with namespace-only access
- ✅ Teams using restrictive RBAC policies
- ✅ Multi-tenant cluster environments
- ✅ Users following principle of least privilege

## Upgrade Notes

### Breaking Changes
None. All changes are backward compatible.

### Behavioral Changes
1. **Smarter permission detection**: Automatically uses namespace-scoped testing when possible
2. **Better error messages**: Clear distinction between permission levels
3. **No user action required**: Automatically adapts to your permissions

### Testing Your Setup

```bash
# Test with namespace permissions
kdiff -c my-cluster -n myapp,staging

# Test with cluster permissions (if available)
kdiff -c1 prod -c2 staging
```

## Compatibility

- ✅ Works with all Kubernetes RBAC configurations
- ✅ Compatible with namespace-scoped service accounts
- ✅ Supports multi-tenant environments
- ✅ No changes to existing command-line interface

---

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

## Improvements
- UI consistency: All toggle buttons use same style (⇅ icon)
- Better visual feedback for interactive elements
- More intuitive report organization
- Fixed alignment issues in console output
- Corrected cluster name display throughout reports

## Installation

```bash
pip install kdiff==1.1.0
```

Or with Docker:
```bash
docker pull mabombo/kdiff:1.1.0
```

See [CHANGELOG.md](./CHANGELOG.md) for complete details.
