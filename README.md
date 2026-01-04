<div align="center">
  <img src="loghi/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# kdiff — Intelligent Kubernetes Resource Comparison Between Two Clusters

## 📋 Overview

**kdiff** is a professional Python tool for comparing Kubernetes configurations between two remote clusters. It quickly identifies missing, different, or cluster-specific resources, with support for intelligent diffs and interactive HTML reports.

### 🎯 Main Use Cases

- **Verify configurations across environments** (dev vs prod, staging vs prod)
- **Pre-migration audits** (old cluster vs new)
- **Troubleshoot differences** between deployments that should be identical
- **Document differences** with navigable HTML reports
- **CI/CD validation** of configurations across environments

### ✨ Key Features

- ✅ **Intelligent normalization**: automatically removes volatile fields (uid, resourceVersion, timestamps, etc)
- ✅ **Smart ConfigMap diff**: shows only modified lines in config files, not the entire blob
- ✅ **Non-positional env comparison**: environment variables compared by name, not array position
- ✅ **Interactive HTML reports**: web interface with collapsible sections, zoom, and inline diff visualization
- ✅ **Side-by-side diff viewer**: VS Code-style dual-pane comparison with synchronized scrolling
  * Click "⚖️ Side-by-Side" button on any resource with differences
  * Two-pane layout (50/50 split) with actual cluster names
  * Line-by-line comparison with color highlighting:
    - 🔴 Red background: lines only in first cluster (removed)
    - 🟢 Green background: lines only in second cluster (added)
    - 🔵 Blue background: lines modified between clusters
  * Powered by [jsdiff](https://github.com/kpdecker/jsdiff) for robust diff algorithm
  * Zoom controls (+, ⟲, -) for adjusting font size
  * Synchronized scrolling between panes
  * Line numbers on both sides for easy reference
  * Proper handling of complex JSON structures and embedded newlines
- ✅ **Interactive resource cards**: Enhanced "Resources Only in One Cluster" card with eye icon and improved hover effects for better visibility
- ✅ **Noise reduction**: labels and annotations optional (default: removed to focus on substantial changes)
- ✅ **Fixed output directory**: always uses `latest/` for easy refresh workflow
- ✅ **Flexible filters**: include/exclude specific resources or types
- ✅ **Real cluster names**: uses actual names instead of generic "cluster1/cluster2"

---

## 📦 Installation and Requirements

### Requirements

- **Python 3.8+** (tested on 3.8-3.13)
- **kubectl** configured with access to clusters to compare
- **Operating system**: macOS, Linux (including WSL on Windows)

### Installation

#### Method 1: Automatic installation (recommended)

```bash
# Clone repository
git clone <repo-url>
cd kdiff

# Install in ~/.local (no sudo required)
PREFIX=$HOME/.local ./install.sh

# Add ~/.local/bin to PATH (if not already present)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or source ~/.zshrc

# Verify installation
kdiff --help
```

For system-wide installation (requires sudo):

```bash
sudo ./install.sh  # Installs in /usr/local
```

#### Method 2: Installation with pip (requires virtual environment)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Verify
kdiff --help
```

#### Method 3: Direct usage (no installation)

```bash
# Clone repository
git clone <repo-url>
cd kdiff

# Use directly
./bin/kdiff --help
```

**No external Python dependencies required!** Uses only standard library.

### Installation Verification

```bash
# Check that kdiff is installed
which kdiff

# Verify dependencies
python3 --version  # >= 3.8
kubectl version --client

# Run tests
cd <repository-directory>
bash tests/run_tests.sh
```

#### Method 4: Docker (containerized)

```bash
# Pull image from Docker Hub
docker pull YOUR_DOCKERHUB_USERNAME/kdiff:latest

# Run with kubeconfig mount
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  YOUR_DOCKERHUB_USERNAME/kdiff:latest \
  -c1 prod-cluster -c2 staging-cluster -n myapp

# Or use the wrapper script for easier usage
./kdiff-docker -c1 prod-cluster -c2 staging-cluster -n myapp
```

**Docker advantages:**
- ✅ No Python installation required
- ✅ No dependencies to manage
- ✅ Consistent environment across systems
- ✅ Isolated execution
- ✅ Perfect for CI/CD pipelines

See [DOCKER_HUB_GUIDE.md](DOCKER_HUB_GUIDE.md) for publishing instructions.

---

## 🚀 Quick Start

### Basic example

```bash
# Compare two kubectl contexts (console output)
./bin/kdiff -c1 prod-cluster -c2 staging-cluster

# JSON output in specific directory
./bin/kdiff -c1 prod -c2 staging -f json -o ./reports/prod-vs-staging
```

### Advanced examples

```bash
# Only deployments and configmaps from a specific namespace
./bin/kdiff -c1 prod -c2 dev \
    -n myapp \
    -r deployment,configmap

# Exclude specific resources
./bin/kdiff -c1 prod -c2 staging \
    --exclude-resources deployment__ns__legacy-app

# Include Service/Ingress (normally excluded to reduce noise)
./bin/kdiff -c1 prod -c2 staging \
    --include-services-ingress

# Keep metadata (labels/annotations) for detailed debugging
./bin/kdiff -c1 prod -c2 staging \
    --show-metadata
```

---

## 📊 Output and Reports

### Output directory structure

```
kdiff_output/
└── latest/                      # ← Fixed directory (always the same)
    ├── summary.json             # ← Machine-readable summary
    ├── diff-details.html        # ← Interactive HTML report ⭐
    ├── diff-details.json        # ← Diff details for automation
    ├── diffs/                   # ← .diff files for each modified resource
    │   ├── configmap__myns__app-config.json.diff
    │   └── deployment__myns__webapp.json.diff
    ├── prod-cluster/            # ← Normalized resources cluster 1
    │   ├── configmap__myns__app-config.json
    │   └── deployment__myns__webapp.json
    └── staging-cluster/         # ← Normalized resources cluster 2
        ├── configmap__myns__app-config.json
        └── service__myns__webapp-svc.json
```

**Important note:** kdiff always uses the `kdiff_output/latest/` directory (instead of creating timestamps). This allows:
- Open HTML report always at the same path: `kdiff_output/latest/diff-details.html`
- Update report simply with a browser refresh (F5)
- Avoid accumulation of old directories

The directory is automatically cleaned on each execution.

### 📄 summary.json

```json
{
  "missing_in_2": ["deployment__prod__legacy-app.json"],
  "missing_in_1": ["service__staging__new-feature-svc.json"],
  "different": ["configmap__shared__app-config.json"],
  "counts": {
    "missing_in_2": 1,
    "missing_in_1": 1,
    "different": 1
  },
  "by_kind": {
    "deployment": {"missing_in_2": 1, "missing_in_1": 0, "different": 0},
    "service": {"missing_in_2": 0, "missing_in_1": 1, "different": 0},
    "configmap": {"missing_in_2": 0, "missing_in_1": 0, "different": 1}
  }
}
```

### 🌐 Interactive HTML Report

The `diff-details.html` file provides:

- **Dashboard with statistics**: total changes, resources by kind, missing resources
- **Interactive resource cards**: Click on "Resources Only in One Cluster" card (with eye icon 👁️) to view detailed list
- **Color-coded diff visualization**: green for additions, red for removals
- **Two viewing modes for diffs**:
  * **View Diff**: Standard unified diff view with syntax highlighting and zoom
  * **⚖️ Side-by-Side**: VS Code-style dual-pane comparison with:
    - Perfect 50/50 split showing both cluster versions
    - Synchronized scrolling between panes
    - Color-coded line-by-line differences (red/green/blue)
    - Independent zoom controls
    - Line numbers on both sides
- **Modal popups**: Full-screen zoomable views for detailed inspection
- **Collapsible sections**: click to expand/collapse each resource
- **Cluster name tooltips**: hover over diff lines to see which cluster
- **Direct links to resources**: quick navigation within report

### 📋 Console Output

```
K8s diff summary — Missing in staging: 1, Missing in prod: 0, Different: 3

Top resource kinds by total changes:
- deployment: 2
- configmap: 1
- service: 1

Per-kind breakdown:

RESOURCE                        M2       M1       DIFF
deployment                       1        0          1
configmap                        0        0          1
service                          0        0          1
```

---

## 🔧 Command Line Options

### Basic Options

```bash
kdiff -c1 CONTEXT1 -c2 CONTEXT2 \
    [-n NAMESPACE] \              # Namespace (default: all)
    [-r RESOURCES] \              # Resource types (comma-separated)
    [-o OUTPUT_DIR] \             # Output directory (default: ./kdiff_output/latest)
    [-f FORMAT] \                 # text|json (default: text)
    [--show-metadata] \           # Keep labels/annotations
    [--include-services-ingress] \  # Include Service/Ingress
    [--exclude-resources RES1,RES2]  # Exclude specific resources
```

See `docs/usage.md` for complete details.

---

## 🏗️ Architecture

### Main Files

```
kdiff/
├── bin/kdiff                    # Main CLI
├── lib/
│   ├── normalize.py             # Resource normalization
│   ├── compare.py               # Comparison and diff generation
│   ├── report.py                # Console report
│   ├── report_md.py             # Markdown/HTML report
│   └── diff_details.py          # Interactive HTML report ⭐
├── tests/
│   ├── test_kdiff.py            # Complete test suite
│   └── run_tests.sh
└── docs/
    ├── usage.md                 # Detailed usage guide
    └── diff_details.md          # HTML report documentation
```

### Execution Flow

```
1. bin/kdiff → fetch resources via kubectl
2. lib/normalize.py → remove volatile fields
3. Save normalized JSON
4. lib/compare.py → generate diff (smart ConfigMap + standard)
5. lib/diff_details.py → interactive HTML report
6. Directory cleaned automatically (always latest/)
```

---

## 🔍 Advanced Features

### Smart ConfigMap Diff

Instead of showing entire JSON as modified, extracts each `data.*` field and compares line by line:

```diff
=== data.application.yaml ===
--- data.application.yaml (prod)
+++ data.application.yaml (staging)
@@ -10,7 +10,7 @@
 server:
   port: 8080
-  max-connections: 100
+  max-connections: 200
   timeout: 30s
```

### Env Arrays → Dictionaries Conversion

Environment variables compared by name, not array position → **no false positives** from reordering.

---

## 🗑️ Uninstallation

### If installed with install.sh

```bash
# Installation in ~/.local
rm -rf ~/.local/lib/kdiff
rm ~/.local/bin/kdiff

# System-wide installation (/usr/local)
sudo rm -rf /usr/local/lib/kdiff
sudo rm /usr/local/bin/kdiff
```

### If installed with pip

```bash
# Within virtual environment
pip uninstall kdiff
```

---

## 📚 Additional Documentation

- [docs/usage.md](docs/usage.md) - Complete usage guide and parameters
- [docs/diff_details.md](docs/diff_details.md) - HTML report documentation

---

## 🐛 Troubleshooting

### kdiff: command not found

Verify that PATH includes installation directory:

```bash
# If installed in ~/.local
echo $PATH | grep -o "$HOME/.local/bin"

# If not present, add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Error "kubectl not found"

```bash
# Verify kubectl installation
which kubectl

# On macOS (with Homebrew)
brew install kubectl

# On Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Incompatible Python version

```bash
# Verify Python version (requires >= 3.8)
python3 --version

# On macOS with Homebrew
brew install python@3.11

# On Ubuntu/Debian
sudo apt update
sudo apt install python3.11
```

### Insufficient permissions / Forbidden errors

```bash
# Error: "Forbidden: cannot list resource at cluster scope"
# Solution: specify a namespace
kdiff -c1 prod -c2 staging -n myapp

# Verify your RBAC permissions
kubectl auth can-i list deployments --all-namespaces
kubectl auth can-i list deployments -n myapp
```

### Connection errors / DNS failures

```bash
# Error: "no such host" or "dial tcp" errors
# Check:
1. VPN connection is active
2. Cluster API server is reachable
3. DNS resolution works: nslookup <cluster-hostname>
4. kubectl context is valid: kubectl config get-contexts
5. Try accessing cluster: kubectl --context <name> get nodes
```

---

## 🤝 Contributions

Suggestions welcome! Open an issue or submit a PR.

---

## 📝 License

MIT License - see [LICENSE](LICENSE)

---

**Version**: 1.1.0  
**Last updated**: January 2026
