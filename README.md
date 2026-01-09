<div align="center">
  <img src="images/kdiff_logo_3.png" alt="kdiff logo" width="300"/>
</div>

# kdiff - Kubernetes Resource Comparison Tool

kdiff is a Python tool for comparing Kubernetes configurations between two clusters or across multiple namespaces within the same cluster. It identifies missing, different, or cluster-specific resources and generates interactive HTML reports with detailed diff visualization.

## Features

- Intelligent normalization: removes volatile fields (uid, resourceVersion, timestamps)
- Smart ConfigMap diff: shows only modified lines instead of entire content
- Environment variables compared by name, not array position
- Interactive HTML reports with collapsible sections and dual-pane diff viewer
- Side-by-side comparison with inline character-level highlighting
- Filter capabilities for added/removed/modified lines
- Automated detection and disabling of non-applicable filters
- Support for multiple resource types (Deployment, ConfigMap, Secret, etc.)

## Requirements

- Python 3.10 or higher
- kubectl configured with access to the clusters to compare
- Operating System: macOS, Linux, WSL on Windows

## Installation

### Local Installation

#### Method 1: Automatic (recommended)

```bash
git clone <repo-url>
cd kdiff

# Install in ~/.local (no sudo)
PREFIX=$HOME/.local ./install.sh

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
kdiff --help
```

#### Method 2: pip (with virtual environment)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
kdiff --help
```

#### Method 3: Direct execution

```bash
./bin/kdiff --help
```

### Docker Installation

```bash
# Pull from Docker Hub
docker pull mabombo/kdiff:latest

# Run with kubeconfig mount
docker run --rm \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  --network host \
  mabombo/kdiff:latest \
  -c1 CONTEXT1 -c2 CONTEXT2 -n NAMESPACE
```

## Usage

### Basic Syntax

**Two-cluster comparison:**
```bash
kdiff -c1 CONTEXT1 -c2 CONTEXT2 [OPTIONS]
```

**Single-cluster namespace comparison:**
```bash
kdiff -c CONTEXT --namespaces NS1,NS2[,NS3...] [OPTIONS]
```

### Parameters

**Required (choose one mode):**

*Two-cluster mode:*
- `-c1 CONTEXT1` : First Kubernetes context
- `-c2 CONTEXT2` : Second Kubernetes context

*Single-cluster mode:*
- `-c CONTEXT` : Kubernetes context
- `-n NS1,NS2,...` : Comma-separated list of namespaces to compare (minimum 2)

**Optional:**
- `-n NAMESPACE(S)` : Single namespace or comma-separated list. For single-cluster mode, minimum 2 required. For two-cluster mode, optional (default: all namespaces)
- `-r RESOURCES` : Comma-separated resource types to compare
- `-o OUTPUT_DIR` : Output directory (default: ./kdiff_output/latest)
- `-f FORMAT` : Output format: text (default) or json
- `--show-metadata` : Include labels and annotations in comparison
- `--include-services-ingress` : Include Service and Ingress resources
- `--include-resource-types TYPES` : Specify resource types to include
- `--exclude-resources TYPES` : Exclude specific resource types
- `--include-volatile` : Include volatile resources (Pod, ReplicaSet)

### Examples

**Two-cluster comparison:**
```bash
# Compare all resources in a namespace between two clusters
kdiff -c1 prod-cluster -c2 staging-cluster -n myapp

# Compare multiple namespaces between two clusters
kdiff -c1 prod-cluster -c2 staging-cluster --namespaces ns1,ns2,ns3

# Compare only specific resource types
kdiff -c1 prod -c2 dev -r deployment,configmap -n myapp

# Generate JSON output
kdiff -c1 prod -c2 staging -f json -o ./reports

# Include metadata for detailed comparison
kdiff -c1 prod -c2 staging --show-metadata

# Exclude specific resources
kdiff -c1 prod -c2 staging --exclude-resources secret,configmap
```

**Single-cluster namespace comparison:**
```bash
# Compare resources between two namespaces in the same cluster
kdiff -c prod-cluster -n namespace1,namespace2

# Compare multiple namespaces (pairwise comparison)
kdiff -c prod-cluster -n ns1,ns2,ns3

# Compare only configmaps between namespaces
kdiff -c prod-cluster -n dev,staging,prod -r configmap

# Include metadata in namespace comparison
kdiff -c prod-cluster -n ns1,ns2 --show-metadata
```

## Output Structure

**Two-cluster mode:**
```
kdiff_output/
└── latest/
    ├── summary.json              # Machine-readable summary
    ├── diff-details.html         # Interactive HTML report
    ├── diff-details.json         # Detailed diff data
    ├── diffs/                    # Individual diff files
    ├── <CONTEXT1>/              # Normalized resources from context 1
    └── <CONTEXT2>/              # Normalized resources from context 2
```

**Single-cluster namespace comparison:**
```
kdiff_output/
└── latest/
    ├── ns1_vs_ns2/              # Comparison between ns1 and ns2
    │   ├── summary.json         # Comparison summary
    │   ├── diff-details.html    # HTML report for this pair
    │   ├── diff-details.json    # Detailed diff data
    │   ├── diffs/               # Individual diff files
    │   ├── <CONTEXT>_ns1/       # Resources from namespace 1
    │   └── <CONTEXT>_ns2/       # Resources from namespace 2
    ├── ns1_vs_ns3/              # Comparison between ns1 and ns3
    └── ns2_vs_ns3/              # Comparison between ns2 and ns3
```

The `latest/` directory is automatically cleaned on each execution.

## HTML Report Features

The interactive HTML report (`diff-details.html`) provides:

- Statistics dashboard with resource counts
- Collapsible sections grouped by resource type
- Two diff viewing modes:
  - Standard unified diff view
  - Side-by-side dual-pane comparison
- Character-level highlighting for modified lines
- Interactive filters for added/removed/modified/unchanged lines
- Zoom controls for detailed inspection
- Synchronized scrolling between panes

## Resource Types Compared

Default resources:
- Deployment, StatefulSet, DaemonSet
- ConfigMap, Secret
- PersistentVolumeClaim
- ServiceAccount, Role, RoleBinding
- HorizontalPodAutoscaler
- CronJob, Job

Optional (use `--include-services-ingress`):
- Service, Ingress

Volatile (use `--include-volatile`):
- Pod, ReplicaSet

## Uninstallation

```bash
# Local installation (~/.local)
rm -rf ~/.local/lib/kdiff
rm ~/.local/bin/kdiff

# System installation (/usr/local)
sudo rm -rf /usr/local/lib/kdiff
sudo rm /usr/local/bin/kdiff

# pip installation
pip uninstall kdiff
```

## Troubleshooting

**Command not found:**
```bash
# Verify PATH
echo $PATH | grep "$HOME/.local/bin"

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

**kubectl not found:**
```bash
# Verify kubectl
which kubectl

# Install kubectl
# macOS: brew install kubectl
# Linux: curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

**Permission errors:**
```bash
# Specify namespace instead of cluster-wide
kdiff -c1 prod -c2 staging -n myapp

# Verify permissions
kubectl auth can-i list deployments -n myapp
```

## Testing

```bash
cd kdiff
bash tests/run_tests.sh
```

## Additional Documentation

- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Detailed installation guide
- [docs/diff_details.md](docs/diff_details.md) - HTML report documentation
- [DOCKER_README.md](DOCKER_README.md) - Docker usage guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## License

MIT License - see [LICENSE](LICENSE)

## Version

Current version: 1.5.2

