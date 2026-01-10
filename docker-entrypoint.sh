#!/bin/bash
set -e

# Entrypoint script for kdiff Docker container
# Handles kubeconfig permission issues automatically

KUBECONFIG_PATH="${KUBECONFIG:-/home/kdiff/.kube/config}"
TEMP_KUBECONFIG="/tmp/kubeconfig"

# Check if kubeconfig exists and is readable
if [ -f "$KUBECONFIG_PATH" ]; then
    # Try to read the file
    if ! cat "$KUBECONFIG_PATH" > /dev/null 2>&1; then
        echo "[INFO] kubeconfig not readable, creating temporary copy with correct permissions..."
        
        # Create temp directory if it doesn't exist
        mkdir -p /tmp
        
        # Try to copy with cat (works even with permission issues in some cases)
        if cat "$KUBECONFIG_PATH" > "$TEMP_KUBECONFIG" 2>/dev/null; then
            chmod 600 "$TEMP_KUBECONFIG"
            export KUBECONFIG="$TEMP_KUBECONFIG"
            echo "[INFO] Using temporary kubeconfig at $TEMP_KUBECONFIG"
        else
            echo "[ERROR] Unable to read kubeconfig at $KUBECONFIG_PATH"
            echo "[ERROR] Please ensure the file has appropriate permissions (chmod 644)"
            echo ""
            echo "Solutions:"
            echo "  1. chmod 644 ~/.kube/config"
            echo "  2. Run container as your user: --user \$(id -u):\$(id -g)"
            exit 1
        fi
    else
        echo "[INFO] Using kubeconfig at $KUBECONFIG_PATH"
    fi
else
    echo "[WARNING] kubeconfig not found at $KUBECONFIG_PATH"
    echo "[WARNING] kubectl commands may fail"
fi

# Execute kdiff with all arguments
exec kdiff "$@"
