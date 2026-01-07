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
