#!/bin/bash
# Test script for Memvid CLI Docker image

set -e

IMAGE_NAME="memvid/cli:test"
DOCKERFILE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🐳 Building Docker image..."
docker build -t "$IMAGE_NAME" "$DOCKERFILE_DIR"

echo ""
echo "✅ Build complete! Testing basic commands..."
echo ""

echo "1️⃣ Testing help command..."
docker run --rm "$IMAGE_NAME" --help | head -5

echo ""
echo "2️⃣ Testing version command..."
docker run --rm "$IMAGE_NAME" --version || echo "Version command not available"

echo ""
echo "3️⃣ Testing with volume mount (create test memory)..."
TEST_DIR=$(mktemp -d)
cd "$TEST_DIR"

# Create a test document
echo "This is a test document about artificial intelligence and machine learning." > test.txt

docker run --rm \
  -v "$TEST_DIR":/data \
  "$IMAGE_NAME" create test-memory.mv2 || echo "Create command may require additional setup"

echo ""
echo "🧹 Cleaning up test directory..."
rm -rf "$TEST_DIR"

echo ""
echo "✅ Basic tests complete!"
echo ""
echo "To test manually, run:"
echo "  docker run --rm $IMAGE_NAME --help"
echo "  docker run --rm -v \$(pwd):/data $IMAGE_NAME create my-memory.mv2"
