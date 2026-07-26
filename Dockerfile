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
    "./packages/techtide-swarm[supabase]"

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="TechTide Swarm 357 API"
LABEL org.opencontainers.image.description="357 Claude AI agents, HTTP API"
LABEL org.opencontainers.image.source="https://github.com/TechTideOhio/swarm-357"
LABEL org.opencontainers.image.url="https://swarm357fe.up.railway.app"
LABEL org.opencontainers.image.documentation="https://swarm357fe.up.railway.app/docs"
LABEL org.opencontainers.image.licenses="Apache-2.0"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local
# Copy runtime assets
COPY --from=builder /build/config ./config
COPY --from=builder /build/templates ./templates

# Create a non-root user with a writable runtime directory
RUN adduser --disabled-password --gecos "" swarm \
    && mkdir -p /app/.swarm /tmp/swarm357 \
    && chown -R swarm:swarm /app/.swarm /tmp/swarm357
ENV SWARM_CHECKPOINT_DIR=/app/.swarm
USER swarm

# Expose the API port
EXPOSE 8000

ENV PORT=8000
ENV SWARM_CONFIG_PATH=/app/config/swarm-compact.yaml
ENV SWARM_SERVER_MODE=1

# Health check (uses PORT when set by the platform)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ.get('PORT','8000')}/api/health\")"

# Start the server (Railway injects PORT)
CMD ["sh", "-c", "uvicorn techtide_swarm.server:app --host 0.0.0.0 --port ${PORT:-8000}"]
