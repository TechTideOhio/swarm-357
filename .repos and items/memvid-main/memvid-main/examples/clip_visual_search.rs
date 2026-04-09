//! CLIP Visual Search Example
//!
//! Demonstrates using CLIP embeddings to search PDF pages and images
//! using natural language queries.
//!
//! Run with:
//! ```bash
//! cargo run --example clip_visual_search --features clip,pdfium -- /path/to/pdf
//! ```
//!
//! Prerequisites:
//! 1. Download the MobileCLIP-S2 ONNX models:
//!    ```bash
//!    mkdir -p ~/.local/share/memvid/models
//!    curl -L 'https://huggingface.co/Xenova/mobileclip_s2/resolve/main/onnx/vision_model_int8.onnx' \
//!         -o ~/.local/share/memvid/models/mobileclip-s2_vision.onnx
//!    curl -L 'https://huggingface.co/Xenova/mobileclip_s2/resolve/main/onnx/text_model_int8.onnx' \
//!         -o ~/.local/share/memvid/models/mobileclip-s2_text.onnx
//!    ```
//!
//! 2. For PDF page rendering, install pdfium:
//!    - macOS: `brew install nicbarker/pdfium/pdfium-mac-arm64` or `pdfium-mac-x64`
//!    - Linux: Download from https://github.com/nicbarker/pdfium-builds/releases

fn main() -> memvid_core::Result<()> {
    #[cfg(not(feature = "clip"))]
    {
        eprintln!("This example requires the 'clip' feature.");
        eprintln!("Run with: cargo run --example clip_visual_search --features clip");
        Ok(())
    }

    #[cfg(feature = "clip")]
    {
        use memvid_core::clip::{ClipConfig, ClipIndex, ClipIndexBuilder, ClipModel};
        use std::env;
        use std::path::PathBuf;
        use tempfile::tempdir;

        println!("=== CLIP Visual Search Example ===\n");

        // Get PDF path from args or use default
        let args: Vec<String> = env::args().collect();
        let pdf_path = if args.len() > 1 {
            PathBuf::from(&args[1])
        } else {
            // Default to the SP Global Impact Report if no path provided
            PathBuf::from(
                "/Users/olow/Desktop/memvid-org/brickfield/sp-global-impact-report-2024.pdf",
            )
        };

        if !pdf_path.exists() {
            eprintln!("PDF not found: {}", pdf_path.display());
            eprintln!(
                "Usage: cargo run --example clip_visual_search --features clip,pdfium -- /path/to/pdf"
            );
            return Ok(());
        }

        println!("PDF: {}", pdf_path.display());

        // Initialize CLIP model
        println!("\n1. Loading CLIP model...");
        let config = ClipConfig::default();
        println!("   Model: {}", config.model_name);
        println!("   Models dir: {}", config.models_dir.display());

        let clip = match ClipModel::new(config) {
            Ok(model) => {
                println!("   Model initialized (lazy loading)");
                model
            }
            Err(e) => {
                eprintln!("   Failed to initialize CLIP: {}", e);
                eprintln!("\n   Make sure to download the models first:");
                eprintln!("   mkdir -p ~/.local/share/memvid/models");
                eprintln!(
                    "   curl -L 'https://huggingface.co/Xenova/mobileclip_s2/resolve/main/onnx/vision_model_int8.onnx' \\"
                );
                eprintln!("        -o ~/.local/share/memvid/models/mobileclip-s2_vision.onnx");
                return Ok(());
            }
        };

        // For this demo, we'll create synthetic embeddings since PDF rendering
        // requires pdfium which may not be available
        println!("\n2. Building CLIP index with sample embeddings...");

        let mut builder = ClipIndexBuilder::new();

        // Simulate embeddings for 10 "pages" with different visual concepts
        // In real usage, you would:
        // 1. Render each PDF page to an image
        // 2. Pass the image to clip.encode_image(&image)
        // 3. Store the embedding with the page's frame_id

        let sample_concepts: Vec<(&str, Vec<f32>)> = vec![
            // These would be real embeddings from actual images in production
            (
                "charts and graphs",
                random_embedding(clip.dims() as usize, 1),
            ),
            (
                "sustainability report cover",
                random_embedding(clip.dims() as usize, 2),
            ),
            (
                "ESG metrics table",
                random_embedding(clip.dims() as usize, 3),
            ),
            (
                "environmental impact diagram",
                random_embedding(clip.dims() as usize, 4),
            ),
            (
                "carbon emissions chart",
                random_embedding(clip.dims() as usize, 5),
            ),
            (
                "renewable energy infographic",
                random_embedding(clip.dims() as usize, 6),
            ),
            (
                "corporate governance structure",
                random_embedding(clip.dims() as usize, 7),
            ),
            (
                "diversity statistics",
                random_embedding(clip.dims() as usize, 8),
            ),
            (
                "supply chain map",
                random_embedding(clip.dims() as usize, 9),
            ),
            (
                "financial highlights",
                random_embedding(clip.dims() as usize, 10),
            ),
        ];

        for (i, (concept, embedding)) in sample_concepts.iter().enumerate() {
            builder.add_document(i as u64, Some(i as u32), embedding.clone());
            println!("   Added page {} ({})", i + 1, concept);
        }

        let artifact = builder.finish()?;
        println!(
            "\n   Index built: {} vectors, {} dimensions",
            artifact.vector_count, artifact.dimension
        );

        // Decode the index for searching
        let index = ClipIndex::decode(&artifact.bytes)?;

        // Demonstrate text-to-image search
        println!("\n3. Searching with natural language queries...\n");

        // Try encoding a text query
        println!("   Encoding query: 'sustainability charts'");
        match clip.encode_text("sustainability charts") {
            Ok(query_embedding) => {
                println!("   Query embedding: {} dimensions", query_embedding.len());

                let hits = index.search(&query_embedding, 3);
                println!("\n   Top 3 matches:");
                for (rank, hit) in hits.iter().enumerate() {
                    let concept = sample_concepts
                        .get(hit.frame_id as usize)
                        .map(|(c, _)| *c)
                        .unwrap_or("unknown");
                    println!(
                        "   {}. Page {} ({}) - distance: {:.4}",
                        rank + 1,
                        hit.frame_id + 1,
                        concept,
                        hit.distance
                    );
                }
            }
            Err(e) => {
                eprintln!("   Failed to encode text (model not loaded): {}", e);
                eprintln!("   Make sure the text model ONNX file is downloaded.");
            }
        }

        // Demo with Memvid integration
        println!("\n4. Creating Memvid memory with CLIP support...");

        let dir = tempdir().expect("failed to create temp dir");
        let path = dir.path().join("clip_demo.mv2");

        let mut mem = memvid_core::Memvid::create(&path)?;

        // Enable CLIP index
        mem.enable_clip()?;
        println!("   CLIP index enabled");

        // Add some sample documents
        let options = memvid_core::PutOptions::builder()
            .title("SP Global Impact Report 2024 - Page 1")
            .uri("mv2://reports/sp-global/page-1")
            .build();
        mem.put_bytes_with_options(
            b"This page contains sustainability charts and ESG metrics.",
            options,
        )?;

        mem.commit()?;
        println!("   Added sample document");

        let stats = mem.stats()?;
        println!("\n   Memory stats:");
        println!("   - Frames: {}", stats.frame_count);
        println!("   - Has CLIP index: {}", stats.has_clip_index);

        // Search CLIP index (would use pre-computed query embedding in production)
        // Since we haven't added actual CLIP embeddings to the memory,
        // the search would return empty results - this is just to show the API

        println!("\n=== Example completed successfully! ===");
        println!("\nTo use CLIP in production:");
        println!("1. During ingestion: Generate CLIP embeddings for images/PDF pages");
        println!("2. Store embeddings in the CLIP index alongside text content");
        println!("3. At query time: Encode the text query with clip.encode_text()");
        println!("4. Search the CLIP index with mem.search_clip(&query_embedding, limit)");

        Ok(())
    }
}

/// Generate a pseudo-random embedding for demo purposes
/// In production, use clip.encode_image() on actual images
#[cfg(feature = "clip")]
fn random_embedding(dims: usize, seed: u64) -> Vec<f32> {
    use std::collections::hash_map::DefaultHasher;
    use std::hash::{Hash, Hasher};

    let mut hasher = DefaultHasher::new();
    let mut embedding = Vec::with_capacity(dims);

    for i in 0..dims {
        (seed, i).hash(&mut hasher);
        let hash = hasher.finish();
        // Generate pseudo-random float between -1 and 1
        let val = ((hash as f32) / (u64::MAX as f32)) * 2.0 - 1.0;
        embedding.push(val);
        hasher = DefaultHasher::new();
    }

    // L2 normalize
    let norm: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
    if norm > 1e-10 {
        for v in &mut embedding {
            *v /= norm;
        }
    }

    embedding
}
