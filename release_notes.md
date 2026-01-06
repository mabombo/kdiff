# kdiff v1.1.0 - Enhanced User Experience & Reporting

## 🎉 New Features

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
