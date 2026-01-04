# kdiff v1.1.0 - Enhanced Side-by-Side Diff Visualization

## 🎉 New Features

### Side-by-Side Diff Viewer
- **VS Code-style two-pane layout** for comparing resources
- **Integrated jsdiff library** for robust line-by-line comparison
- **Color-coded differences**:
  - 🔴 Red: Lines only in first cluster (removed)
  - 🟢 Green: Lines only in second cluster (added)
  - 🔵 Blue: Modified lines
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
- UI consistency: Side-by-side modal buttons now match View Diff modal style
- Better visual feedback for interactive elements

## 📦 Installation

```bash
pip install kdiff==1.1.0
```

Or with Docker:
```bash
docker pull YOUR_DOCKERHUB_USERNAME/kdiff:1.1.0
```

See [CHANGELOG.md](./CHANGELOG.md) for complete details.
