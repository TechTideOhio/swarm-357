# Memvid CLI Docker Image
FROM ubuntu:24.04

LABEL org.opencontainers.image.title="Memvid CLI"
LABEL org.opencontainers.image.description="AI memory CLI with semantic search"
LABEL org.opencontainers.image.url="https://memvid.com"
LABEL org.opencontainers.image.source="https://github.com/memvid/memvid"
LABEL org.opencontainers.image.vendor="Memvid"
LABEL org.opencontainers.image.version="2.0.131"

# Install system deps + Node.js 24
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libssl3 \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install memvid CLI (pinned version)
RUN npm install -g memvid-cli@latest \
    && npm cache clean --force

# Create non-root user (recommended)
RUN useradd -m memvid
USER memvid

# Working directory for memory files
WORKDIR /data

# Entrypoint
ENTRYPOINT ["memvid"]
CMD ["--help"]
