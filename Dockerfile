# Classroom Optimizer Dockerfile
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy all files (needed for package metadata including README)
COPY . /app/

# Create virtual environment and install dependencies
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --no-dev

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . /app/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN useradd -m -u 1000 optimizer && \
    chown -R optimizer:optimizer /app

USER optimizer

# Expose port
EXPOSE 7070

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 7070)); s.close()"

# Run the application
CMD ["adk", "web", ".", "--host", "0.0.0.0", "--port", "7070"]

