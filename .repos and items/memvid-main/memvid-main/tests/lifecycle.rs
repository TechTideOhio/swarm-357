//! Integration tests for Memvid lifecycle operations.
//! Tests: create, open, open_read_only, commit, stats, verify

use memvid_core::{Memvid, PutOptions, VerificationStatus};
use std::fs;
use tempfile::TempDir;

/// Test basic create and open lifecycle.
#[test]
fn create_and_open() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create new memory
    {
        let mut mem = Memvid::create(&path).unwrap();
        mem.commit().unwrap();
    }

    // Open existing memory
    {
        let _mem = Memvid::open(&path).unwrap();
    }

    // Open read-only
    {
        let _mem = Memvid::open_read_only(&path).unwrap();
    }

    assert!(path.exists(), "MV2 file should exist");
}

/// Test that create handles existing file.
/// Note: The current implementation allows creating even if file exists,
/// this tests that behavior (may change in future versions).
#[test]
fn create_handles_existing_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create first time
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc1".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"First content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Create second time - this tests current behavior
    // (Either it fails OR it creates a new file - both are valid implementations)
    let result = Memvid::create(&path);
    if let Ok(mut mem) = result {
        // If create succeeds, the old data should be gone (new file)
        // let mut mem = result.unwrap();
        mem.commit().unwrap();
        // Reopen and verify it's empty (new file was created)
        let mem = Memvid::open_read_only(&path).unwrap();
        let stats = mem.stats().unwrap();
        assert_eq!(stats.frame_count, 0, "New file should be empty");
    }
    // If it fails, that's also valid behavior
}

/// Test that open fails if file doesn't exist.
#[test]
fn open_fails_if_not_exists() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("nonexistent.mv2");

    let result = Memvid::open(&path);
    assert!(result.is_err(), "Open should fail if file doesn't exist");
}

/// Test stats on empty memory.
#[test]
fn stats_empty_memory() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();
        mem.commit().unwrap();
    }

    let mem = Memvid::open_read_only(&path).unwrap();
    let stats = mem.stats().unwrap();

    assert_eq!(stats.frame_count, 0, "Empty memory should have 0 frames");
}

/// Test stats after adding content.
#[test]
fn stats_with_content() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        for i in 0..5 {
            let content = format!("Test content {}", i);
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                title: Some(format!("Document {}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(content.as_bytes(), opts)
                .unwrap();
        }

        mem.commit().unwrap();
    }

    let mem = Memvid::open_read_only(&path).unwrap();
    let stats = mem.stats().unwrap();

    assert_eq!(stats.frame_count, 5, "Should have 5 frames");
}

/// Test verify on healthy file.
#[test]
fn verify_healthy_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            title: Some("Test".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Test content", opts).unwrap();
        mem.commit().unwrap();
    }

    let report = Memvid::verify(&path, false).unwrap();

    assert_eq!(
        report.overall_status,
        VerificationStatus::Passed,
        "Healthy file should verify as passed"
    );
}

/// Test verify detects corruption (footer zeroed).
/// Note: With severe corruption, verify may return an error instead of a report.
#[test]
fn verify_detects_corruption() {
    use std::io::{Seek, SeekFrom, Write};

    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create valid file
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Test content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Corrupt the footer (zero last 16 bytes)
    {
        let mut file = fs::OpenOptions::new().write(true).open(&path).unwrap();
        let len = file.metadata().unwrap().len();
        if len > 16 {
            file.seek(SeekFrom::End(-16)).unwrap();
            file.write_all(&[0u8; 16]).unwrap();
            file.flush().unwrap();
        }
    }

    // With severe corruption, verify may error out entirely
    // or return a failed status - both are valid responses
    let result = Memvid::verify(&path, false);
    match result {
        Ok(report) => {
            assert_ne!(
                report.overall_status,
                VerificationStatus::Passed,
                "Corrupted file should not verify as passed"
            );
        }
        Err(_) => {
            // Error is also a valid response to severe corruption
        }
    }
}

/// Test multiple commits preserve data.
#[test]
fn multiple_commits_preserve_data() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // First commit
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc1".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"First document", opts).unwrap();
        mem.commit().unwrap();
    }

    // Second commit
    {
        let mut mem = Memvid::open(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc2".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Second document", opts)
            .unwrap();
        mem.commit().unwrap();
    }

    // Verify both documents exist
    let mem = Memvid::open_read_only(&path).unwrap();
    let stats = mem.stats().unwrap();

    assert_eq!(
        stats.frame_count, 2,
        "Should have 2 frames after multiple commits"
    );
}

/// Test commit without changes is a no-op.
#[test]
fn commit_without_changes() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc1".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    let size_before = fs::metadata(&path).unwrap().len();

    // Open and commit without changes
    {
        let mut mem = Memvid::open(&path).unwrap();
        mem.commit().unwrap();
    }

    let size_after = fs::metadata(&path).unwrap().len();

    // Size should be approximately the same (may differ slightly due to timestamp updates)
    assert!(
        (size_after as i64 - size_before as i64).abs() < 1024,
        "Commit without changes should not significantly change file size"
    );
}
