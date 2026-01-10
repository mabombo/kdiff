#!/bin/bash
set -e

# Entrypoint script for kdiff Docker container
# Sets up kubeconfig path and provides helpful error messages if needed

KUBECONFIG_PATH="${KUBECONFIG:-/home/kdiff/.kube/config}"

# Check if kubeconfig file exists
if [ -f "$KUBECONFIG_PATH" ]; then
    echo "[INFO] Using kubeconfig at $KUBECONFIG_PATH"
else
    echo "[WARNING] kubeconfig not found at $KUBECONFIG_PATH"
    echo "[WARNING] kubectl commands may fail"
    echo ""
    echo "Make sure you mounted the kubeconfig file:"
    echo "  -v ~/.kube/config:/home/kdiff/.kube/config:ro"
fi

# Execute kdiff with all arguments
# If there are permission issues, kubectl will report them directly
exec kdiff "$@"
