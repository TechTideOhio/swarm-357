# Memvid Integration Design

## Current state

The integration is **working as a vertical slice**:

1. `MemoryManager` (memory.py) optionally wraps `MemvidBridge` (memvid_bridge.py)
2. `MemvidBridge` invokes `memvid-swarm-bridge` (Rust CLI) via subprocess
3. Rust CLI links against `memvid-core` (in-tree at `.repos and items/memvid-main/memvid-main/`)
4. Operations: `create`, `put`, `search`, `verify`

## Bridge protocol

```
Python                          Rust CLI                    memvid-core
------                          --------                    -----------
MemvidBridge.create(path)  -->  create <path>          -->  Memvid::create()
MemvidBridge.put(...)      -->  put <path> --uri --title    Memvid::open() + put_bytes_with_options() + commit()
                                stdin: body bytes
MemvidBridge.search(q, k)  -->  search <path> <q> --top-k  Memvid::open() + search(SearchRequest)
                                stdout: JSON SearchResponse
MemvidBridge.verify(deep)  -->  verify <path> [--deep]      Memvid::verify()
                                stdout: JSON VerificationReport
```

## Per-layer vs per-agent .mv2

**Recommendation: per-layer by default.**

- 6 layers + 1 management = 7 `.mv2` files
- Agents within a layer share memory naturally (sales agents share lead knowledge)
- Per-agent `.mv2` is an override for isolated agents (e.g., audit agent)
- Configuration: `memvid_path` in MemoryManager constructor

```python
# Per-layer (recommended)
mem = MemoryManager(memvid_path=Path(".swarm/layer-research.mv2"))

# Per-agent (override)
mem = MemoryManager(memvid_path=Path(".swarm/agents/audit-001.mv2"))
```

## Migration path: .swarm/ -> .mv2

`MemoryManager.migrate_flat_to_memvid(dest)` already implements bulk migration:

1. Reads all `.swarm/topics/*.json` files
2. Calls `bridge.put()` for each with `swarm://<key>` URI
3. Returns `{"status": "ok", "files_migrated": N, "mv2": path}` or skip if bridge unavailable

## Transaction boundaries

- Each `put()` calls `commit()` in the Rust CLI (one WAL flush per document)
- For bulk ingestion: consider a `put-batch` command that accepts NDJSON on stdin and commits once
- Memvid is synchronous; Python MemoryManager calls are blocking (acceptable for CLI use)

## Feature flags from upstream

Currently used: default features only (lex, pdf_extract, simd).

Future candidates:
- `vec` -- HNSW vector similarity search (requires embedding model)
- `encryption` -- AES-256-GCM for `.mv2e` files
- `replay` -- time-travel session replay
- `api_embed` -- OpenAI/Anthropic embeddings for vector search

## Failure modes

| Scenario | Behavior |
|----------|----------|
| Bridge binary missing | MemvidBridge.available returns False; MemoryManager falls back to flat files |
| .mv2 corrupted | search/put raise MemvidBridgeError; flat files unaffected |
| Bridge crashes mid-put | WAL ensures crash safety; next open recovers |
| Disk full | Rust returns error; Python surfaces MemvidBridgeError |
