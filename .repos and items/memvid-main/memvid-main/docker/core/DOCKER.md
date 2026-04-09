# Docker Setup for Memvid Core

This document describes how to use Docker with the Memvid Core Rust library.

## Quick Start

### Development Environment

```bash
# From project root or docker/core directory
cd docker/core
docker-compose up -d dev

# Enter the container
docker-compose exec dev bash

# Inside container, you can run:
cargo build
cargo test
cargo run --example basic_usage
```

### Run Tests

```bash
# Run all tests
cd docker/core
docker-compose run --rm test

# Or build test image manually (from project root)
docker build -f docker/core/Dockerfile.test -t memvid-test .
docker run --rm memvid-test
```

### Build Release

```bash
# Build release version
cd docker/core
docker-compose run --rm build

# Or build manually (from project root)
docker build -f docker/core/Dockerfile -t memvid-core:latest .
```

## Docker Images

### 1. Development Image (`Dockerfile.dev`)

Full development environment with all tools:

```bash
# From project root
docker build -f docker/core/Dockerfile.dev -t memvid-dev .
docker run -it --rm -v $(pwd):/app memvid-dev bash
```

**Features:**
- Rust toolchain 1.92
- All build dependencies
- Cargo watch (optional)
- Volume mounting for live development

### 2. Test Image (`Dockerfile.test`)

Optimized for running tests:

```bash
# From project root
docker build -f docker/core/Dockerfile.test -t memvid-test .
docker run --rm memvid-test
```

**Features:**
- Rust toolchain 1.92
- Test dependencies
- Runs tests automatically

### 3. Production Build (`Dockerfile`)

Multi-stage build for optimized production image:

```bash
# From project root
docker build -f docker/core/Dockerfile -t memvid-core:latest .
```

**Features:**
- Multi-stage build (smaller final image)
- Only runtime dependencies
- Optimized release build

## Docker Compose

### Services

- **`dev`** - Development environment with live code mounting
- **`test`** - Test runner
- **`build`** - Release builder

### Usage

```bash
# Start development environment
docker-compose up -d dev

# Run tests
docker-compose run --rm test

# Build release
docker-compose run --rm build

# Stop all services
docker-compose down
```

## Examples

### Run Examples in Docker

```bash
# Development container
docker-compose exec dev cargo run --example basic_usage

# With features
docker-compose exec dev cargo run --example pdf_ingestion --features lex,pdf_extract
```

### Memory-Constrained Testing

Test OOM prevention with memory limits:

```bash
# Test with memory limit (for OOM testing)
docker run --rm --memory=150m --memory-swap=150m \
  -v $(pwd):/app \
  memvid-test cargo test --features encryption --test encryption_capsule
```

### Build with Specific Features

```bash
# Build with all features
docker-compose exec dev cargo build --release --all-features

# Build with specific features
docker-compose exec dev cargo build --release --features lex,vec,encryption
```

## Volume Mounts

The docker-compose setup uses volumes for:
- **Source code** - Live mounting for development
- **Cargo cache** - Speeds up builds
- **Target cache** - Preserves build artifacts

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t memvid-core:test .
      - name: Run tests
        run: docker run --rm memvid-core:test cargo test
```

## Troubleshooting

### Build Fails

```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache
```

### Permission Issues

```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

### Out of Memory

```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use memory limits in docker run:
docker run --memory=2g --memory-swap=2g ...
```

## Best Practices

1. **Use docker-compose** for development
2. **Cache volumes** for faster builds
3. **Multi-stage builds** for production
4. **Test in containers** to match CI/CD environment
5. **Use .dockerignore** to exclude unnecessary files

## Related

- [CLI Docker Setup](../cli/README.md)
- [Docker Overview](../README.md)
- [Main Project README](../../README.md)
- [Contributing Guide](../../CONTRIBUTING.md)
