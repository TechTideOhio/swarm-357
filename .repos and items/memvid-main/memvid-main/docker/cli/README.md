# Memvid CLI Docker Image

AI memory CLI with crash-safe, single-file storage and semantic search.

## Quick Start

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

## Basic Commands

```bash
# Show help
docker run --rm memvid/cli

# Show version
docker run --rm memvid/cli --version

# Create a memory file (mount local directory)
docker run --rm -v $(pwd):/data memvid/cli create my-memory.mv2

# Ingest a document
docker run --rm -v $(pwd):/data memvid/cli put my-memory.mv2 --input document.pdf

# Search the memory
docker run --rm -v $(pwd):/data memvid/cli find my-memory.mv2 --query "search term"

# Ask questions (requires API key for LLM)
docker run --rm -v $(pwd):/data \
  -e OPENAI_API_KEY="sk-..." \
  memvid/cli ask my-memory.mv2 "What is this about?" -m openai

# View stats
docker run --rm -v $(pwd):/data memvid/cli stats my-memory.mv2
```

## With API Keys

```bash
# Pass Memvid API key for cloud features
docker run --rm -v $(pwd):/data \
  -e MEMVID_API_KEY="mv2_..." \
  -e OPENAI_API_KEY="sk-..." \
  memvid/cli ask my-memory.mv2 "your question"
```

## Shell Alias (Recommended)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias memvid='docker run --rm -v $(pwd):/data -e MEMVID_API_KEY -e OPENAI_API_KEY memvid/cli'
```

Then use normally:

```bash
memvid create my-memory.mv2
memvid put my-memory.mv2 --input docs/
memvid find my-memory.mv2 --query "hello"
```

## Docker Compose Example

```yaml
version: '3.8'
services:
  memvid:
    image: memvid/cli:latest
    volumes:
      - ./data:/data
    environment:
      - MEMVID_API_KEY=${MEMVID_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    entrypoint: ["memvid"]
    command: ["stats", "my-memory.mv2"]
```

## Features

- Single-file `.mv2` storage
- Semantic + lexical search
- RAG question answering
- PDF, DOCX, images, audio support

## Links

- Website: https://memvid.com
- Docs: https://docs.memvid.com
- GitHub: https://github.com/memvid/memvid
