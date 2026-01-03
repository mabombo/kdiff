# Use minimal Alpine Linux with Python
FROM python:3.12-alpine

LABEL maintainer="Mauro Casiraghi"
LABEL description="kdiff - Kubernetes cluster comparison tool"
LABEL version="1.0.0"

# Install kubectl and runtime dependencies
RUN apk add --no-cache \
    curl \
    ca-certificates \
    bash \
    && curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/ \
    && kubectl version --client

# Create non-root user for security
RUN addgroup -g 1000 kdiff && \
    adduser -D -u 1000 -G kdiff kdiff

# Set working directory
WORKDIR /app

# Copy kdiff files
COPY --chown=kdiff:kdiff bin/kdiff /usr/local/bin/kdiff
COPY --chown=kdiff:kdiff lib/ /app/lib/

# Make kdiff executable
RUN chmod +x /usr/local/bin/kdiff

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

# Default command shows help
ENTRYPOINT ["kdiff"]
CMD ["--help"]
