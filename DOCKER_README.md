# kdiff - Kubernetes Cluster Comparison Tool

![Docker Image Size](https://img.shields.io/docker/image-size/mabombo/kdiff)
![Docker Pulls](https://img.shields.io/docker/pulls/mabombo/kdiff)

kdiff is a powerful command-line tool for comparing Kubernetes resources between two clusters or contexts. It generates detailed HTML reports showing differences in deployments, configmaps, secrets, and other resources.

## Features

- 🔍 **Intelligent Diff Detection** - Normalizes and compares Kubernetes resources
- 📊 **Interactive HTML Reports** - Beautiful, interactive reports with color-coded diffs
- 🎯 **Resource Filtering** - Compare specific namespaces and resource types
- 🚀 **Fast & Lightweight** - Alpine-based image (~182MB)
- 🔒 **Secure** - Runs as non-root user

## Quick Start

### Using Docker

```bash
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod-cluster -c2 staging-cluster -n myapp
```

### Using the Wrapper Script

For easier usage, download and use the `kdiff-docker` wrapper script:

```bash
# Make it executable
chmod +x kdiff-docker

# Run kdiff
./kdiff-docker -c1 prod-cluster -c2 staging-cluster -n myapp
```

## Usage Examples

### Compare entire namespaces
```bash
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 production -c2 staging -n myapp
```

### Compare specific resource types
```bash
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp \
  --include-resource-types deployment,configmap
```

### Include services and ingress resources
```bash
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp \
  --include-services-ingress
```

### Show full metadata in diffs
```bash
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  mabombo/kdiff:latest \
  -c1 prod -c2 staging -n myapp \
  --show-metadata
```

## Configuration

### Volume Mounts

- **kubeconfig**: Mount your kubeconfig file to `/home/kdiff/.kube/config:ro` (read-only)
- **Output**: Mount a local directory to `/app/kdiff_output` to persist reports

### Environment Variables

- `KUBECONFIG`: Path to kubeconfig file inside container (default: `/home/kdiff/.kube/config`)
- `PYTHONUNBUFFERED=1`: Ensures real-time output

## Command-Line Options

```
usage: kdiff [-h] -c1 C1 -c2 C2 [-r R] [-n N] [-o O] [-f FORMAT]
             [--include-volatile] [--include-services-ingress]
             [--include-resource-types TYPES] [--exclude-resources RESOURCES]
             [--show-metadata]

Required arguments:
  -c1 C1                First Kubernetes context
  -c2 C2                Second Kubernetes context

Optional arguments:
  -n N                  Namespace to compare
  -r R                  Resource type to compare
  -o O                  Output directory (default: kdiff_output)
  -f FORMAT             Output format: html, json, md (default: html)
  --include-volatile    Include volatile fields in comparison
  --include-services-ingress
                        Include service and ingress resources
  --include-resource-types TYPES
                        Comma-separated list of resource types
  --exclude-resources RESOURCES
                        Comma-separated list of resources to exclude
  --show-metadata       Show full metadata in diffs
```

## Output

Reports are generated in `/app/kdiff_output/latest/`:

- `diff-details.html` - Interactive HTML report with visualizations
- `summary.json` - JSON summary of all differences
- `diff-details.json` - Detailed JSON of all diffs
- `diffs/` - Individual diff files per resource

## Building from Source

```bash
# Clone the repository
git clone https://github.com/mabombo/kdiff.git
cd kdiff

# Build the Docker image
docker build -t kdiff:latest .

# Run
docker run --rm -it \
  -v ~/.kube/config:/home/kdiff/.kube/config:ro \
  -v $(pwd)/kdiff_output:/app/kdiff_output \
  kdiff:latest -c1 context1 -c2 context2 -n namespace
```

## Requirements

- Docker
- Kubernetes clusters with configured contexts in kubeconfig
- kubectl contexts must be accessible from the container

## Security

- Image runs as non-root user (uid 1000, gid 1000)
- kubeconfig is mounted read-only
- Alpine-based for minimal attack surface
- No external dependencies beyond Python stdlib

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/mabombo/kdiff
- Issues: https://github.com/mabombo/kdiff/issues

## Version

Current version: 1.0.0
