# Testing Memvid CLI Docker Image

## Quick Test

### 1. Build the Image

```bash
cd docker/cli
docker build -t memvid/cli:test .
```

### 2. Test Basic Commands

```bash
# Test help command
docker run --rm memvid/cli:test --help

# Test version (if available)
docker run --rm memvid/cli:test --version
```

### 3. Test with Volume Mount

```bash
# Create a test directory
mkdir -p /tmp/memvid-test
cd /tmp/memvid-test

# Create a test document
echo "This is a test document about AI and machine learning." > test.txt

# Create a memory file
docker run --rm \
  -v $(pwd):/data \
  memvid/cli:test create test-memory.mv2

# Add the document
docker run --rm \
  -v $(pwd):/data \
  memvid/cli:test put test-memory.mv2 --input test.txt

# Search the memory
docker run --rm \
  -v $(pwd):/data \
  memvid/cli:test find test-memory.mv2 --query "AI"

# View stats
docker run --rm \
  -v $(pwd):/data \
  memvid/cli:test stats test-memory.mv2
```

### 4. Test with API Keys (if needed)

```bash
docker run --rm \
  -v $(pwd):/data \
  -e OPENAI_API_KEY="sk-..." \
  memvid/cli:test ask test-memory.mv2 "What is this about?" -m openai
```

## Automated Testing

Run the test script:

```bash
cd docker/cli
./test.sh
```

## Multi-Architecture Testing

To test multi-arch builds locally (requires buildx):

```bash
# Create builder
docker buildx create --name memvid-builder --use

# Build for specific platform
docker buildx build \
  --platform linux/amd64 \
  --tag memvid/cli:test-amd64 \
  --load \
  .

# Test the amd64 image
docker run --rm memvid/cli:test-amd64 --help
```

## Troubleshooting

### Image not found
Make sure you've built the image:
```bash
docker build -t memvid/cli:test docker/cli
```

### Permission errors
Ensure Docker has permission to access the mounted directory:
```bash
chmod 755 /path/to/your/directory
```

### CLI not found
Verify the npm package exists:
```bash
docker run --rm memvid/cli:test which memvid
```
