//! Whisper transcription example demonstrating audio transcription.
//!
//! Run with:
//! ```bash
//! cargo run --example test_whisper --features whisper -- /path/to/audio
//! ```

#[cfg(feature = "whisper")]
use memvid_core::{WhisperConfig, WhisperTranscriber};
#[cfg(feature = "whisper")]
use std::env;
#[cfg(feature = "whisper")]
use std::path::PathBuf;
#[cfg(feature = "whisper")]
use std::time::Instant;

#[cfg(not(feature = "whisper"))]
fn main() {
    eprintln!(
        "This example requires the `whisper` feature.\n\
         Re-run with:\n\
         cargo run --example test_whisper --features whisper -- /path/to/audio"
    );
}

#[cfg(feature = "whisper")]
fn main() {
    // Get audio path from args
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: cargo run --example test_whisper --features whisper -- /path/to/audio");
        eprintln!("\nExample:");
        eprintln!(
            "  cargo run --example test_whisper --features whisper -- examples/call_sale.mp3"
        );
        return;
    }

    let audio_path = PathBuf::from(&args[1]);

    if !audio_path.exists() {
        eprintln!("ERROR: Audio file not found at {:?}", audio_path);
        eprintln!("Usage: cargo run --example test_whisper --features whisper -- /path/to/audio");
        return;
    }

    println!("=== Whisper Transcription Example ===\n");
    println!("Creating Whisper transcriber...");
    let start = Instant::now();
    let config = WhisperConfig::default();
    println!("Model dir: {:?}", config.models_dir);
    println!("Model name: {}", config.model_name);

    let mut transcriber = WhisperTranscriber::new(&config).expect("Failed to create transcriber");
    println!("Transcriber created in {:?}", start.elapsed());

    println!("\nTranscribing audio file: {}", audio_path.display());
    let start = Instant::now();

    match transcriber.transcribe_file(&audio_path) {
        Ok(result) => {
            println!("Transcription completed in {:?}", start.elapsed());
            println!("\n=== Transcription Result ===");
            println!("Duration: {:.2} seconds", result.duration_secs);
            println!("Language: {}", result.language);
            println!("\nText:\n{}", result.text);

            if !result.segments.is_empty() {
                println!("\n=== Segments ===");
                for seg in &result.segments {
                    println!("[{:.2}s - {:.2}s] {}", seg.start, seg.end, seg.text);
                }
            }
        }
        Err(e) => {
            eprintln!("Transcription failed: {}", e);
        }
    }

    println!("\n=== Transcription example completed! ===");
}
