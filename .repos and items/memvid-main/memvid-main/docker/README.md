# Docker Images for Memvid

This directory contains Docker configurations for Memvid components.

## Available Images

### Memvid Core (`core/`)

The Memvid Core Docker images provide containerized Rust development, testing, and build environments for the `memvid-core` library.

**Quick Start:**
```bash
# Development environment
cd core
docker-compose up -d dev
docker-compose exec dev bash

# Run tests
docker-compose run --rm test

# Build release
docker-compose run --rm build
```

For detailed usage, see [core/README.md](core/README.md).

### Memvid CLI (`cli/`)

The Memvid CLI Docker image provides a containerized version of the `memvid-cli` tool, allowing you to run Memvid commands without installing Node.js or dealing with platform-specific binaries.

**Quick Start:**

```bash
# Pull the image
docker pull memvid/cli

# Create a memory
docker run --rm -v $(pwd):/data memvid/cli create my-memory.mv2

# Add documents
docker run --rm -v $(pwd):/data memvid/cli put my-memory.mv2 --input doc.pdf

# Search
docker run --rm -v $(pwd):/data memvid/cli find my-memory.mv2 --query "search"
```

For detailed usage instructions, examples, and Docker Compose configurations, see [cli/README.md](cli/README.md).

## Building Images

### Build CLI Image Locally

```bash
cd cli
docker build -t memvid/cli:test .
```

## Publishing

Docker images are automatically built and published to Docker Hub via GitHub Actions when tags are pushed. See `.github/workflows/docker-release.yml` for the CI/CD configuration.

**Image Registry:**
- Docker Hub: `memvid/cli`
- Tags: `latest`, `2.0.129`, and version-specific tags

## Architecture Support

The CLI image supports multi-architecture builds:
- `linux/amd64`
- `linux/arm64`

## Security

The CLI image runs as a non-root user (`memvid`) for improved security. When mounting volumes, ensure your host directories have appropriate permissions.

## Links

- [Core Documentation](core/README.md)
- [CLI Documentation](cli/README.md)
- [CLI Testing Guide](cli/TESTING.md)
- [Main Project README](../README.md)
- [Memvid Documentation](https://docs.memvid.com)
