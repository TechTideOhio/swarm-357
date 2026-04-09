//! Integration tests for single-file guarantee.
//! Ensures .mv2 files are completely self-contained with no sidecar files.

use memvid_core::{Memvid, PutOptions};
use std::fs;
use tempfile::TempDir;

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

/// Helper to count files in a directory (excluding hidden).
fn count_files(dir: &std::path::Path) -> usize {
    fs::read_dir(dir)
        .unwrap()
        .filter_map(|e| e.ok())
        .filter(|e| !e.file_name().to_string_lossy().starts_with('.'))
        .count()
}

/// Helper to list files in a directory.
fn list_files(dir: &std::path::Path) -> Vec<String> {
    fs::read_dir(dir)
        .unwrap()
        .filter_map(|e| e.ok())
        .map(|e| e.file_name().to_string_lossy().to_string())
        .collect()
}

/// Test that create produces exactly one file.
#[test]
fn create_produces_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();
        mem.commit().unwrap();
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Create should produce exactly 1 file, found: {:?}",
        list_files(dir.path())
    );
}

/// Test that put maintains single file.
#[test]
fn put_maintains_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        for i in 0..10 {
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(format!("Content {}", i).as_bytes(), opts)
                .unwrap();
        }

        mem.commit().unwrap();
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Put should maintain single file, found: {:?}",
        list_files(dir.path())
    );
}

/// Test that multiple commits maintain single file.
#[test]
fn multiple_commits_maintain_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // First commit
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc1".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content 1", opts).unwrap();
        mem.commit().unwrap();
    }

    let file_count_1 = count_files(dir.path());
    assert_eq!(
        file_count_1,
        1,
        "After first commit: {:?}",
        list_files(dir.path())
    );

    // Second commit
    {
        let mut mem = Memvid::open(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc2".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content 2", opts).unwrap();
        mem.commit().unwrap();
    }

    let file_count_2 = count_files(dir.path());
    assert_eq!(
        file_count_2,
        1,
        "After second commit: {:?}",
        list_files(dir.path())
    );

    // Third commit
    {
        let mut mem = Memvid::open(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://doc3".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content 3", opts).unwrap();
        mem.commit().unwrap();
    }

    let file_count_3 = count_files(dir.path());
    assert_eq!(
        file_count_3,
        1,
        "After third commit: {:?}",
        list_files(dir.path())
    );
}

/// Test that update maintains single file.
#[test]
fn update_maintains_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            title: Some("Original".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Update
    {
        let mut mem = Memvid::open(&path).unwrap();
        let update_opts = PutOptions {
            title: Some("Updated".to_string()),
            ..Default::default()
        };
        mem.update_frame(0, None, update_opts, None).unwrap();
        mem.commit().unwrap();
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Update should maintain single file, found: {:?}",
        list_files(dir.path())
    );
}

/// Test that delete maintains single file.
#[test]
fn delete_maintains_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create with content
    {
        let mut mem = Memvid::create(&path).unwrap();
        for i in 0..5 {
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(format!("Content {}", i).as_bytes(), opts)
                .unwrap();
        }
        mem.commit().unwrap();
    }

    // Delete
    {
        let mut mem = Memvid::open(&path).unwrap();
        mem.delete_frame(2).unwrap();
        mem.commit().unwrap();
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Delete should maintain single file, found: {:?}",
        list_files(dir.path())
    );
}

/// Test that enabling lex maintains single file.
#[test]
#[cfg(feature = "lex")]
fn enable_lex_maintains_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();
        mem.enable_lex().unwrap();

        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            search_text: Some("Searchable content".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Lex index should be embedded, found: {:?}",
        list_files(dir.path())
    );
}

/// Test that doctor maintains single file.
#[test]
fn doctor_maintains_single_file() {
    use memvid_core::DoctorOptions;

    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Run doctor
    {
        let _report = Memvid::doctor(
            &path,
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
    }

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Doctor should maintain single file, found: {:?}",
        list_files(dir.path())
    );
}

/// Test no WAL sidecar files.
///
/// NOTE: Skipped on Windows due to Tantivy file locking behavior.
/// See `large_file_maintains_single_file` for detailed explanation.
#[test]
#[cfg(not(target_os = "windows"))]
fn no_wal_sidecar_files() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        // Do multiple operations that would touch WAL
        for i in 0..100 {
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(format!("Content {}", i).as_bytes(), opts)
                .unwrap();
        }

        mem.commit().unwrap();
    }

    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    let files = list_files(dir.path());

    // Check for forbidden sidecar patterns
    for file in &files {
        assert!(!file.ends_with(".wal"), "Found WAL sidecar file: {}", file);
        assert!(!file.ends_with(".shm"), "Found SHM sidecar file: {}", file);
        assert!(!file.ends_with("-wal"), "Found -wal sidecar file: {}", file);
        assert!(!file.ends_with("-shm"), "Found -shm sidecar file: {}", file);
        assert!(
            !file.ends_with(".lock"),
            "Found lock sidecar file: {}",
            file
        );
        assert!(
            !file.ends_with("-journal"),
            "Found journal sidecar file: {}",
            file
        );
    }

    assert_eq!(files.len(), 1, "Should have exactly 1 file");
}

/// Test file is self-contained (can be copied and used).
#[test]
fn file_is_self_contained() {
    let dir1 = TempDir::new().unwrap();
    let dir2 = TempDir::new().unwrap();
    let path1 = dir1.path().join("original.mv2");
    let path2 = dir2.path().join("copy.mv2");

    // Create original
    {
        let mut mem = Memvid::create(&path1).unwrap();
        for i in 0..5 {
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                title: Some(format!("Document {}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(format!("Content {}", i).as_bytes(), opts)
                .unwrap();
        }
        mem.commit().unwrap();
    }

    // Copy file to new location
    fs::copy(&path1, &path2).unwrap();

    // Verify copy works independently
    let mem = Memvid::open_read_only(&path2).unwrap();
    let stats = mem.stats().unwrap();

    assert_eq!(stats.frame_count, 5, "Copied file should have all frames");

    // Verify we can read frames from copy
    let frame = mem.frame_by_id(0).unwrap();
    assert_eq!(frame.uri.as_deref(), Some("mv2://doc0"));
    assert_eq!(frame.title.as_deref(), Some("Document 0"));
}

/// Test large file maintains single file.
///
/// NOTE: Skipped on Windows due to Tantivy file locking behavior.
/// When running with `lex` feature (default), Tantivy creates temporary index files
/// that Windows holds open longer than Unix systems. This causes sporadic
/// "Access is denied (os error 5)" failures during tempdir cleanup.
/// The underlying single-file guarantee is platform-independent and tested on Unix.
/// See also: `tests_lex_flag.rs` which uses the same skip pattern.
#[test]
#[cfg(not(target_os = "windows"))]
fn large_file_maintains_single_file() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        // Add 100 documents with ~10KB each
        for i in 0..100 {
            let large_content = vec![b'x'; 10 * 1024];
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                ..Default::default()
            };
            mem.put_bytes_with_options(&large_content, opts).unwrap();
        }

        mem.commit().unwrap();
    }

    // Windows needs extra time for Tantivy to release file handles
    windows_file_handle_delay();

    let file_count = count_files(dir.path());
    assert_eq!(
        file_count,
        1,
        "Large file should remain single, found: {:?}",
        list_files(dir.path())
    );
}
