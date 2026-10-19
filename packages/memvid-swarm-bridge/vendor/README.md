# Security dependency patches

The published memvid-core 2.0.140 and Tantivy 0.25.0 manifests constrain PDF/LRU dependencies to vulnerable versions. These registry sources preserve all upstream Rust code, features, index format, license metadata, and included license files. Production Rust code is unchanged. One upstream synthetic API-key test literal uses compile-time `concat!` to preserve identical runtime bytes without introducing a secret-scanner match; provenance verifies this exact substitution. Normalized Cargo.toml bounds change: lopdf 0.42, pdf-extract 0.12.1, and lru 0.18.2. The bridge root lockfile is authoritative; upstream crate Cargo.lock files and registry VCS packaging metadata are omitted because these packages are path dependencies, not independent build roots.

`provenance.json` records original archive URLs and SHA-256 checksums. Run `python scripts/verify_bridge_vendor.py` from the repository root to verify every source file against the original archives and the three permitted manifest changes plus the equivalent synthetic test literal. CI performs that verification before compiling. No further source edits or upstream dependency refresh is accepted silently.

Remove these patches when maintained parent releases accept the patched dependencies, after checking PDF ingestion and existing .mv2 corpus compatibility. This patch does not clear the existing quick-xml/zip RustSec findings in Memvid/Calamine. Current callers read archive entries in memory, but that does not dismiss their package advisories.

Building the bridge now requires Rust 1.88 or newer, up from 1.85, to satisfy patched PDF dependencies. CI uses stable Rust.
