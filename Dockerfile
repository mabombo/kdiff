# Use minimal Alpine Linux with Python
FROM python:3.12-alpine

LABEL maintainer="Mauro Casiraghi"
LABEL description="kdiff - Kubernetes cluster comparison tool"
LABEL version="1.5.5"

# Upgrade pip to latest version to fix security vulnerabilities
RUN pip install --no-cache-dir --upgrade pip

# Install kubectl and runtime dependencies
# TARGETARCH is automatically set by buildx for multi-platform builds
ARG TARGETARCH
RUN apk add --no-cache \
    curl \
    ca-certificates \
    bash \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${TARGETARCH}/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && kubectl version --client

# Create non-root user for security with home directory
RUN addgroup -g 1000 kdiff && \
    adduser -D -u 1000 -G kdiff -h /home/kdiff kdiff && \
    mkdir -p /home/kdiff/.kube && \
    chown -R kdiff:kdiff /home/kdiff

# Set working directory
WORKDIR /app

# Copy kdiff files
COPY --chown=kdiff:kdiff bin/kdiff /usr/local/bin/kdiff
COPY --chown=kdiff:kdiff lib/ /usr/local/lib/
COPY --chown=kdiff:kdiff docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Make kdiff and entrypoint executable
RUN chmod +x /usr/local/bin/kdiff && \
    chmod +x /usr/local/bin/docker-entrypoint.sh

# Add lib to Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Create output directory with correct permissions
RUN mkdir -p /app/kdiff_output && \
    chown -R kdiff:kdiff /app

# Switch to non-root user
USER kdiff

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV KDIFF_OUTPUT_DIR=/app/kdiff_output

# Volume for output and kubeconfig
VOLUME ["/app/kdiff_output", "/home/kdiff/.kube"]

# Use custom entrypoint to handle permission issues
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["--help"]
