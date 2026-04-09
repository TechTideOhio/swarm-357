<!-- HEADER:START -->
<img width="2000" height="524" alt="Social Cover (9)" src="https://github.com/user-attachments/assets/cf66f045-c8be-494b-b696-b8d7e4fb709c" />
<!-- HEADER:END -->

<!-- FLAGS:START -->
<p align="center">
 <a href="../../README.md">🇺🇸 English</a>
 <a href="README.es.md">🇪🇸 Español</a>
 <a href="README.fr.md">🇫🇷 Français</a>
 <a href="README.so.md">🇸🇴 Soomaali</a>
 <a href="README.ar.md">🇸🇦 العربية</a>
 <a href="README.nl.md">🇧🇪/🇳🇱 Nederlands</a>
 <a href="README.hi.md">🇮🇳 हिन्दी</a>
 <a href="README.bn.md">🇧🇩 বাংলা</a>
 <a href="README.cs.md">🇨🇿 Čeština</a>
 <a href="README.ko.md">🇰🇷 한국어</a>
 <a href="README.ja.md">🇯🇵 日本語</a>
 <!-- Next Flag -->
</p>
<!-- FLAGS:END -->

<!-- NAV:START -->
<p align="center">
  <a href="https://www.memvid.com">Website</a>
  ·
  <a href="https://sandbox.memvid.com">Try Sandbox</a>
  ·
  <a href="https://docs.memvid.com">Docs</a>
  ·
  <a href="https://github.com/memvid/memvid/discussions">Discussions</a>
</p>
<!-- NAV:END -->

<!-- BADGES:START -->
<p align="center">
  <a href="https://crates.io/crates/memvid-core"><img src="https://img.shields.io/crates/v/memvid-core?style=flat-square&logo=rust" alt="Crates.io" /></a>
  <a href="https://docs.rs/memvid-core"><img src="https://img.shields.io/docsrs/memvid-core?style=flat-square&logo=docs.rs" alt="docs.rs" /></a>
  <a href="https://github.com/memvid/memvid/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License" /></a>
</p>

<p align="center">
  <a href="https://github.com/memvid/memvid/stargazers"><img src="https://img.shields.io/github/stars/memvid/memvid?style=flat-square&logo=github" alt="Stars" /></a>
  <a href="https://github.com/memvid/memvid/network/members"><img src="https://img.shields.io/github/forks/memvid/memvid?style=flat-square&logo=github" alt="Forks" /></a>
  <a href="https://github.com/memvid/memvid/issues"><img src="https://img.shields.io/github/issues/memvid/memvid?style=flat-square&logo=github" alt="Issues" /></a>
  <a href="https://discord.gg/2mynS7fcK7"><img src="https://img.shields.io/discord/1442910055233224745?style=flat-square&logo=discord&label=discord" alt="Discord" /></a>
</p>

<p align="center">
    <a href="https://trendshift.io/repositories/17293" target="_blank"><img src="https://trendshift.io/api/badge/repositories/17293" alt="memvid%2Fmemvid | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>
<!-- BADGES:END -->

<p align="center">
  <strong>Memvid est une couche mémoire à fichier unique pour agents IA, avec récupération instantanée et mémoire long terme.</strong><br/>
  Mémoire persistante, versionnée et portable, sans bases de données.
</p>

<h2 align="center">⭐️ Laissez une STAR pour soutenir le projet ⭐️</h2>
</p>

## Qu'est-ce que Memvid ?

Memvid est un système de mémoire IA portable qui regroupe vos données, embeddings, structure de recherche et métadonnées dans un seul fichier.

Au lieu d'exécuter des pipelines RAG complexes ou des bases de données vectorielles côté serveur, Memvid permet une récupération rapide directement depuis le fichier.

Le résultat est une couche mémoire agnostique au modèle, sans infrastructure, qui donne aux agents IA une mémoire persistante et longue durée qu'ils peuvent emporter partout.

---

## Pourquoi des images vidéo ?

Memvid s'inspire de l'encodage vidéo, non pas pour stocker de la vidéo, mais pour **organiser la mémoire IA en une séquence append-only ultra-efficace de Smart Frames.**

Une Smart Frame est une unité immuable qui stocke le contenu avec des horodatages, des checksums et des métadonnées de base.
Les frames sont regroupées d'une manière qui permet une compression, une indexation et des lectures parallèles efficaces.

Ce design basé sur les frames permet :

- Écritures append-only sans modifier ni corrompre les données existantes
- Requêtes sur des états mémoire passés
- Inspection type timeline de l'évolution des connaissances
- Sécurité en cas de crash via des frames immuables et validées
- Compression efficace grâce à des techniques adaptées de l'encodage vidéo

Le résultat est un fichier unique qui se comporte comme une timeline mémoire rembobinable pour les systèmes IA.

---

## Concepts de base

- **Moteur de mémoire vivant**
  Ajoutez, branchez et faites évoluer la mémoire en continu entre les sessions.

- **Capsule de Contexte  (`.mv2`)**
  Capsules mémoire autonomes et partageables avec règles et expiration.

- **Débogage par 'voyage temporel'**
  Rembobinez, rejouez ou branchez n'importe quel état mémoire.

- **Rappel intelligent**
  Accès mémoire local en moins de 5 ms avec cache prédictif.

- **Intelligence du codec**
  Sélection et mise à niveau automatiques de la compression au fil du temps.

---

## Cas d'usage
Memvid est une couche mémoire portable et sans serveur qui donne aux agents IA une mémoire persistante et un rappel rapide. Parce qu'il est agnostique au modèle, multimodal et fonctionne entièrement hors ligne, les développeurs utilisent Memvid pour un large éventail d'applications réelles.

- Agents IA longue durée
- Bases de connaissances d'entreprise
- Systèmes IA offline-first
- Compréhension de codebase
- Agents de support client
- Automatisation des workflows
- Copilotes ventes et marketing
- Assistants de connaissance personnels
- Agents médicaux, juridiques et financiers
- Workflows IA auditables et débogables
- Applications sur mesure

---

## SDKs & CLI

Utilisez Memvid dans votre langage préféré :

| Package | Installation | Liens |
|---------|---------|-------|
| **CLI** | `npm install -g memvid-cli` | [![npm](https://img.shields.io/npm/v/memvid-cli?style=flat-square)](https://www.npmjs.com/package/memvid-cli) |
| **Node.js SDK** | `npm install @memvid/sdk` | [![npm](https://img.shields.io/npm/v/@memvid/sdk?style=flat-square)](https://www.npmjs.com/package/@memvid/sdk) |
| **Python SDK** | `pip install memvid-sdk` | [![PyPI](https://img.shields.io/pypi/v/memvid-sdk?style=flat-square)](https://pypi.org/project/memvid-sdk/) |
| **Rust** | `cargo add memvid-core` | [![Crates.io](https://img.shields.io/crates/v/memvid-core?style=flat-square)](https://crates.io/crates/memvid-core) |

---

## Installation (Rust)

### Prérequis

- **Rust 1.85.0+** — Installer depuis [rustup.rs](https://rustup.rs)

### Ajouter à votre projet

```toml
[dependencies]
memvid-core = "2.0"
```

### Feature Flags

| Feature | Description |
|---------|-------------|
| `lex` | Full-text search with BM25 ranking (Tantivy) |
| `pdf_extract` | Pure Rust PDF text extraction |
| `vec` | Vector similarity search (HNSW + ONNX) |
| `clip` | CLIP visual embeddings for image search |
| `whisper` | Audio transcription with Whisper |
| `temporal_track` | Natural language date parsing ("last Tuesday") |
| `parallel_segments` | Multi-threaded ingestion |
| `encryption` | Password-based encryption capsules (.mv2e) |

Activez les features selon vos besoins :

```toml
[dependencies]
memvid-core = { version = "2.0", features = ["lex", "vec", "temporal_track"] }
```

---

## Démarrage rapide

```rust
use memvid_core::{Memvid, PutOptions, SearchRequest};

fn main() -> memvid_core::Result<()> {
    // Créer un nouveau fichier de mémoire
    let mut mem = Memvid::create("knowledge.mv2")?;

    // Ajouter des documents avec des métadonnées
    let opts = PutOptions::builder()
        .title("Meeting Notes")
        .uri("mv2://meetings/2024-01-15")
        .tag("project", "alpha")
        .build();
    mem.put_bytes_with_options(b"Q4 planning discussion...", opts)?;
    mem.commit()?;

    // Rechercher
    let response = mem.search(SearchRequest {
        query: "planning".into(),
        top_k: 10,
        snippet_chars: 200,
        ..Default::default()
    })?;

    for hit in response.hits {
        println!("{}: {}", hit.title.unwrap_or_default(), hit.text);
    }

    Ok(())
}
```

---

## Compiler

Cloner le repository :

```bash
git clone https://github.com/memvid/memvid.git
cd memvid
```

Compiler en mode debug :

```bash
cargo build
```

Compiler en mode release (optimisé) :

```bash
cargo build --release
```

Compiler avec des features spécifiques :

```bash
cargo build --release --features "lex,vec,temporal_track"
```

---

## Exécuter les tests

Exécuter tous les tests :

```bash
cargo test
```

Exécuter les tests avec sortie :

```bash
cargo test -- --nocapture
```

Exécuter un test spécifique :

```bash
cargo test test_name
```

Exécuter uniquement les tests d'intégration :

```bash
cargo test --test lifecycle
cargo test --test search
cargo test --test mutation
```

---

## Exemples

Le répertoire `examples/` contient des exemples fonctionnels :

### Utilisation de base

Démontre create, put, search et les opérations de timeline :

```bash
cargo run --example basic_usage
```

### Ingestion de PDF

Ingérer et rechercher des documents PDF (utilise l'article "Attention Is All You Need") :

```bash
cargo run --example pdf_ingestion
```

### Recherche visuelle CLIP

Recherche d'images à l'aide d'embeddings CLIP (nécessite la feature `clip`) :

```bash
cargo run --example clip_visual_search --features clip
```

### Transcription Whisper

Transcription audio (nécessite la feature `whisper`) :

```bash
cargo run --example test_whisper --features whisper
```

---

## Format de fichier

Tout est dans un seul fichier `.mv2` :

```
┌────────────────────────────┐
│ Header (4KB)               │  Magic, version, capacity
├────────────────────────────┤
│ Embedded WAL (1-64MB)      │  Crash recovery
├────────────────────────────┤
│ Data Segments              │  Compressed frames
├────────────────────────────┤
│ Lex Index                  │  Tantivy full-text
├────────────────────────────┤
│ Vec Index                  │  HNSW vectors
├────────────────────────────┤
│ Time Index                 │  Chronological ordering
├────────────────────────────┤
│ TOC (Footer)               │  Segment offsets
└────────────────────────────┘
```

Pas de `.wal`, `.lock`, `.shm` ou fichiers auxiliaires. Jamais.

Voir [MV2_SPEC.md](MV2_SPEC.md) pour la spécification complète du format de fichier.

---

## Support

Vous avez des questions ou des retours ?
Email : contact@memvid.com

**Laissez une ⭐ pour montrer votre soutien**

---

## Licence

Apache License 2.0 — voir le fichier [LICENSE](LICENSE) pour plus de détails.
