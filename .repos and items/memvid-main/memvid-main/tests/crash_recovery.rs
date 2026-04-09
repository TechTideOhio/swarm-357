use std::fs::OpenOptions;
use std::io::{Seek, SeekFrom, Write};

use memvid_core::{DoctorOptions, DoctorStatus, Memvid, MemvidError};

#[test]
#[cfg(not(target_os = "windows"))] // Windows file locking prevents proper corruption simulation
fn doctor_recovers_from_corrupted_commit_footer_single_commit() {
    let dir = tempfile::tempdir().expect("tmp");
    let path = dir.path().join("corrupt-footer.mv2");

    {
        let mut mem = Memvid::create(&path).expect("create");
        mem.put_bytes(b"hello world").expect("put");
        mem.commit().expect("commit");
    }

    // Corrupt the final bytes of the commit footer. This simulates an interrupted/partial write
    // at the end of the file (e.g., crash during sync).
    {
        let mut file = OpenOptions::new()
            .read(true)
            .write(true)
            .open(&path)
            .expect("open mv2");
        let len = file.metadata().expect("stat").len();
        assert!(len > 16, "mv2 too small to corrupt footer");
        file.seek(SeekFrom::End(-16)).expect("seek footer tail");
        file.write_all(&[0u8; 16]).expect("corrupt footer tail");
        file.sync_all().expect("sync");
    }

    // Snapshot reads are strict: without a valid commit footer, they fail fast.
    let err = Memvid::open_read_only(&path)
        .err()
        .expect("expected open_read_only to fail on corrupted footer");
    match err {
        MemvidError::InvalidToc { reason } => {
            let reason = reason.to_string();
            assert!(
                reason.contains("no valid commit footer")
                    || reason.contains("commit footer")
                    || reason.contains("footer"),
                "unexpected invalid toc reason: {reason}"
            );
        }
        other => panic!("unexpected error: {other}"),
    }

    // Exclusive opens can recover the TOC even when the footer is corrupted.
    Memvid::open(&path).expect("open with recovery");

    // Doctor should rewrite a clean TOC+footer so snapshot reads succeed again.
    let report = Memvid::doctor(&path, DoctorOptions::default()).expect("doctor");
    assert!(
        matches!(report.status, DoctorStatus::Healed | DoctorStatus::Clean),
        "unexpected doctor status: {:?}",
        report.status
    );

    Memvid::open_read_only(&path).expect("open_read_only after doctor");
}
