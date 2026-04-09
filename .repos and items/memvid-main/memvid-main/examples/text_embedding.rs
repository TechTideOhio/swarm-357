//! Example demonstrating local text embedding usage.
//!
//! This example shows how to:
//! - Create a local text embedder with default configuration (BGE-small)
//! - Generate embeddings for sample texts
//! - Compute cosine similarity between embeddings  
//! - Batch process multiple texts
//! - Use different models (BGE-base, Nomic, GTE-large)
//!
//! ## Prerequisites
//!
//! Before running this example, download the BGE-small model:
//!
//! ```bash
//! mkdir -p ~/.cache/memvid/text-models
//! curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/onnx/model.onnx' \
//!   -o ~/.cache/memvid/text-models/bge-small-en-v1.5.onnx
//! curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer.json' \
//!   -o ~/.cache/memvid/text-models/bge-small-en-v1.5_tokenizer.json
//! ```
//!
//! ## Run
//!
//! ```bash
//! cargo run --example text_embedding --features vec
//! ```

use memvid_core::Result;
#[cfg(feature = "vec")]
use memvid_core::text_embed::{LocalTextEmbedder, TextEmbedConfig};
#[cfg(feature = "vec")]
use memvid_core::types::embedding::EmbeddingProvider;

/// Compute cosine similarity between two vectors
fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
    assert_eq!(a.len(), b.len(), "Vectors must have same length");

    let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
    let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

    if norm_a > 0.0 && norm_b > 0.0 {
        dot_product / (norm_a * norm_b)
    } else {
        0.0
    }
}

fn main() -> Result<()> {
    println!("=== Local Text Embedding Example ===\n");

    // Create embedder with default config (BGE-small, 384 dimensions)
    println!("Creating local text embedder (BGE-small-en-v1.5)...");
    let config = TextEmbedConfig::default();
    let embedder = LocalTextEmbedder::new(config)?;

    println!("Model: {}", embedder.model());
    println!("Kind: {}", embedder.kind());
    println!("Dimensions: {}", embedder.dimension());
    println!("Ready: {}\n", embedder.is_ready());

    // Example 1: Generate embeddings for sample texts
    println!("--- Example 1: Single Text Embeddings ---");
    let text1 = "The quick brown fox jumps over the lazy dog";
    let text2 = "A fast auburn canine leaps above an idle hound";
    let text3 = "Python is a programming language";

    println!("Generating embeddings...");
    let emb1 = embedder.embed_text(text1)?;
    let emb2 = embedder.embed_text(text2)?;
    let emb3 = embedder.embed_text(text3)?;

    println!("✓ Generated {} embeddings of dimension {}\n", 3, emb1.len());

    // Example 2: Compute semantic similarity
    println!("--- Example 2: Semantic Similarity ---");
    let sim_1_2 = cosine_similarity(&emb1, &emb2);
    let sim_1_3 = cosine_similarity(&emb1, &emb3);
    let sim_2_3 = cosine_similarity(&emb2, &emb3);

    println!("Text 1: \"{}\"", text1);
    println!("Text 2: \"{}\"", text2);
    println!("Text 3: \"{}\"", text3);
    println!();
    println!("Similarity (1 ↔ 2): {:.4}", sim_1_2);
    println!("Similarity (1 ↔ 3): {:.4}", sim_1_3);
    println!("Similarity (2 ↔ 3): {:.4}", sim_2_3);
    println!();

    if sim_1_2 > sim_1_3 {
        println!("✓ As expected, similar texts (1 & 2) have higher similarity!");
    }
    println!();

    // Example 3: Batch processing
    println!("--- Example 3: Batch Processing ---");
    let documents = vec![
        "Artificial intelligence and machine learning",
        "Deep neural networks for computer vision",
        "Natural language processing with transformers",
        "The history of ancient Rome",
        "Cooking recipes for Italian cuisine",
    ];

    println!("Processing {} documents in batch...", documents.len());
    let batch_embeddings = embedder.embed_batch(&documents)?;
    println!("✓ Generated {} embeddings\n", batch_embeddings.len());

    // Find most similar pair
    println!("Finding most similar document pair...");
    let mut max_sim = 0.0;
    let mut max_pair = (0, 0);

    for i in 0..batch_embeddings.len() {
        for j in (i + 1)..batch_embeddings.len() {
            let sim = cosine_similarity(&batch_embeddings[i], &batch_embeddings[j]);
            if sim > max_sim {
                max_sim = sim;
                max_pair = (i, j);
            }
        }
    }

    println!("Most similar pair (similarity: {:.4}):", max_sim);
    println!("  [{}] \"{}\"", max_pair.0, documents[max_pair.0]);
    println!("  [{}] \"{}\"\n", max_pair.1, documents[max_pair.1]);

    // Example 4: Search query use case
    println!("--- Example 4: Search Query ---");
    let query = "machine learning algorithms";
    let query_emb = embedder.embed_text(query)?;

    println!("Query: \"{}\"", query);
    println!("\nRanked results:");

    let mut scores: Vec<(usize, f32)> = batch_embeddings
        .iter()
        .enumerate()
        .map(|(i, emb)| (i, cosine_similarity(&query_emb, emb)))
        .collect();

    scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

    for (rank, (idx, score)) in scores.iter().take(3).enumerate() {
        println!("  {}. [{:.4}] \"{}\"", rank + 1, score, documents[*idx]);
    }
    println!();

    // Example 5: Model unloading (memory management)
    println!("--- Example 5: Memory Management ---");
    println!("Model loaded: {}", embedder.is_loaded());
    embedder.unload()?;
    println!("After unload: {}", embedder.is_loaded());
    println!("✓ Model can be lazily reloaded on next use\n");

    // Example 6: Using different models (commented out - requires model download)
    println!("--- Example 6: Different Models ---");
    println!("Available models:");
    println!("  - bge-small-en-v1.5 (384d) - Default, fast");
    println!("  - bge-base-en-v1.5 (768d) - Better quality");
    println!("  - nomic-embed-text-v1.5 (768d) - Versatile");
    println!("  - gte-large (1024d) - Highest quality");
    println!();
    println!("To use a different model:");
    println!("  let config = TextEmbedConfig::bge_base();");
    println!("  let embedder = LocalTextEmbedder::new(config)?;");
    println!();

    println!("=== Example Complete ===");
    println!("\nKey takeaways:");
    println!("✓ Local embeddings run entirely offline (no API calls)");
    println!("✓ Models are lazy-loaded on first use");
    println!("✓ Embeddings are L2-normalized for cosine similarity");
    println!("✓ Batch processing is efficient for multiple texts");
    println!("✓ Similar texts have higher cosine similarity scores");

    Ok(())
}
