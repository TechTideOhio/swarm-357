//! Integration tests for the structured XLSX extraction pipeline.
//!
//! Uses `/Users/olow/Desktop/memvid-org/arden.xlsx` — a real-world 1.7 MB
//! real-estate pro forma with 19 sheets, merged cells, currency/date formats,
//! and multi-table layouts.

use std::time::Instant;

use memvid_core::{
    DetectedTable, Memvid, PutOptions, SearchRequest, XlsxChunkingOptions, XlsxReader,
};
use tempfile::TempDir;

const ARDEN_PATH: &str = "/Users/olow/Desktop/memvid-org/arden.xlsx";

/// Load the test fixture. Returns `None` when the file is not present (CI).
fn try_load_arden() -> Option<Vec<u8>> {
    std::fs::read(ARDEN_PATH).ok()
}

macro_rules! require_arden {
    () => {
        match try_load_arden() {
            Some(bytes) => bytes,
            None => {
                eprintln!("SKIP: arden.xlsx not found at {ARDEN_PATH}");
                return;
            }
        }
    };
}

// ---------------------------------------------------------------------------
// Phase 1: Structured extraction speed + completeness
// ---------------------------------------------------------------------------

#[test]
fn structured_extraction_completes_under_5s() {
    let bytes = require_arden!();
    let start = Instant::now();
    let result = XlsxReader::extract_structured(&bytes).expect("extraction must succeed");
    let elapsed = start.elapsed();

    println!("Extraction time: {elapsed:?}");
    println!("Flat text length: {} chars", result.text.len());
    println!("Tables detected: {}", result.tables.len());
    println!("Chunks produced: {}", result.chunks.chunks.len());
    println!(
        "Diagnostics warnings: {}",
        result.diagnostics.warnings.len()
    );

    assert!(
        elapsed.as_secs() < 5,
        "Structured extraction took {elapsed:?} — should be under 5s"
    );
}

#[test]
fn detects_multiple_tables_across_sheets() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    // 19 sheets — should detect at least several tables
    assert!(
        result.tables.len() >= 5,
        "Expected at least 5 tables from a 19-sheet workbook, got {}",
        result.tables.len()
    );

    // Collect unique sheet names
    let sheet_names: std::collections::HashSet<&str> = result
        .tables
        .iter()
        .map(|t| t.sheet_name.as_str())
        .collect();
    println!("Sheets with tables: {sheet_names:?}");

    assert!(
        sheet_names.len() >= 3,
        "Tables should span at least 3 sheets, got {}",
        sheet_names.len()
    );
}

#[test]
fn chunks_have_header_context() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    assert!(
        !result.chunks.chunks.is_empty(),
        "Should produce at least one chunk"
    );

    // Every chunk should contain sheet context prefix
    let chunks_with_sheet = result
        .chunks
        .chunks
        .iter()
        .filter(|c| c.text.contains("[Sheet:"))
        .count();

    let ratio = chunks_with_sheet as f64 / result.chunks.chunks.len() as f64;
    println!(
        "Chunks with [Sheet:] prefix: {chunks_with_sheet}/{} ({:.0}%)",
        result.chunks.chunks.len(),
        ratio * 100.0
    );

    assert!(
        ratio > 0.8,
        "At least 80% of chunks should have sheet context, got {:.0}%",
        ratio * 100.0
    );
}

#[test]
fn chunks_respect_row_boundaries() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    for chunk in &result.chunks.chunks {
        // No chunk should end with a partial header:value pair mid-line
        // Each data line should have balanced pipes (Header: Value | Header: Value)
        for line in chunk.text.lines().skip(2) {
            // skip [Sheet:] prefix + header row
            if line.trim().is_empty() {
                continue;
            }
            // Lines should not be cut mid-cell (no trailing ':' without a value)
            let trailing_colon = line.trim_end().ends_with(':');
            assert!(
                !trailing_colon,
                "Chunk has a line ending with bare colon (mid-row split?): {:?}",
                &line[..line.len().min(80)]
            );
        }
    }
}

#[test]
fn chunk_sizes_near_target() {
    let bytes = require_arden!();
    let opts = XlsxChunkingOptions {
        max_chars: 1200,
        max_chunks: 500,
    };
    let result = XlsxReader::extract_structured_with_options(&bytes, opts).unwrap();

    let sizes: Vec<usize> = result.chunks.chunks.iter().map(|c| c.text.len()).collect();
    let avg = sizes.iter().sum::<usize>() as f64 / sizes.len().max(1) as f64;
    let max = sizes.iter().max().copied().unwrap_or(0);

    println!(
        "Chunk count: {}, avg size: {avg:.0} chars, max: {max} chars",
        sizes.len()
    );

    // Average should be in a reasonable range
    assert!(
        avg < 2000.0,
        "Average chunk is {avg:.0} chars — way over target"
    );

    // No chunk should be absurdly large (allow 3x target for wide rows)
    assert!(
        max < 5000,
        "Max chunk is {max} chars — should be under 5000"
    );
}

// ---------------------------------------------------------------------------
// Phase 2: OOXML metadata (merged cells, number formats)
// ---------------------------------------------------------------------------

#[test]
fn merged_regions_detected() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    let total_merged: usize = result
        .metadata
        .merged_regions
        .values()
        .map(|v| v.len())
        .sum();
    println!("Total merged regions: {total_merged}");

    // A complex real-estate pro forma with 19 sheets should have many merged cells
    assert!(
        total_merged > 0,
        "Expected merged regions in a complex workbook"
    );
}

#[test]
fn number_formats_parsed() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    println!("Number format entries: {}", result.metadata.num_fmts.len());
    println!("Cell XF entries: {}", result.metadata.cell_xfs.len());

    // Financial workbook should have custom number formats
    assert!(
        !result.metadata.num_fmts.is_empty() || !result.metadata.cell_xfs.is_empty(),
        "Expected number format metadata from a financial workbook"
    );
}

// ---------------------------------------------------------------------------
// Phase 3: Flat text backward compatibility
// ---------------------------------------------------------------------------

#[test]
fn flat_text_contains_key_data() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    let text = &result.text;
    assert!(
        text.len() > 1000,
        "Flat text should be substantial, got {} chars",
        text.len()
    );

    // Check for known content from the arden.xlsx file
    let text_lower = text.to_lowercase();

    // The file is a real estate deal for "TRG Apartments" in SLC, UT
    let key_terms = [
        "sheet:", // Should have sheet labels
        "248",    // 248 units
    ];

    for term in &key_terms {
        assert!(
            text_lower.contains(&term.to_lowercase()),
            "Flat text should contain '{term}'"
        );
    }
}

// ---------------------------------------------------------------------------
// Phase 4: End-to-end ingestion + search accuracy
// ---------------------------------------------------------------------------

/// Ingest the XLSX into a Memvid file and return the path + temp dir (to keep alive).
/// Returns `None` when arden.xlsx is not available (CI).
fn ingest_arden() -> Option<(std::path::PathBuf, TempDir)> {
    let bytes = try_load_arden()?;
    let dir = TempDir::new().unwrap();
    let mv2_path = dir.path().join("arden.mv2");
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    let mut mem = Memvid::create(&mv2_path).unwrap();
    mem.enable_lex().unwrap();

    // Ingest each chunk as a separate frame with search_text set to the chunk content
    for (i, chunk) in result.chunks.chunks.iter().enumerate() {
        let opts = PutOptions {
            uri: Some(format!("mv2://arden/chunk/{i}")),
            title: Some(format!("Arden XLSX chunk {i}")),
            search_text: Some(chunk.text.clone()),
            auto_tag: false,
            extract_dates: false,
            extract_triplets: false,
            ..Default::default()
        };
        mem.put_bytes_with_options(chunk.text.as_bytes(), opts)
            .unwrap();
    }

    mem.commit().unwrap();
    Some((mv2_path, dir))
}

fn search_arden(mem: &mut Memvid, query: &str, top_k: usize) -> Vec<memvid_core::SearchHit> {
    mem.search(SearchRequest {
        query: query.to_string(),
        top_k,
        snippet_chars: 300,
        uri: None,
        scope: None,
        cursor: None,
        #[cfg(feature = "temporal_track")]
        temporal: None,
        as_of_frame: None,
        as_of_ts: None,
        no_sketch: false,
        acl_context: None,
        acl_enforcement_mode: memvid_core::types::AclEnforcementMode::Audit,
    })
    .unwrap()
    .hits
}

#[test]
#[cfg(feature = "lex")]
fn ingest_and_search_units() {
    let Some((path, _dir)) = ingest_arden() else {
        eprintln!("SKIP");
        return;
    };
    let mut mem = Memvid::open_read_only(&path).unwrap();

    // Search for unit count — the file has 248 multifamily units
    let hits = search_arden(&mut mem, "248 units", 5);

    println!("Query '248 units' — {} hits", hits.len());
    for (i, h) in hits.iter().enumerate() {
        println!(
            "  [{i}] score={:.3} uri={} text={:.120}",
            h.score.unwrap_or(0.0),
            h.uri,
            h.text.replace('\n', " ")
        );
    }

    assert!(!hits.is_empty(), "Should find results for '248 units'");

    // At least one hit should contain "248"
    let has_248 = hits.iter().any(|h| h.text.contains("248"));
    assert!(has_248, "At least one hit should contain '248'");
}

#[test]
#[cfg(feature = "lex")]
fn ingest_and_search_financial_terms() {
    let Some((path, _dir)) = ingest_arden() else {
        eprintln!("SKIP");
        return;
    };
    let mut mem = Memvid::open_read_only(&path).unwrap();

    // The file contains construction costs, debt service, NOI, etc.
    let queries = ["construction", "debt", "occupancy", "revenue", "lease"];

    let mut found_count = 0;
    for query in &queries {
        let hits = search_arden(&mut mem, query, 3);
        println!("Query '{query}': {} hits", hits.len());

        if !hits.is_empty() {
            found_count += 1;
            println!(
                "  Top hit: score={:.3} text={:.100}",
                hits[0].score.unwrap_or(0.0),
                hits[0].text.replace('\n', " ")
            );
        }
    }

    // At least 3 out of 5 financial queries should return results
    assert!(
        found_count >= 3,
        "Expected at least 3/5 financial queries to match, got {found_count}/5"
    );
}

#[test]
#[cfg(feature = "lex")]
fn search_hits_contain_header_context() {
    let Some((path, _dir)) = ingest_arden() else {
        eprintln!("SKIP");
        return;
    };
    let mut mem = Memvid::open_read_only(&path).unwrap();

    let hits = search_arden(&mut mem, "construction", 5);

    if hits.is_empty() {
        println!("WARN: no hits for 'construction' — skipping header context check");
        return;
    }

    // Check that hit text contains structured context (sheet/table prefix or header:value pairs)
    let has_context = hits
        .iter()
        .any(|h| h.text.contains("[Sheet:") || h.text.contains(':'));

    assert!(
        has_context,
        "Search hits should contain structured context (sheet prefix or header:value pairs)"
    );
}

// ---------------------------------------------------------------------------
// Phase 5: Full pipeline timing benchmark
// ---------------------------------------------------------------------------

#[test]
#[cfg(feature = "lex")]
fn full_pipeline_timing() {
    let bytes = require_arden!();

    // Step 1: Structured extraction
    let t0 = Instant::now();
    let result = XlsxReader::extract_structured(&bytes).unwrap();
    let extraction_time = t0.elapsed();

    // Step 2: Memvid create + lex enable
    let dir = TempDir::new().unwrap();
    let mv2_path = dir.path().join("bench.mv2");

    let t1 = Instant::now();
    let mut mem = Memvid::create(&mv2_path).unwrap();
    mem.enable_lex().unwrap();

    // Step 3: Ingest all chunks
    for (i, chunk) in result.chunks.chunks.iter().enumerate() {
        let opts = PutOptions {
            uri: Some(format!("mv2://arden/chunk/{i}")),
            title: Some(format!("Chunk {i}")),
            search_text: Some(chunk.text.clone()),
            auto_tag: false,
            extract_dates: false,
            extract_triplets: false,
            ..Default::default()
        };
        mem.put_bytes_with_options(chunk.text.as_bytes(), opts)
            .unwrap();
    }
    mem.commit().unwrap();
    let ingest_time = t1.elapsed();

    // Step 4: Search
    let mut mem = Memvid::open_read_only(&mv2_path).unwrap();
    let t2 = Instant::now();
    let hits = search_arden(&mut mem, "construction cost", 10);
    let search_time = t2.elapsed();

    let total = extraction_time + ingest_time + search_time;

    println!("=== Full Pipeline Timing ===");
    println!("  XLSX extraction:  {extraction_time:?}");
    println!(
        "  Memvid ingest:    {ingest_time:?}  ({} chunks)",
        result.chunks.chunks.len()
    );
    println!("  Search query:     {search_time:?}  ({} hits)", hits.len());
    println!("  TOTAL:            {total:?}");
    println!("  Tables detected:  {}", result.tables.len());
    println!("  Flat text chars:  {}", result.text.len());
    println!(
        "  MV2 file size:    {} KB",
        std::fs::metadata(&mv2_path).unwrap().len() / 1024
    );

    // In release mode, target is under 40s. Debug mode gets 3x slack for
    // unoptimized Tantivy indexing on 500 individual put_bytes calls.
    let limit = if cfg!(debug_assertions) { 180 } else { 40 };
    assert!(
        total.as_secs() < limit,
        "Full pipeline took {total:?} — target is under {limit}s"
    );
}

// ---------------------------------------------------------------------------
// Phase 6: Table detection quality
// ---------------------------------------------------------------------------

#[test]
fn tables_have_headers() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    let tables_with_headers: Vec<&DetectedTable> = result
        .tables
        .iter()
        .filter(|t| !t.headers.is_empty())
        .collect();

    println!(
        "Tables with headers: {}/{}",
        tables_with_headers.len(),
        result.tables.len()
    );

    for t in &tables_with_headers {
        println!(
            "  [{}] '{}' — {} headers, {} rows, confidence={:.2}",
            t.sheet_name,
            t.name,
            t.headers.len(),
            t.last_data_row.saturating_sub(t.first_data_row) + 1,
            t.confidence
        );
    }

    // Most tables should have detected headers
    let ratio = tables_with_headers.len() as f64 / result.tables.len().max(1) as f64;
    assert!(
        ratio > 0.5,
        "At least 50% of tables should have headers, got {:.0}%",
        ratio * 100.0
    );
}

#[test]
fn table_column_types_inferred() {
    let bytes = require_arden!();
    let result = XlsxReader::extract_structured(&bytes).unwrap();

    let tables_with_types: Vec<&DetectedTable> = result
        .tables
        .iter()
        .filter(|t| !t.column_types.is_empty())
        .collect();

    println!(
        "Tables with column types: {}/{}",
        tables_with_types.len(),
        result.tables.len()
    );

    for t in &tables_with_types[..tables_with_types.len().min(5)] {
        println!(
            "  [{}] '{}' — types: {:?}",
            t.sheet_name, t.name, t.column_types
        );
    }

    assert!(
        !tables_with_types.is_empty(),
        "At least some tables should have inferred column types"
    );
}
