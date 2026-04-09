//! Regression tests for replay segment persistence/integrity.
//!
//! The replay segment is written to the `.mv2` file when ending a recording session.
//! Historically this could corrupt Tantivy (lexical) segments by writing replay bytes
//! at an incorrect offset and moving the TOC footer backwards.

#[cfg(all(feature = "lex", feature = "replay"))]
use memvid_core::{Memvid, PutOptions, SearchRequest};
#[cfg(all(feature = "lex", feature = "replay"))]
use tempfile::TempDir;

#[test]
#[cfg(all(feature = "lex", feature = "replay"))]
fn replay_save_does_not_corrupt_lex_index() {
    let dir = TempDir::new().unwrap();
    let path = dir.path().join("replay_integrity.mv2");

    // Create a memory with a Tantivy-backed lexical index.
    {
        let mut mem = Memvid::create(&path).unwrap();
        mem.enable_lex().unwrap();

        let opts = PutOptions {
            uri: Some("mv2://doc/0".to_string()),
            title: Some("Doc".to_string()),
            search_text: Some("Climate change and sustainability are important.".to_string()),
            ..Default::default()
        };
        mem.put_bytes_with_options(b"climate", opts).unwrap();
        mem.commit().unwrap();

        // Record a session that includes a FIND action.
        mem.start_session(Some("Test".to_string()), None).unwrap();
        let _ = mem
            .search(SearchRequest {
                query: "climate".to_string(),
                top_k: 5,
                snippet_chars: 120,
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
        mem.end_session().unwrap();

        // Mirror CLI behaviour: finalize, save replay, then commit again.
        mem.commit().unwrap();
        mem.save_replay_sessions().unwrap();
        mem.commit().unwrap();
    }

    // Reopen and ensure Tantivy loads and lexical search still works.
    let mut reopened = Memvid::open_read_only(&path).unwrap();
    let results = reopened
        .search(SearchRequest {
            query: "climate".to_string(),
            top_k: 5,
            snippet_chars: 120,
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
        "expected lexical search to work after saving replay sessions"
    );

    // Also ensure replay sessions can be loaded (read-only is fine).
    reopened.load_replay_sessions().unwrap();
    let sessions = reopened.list_sessions();
    assert_eq!(sessions.len(), 1, "expected one recorded replay session");
}
