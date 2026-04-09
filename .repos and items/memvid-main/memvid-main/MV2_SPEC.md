# MV2 File Format Specification

Version 2.1

## Overview

MV2 is a single-file format for AI memory storage. Everything lives in one file: header, write-ahead log, data segments, search indices, and metadata. No sidecar files.

```
┌─────────────────────────────────────────────────────────────┐
│                        .mv2 FILE                            │
├─────────────────────────────────────────────────────────────┤
│ Header                 │ 4 KB                               │
├─────────────────────────────────────────────────────────────┤
│ Embedded WAL           │ 1-64 MB (capacity-dependent)       │
├─────────────────────────────────────────────────────────────┤
│ Data Segments          │ Variable                           │
│   - Frame payloads                                          │
│   - Compressed content                                      │
├─────────────────────────────────────────────────────────────┤
│ Lex Index Segment      │ Tantivy index (optional)           │
├─────────────────────────────────────────────────────────────┤
│ Vec Index Segment      │ HNSW vectors (optional)            │
├─────────────────────────────────────────────────────────────┤
│ Time Index Segment     │ Chronological ordering             │
├─────────────────────────────────────────────────────────────┤
│ TOC (Footer)           │ Segment catalog + checksums        │
└─────────────────────────────────────────────────────────────┘
```

## Header (4096 bytes)

The header occupies the first 4 KB of the file.

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 4 | `magic` | `MV2\0` (0x4D 0x56 0x32 0x00) |
| 4 | 2 | `version` | Format version (little-endian) |
| 6 | 1 | `spec_major` | Spec major version (2) |
| 7 | 1 | `spec_minor` | Spec minor version (1) |
| 8 | 8 | `footer_offset` | Byte offset to TOC |
| 16 | 8 | `wal_offset` | Byte offset to WAL (always 4096) |
| 24 | 8 | `wal_size` | WAL region size in bytes |
| 32 | 8 | `wal_checkpoint_pos` | Last checkpointed sequence |
| 40 | 8 | `wal_sequence` | Current WAL sequence number |
| 48 | 32 | `toc_checksum` | SHA-256 of TOC segment |
| 80 | 4016 | reserved | Zero-filled, reserved for future use |

All multi-byte integers are little-endian.

## Write-Ahead Log (WAL)

The embedded WAL provides crash recovery. It starts at byte 4096 and has a capacity determined by the file's target size:

| File Capacity | WAL Size |
|---------------|----------|
| < 100 MB | 1 MB |
| < 1 GB | 4 MB |
| < 10 GB | 16 MB |
| >= 10 GB | 64 MB |

### WAL Entry Format

```
┌──────────────────────────────────────┐
│ sequence    │ 8 bytes (u64 LE)       │
│ entry_type  │ 1 byte                 │
│ payload_len │ 4 bytes (u32 LE)       │
│ payload     │ variable               │
│ checksum    │ 4 bytes (CRC32)        │
└──────────────────────────────────────┘
```

Entry types:
- `0x01` - Frame append
- `0x02` - Frame update
- `0x03` - Frame delete (tombstone)
- `0x04` - Index update

### Checkpoint Behavior

- Checkpoint triggers at 75% WAL occupancy or every 1,000 transactions
- Checkpoint flushes WAL entries to data segments
- `seal()` forces immediate checkpoint
- Recovery replays entries with `sequence > wal_checkpoint_pos`

## Frame Structure

Each frame represents a single piece of content.

| Field | Type | Description |
|-------|------|-------------|
| `frame_id` | u64 | Unique identifier (monotonic) |
| `uri` | String | Hierarchical path (`mv2://path/to/doc`) |
| `title` | String? | Optional display title |
| `created_at` | u64 | Unix timestamp (seconds) |
| `encoding` | u8 | Content encoding (see below) |
| `payload` | bytes | Compressed content |
| `payload_checksum` | [u8; 32] | SHA-256 of uncompressed payload |
| `tags` | Map<String, String> | User-defined key-value pairs |
| `status` | u8 | 0=active, 1=tombstoned |

### Encoding Types

| Value | Name | Description |
|-------|------|-------------|
| 0 | Raw | Uncompressed bytes |
| 1 | Zstd | Zstandard compression |
| 2 | Lz4 | LZ4 compression |

## Data Segments

Frames are grouped into segments for efficient storage and retrieval.

### Segment Header

```
┌──────────────────────────────────────┐
│ magic         │ 4 bytes              │
│ version       │ 2 bytes              │
│ segment_type  │ 1 byte               │
│ frame_count   │ 4 bytes              │
│ compressed    │ 1 byte (bool)        │
│ checksum      │ 32 bytes             │
└──────────────────────────────────────┘
```

Segment types:
- `0x01` - Data segment (frames)
- `0x02` - Lex index segment
- `0x03` - Vec index segment
- `0x04` - Time index segment

## Time Index

The time index enables chronological queries and time-travel.

### Time Index Entry

| Field | Size | Description |
|-------|------|-------------|
| `frame_id` | 8 | Frame identifier |
| `timestamp` | 8 | Unix timestamp |
| `offset` | 8 | Byte offset in data segment |

Magic: `MVTI` (0x4D 0x56 0x54 0x49)

## Lex Index (Full-Text Search)

When the `lex` feature is enabled, the file contains a Tantivy index segment.

Indexed fields:
- `body` - Full text content
- `title` - Document title
- `uri` - Document URI
- `tags` - Flattened tag values

Supports:
- BM25 ranking
- Phrase queries
- Boolean operators
- Date range filters

## Vec Index (Vector Search)

When the `vec` feature is enabled, the file contains an HNSW index segment.

| Parameter | Value |
|-----------|-------|
| Dimensions | 384 (BGE-small) |
| Distance | Cosine similarity |
| M | 16 |
| ef_construction | 200 |

## Table of Contents (TOC)

The TOC is the final segment, pointed to by `footer_offset` in the header.

```
┌──────────────────────────────────────┐
│ magic         │ "MVTC"               │
│ version       │ 2 bytes              │
│ segment_count │ 4 bytes              │
│ segments[]    │ SegmentDescriptor[]  │
│ manifests     │ IndexManifests       │
│ checksum      │ 32 bytes             │
└──────────────────────────────────────┘
```

### Segment Descriptor

| Field | Size | Description |
|-------|------|-------------|
| `segment_type` | 1 | Type identifier |
| `offset` | 8 | Byte offset in file |
| `length` | 8 | Segment size in bytes |
| `checksum` | 32 | SHA-256 of segment |

## URI Scheme

All content is addressable via `mv2://` URIs:

```
mv2://[track/][path/]name
```

Examples:
- `mv2://meetings/2024-01-15`
- `mv2://docs/api/reference.md`
- `mv2://media/photo.png`

## Invariants

1. **Single-file guarantee**: No `.wal`, `.shm`, `.lock`, or other sidecar files
2. **Append-only frames**: Existing frames are never modified in place
3. **Determinism**: Same API calls produce identical bytes
4. **Crash safety**: WAL ensures durability across unexpected termination
5. **Self-describing**: TOC contains all metadata needed to parse the file

## Version History

| Version | Changes |
|---------|---------|
| 2.1 | Current version. Embedded WAL, temporal track support |
| 2.0 | Single-file format, removed external indices |
| 1.x | Legacy format (deprecated) |
