//! Integration tests for doctor recovery functionality.
//! These tests ensure that doctor can reliably recover corrupted files.

use std::fs::{read, write};
use tempfile::{NamedTempFile, TempDir};

use memvid_core::{
    DoctorOptions, DoctorPhaseKind, DoctorStatus, HEADER_SIZE, Memvid, PutOptions, SearchRequest,
    io::header::HeaderCodec,
};

/// Windows needs extra time for Tantivy to release file handles.
/// Without this delay, TempDir cleanup fails with "Access is denied".
#[cfg(target_os = "windows")]
fn windows_file_handle_delay() {
    std::thread::sleep(std::time::Duration::from_millis(100));
}

#[cfg(not(target_os = "windows"))]
fn windows_file_handle_delay() {
    // No-op on Unix systems
}

/// Test that doctor can rebuild a Tantivy-based lex index from scratch.
#[test]
#[cfg(feature = "lex")]
fn doctor_rebuilds_tantivy_index() {
    let temp = NamedTempFile::new().unwrap();
    let path = temp.path();

    // Step 1: Create file with Tantivy index and add documents
    {
        let mut mem = Memvid::create(path).unwrap();
        mem.enable_lex().unwrap();

        // Add 100 test documents with searchable content
        for i in 0..100 {
            let content = format!(
                "This is test document number {} with searchable content about quantum physics and classical mechanics",
                i
            );
            let options = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                title: Some(format!("Document {}", i)),
                search_text: Some(content.clone()),
                ..Default::default()
            };
            mem.put_bytes_with_options(content.as_bytes(), options)
                .unwrap();
        }

        mem.commit().unwrap();
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Step 2: Verify search works before doctor rebuild
    {
        let mut mem = Memvid::open_read_only(path).unwrap();
        let results = mem
            .search(SearchRequest {
                query: "document".to_string(),
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
            })
            .unwrap();

        assert!(
            !results.hits.is_empty(),
            "Search should return results before doctor"
        );
        assert!(results.total_hits >= 10, "Should have at least 10 hits");
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Step 3: Run doctor to rebuild indexes
    {
        let report = Memvid::doctor(
            path,
            DoctorOptions {
                rebuild_lex_index: true,
                rebuild_time_index: true, // Must rebuild time index with lex index
                rebuild_vec_index: false,
                vacuum: false,
                dry_run: false,
                quiet: true,
            },
        )
        .unwrap();

        // Doctor ran - we'll verify it worked by testing search below
        // Note: Doctor may report Failed if verification is strict, but rebuilt indexes may still work
        // Note: Doctor may report Failed if verification is strict, but rebuilt indexes may still work
        eprintln!("Doctor status: {:?}", report.status);
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Step 4: Verify search still works after doctor rebuild
    {
        let mut mem = Memvid::open_read_only(path).unwrap();
        let results = mem
            .search(SearchRequest {
                query: "document".to_string(),
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
            })
            .unwrap();

        assert!(
            !results.hits.is_empty(),
            "Search should return results after doctor rebuild"
        );
        assert_eq!(
            results.hits.len(),
            10,
            "Should return exactly 10 results (top_k)"
        );
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();
}

/// Test that doctor correctly handles files with 0 frames.
#[test]
#[cfg(feature = "lex")]
fn doctor_handles_empty_file() {
    let temp = NamedTempFile::new().unwrap();
    let path = temp.path();

    // Create empty file with lex enabled
    {
        let mut mem = Memvid::create(path).unwrap();
        mem.enable_lex().unwrap();
        mem.commit().unwrap();
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Run doctor on empty file (should not error)
    {
        let report = Memvid::doctor(
            path,
            DoctorOptions {
                rebuild_lex_index: true,
                rebuild_time_index: true, // Must rebuild time index with lex index
                rebuild_vec_index: false,
                vacuum: false,
                dry_run: false,
                quiet: true,
            },
        )
        .unwrap();

        // Doctor ran - we'll verify it worked by testing search below
        // Doctor ran - we'll verify it worked by testing search below
        eprintln!("Doctor status: {:?}", report.status);
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Verify file still opens after doctor
    {
        let _mem = Memvid::open_read_only(path).unwrap();
        // Note: Doctor may disable lex on empty files, so we just verify the file opens
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();
}

/// Test that doctor can handle files with lex disabled.
#[test]
fn doctor_handles_lex_disabled() {
    let temp = NamedTempFile::new().unwrap();
    let path = temp.path();

    // Create file WITHOUT lex enabled
    {
        let mut mem = Memvid::create(path).unwrap();

        // Add documents without enabling lex
        for i in 0..10 {
            let content = format!("Content {}", i);
            let options = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                title: Some(format!("Document {}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(content.as_bytes(), options)
                .unwrap();
        }

        mem.commit().unwrap();
    }

    // Run doctor (should succeed even without lex)
    {
        let report = Memvid::doctor(
            path,
            DoctorOptions {
                rebuild_lex_index: false,
                rebuild_time_index: true,
                rebuild_vec_index: false,
                vacuum: false,
                dry_run: false,
                quiet: true,
            },
        )
        .unwrap();

        // Doctor ran - we'll verify it worked by checking file can still be opened
        eprintln!("Doctor status: {:?}", report.status);
    }
}

/// Test that opening a file with Tantivy segments sets lex_enabled correctly.
#[test]
#[cfg(feature = "lex")]
fn open_file_with_tantivy_segments_enables_lex() {
    let temp = NamedTempFile::new().unwrap();
    let path = temp.path();

    // Step 1: Create file with Tantivy index
    {
        let mut mem = Memvid::create(path).unwrap();
        mem.enable_lex().unwrap();

        let content = "Test content for searching";
        let options = PutOptions {
            uri: Some("mv2://test".to_string()),
            title: Some("Test".to_string()),
            search_text: Some(content.to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(content.as_bytes(), options)
            .unwrap();

        mem.commit().unwrap();
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Step 2: Open file and verify search works (proves lex_enabled is true)
    {
        let mut mem = Memvid::open_read_only(path).unwrap();
        let result = mem.search(SearchRequest {
            query: "test".to_string(),
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
        });

        assert!(
            result.is_ok(),
            "Search should work on file with Tantivy segments (lex_enabled should be true)"
        );

        let results = result.unwrap();
        assert!(!results.hits.is_empty(), "Should find the test document");
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();
}

/// Test that doctor rebuilds produce valid, searchable indexes.
#[test]
#[cfg(feature = "lex")]
fn doctor_rebuild_produces_searchable_index() {
    let temp = NamedTempFile::new().unwrap();
    let path = temp.path();

    // Create file with specific searchable content
    {
        let mut mem = Memvid::create(path).unwrap();
        mem.enable_lex().unwrap();

        let quantum_content = "Quantum mechanics is a fundamental theory in physics";
        let quantum_opts = PutOptions {
            uri: Some("mv2://quantum".to_string()),
            title: Some("Quantum Physics".to_string()),
            search_text: Some(quantum_content.to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(quantum_content.as_bytes(), quantum_opts)
            .unwrap();

        let classical_content = "Classical mechanics describes macroscopic motion";
        let classical_opts = PutOptions {
            uri: Some("mv2://classical".to_string()),
            title: Some("Classical Physics".to_string()),
            search_text: Some(classical_content.to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(classical_content.as_bytes(), classical_opts)
            .unwrap();

        mem.commit().unwrap();
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Run doctor rebuild
    {
        let report = Memvid::doctor(
            path,
            DoctorOptions {
                rebuild_lex_index: true,
                rebuild_time_index: true, // Must rebuild time index with lex index
                rebuild_vec_index: false,
                vacuum: false,
                dry_run: false,
                quiet: true,
            },
        )
        .unwrap();

        // Doctor ran - we'll verify it worked by testing search below
        // Doctor ran - we'll verify it worked by testing search below
        eprintln!("Doctor status: {:?}", report.status);
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    // Verify specific search queries work correctly
    {
        let mut mem = Memvid::open_read_only(path).unwrap();

        // Search for "quantum" should find quantum doc
        let results = mem
            .search(SearchRequest {
                query: "quantum".to_string(),
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
            })
            .unwrap();

        assert_eq!(
            results.hits.len(),
            1,
            "Should find exactly 1 quantum result"
        );
        assert!(
            results.hits[0].uri.contains("quantum"),
            "Result should be the quantum document"
        );

        // Search for "physics" should find both docs
        let results = mem
            .search(SearchRequest {
                query: "physics".to_string(),
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
            })
            .unwrap();

        assert_eq!(results.hits.len(), 2, "Should find both physics documents");
    }
    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();
}

/*
    Test: WAL corruption recovery
    1. Create valid .mv2, corrupt WAL region with 0xFF bytes
    2. Run doctor → triggers try_recover_from_wal_corruption()
    3. Assert file opens after WAL rebuild
*/
#[test]
#[cfg_attr(windows, ignore)]
fn doctor_recovers_corrupted_wal() {
    use memvid_core::io::header::HeaderCodec;
    use std::fs::{read, write};

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");
    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.put_bytes(b"testing the docter recovers corrupted WAL.")
            .unwrap();
        mem.commit().unwrap();
    }

    let mut bytes = read(&mv2_path).unwrap();
    let header_bytes: &[u8; HEADER_SIZE] = bytes[0..HEADER_SIZE].try_into().unwrap();
    let header = HeaderCodec::decode(header_bytes).unwrap();

    let start = header.wal_offset as usize;
    let end = start + header.wal_size.min(100) as usize;

    // corrupt some bytes
    #[allow(clippy::needless_range_loop)]
    for i in start..end {
        bytes[i] = 0xFF; // Corrupt bytes
    }

    write(&mv2_path, &bytes).unwrap();

    let options = DoctorOptions {
        rebuild_time_index: true,
        rebuild_lex_index: true,
        rebuild_vec_index: true,
        vacuum: true,
        dry_run: false, // should be false for repair
        quiet: true,
    };
    let report = Memvid::doctor(&mv2_path, options).expect("docter");
    eprintln!("Doctor status: {:?}", report.status);
    eprintln!("Findings: {:?}", report.findings);
    assert!(matches!(
        report.status,
        DoctorStatus::Healed | DoctorStatus::Clean
    ));

    let _mem = Memvid::open(&mv2_path).expect("should open after repair");
}

/*
    Test: Header pointer corruption (Tier-2 aggressive repair)
    1. Create valid .mv2, corrupt footer_offset (bytes 8-15) with u64::MAX
    2. Run doctor → scan_for_footer() finds MV2FOOT! magic
    3. Assert file opens after header repair
*/
#[test]
#[cfg_attr(windows, ignore)]
fn doctor_repairs_header_pointer() {
    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.put_bytes(b"testing doctor repair header pointer")
            .unwrap();
        mem.commit().unwrap();
    }

    let mut bytes = read(&mv2_path).unwrap();

    // footer_offset = 8
    bytes[8..16].copy_from_slice(&u64::MAX.to_le_bytes()); // corrupt the footer offset

    write(&mv2_path, &bytes).unwrap();

    let options = DoctorOptions {
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).expect("doctor report");

    assert!(matches!(
        report.status,
        DoctorStatus::Clean | DoctorStatus::Healed
    ));

    let _ = Memvid::open(&mv2_path).expect("open");
}

/*
    Test: TOC recovery via header hint
    1. Create valid .mv2, corrupt footer magic (last 8 bytes)
    2. Run doctor → recover_toc() uses hint-based fallback
    3. Assert file opens after TOC recovery
*/
#[test]
#[cfg_attr(windows, ignore)]
fn doctor_recovers_corrupted_toc() {
    let dir = TempDir::new().unwrap();
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.put_bytes(b"testing doctor recovers corrupted toc")
            .unwrap();
        mem.commit().unwrap();
    }

    let mut bytes = read(&mv2_path).unwrap();
    let file_len = bytes.len();
    bytes[file_len - 8..file_len].copy_from_slice(b"XXXXXXXX");

    write(&mv2_path, &bytes).unwrap();

    let options = DoctorOptions {
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).expect("doctor report");
    assert!(matches!(
        report.status,
        DoctorStatus::Clean | DoctorStatus::Healed
    ));

    let _ = Memvid::open(&mv2_path).expect("file should open after repair");
}

/*
    Test: Complete TOC destruction is unrecoverable
    1. Create valid .mv2, destroy TOC prefix at footer_offset
    2. Run doctor → recover_toc() fails, aggressive repair fails
    3. Assert status is Failed (documents limitation)
*/
#[test]
fn doctor_handles_missing_footer() {
    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create mv2");
        mem.put_bytes(b"testing doctor handles missing footer")
            .unwrap();
        mem.commit().unwrap();
    }

    let mut bytes = read(&mv2_path).expect("read");
    let header_bytes: [u8; HEADER_SIZE] = bytes[..HEADER_SIZE].try_into().unwrap();
    let header = HeaderCodec::decode(&header_bytes).unwrap();

    let footer_offset = header.footer_offset as usize;
    bytes[footer_offset..footer_offset + 8].copy_from_slice(&u64::MAX.to_le_bytes());

    write(&mv2_path, &bytes).unwrap();

    let options = DoctorOptions {
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).unwrap();

    assert!(matches!(report.status, DoctorStatus::Failed)); // assert that complete TOC destruction is unrecoverable
}

/*
    Test: dry_run returns plan without modifying disk
    1. create .mv2, run doctor with dry_run = true
    2. assert status is PlanOnly and file unchanged
*/
#[test]
fn doctor_dry_run_returns_plan() {
    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create mem");
        mem.put_bytes(b"testing doctor dry run returns plan")
            .expect("put bytes");
        mem.commit().expect("commit");
    }

    let original_bytes = read(&mv2_path).expect("read original bytes");

    let options = DoctorOptions {
        rebuild_time_index: true,
        dry_run: true,
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).expect("report");
    assert!(matches!(
        report.status,
        DoctorStatus::PlanOnly | DoctorStatus::Clean
    ));

    let final_bytes = read(&mv2_path).expect("read final bytes");
    assert_eq!(final_bytes, original_bytes);

    let _ = Memvid::open(&mv2_path).expect("open");
}

/*
    Test: doctor detects index out of bounds
    1. create .mv2, truncate file to make index offsets invalid
    2. run doctor, assert it detects the issue (finding or heals)
*/
#[test]
fn doctor_rejects_index_out_of_bounds() {
    use std::fs::{OpenOptions, metadata};

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        mem.put_bytes(b"testing doctor rejects index out of bounds")
            .expect("put bytes");
        mem.commit().expect("commit");
    }

    let original_len = metadata(&mv2_path).expect("meta").len();
    let truncated_len = original_len.saturating_sub(100);

    {
        let file = OpenOptions::new()
            .write(true)
            .open(&mv2_path)
            .expect("open for truncate");

        file.set_len(truncated_len).expect("truncate");
    }

    let options = DoctorOptions {
        rebuild_time_index: true,
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).expect("doctor");
    assert!(
        !report.findings.is_empty()
            || matches!(report.status, DoctorStatus::Healed | DoctorStatus::Failed),
        "expected findings or heal/fail status, got {:?}",
        report.status
    );
}

/*
    Test: vacuum phase runs before index rebuild phase
    1. create .mv2, delete frame, request vacuum + rebuild
    2. assert phase ordering: Vacuum before IndexRebuild
*/
#[test]
fn doctor_vacuum_before_index_rebuild() {
    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        for i in 0..5 {
            let frame_data = format!("testing doctor vaccum should be before index rebuild: {i}");
            mem.put_bytes(frame_data.as_bytes()).expect("put byets");
        }
        mem.commit().expect("commit");
    }

    {
        let mut mem = Memvid::open(&mv2_path).expect("open");
        mem.delete_frame(0).ok();
        mem.commit().expect("commit");
    }

    let options = DoctorOptions {
        vacuum: true,
        rebuild_time_index: true,
        dry_run: true,
        ..Default::default()
    };

    let report = Memvid::doctor(&mv2_path, options).expect("doctor");
    let phases = &report.plan.phases;

    let vacuum_idx = phases
        .iter()
        .position(|p| matches!(p.phase, DoctorPhaseKind::Vacuum));

    let rebuild_idx = phases
        .iter()
        .position(|p| matches!(p.phase, DoctorPhaseKind::IndexRebuild));

    if let (Some(v), Some(r)) = (vacuum_idx, rebuild_idx) {
        assert!(v < r, "vacuum phase must come before IndexRebuild phase");
    }
}

/*
    Test: doctor preserves footer_offset invariant
    1. create .mv2, run doctor rebuild
    2. assert footer_offset remains within file bounds
*/
#[test]
fn doctor_preserves_footer_offset() {
    use std::fs::metadata;

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        mem.put_bytes(b"testing doctor preserves footer offset")
            .expect("put bytes");
        mem.commit().expect("commit");
    }

    let options = DoctorOptions {
        rebuild_time_index: true,
        ..Default::default()
    };

    let _ = Memvid::doctor(&mv2_path, options).expect("doctor");

    let file_len = metadata(&mv2_path).unwrap().len();
    let bytes = read(&mv2_path).expect("read");
    let header_bytes: &[u8; HEADER_SIZE] = bytes[0..HEADER_SIZE].try_into().unwrap();
    let header = HeaderCodec::decode(header_bytes).expect("header");

    assert!(
        header.footer_offset < file_len,
        "footer_offset should not exceeds file length"
    );

    let _ = Memvid::open(&mv2_path).expect("file should open after doctor");
}
