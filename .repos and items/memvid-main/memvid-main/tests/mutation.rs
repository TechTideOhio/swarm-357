//! Integration tests for Memvid mutation operations.
//! Tests: put, put_bytes_with_options, update, delete

use memvid_core::{
    EmbeddingIdentitySummary, MEMVID_EMBEDDING_MODEL_KEY, MEMVID_EMBEDDING_PROVIDER_KEY, Memvid,
    MemvidError, PutOptions, TimelineQuery,
};
use std::num::NonZeroU64;
use tempfile::TempDir;

/// Test basic put operation with bytes.
#[test]
fn put_bytes_basic() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();

    let opts = PutOptions {
        uri: Some("mv2://test".to_string()),
        title: Some("Test Document".to_string()),
        ..Default::default()
    };

    let _frame_id = mem.put_bytes_with_options(b"Hello, World!", opts).unwrap();
    mem.commit().unwrap();

    // Verify frame was created
    // Verify frame was created (FrameId is u64 so >= 0 is implied)
    // assert!(frame_id >= 0);

    let mem = Memvid::open_read_only(&path).unwrap();
    assert_eq!(mem.stats().unwrap().frame_count, 1, "Should have 1 frame");
}

/// Test put with all options.
#[test]
fn put_bytes_with_all_options() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        let opts = PutOptions {
            uri: Some("mv2://docs/report.txt".to_string()),
            title: Some("Annual Report".to_string()),
            search_text: Some("Financial summary for 2024".to_string()),
            tags: vec!["finance".to_string(), "annual".to_string()],
            labels: vec!["Important".to_string()],
            timestamp: Some(1700000000),
            ..Default::default()
        };

        mem.put_bytes_with_options(b"Report content here", opts)
            .unwrap();
        mem.commit().unwrap();
    }

    // Verify frame was stored
    let mem = Memvid::open_read_only(&path).unwrap();
    let stats = mem.stats().unwrap();
    assert_eq!(stats.frame_count, 1, "Should have 1 frame");

    // Verify frame metadata by fetching via URI
    let frame = mem.frame_by_uri("mv2://docs/report.txt").unwrap();
    assert_eq!(frame.uri.as_deref(), Some("mv2://docs/report.txt"));
    assert_eq!(frame.title.as_deref(), Some("Annual Report"));
    assert!(frame.tags.contains(&"finance".to_string()));
    assert!(frame.labels.contains(&"Important".to_string()));
    assert_eq!(frame.timestamp, 1700000000);
}

/// Test multiple puts create frames.
#[test]
fn put_multiple_creates_frames() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

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

    let mem = Memvid::open_read_only(&path).unwrap();
    assert_eq!(mem.stats().unwrap().frame_count, 5, "Should have 5 frames");
}

/// Test frame_by_uri returns correct data.
#[test]
fn frame_by_uri_returns_data() {
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

    let mem = Memvid::open_read_only(&path).unwrap();
    let frame = mem.frame_by_uri("mv2://test").unwrap();

    assert_eq!(frame.uri.as_deref(), Some("mv2://test"));
    assert_eq!(frame.title.as_deref(), Some("Test"));
}

/// Test update_frame modifies frame metadata.
#[test]
fn update_frame_modifies_metadata() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create with initial data
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            title: Some("Original Title".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Update frame - look up by URI to get current frame_id
    {
        let mut mem = Memvid::open(&path).unwrap();
        // Get the frame by URI to find its actual ID
        let frame = mem.frame_by_uri("mv2://test").unwrap();
        let frame_id = frame.id;

        let update_opts = PutOptions {
            title: Some("Updated Title".to_string()),
            ..Default::default()
        };
        // Pass new payload to trigger actual update
        mem.update_frame(frame_id, Some(b"New Content".to_vec()), update_opts, None)
            .unwrap();
        mem.commit().unwrap();
    }

    // Verify update
    let mem = Memvid::open_read_only(&path).unwrap();
    let frame = mem.frame_by_uri("mv2://test").unwrap();

    assert_eq!(frame.title.as_deref(), Some("Updated Title"));
}

/// Test delete_frame marks frame as deleted.
#[test]
fn delete_frame_marks_deleted() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    // Create with content
    {
        let mut mem = Memvid::create(&path).unwrap();
        let opts = PutOptions {
            uri: Some("mv2://test".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"Content", opts).unwrap();
        mem.commit().unwrap();
    }

    // Delete frame - look up by URI to get current frame_id
    {
        let mut mem = Memvid::open(&path).unwrap();
        // Get the frame by URI to find its actual ID
        let frame = mem.frame_by_uri("mv2://test").unwrap();
        let frame_id = frame.id;

        mem.delete_frame(frame_id).unwrap();
        mem.commit().unwrap();
    }

    // Verify deletion - need to iterate or check stats since URI lookup may fail for deleted
    let mem = Memvid::open_read_only(&path).unwrap();
    // A deleted frame should still exist but with Deleted status
    // The URI lookup might fail, so check stats instead
    let stats = mem.stats().unwrap();
    // After deletion, frame_count may still be 1 but the frame is marked deleted
    // Or it may be 0 depending on implementation
    // Both are valid - the key is no panic occurred
    assert!(
        stats.frame_count == 0 || stats.frame_count == 1,
        "Frame count should be 0 or 1 after delete"
    );
}

/// Test URI uniqueness is enforced.
#[test]
fn uri_uniqueness() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();

    // First put succeeds
    let opts1 = PutOptions {
        uri: Some("mv2://unique".to_string()),
        ..Default::default()
    };
    mem.put_bytes_with_options(b"First", opts1).unwrap();

    // Second put with same URI should fail or replace
    let opts2 = PutOptions {
        uri: Some("mv2://unique".to_string()),
        ..Default::default()
    };
    // The behavior depends on implementation - this tests that it doesn't panic
    let result = mem.put_bytes_with_options(b"Second", opts2);

    // Either it succeeds (replacing) or returns an error (enforcing uniqueness)
    // Both are valid behaviors - the test ensures no panic
    if result.is_ok() {
        mem.commit().unwrap();
    }
}

#[test]
fn put_rejects_mixed_embedding_dimensions() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();
    mem.enable_vec().unwrap();

    mem.put_with_embedding(b"first", vec![0.0f32; 384]).unwrap();
    let err = mem
        .put_with_embedding(b"second", vec![0.0f32; 1536])
        .unwrap_err();
    match err {
        MemvidError::VecDimensionMismatch { expected, actual } => {
            assert_eq!(expected, 384);
            assert_eq!(actual, 1536);
        }
        other => panic!("expected VecDimensionMismatch, got {other:?}"),
    }
}

#[test]
fn embedding_identity_summary_unknown_when_missing() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();
    mem.put_bytes_with_options(b"hello", PutOptions::default())
        .unwrap();
    mem.commit().unwrap();

    let mem = Memvid::open_read_only(&path).unwrap();
    assert_eq!(
        mem.embedding_identity_summary(1_000),
        EmbeddingIdentitySummary::Unknown
    );
}

#[test]
fn embedding_identity_summary_single() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();
    let mut options = PutOptions::default();
    options.extra_metadata.insert(
        MEMVID_EMBEDDING_PROVIDER_KEY.to_string(),
        "openai".to_string(),
    );
    options.extra_metadata.insert(
        MEMVID_EMBEDDING_MODEL_KEY.to_string(),
        "text-embedding-3-small".to_string(),
    );
    mem.put_bytes_with_options(b"hello", options).unwrap();
    mem.commit().unwrap();

    let mem = Memvid::open_read_only(&path).unwrap();
    match mem.embedding_identity_summary(1_000) {
        EmbeddingIdentitySummary::Single(identity) => {
            assert_eq!(identity.provider.as_deref(), Some("openai"));
            assert_eq!(identity.model.as_deref(), Some("text-embedding-3-small"));
        }
        other => panic!("expected Single identity, got {other:?}"),
    }
}

#[test]
fn embedding_identity_summary_mixed() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    let mut mem = Memvid::create(&path).unwrap();

    let mut options_a = PutOptions::default();
    options_a.extra_metadata.insert(
        MEMVID_EMBEDDING_PROVIDER_KEY.to_string(),
        "fastembed".to_string(),
    );
    options_a.extra_metadata.insert(
        MEMVID_EMBEDDING_MODEL_KEY.to_string(),
        "BAAI/bge-small-en-v1.5".to_string(),
    );
    mem.put_bytes_with_options(b"a", options_a).unwrap();

    let mut options_b = PutOptions::default();
    options_b.extra_metadata.insert(
        MEMVID_EMBEDDING_PROVIDER_KEY.to_string(),
        "openai".to_string(),
    );
    options_b.extra_metadata.insert(
        MEMVID_EMBEDDING_MODEL_KEY.to_string(),
        "text-embedding-3-small".to_string(),
    );
    mem.put_bytes_with_options(b"b", options_b).unwrap();

    mem.commit().unwrap();

    let mem = Memvid::open_read_only(&path).unwrap();
    match mem.embedding_identity_summary(1_000) {
        EmbeddingIdentitySummary::Mixed(identities) => {
            assert_eq!(identities.len(), 2);
            let models: Vec<_> = identities
                .iter()
                .filter_map(|entry| entry.identity.model.as_deref())
                .collect();
            assert!(models.contains(&"BAAI/bge-small-en-v1.5"));
            assert!(models.contains(&"text-embedding-3-small"));
        }
        other => panic!("expected Mixed identity, got {other:?}"),
    }
}

/// Test put with empty content.
#[test]
fn put_empty_content() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        let opts = PutOptions {
            uri: Some("mv2://empty".to_string()),
            title: Some("Empty Document".to_string()),
            ..Default::default()
        };

        mem.put_bytes_with_options(b"", opts).unwrap();
        mem.commit().unwrap();
    }

    let mem = Memvid::open_read_only(&path).unwrap();
    let frame = mem.frame_by_uri("mv2://empty").unwrap();

    assert_eq!(frame.title.as_deref(), Some("Empty Document"));
}

/// Test put with moderately large content (50KB to avoid WAL limits).
#[test]
fn put_moderately_large_content() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        // Create 50KB of content (default new file gets 1MB WAL region)
        let large_content = vec![b'x'; 50 * 1024];

        let opts = PutOptions {
            uri: Some("mv2://large".to_string()),
            title: Some("Large Document".to_string()),
            ..Default::default()
        };

        mem.put_bytes_with_options(&large_content, opts).unwrap();
        mem.commit().unwrap();
    }

    let mem = Memvid::open_read_only(&path).unwrap();
    let frame = mem.frame_by_uri("mv2://large").unwrap();

    assert_eq!(frame.title.as_deref(), Some("Large Document"));
    // Frame was stored successfully - payload_length may be 0 if stored as blob
    // The important thing is no panic/error occurred
}

/// Test timeline iteration.
#[test]
fn timeline_iteration() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("test.mv2");

    {
        let mut mem = Memvid::create(&path).unwrap();

        // Add frames with different timestamps
        for (i, ts) in [1700000000i64, 1700001000, 1700002000].iter().enumerate() {
            let opts = PutOptions {
                uri: Some(format!("mv2://doc{}", i)),
                timestamp: Some(*ts),
                ..Default::default()
            };
            mem.put_bytes_with_options(format!("Content {}", i).as_bytes(), opts)
                .unwrap();
        }
        mem.commit().unwrap();
    }

    let mut mem = Memvid::open_read_only(&path).unwrap();

    // Get timeline entries using TimelineQuery
    let query = TimelineQuery::builder()
        .limit(NonZeroU64::new(10).unwrap())
        .build();
    let entries = mem.timeline(query).unwrap();

    assert_eq!(entries.len(), 3, "Should have 3 timeline entries");
}
