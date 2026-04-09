# Memvid swarm bridge

The Python package talks to **Memvid** through a small Rust binary so you do not need Python–Rust FFI to get a vertical slice working.

## Build

```bash
cd packages/memvid-swarm-bridge
cargo build --release
```

On Windows the binary is `target/release/memvid-swarm-bridge.exe`.

## Configure

Set either:

- `MEMVID_SWARM_BRIDGE` to the full path of the binary, or
- add the binary directory to `PATH` so `memvid-swarm-bridge` resolves.

## Use from Python

```python
from pathlib import Path
from techtide_swarm import MemoryManager

mem = MemoryManager(memvid_path=Path(".swarm/layer-research.mv2"))
mem.share(
    from_agent="research-001",
    to_agent="sales-001",
    key="lead/acme",
    content="Acme is evaluating us Q2.",
)
```

If the bridge is missing, `MemoryManager` still works with `.swarm/topics/` only.

## Verify integrity

```bash
memvid-swarm-bridge verify path/to/file.mv2
memvid-swarm-bridge verify path/to/file.mv2 --deep
```

JSON output matches Memvid `VerificationReport` (see upstream docs).
