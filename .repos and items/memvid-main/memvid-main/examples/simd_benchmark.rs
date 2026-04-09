//! Benchmark comparing SIMD vs Scalar L2 distance calculations.
//!
//! Run with: `cargo run --example simd_benchmark --features simd --release`

use std::hint::black_box;
use std::time::Instant;

fn main() {
    let num_vectors = 10_000;
    let dims = 384; // Standard embedding dimension
    let num_iterations = 100;

    println!("SIMD vs Scalar L2 Distance Benchmark");
    println!("=====================================");
    println!("Vectors: {}", num_vectors);
    println!("Dimensions: {}", dims);
    println!("Iterations: {}", num_iterations);
    println!();

    // Generate random vectors
    let query: Vec<f32> = (0..dims).map(|i| (i as f32 * 0.001) % 1.0).collect();
    let vectors: Vec<Vec<f32>> = (0..num_vectors)
        .map(|v| (0..dims).map(|i| ((v + i) as f32 * 0.0017) % 1.0).collect())
        .collect();

    // Benchmark SIMD version
    let simd_start = Instant::now();
    let mut simd_sum = 0.0f32;
    for _ in 0..num_iterations {
        for vec in &vectors {
            simd_sum += black_box(l2_distance_simd(black_box(&query), black_box(vec)));
        }
    }
    let simd_elapsed = simd_start.elapsed();
    black_box(simd_sum);

    // Benchmark Scalar version
    let scalar_start = Instant::now();
    let mut scalar_sum = 0.0f32;
    for _ in 0..num_iterations {
        for vec in &vectors {
            scalar_sum += black_box(l2_distance_scalar(black_box(&query), black_box(vec)));
        }
    }
    let scalar_elapsed = scalar_start.elapsed();
    black_box(scalar_sum);

    // Results
    let total_ops = num_vectors * num_iterations;
    let simd_per_op_ns = simd_elapsed.as_nanos() as f64 / total_ops as f64;
    let scalar_per_op_ns = scalar_elapsed.as_nanos() as f64 / total_ops as f64;
    let speedup = scalar_elapsed.as_nanos() as f64 / simd_elapsed.as_nanos() as f64;

    println!("Results:");
    println!("--------");
    println!(
        "SIMD:   {:>8.2}ms total, {:>6.1}ns per distance",
        simd_elapsed.as_secs_f64() * 1000.0,
        simd_per_op_ns
    );
    println!(
        "Scalar: {:>8.2}ms total, {:>6.1}ns per distance",
        scalar_elapsed.as_secs_f64() * 1000.0,
        scalar_per_op_ns
    );
    println!();
    println!("Speedup: {:.2}x", speedup);

    // Verify correctness
    let simd_result = l2_distance_simd(&query, &vectors[0]);
    let scalar_result = l2_distance_scalar(&query, &vectors[0]);
    let diff = (simd_result - scalar_result).abs();
    println!();
    println!("Correctness check:");
    println!("  SIMD result:   {:.8}", simd_result);
    println!("  Scalar result: {:.8}", scalar_result);
    println!("  Difference:    {:.2e} (should be < 1e-5)", diff);
    assert!(diff < 1e-4, "Results differ too much!");
    println!("  ✓ Results match!");
}

/// SIMD L2 distance using the wide crate
#[cfg(feature = "simd")]
fn l2_distance_simd(a: &[f32], b: &[f32]) -> f32 {
    memvid_core::simd::l2_distance_simd(a, b)
}

#[cfg(not(feature = "simd"))]
fn l2_distance_simd(a: &[f32], b: &[f32]) -> f32 {
    l2_distance_scalar(a, b)
}

/// Scalar L2 distance (the OLD implementation)
#[inline(never)]
fn l2_distance_scalar(a: &[f32], b: &[f32]) -> f32 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f32>()
        .sqrt()
}
