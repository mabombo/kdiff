#!/bin/bash
set -e

# Entrypoint script for kdiff Docker container
# Sets up environment and provides helpful error messages if needed

# Set HOME to /home/kdiff if it's not already set correctly
# This is needed when running with --user flag which doesn't set HOME
if [ "$HOME" = "/" ] || [ -z "$HOME" ]; then
    export HOME=/home/kdiff
fi

KUBECONFIG_PATH="${KUBECONFIG:-$HOME/.kube/config}"

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
