//! Test to demonstrate the implicit OR bug in query parsing
//!
//! Run with: cargo run --example test_implicit_or_bug --features lex

use memvid_core::{Memvid, PutOptions, SearchRequest};

fn main() -> memvid_core::Result<()> {
    let test_file = "/tmp/test_implicit.mv2";

    // Clean up old file if exists
    let _ = std::fs::remove_file(test_file);

    println!("Creating test .mv2 file...");
    let mut mem = Memvid::create(test_file)?;

    // Add documents
    println!("Adding test documents...");
    mem.put_bytes_with_options(
        b"I love machine learning",
        PutOptions::builder().title("Doc 1").build(),
    )?;
    mem.put_bytes_with_options(
        b"I love Python programming",
        PutOptions::builder().title("Doc 2").build(),
    )?;
    mem.put_bytes_with_options(
        b"Machine learning with Python is awesome",
        PutOptions::builder().title("Doc 3").build(),
    )?;
    mem.commit()?;

    println!();
    println!("=== TESTING IMPLICIT OPERATOR BEHAVIOR ===");
    println!("Query: 'machine python'");
    println!();
    println!("Expected behavior (AND): Should return 1 result");
    println!("  - Only Doc 3 has BOTH 'machine' AND 'python'");
    println!();
    println!("Current behavior (OR): Returns 3 results");
    println!("  - Any doc with 'machine' OR 'python'");
    println!();

    // Search with implicit operator
    let results = mem.search(SearchRequest {
        query: "machine python".to_string(),
        top_k: 10,
        snippet_chars: 200,
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
    })?;

    println!("ACTUAL RESULTS: {} documents found", results.hits.len());
    println!();

    for (i, hit) in results.hits.iter().enumerate() {
        let title = hit
            .title
            .as_ref()
            .unwrap_or(&"Untitled".to_string())
            .clone();
        let text_lower = hit.text.to_lowercase();
        let has_machine = text_lower.contains("machine");
        let has_python = text_lower.contains("python");
        let is_relevant = has_machine && has_python;

        let status = if is_relevant {
            "✓ RELEVANT"
        } else {
            "✗ NOT RELEVANT"
        };

        println!(
            "  {}. {} [machine={}, python={}] {}",
            i + 1,
            title,
            has_machine,
            has_python,
            status
        );
    }

    println!();

    // Calculate precision
    let relevant_count = results
        .hits
        .iter()
        .filter(|hit| {
            let text = hit.text.to_lowercase();
            text.contains("machine") && text.contains("python")
        })
        .count();

    let precision = if results.hits.is_empty() {
        0.0
    } else {
        (relevant_count as f64 / results.hits.len() as f64) * 100.0
    };

    println!(
        "PRECISION: {:.1}% ({}/{} results are relevant)",
        precision,
        relevant_count,
        results.hits.len()
    );
    println!();

    // Verdict
    if results.hits.len() == 1 && relevant_count == 1 {
        println!("✓ CORRECT: Query uses implicit AND");
        println!("  Perfect precision - returns only relevant docs");
    } else if results.hits.len() > 1 {
        println!("✗ BUG DETECTED: Query uses implicit OR");
        println!("  Low precision - returns docs with EITHER term");
        println!();
    } else {
        println!("? NO RESULTS: Check if lex feature is enabled");
    }

    // Cleanup
    std::fs::remove_file(test_file)?;

    Ok(())
}
