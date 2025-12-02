# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Create virtual environment using uv
RUN uv venv /opt/venv

# Copy project files for dependency installation
COPY pyproject.toml README.md ./

# Install dependencies using uv
RUN uv pip install --python=/opt/venv/bin/python --no-cache .

# =============================================================================
# Stage 2: Production
# =============================================================================
FROM python:3.12-slim AS production

# Labels
LABEL org.opencontainers.image.title="Flexibilizador Service" \
    org.opencontainers.image.description="REST API for applying flexibilizations to DECOMP executions" \
    org.opencontainers.image.version="2.0.0" \
    org.opencontainers.image.vendor="HPC Team"

# Create non-root user
RUN groupadd -r -g 1000 app && useradd -r -u 1000 -g app app

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app main.py ./

# Create temp directory with correct permissions
RUN mkdir -p /tmp/flexibilizador && chown app:app /tmp/flexibilizador

# Set environment variables
ENV HOST=0.0.0.0 \
    PORT=8000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TEMP_DIR=/tmp/flexibilizador

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live')" || exit 1

# Run application with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
