//! CLI bridge for Python `MemoryManager` → Memvid `.mv2` files.

use std::io::{self, Read};
use std::path::PathBuf;

use clap::{Parser, Subcommand};
use memvid_core::{AclEnforcementMode, Memvid, PutOptions, SearchRequest};

#[derive(Parser)]
#[command(name = "memvid-swarm-bridge", version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Create a new `.mv2` file at `path`.
    Create { path: PathBuf },
    /// Put stdin bytes as a document with URI/title; commits.
    Put {
        path: PathBuf,
        #[arg(long)]
        uri: String,
        #[arg(long, default_value = "swarm")]
        title: String,
    },
    /// Lexical search; JSON `SearchResponse` on stdout.
    Search {
        path: PathBuf,
        query: String,
        #[arg(long, default_value_t = 10)]
        top_k: usize,
    },
    /// Integrity verification; JSON `VerificationReport` on stdout.
    Verify {
        path: PathBuf,
        #[arg(long, default_value_t = false)]
        deep: bool,
    },
}

fn main() {
    if let Err(e) = run() {
        eprintln!("memvid-swarm-bridge: {e}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Create { path } => {
            Memvid::create(&path).map_err(|e| e.to_string())?;
            Ok(())
        }
        Commands::Put {
            path,
            uri,
            title,
        } => {
            let mut body = Vec::new();
            io::stdin()
                .read_to_end(&mut body)
                .map_err(|e| e.to_string())?;
            let mut mem = if path.exists() {
                Memvid::open(&path).map_err(|e| e.to_string())?
            } else {
                Memvid::create(&path).map_err(|e| e.to_string())?
            };
            let opts = PutOptions::builder()
                .title(title)
                .uri(uri)
                .tag("source", "swarm357")
                .build();
            mem.put_bytes_with_options(&body, opts)
                .map_err(|e| e.to_string())?;
            mem.commit().map_err(|e| e.to_string())?;
            Ok(())
        }
        Commands::Search {
            path,
            query,
            top_k,
        } => {
            let mem = Memvid::open(&path).map_err(|e| e.to_string())?;
            let request = SearchRequest {
                query,
                top_k,
                snippet_chars: 400,
                uri: None,
                scope: None,
                cursor: None,
                as_of_frame: None,
                as_of_ts: None,
                no_sketch: false,
                acl_context: None,
                acl_enforcement_mode: AclEnforcementMode::Audit,
            };
            let response = mem.search(request).map_err(|e| e.to_string())?;
            let s = serde_json::to_string(&response).map_err(|e| e.to_string())?;
            println!("{s}");
            Ok(())
        }
        Commands::Verify { path, deep } => {
            let report = Memvid::verify(&path, deep).map_err(|e| e.to_string())?;
            let s = serde_json::to_string(&report).map_err(|e| e.to_string())?;
            println!("{s}");
            Ok(())
        }
    }
}
