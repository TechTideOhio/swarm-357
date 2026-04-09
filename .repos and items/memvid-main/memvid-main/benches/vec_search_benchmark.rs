use criterion::{Criterion, black_box, criterion_group, criterion_main};
use memvid_core::types::FrameId;
use memvid_core::vec::{VecDocument, VecIndex, VecIndexBuilder};

fn generate_vectors(count: usize, dim: usize) -> Vec<Vec<f32>> {
    let mut vectors = Vec::with_capacity(count);
    for _ in 0..count {
        let mut vec = Vec::with_capacity(dim);
        for _ in 0..dim {
            vec.push(fastrand::f32());
        }
        vectors.push(vec);
    }
    vectors
}

fn bench_search_10k(c: &mut Criterion) {
    let count = 10_000;
    let dim = 128; // Smaller dimension for faster setup in benchmarks
    let vectors = generate_vectors(count, dim);
    let query = generate_vectors(1, dim).pop().unwrap();

    // Build HNSW Index (via Builder which triggers HNSW for > 1000)
    let mut builder = VecIndexBuilder::new();
    for (i, vec) in vectors.iter().enumerate() {
        builder.add_document(i as FrameId, vec.clone());
    }
    let artifact = builder.finish().expect("finish hnsw");
    let hnsw_index = VecIndex::decode(&artifact.bytes).expect("decode hnsw");

    // Build Brute Force Index (Force Uncompressed)
    let documents: Vec<VecDocument> = vectors
        .iter()
        .enumerate()
        .map(|(i, vec)| VecDocument {
            frame_id: i as FrameId,
            embedding: vec.clone(),
        })
        .collect();
    let brute_index = VecIndex::Uncompressed { documents };

    let mut group = c.benchmark_group("search_10k");

    group.bench_function("hnsw", |b| {
        b.iter(|| {
            hnsw_index.search(black_box(&query), black_box(10));
        })
    });

    group.bench_function("brute_force", |b| {
        b.iter(|| {
            brute_index.search(black_box(&query), black_box(10));
        })
    });

    group.finish();
}

fn bench_search_50k(c: &mut Criterion) {
    let count = 50_000;
    let dim = 128;
    let vectors = generate_vectors(count, dim);
    let query = generate_vectors(1, dim).pop().unwrap();

    let mut builder = VecIndexBuilder::new();
    for (i, vec) in vectors.iter().enumerate() {
        builder.add_document(i as FrameId, vec.clone());
    }
    let artifact = builder.finish().expect("finish hnsw");
    let hnsw_index = VecIndex::decode(&artifact.bytes).expect("decode hnsw");

    let documents: Vec<VecDocument> = vectors
        .iter()
        .enumerate()
        .map(|(i, vec)| VecDocument {
            frame_id: i as FrameId,
            embedding: vec.clone(),
        })
        .collect();
    let brute_index = VecIndex::Uncompressed { documents };

    let mut group = c.benchmark_group("search_50k");

    group.bench_function("hnsw", |b| {
        b.iter(|| {
            hnsw_index.search(black_box(&query), black_box(10));
        })
    });

    group.bench_function("brute_force", |b| {
        b.iter(|| {
            brute_index.search(black_box(&query), black_box(10));
        })
    });

    group.finish();
}

fn bench_search_100k(c: &mut Criterion) {
    let count = 100_000;
    let dim = 128;
    let vectors = generate_vectors(count, dim);
    let query = generate_vectors(1, dim).pop().unwrap();

    let mut builder = VecIndexBuilder::new();
    for (i, vec) in vectors.iter().enumerate() {
        builder.add_document(i as FrameId, vec.clone());
    }
    let artifact = builder.finish().expect("finish hnsw");
    let hnsw_index = VecIndex::decode(&artifact.bytes).expect("decode hnsw");

    let documents: Vec<VecDocument> = vectors
        .iter()
        .enumerate()
        .map(|(i, vec)| VecDocument {
            frame_id: i as FrameId,
            embedding: vec.clone(),
        })
        .collect();
    let brute_index = VecIndex::Uncompressed { documents };

    let mut group = c.benchmark_group("search_100k");

    group.bench_function("hnsw", |b| {
        b.iter(|| {
            let _ = hnsw_index.search(black_box(&query), black_box(10));
        })
    });

    group.bench_function("brute_force", |b| {
        b.iter(|| {
            let _ = brute_index.search(black_box(&query), black_box(10));
        })
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_search_10k,
    bench_search_50k,
    bench_search_100k
);
criterion_main!(benches);
