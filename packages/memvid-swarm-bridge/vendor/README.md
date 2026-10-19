# Security dependency patches

Published memvid-core2.0.140 and Tantivy0.25.0 constrain PDF, XML, ZIP and LRU dependencies to vulnerable versions. These registry sources preserve upstream features, index format, license metadata and included license files. Normalized manifest bounds now select lopdf0.42, pdf-extract0.12.1, lru0.18.2+, Calamine0.37, quick-xml0.42 and ZIP9.0.5+.

Five Memvid reader files adapt the modern document APIs. DOCX/PPTX aggregate text and entity-reference events before unescaping, preserving named/numeric references and inline runs. Excel dates/durations retain numeric serial values through ExcelDateTime.as_f64. The synthetic PII-test key uses compile-time concat with identical runtime bytes and assertions, avoiding a false secret-scanner match. No runtime feature or validation gate is disabled.

`provenance.json` records original archive URLs and SHA-256 checksums. `source-patches.json` records original and migrated hashes for the five reader files. Run `python scripts/verify_bridge_vendor.py` from the repository root: CI verifies every file against original archives, the explicit manifest/fixture substitutions, and the reviewed reader hashes. Review the Git diff when updating these hashes. The root bridge lock is authoritative; upstream crate lockfiles and registry VCS packaging metadata are omitted because these are path dependencies.

Builds require Rust1.88 or newer (previously1.85). Regression coverage includes PDF, DOCX/PPTX entities and whitespace, XLS/XLSX numeric/boolean/date/duration values and shared strings, spreadsheet format/merge metadata, and existing .mv2 corpus compatibility. Calamine requires standard OOXML root relationships; malformed archives missing `_rels/.rels` retain the existing extractor fallback path.

Remove patches when maintained parent releases support these dependencies, after repeating document ingestion and bidirectional corpus compatibility tests. The migrated lock has zero RustSec vulnerability entries; bincode and ttf-parser unmaintained notices remain visible.
