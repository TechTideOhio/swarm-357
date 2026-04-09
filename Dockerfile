# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build tools
RUN pip install --no-cache-dir hatchling

# Copy package source and runtime assets
COPY packages/techtide-swarm/ ./packages/techtide-swarm/
COPY config/ ./config/
COPY templates/ ./templates/

# Install the package into a prefix
RUN pip install --no-cache-dir --prefix=/install \
    "./packages/techtide-swarm"

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="TechTide Swarm 357 API"
LABEL org.opencontainers.image.description="357 Claude AI agents — HTTP API"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local
# Copy runtime assets
COPY --from=builder /build/config ./config
COPY --from=builder /build/templates ./templates

# Create a non-root user
RUN adduser --disabled-password --gecos "" swarm
USER swarm

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Start the server
CMD ["uvicorn", "techtide_swarm.server:app", "--host", "0.0.0.0", "--port", "8000"]
