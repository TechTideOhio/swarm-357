# Multi-stage Dockerfile for Memvid Core (Rust Library)
# Build stage
FROM rust:1.92-slim-trixie AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for better caching
COPY Cargo.toml Cargo.lock ./
COPY rust-toolchain.toml ./

# Create a dummy src/lib.rs to build dependencies
RUN mkdir -p src && \
    echo "// Dummy file for dependency building" > src/lib.rs && \
    cargo build --release --features lex,pdf_extract && \
    rm -rf src

# Copy source code
COPY src ./src
COPY examples ./examples
COPY tests ./tests

# Build the library with default features
RUN cargo build --release --features lex,pdf_extract

# Runtime stage - minimal image for running examples/tests
FROM debian:trixie-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the built artifacts from builder
COPY --from=builder /app/target/release/examples ./examples
COPY --from=builder /app/target/release/deps ./deps
COPY --from=builder /app/target/release/libmemvid_core*.rlib ./lib/

# Set environment variables
ENV RUST_LOG=info
ENV PATH="/app/examples:${PATH}"

# Default command
CMD ["/bin/bash"]
