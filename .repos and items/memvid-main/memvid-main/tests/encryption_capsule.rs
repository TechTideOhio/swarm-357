//! Encryption capsule tests (.mv2e).

#[cfg(feature = "encryption")]
use memvid_core::encryption::{EncryptionError, Mv2eHeader, lock_file, unlock_file};
#[cfg(feature = "encryption")]
use memvid_core::{Memvid, PutOptions};

#[cfg(feature = "encryption")]
use std::fs::read;
#[cfg(feature = "encryption")]
use std::path::Path;
#[cfg(feature = "encryption")]
use tempfile::TempDir;

#[test]
#[cfg(feature = "encryption")]
fn mv2e_header_roundtrip() {
    let header = Mv2eHeader {
        magic: memvid_core::encryption::MV2E_MAGIC,
        version: memvid_core::encryption::MV2E_VERSION,
        kdf_algorithm: memvid_core::encryption::KdfAlgorithm::Argon2id,
        cipher_algorithm: memvid_core::encryption::CipherAlgorithm::Aes256Gcm,
        salt: [1u8; memvid_core::encryption::SALT_SIZE],
        nonce: [2u8; memvid_core::encryption::NONCE_SIZE],
        original_size: 1024,
        reserved: [0u8; 4],
    };

    let encoded = header.encode();
    let decoded = Mv2eHeader::decode(&encoded).expect("decode");

    assert_eq!(decoded.magic, header.magic);
    assert_eq!(decoded.version, header.version);
    assert_eq!(decoded.salt, header.salt);
    assert_eq!(decoded.nonce, header.nonce);
    assert_eq!(decoded.original_size, header.original_size);
}

#[test]
#[cfg(feature = "encryption")]
fn lock_unlock_roundtrip_preserves_bytes() {
    let dir = TempDir::new().expect("tmp");
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");
    let restored_path = dir.path().join("restored.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        mem.put_bytes_with_options(
            b"hello",
            PutOptions {
                title: Some("doc".to_string()),
                labels: vec!["note".to_string()],
                ..Default::default()
            },
        )
        .expect("put");
        mem.commit().expect("commit");
    }

    lock_file(&mv2_path, Some(mv2e_path.as_path()), b"test-password-123").expect("lock");
    unlock_file(
        &mv2e_path,
        Some(restored_path.as_path()),
        b"test-password-123",
    )
    .expect("unlock");

    let original = read(&mv2_path).expect("read original");
    let restored = read(&restored_path).expect("read restored");
    assert_eq!(original, restored);
}

#[test]
#[cfg(feature = "encryption")]
fn wrong_password_fails() {
    let dir = TempDir::new().expect("tmp");
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        mem.put_bytes(b"hello").expect("put");
        mem.commit().expect("commit");
    }

    lock_file(&mv2_path, Some(mv2e_path.as_path()), b"password-a").expect("lock");
    let err = unlock_file(&mv2e_path, None, b"password-b").expect_err("should fail");
    assert!(matches!(err, EncryptionError::Decryption { .. }));
}

/// Test streaming encryption with a large file (>1MB to trigger multiple chunks)
/// Note: The mv2 file format includes a 64MB WAL by default, so even small content
/// creates large files. This test focuses on verifying the streaming format works.
#[test]
#[cfg(feature = "encryption")]
fn streaming_encryption_large_file() {
    let dir = TempDir::new().expect("tmp");
    let mv2_path = dir.path().join("large.mv2");
    let mv2e_path = dir.path().join("large.mv2e");
    let restored_path = dir.path().join("large_restored.mv2");

    // Create a memory file with modest content (the file will be large due to WAL)
    {
        let mut mem = Memvid::create(&mv2_path).expect("create");

        // Add 5 entries - this should create a file >1MB due to WAL overhead
        for i in 0..5 {
            let content = format!("Entry {} with content: {}", i, "x".repeat(10_000));
            mem.put_bytes_with_options(
                content.as_bytes(),
                PutOptions {
                    title: Some(format!("Entry {}", i)),
                    labels: vec!["test".to_string()],
                    ..Default::default()
                },
            )
            .expect("put");
        }
        mem.commit().expect("commit");
    }

    // The file should be >1MB due to embedded WAL
    let original_size = std::fs::metadata(&mv2_path).expect("metadata").len();
    assert!(
        original_size > 1_000_000,
        "File should be >1MB, got {} bytes",
        original_size
    );
    println!(
        "Created test file: {} bytes ({:.2} MB)",
        original_size,
        original_size as f64 / 1_000_000.0
    );

    // Encrypt using streaming
    lock_file(
        &mv2_path,
        Some(mv2e_path.as_path()),
        b"streaming-test-password",
    )
    .expect("lock");

    // Verify encrypted file has streaming marker (reserved[0] == 0x01)
    let encrypted_bytes = read(&mv2e_path).expect("read encrypted");
    let header_bytes: [u8; Mv2eHeader::SIZE] = encrypted_bytes[..Mv2eHeader::SIZE]
        .try_into()
        .expect("slice to array");
    let header = Mv2eHeader::decode(&header_bytes).expect("decode header");
    assert_eq!(
        header.reserved[0], 0x01,
        "Should use streaming format (reserved[0] == 0x01)"
    );
    println!(
        "Encrypted file: {} bytes, streaming format confirmed",
        encrypted_bytes.len()
    );

    // Decrypt
    unlock_file(
        &mv2e_path,
        Some(restored_path.as_path()),
        b"streaming-test-password",
    )
    .expect("unlock");

    // Verify content matches
    let original = read(&mv2_path).expect("read original");
    let restored = read(&restored_path).expect("read restored");
    assert_eq!(original.len(), restored.len(), "Size mismatch");
    assert_eq!(original, restored, "Content mismatch");
    println!(
        "Decryption successful, {} bytes restored correctly",
        restored.len()
    );

    // Verify the restored file is valid and readable
    let mem = Memvid::open(&restored_path).expect("open restored");
    let stats = mem.stats().expect("stats");
    assert!(
        stats.frame_count >= 5,
        "Should have at least 5 frames, got {}",
        stats.frame_count
    );
    println!("Restored memory verified: {} frames", stats.frame_count);
}

/// Test that wrong password still fails with streaming format
#[test]
#[cfg(feature = "encryption")]
fn wrong_password_fails_streaming() {
    let dir = TempDir::new().expect("tmp");
    let mv2_path = dir.path().join("test_stream.mv2");
    let mv2e_path = dir.path().join("test_stream.mv2e");

    // Create a file (will be >1MB due to WAL overhead)
    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        for i in 0..3 {
            let content = format!("Entry {} {}", i, "data".repeat(10_000));
            mem.put_bytes(content.as_bytes()).expect("put");
        }
        mem.commit().expect("commit");
    }

    lock_file(&mv2_path, Some(mv2e_path.as_path()), b"correct-password").expect("lock");

    // Verify streaming format (files >1MB use streaming)
    let encrypted = read(&mv2e_path).expect("read");
    let header_bytes: [u8; Mv2eHeader::SIZE] = encrypted[..Mv2eHeader::SIZE]
        .try_into()
        .expect("slice to array");
    let header = Mv2eHeader::decode(&header_bytes).expect("decode");
    assert_eq!(header.reserved[0], 0x01, "Should use streaming format");

    // Wrong password should fail
    let err = unlock_file(&mv2e_path, None, b"wrong-password").expect_err("should fail");
    assert!(
        matches!(err, EncryptionError::Decryption { .. }),
        "Expected Decryption error, got {:?}",
        err
    );
    println!("Wrong password correctly rejected for streaming format");
}

/// Helper: reads and decodes the Mv2eHeader from an encrypted file.
#[cfg(feature = "encryption")]
fn read_header(path: &Path) -> Mv2eHeader {
    let bytes = read(path).expect("read file");
    let header_bytes: [u8; Mv2eHeader::SIZE] =
        bytes[..Mv2eHeader::SIZE].try_into().expect("header bytes");
    Mv2eHeader::decode(&header_bytes).expect("decode header")
}

/*
    This test verifies two things:
    1. Legacy format marker exists (reserved[0] == 0x00)
    2. Decryption works (new code can decrypt old format files)
*/
#[test]
#[ignore = "legacy_test.mv2 fixture missing - regenerate with legacy encryption code"]
#[cfg(feature = "encryption")]
fn decrypt_legacy_format_with_new_code() {
    use std::path::PathBuf;

    let mut fixture_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    fixture_dir.push("tests/fixtures");

    let original_mv2 = fixture_dir.join("legacy_test.mv2");
    let original_mv2e = fixture_dir.join("legacy_test.mv2e");

    assert!(original_mv2.exists(), "legacy mv2 fixture missing");
    assert!(original_mv2e.exists(), "legacy mv2e fixture missing");

    let header = read_header(&original_mv2e);
    assert_eq!(header.reserved[0], 0x00, "should be legacy format");

    let dir = TempDir::new().expect("temp");
    let decrypted_path = dir.path().join("decrypted.mv2");

    unlock_file(
        &original_mv2e,
        Some(decrypted_path.as_ref()),
        b"legacy-password",
    )
    .expect("unlock");

    let original = read(&original_mv2).expect("original");
    let decrypted = read(&decrypted_path).expect("decrypted");
    assert_eq!(original, decrypted);
}

/*
    This test verifies dispatcher logic selects correct decoder:
    1. New file (reserved[0] = 0x01) → uses streaming path
    2. Legacy file (reserved[0] = 0x00) → uses oneshot path
*/
#[test]
#[cfg(feature = "encryption")]
fn auto_detection_chooses_correct_decoder() {
    // password for legacy file decryption: [b"legacy-password"]
    use std::path::PathBuf;

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");
    let decrypted_path = dir.path().join("decrypted.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).expect("memvid");
        mem.put_bytes(b"testing: auto detection chooses correct decoder.")
            .unwrap();
        mem.commit().unwrap();
    }

    lock_file(&mv2_path, Some(&mv2e_path), b"test-password").expect("lock");

    let header = read_header(&mv2e_path);
    assert_eq!(header.reserved[0], 0x01, "new file should use streaming");

    unlock_file(&mv2e_path, Some(&decrypted_path), b"test-password").expect("unlock");

    let mut fixture_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    fixture_dir.push("tests/fixtures");
    let legacy_mv2e = fixture_dir.join("legacy_test.mv2e");
    let legacy_decrypted = dir.path().join("legacy_decrypted.mv2");

    let header = read_header(&legacy_mv2e);
    assert_eq!(header.reserved[0], 0x00, "legacy file should be oneshot");

    unlock_file(&legacy_mv2e, Some(&legacy_decrypted), b"legacy-password").expect("unlock");
}

/*
    This test verifies legacy file upgrade flow:
    1. Decrypt legacy file (reserved[0] = 0x00)
    2. Re-encrypt → produces streaming format (reserved[0] = 0x01)
    3. Content integrity preserved after upgrade
*/
#[test]
#[ignore = "legacy_test.mv2 fixture missing - regenerate with legacy encryption code"]
#[cfg(feature = "encryption")]
fn legacy_file_upgrade_on_reencrypt() {
    use std::{fs, path::PathBuf};

    let dir = TempDir::new().expect("temp");
    let legacy_mv2 = dir.path().join("test.mv2");
    let legacy_mv2e = dir.path().join("test.mv2e");
    let legacy_decrypted = dir.path().join("decrypt.mv2");
    let new_mv2e = dir.path().join("new.mv2e");
    let new_decrypted = dir.path().join("new_decrypted.mv2");

    let mut fixture_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    fixture_dir.push("tests/fixtures");

    fs::copy(fixture_dir.join("legacy_test.mv2"), &legacy_mv2).expect("copy mv2");
    fs::copy(fixture_dir.join("legacy_test.mv2e"), &legacy_mv2e).expect("copy mv2");

    let header = read_header(&legacy_mv2e);
    assert_eq!(header.reserved[0], 0x00);

    unlock_file(&legacy_mv2e, Some(&legacy_decrypted), b"legacy-password").expect("unlock");

    lock_file(&legacy_decrypted, Some(&new_mv2e), b"new-password").expect("lock");

    let header = read_header(&new_mv2e);
    assert_eq!(header.reserved[0], 0x01, "should now be streaming format");

    unlock_file(&new_mv2e, Some(&new_decrypted), b"new-password").expect("unlock new");

    let original_content = read(&legacy_mv2).expect("read legacy");
    let final_content = read(&new_decrypted).expect("read new decrypted");
    assert_eq!(
        final_content, original_content,
        "content should match after upgrade"
    );
}

/*
    Test: Invalid magic header detection
    1. Create and encrypt a valid .mv2 file
    2. Corrupt the magic bytes (MV2E → 0x00000000)
    3. Attempt decrypt → should return InvalidMagic error
*/
#[test]
#[cfg(feature = "encryption")]
fn invalid_magic_header() {
    use std::fs;

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");

    {
        let mut mem = Memvid::create(&mv2_path).expect("create");
        mem.put_bytes(b"testing invalid magic header").unwrap();
        mem.commit().unwrap();
    }

    lock_file(&mv2_path, Some(&mv2e_path), b"test-password").expect("lock");

    let mut bytes = fs::read(&mv2e_path).unwrap();
    bytes[..4].copy_from_slice(&[0u8; 4]);
    fs::write(&mv2e_path, &bytes).unwrap();

    let err = unlock_file(&mv2e_path, None, b"test-password")
        .expect_err("should fail with invalid magic");

    assert!(matches!(
        err,
        EncryptionError::InvalidMagic {
            expected: _,
            found: _
        }
    ));
}

/*
    Test: Truncated file error handling
    1. Create and encrypt a valid .mv2 file
    2. Truncate the .mv2e file (cut in half)
    3. Attempt decrypt → should return error (not crash)
*/
#[test]
#[cfg(feature = "encryption")]
fn truncated_file_fails_gracefully() {
    use std::fs;

    let dir = TempDir::new().expect("temp");
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");
    let truncated_path = dir.path().join("truncated.mv2e");

    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.put_bytes(b"testing truncated files").unwrap();
        mem.commit().unwrap();
    }

    lock_file(&mv2_path, Some(&mv2e_path), b"test-password").expect("lock");

    let bytes = read(&mv2e_path).unwrap();
    let truncated = &bytes[..bytes.len() / 2];
    fs::write(&truncated_path, truncated).unwrap();

    let result = unlock_file(&truncated_path, None, b"test-password");

    assert!(result.is_err());
}

/*
    Test: Non-MV2 file rejection
    1. Create random file (not .mv2)
    2. Attempt encrypt → should return NotMv2File error
*/
#[test]
#[cfg(feature = "encryption")]
fn non_mv2_file_rejected() {
    use std::fs;

    let dir = TempDir::new().expect("temp");
    let fake_file = dir.path().join("not_a_mv2.txt");

    fs::write(&fake_file, b"this is a fake file, not a mv2 file").unwrap();

    let err =
        lock_file(&fake_file, None, b"test-password").expect_err("should reject non mv2 file");

    assert!(matches!(err, EncryptionError::NotMv2File { path: _ }))
}

/*
    Test: Exact chunk boundary (5MB)
    1. Create 5MB content → multiple 1MB chunks
    2. Encrypt/decrypt roundtrip
    3. Verify content integrity
*/
#[test]
#[cfg(feature = "encryption")]
fn exact_chunk_boundary_file() {
    let dir = TempDir::new().unwrap();
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");
    let decrypted_path = dir.path().join("decrypted.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.put_bytes(&[0u8; 1024 * 1024 * 5]).unwrap();
        mem.commit().unwrap();
    }

    lock_file(&mv2_path, Some(&mv2e_path), b"test-password").expect("lock");

    let header = read_header(&mv2e_path);
    assert_eq!(header.reserved[0], 0x01);

    unlock_file(&mv2e_path, Some(&decrypted_path), b"test-password").expect("unlock");

    let original_content = read(&mv2_path).expect("read original");
    let final_content = read(&decrypted_path).expect("read final");
    assert_eq!(final_content, original_content);
}

/*
    Test: Empty MV2 file encryption
    1. Create .mv2 with no frames
    2. Encrypt/decrypt roundtrip
    3. Verify integrity and Memvid::open works
*/
#[test]
#[cfg(feature = "encryption")]
fn empty_mv2_file_encryption() {
    let dir = TempDir::new().unwrap();
    let mv2_path = dir.path().join("test.mv2");
    let mv2e_path = dir.path().join("test.mv2e");
    let decrypted_path = dir.path().join("decrypted.mv2");

    {
        let mut mem = Memvid::create(&mv2_path).unwrap();
        mem.commit().unwrap();
    }

    lock_file(&mv2_path, Some(&mv2e_path), b"test-password").expect("lock");

    unlock_file(&mv2e_path, Some(&decrypted_path), b"test-password").expect("unlock");

    let original_content = read(&mv2_path).unwrap();
    let final_content = read(&decrypted_path).unwrap();
    assert_eq!(final_content, original_content);

    {
        let mem = Memvid::open(&decrypted_path).expect("should open decrypted file");
        let stats = mem.stats().expect("stats");
        assert_eq!(stats.frame_count, 0, "empty file should have 0 frames");
    }
}
