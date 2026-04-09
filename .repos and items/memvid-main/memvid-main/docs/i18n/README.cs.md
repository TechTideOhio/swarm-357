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
  <strong>Memvid je jednosouborová paměťová vrstva pro AI agenty s okamžitým vyhledáváním a dlouhodobou pamětí.</strong><br/>
  Trvalá, verzovaná a přenosná paměť, bez databází.
</p>

<h2 align="center">⭐️ Zanechte hvězdičku na podporu projektu ⭐️</h2>
</p>

## Co je Memvid?

Memvid je systém pro tvorbu AI pamětí, který balí vaše data, embeddingy, strukturu vyhledávání a metadata do jediného souboru.

Místo spouštění složitých RAG řešení nebo serverových vektorových databází umožňuje Memvid rychlé vyhledávání přímo ze souboru.

Výsledkem je modelově nezávislá paměťová vrstva bez infrastruktury, která poskytuje agentům AI trvalou, dlouhodobou paměť, kterou lze přenášet kamkoli.

---

## Co jsou inteligentní rámce?

Memvid čerpá inspiraci z enkódování videa, nikoli za účelem ukládání videa, ale za účelem **organizace paměti AI jako ultraefektivní sekvence inteligentních rámců, do kterých lze data  pouze přidávat.**

Inteligentní rámec je neměnná jednotka, která ukládá obsah spolu s časovými značkami, kontrolními součty a základními metadaty.
Rámce jsou seskupeny tak, aby umožňovaly efektivní kompresi, indexování a paralelní čtení.

Tento design založený na rámcích umožňuje:

-  Pouze zápisy bez úpravy nebo poškození existujících dat
-  Dotazy na minulé stavy paměti
-  Kontrolu vývoje znalostí ve stylu časové osy
-  Bezpečnost proti selhání díky závazným, neměnným rámcům
-  Efektivní kompresi pomocí technik převzatých z kódování videa

Výsledkem je jediný soubor, který se chová jako časová osa paměti pro systémy AI, ve které lze snadno hledat.

---

## Základní koncepty

-   **Living Memory Engine**
    Kontinuální přidávání, rozvětvování a vývoj paměti, napříč relacemi.

-   **Capsule Context (`.mv2`)**
    Samostatné, sdílené paměťové kapsle s pravidly a dobou platnosti.

-   **Time-Travel Debugging**
    Převíjení, přehrávání nebo rozvětvování libovolného stavu paměti.

-   **Smart Recall**
    Přístup k lokální paměti za méně než 5 ms s prediktivním ukládáním do mezipaměti.

-   **Codec Intelligence**
    Automaticky vybírá a vylepšuje kompresi v průběhu času.

---

## Případy použití

Memvid je přenosná paměťová vrstva bez serveru, která poskytuje agentům AI trvalou paměť a rychlé vyvolání. Protože je modelově nezávislá, multimodální a funguje zcela offline, vývojáři používají Memvid v široké škále reálných aplikací.

- Dlouhodobě běžící AI agenti
- Firemní znalostní báze
- Offline-First AI systémy
- Porozumění kódu
- Agenti zákaznické podpory
- Automatizace pracovních postupů
- Asistenti prodeje a marketingu
- Osobní znalostní asistenti
- Lékařští, právní a finanční agenti
- Auditovatelné a laditelné AI pracovní postupy
- Vlastní aplikace

---

## SDK a CLI

Používejte Memvid ve svém preferovaném jazyce:

| Balíček         | Instalace                   | Odkazy                                                                                                              |
| --------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **CLI**         | `npm install -g memvid-cli` | [![npm](https://img.shields.io/npm/v/memvid-cli?style=flat-square)](https://www.npmjs.com/package/memvid-cli)       |
| **Node.js SDK** | `npm install @memvid/sdk`   | [![npm](https://img.shields.io/npm/v/@memvid/sdk?style=flat-square)](https://www.npmjs.com/package/@memvid/sdk)     |
| **Python SDK**  | `pip install memvid-sdk`    | [![PyPI](https://img.shields.io/pypi/v/memvid-sdk?style=flat-square)](https://pypi.org/project/memvid-sdk/)         |
| **Rust**        | `cargo add memvid-core`     | [![Crates.io](https://img.shields.io/crates/v/memvid-core?style=flat-square)](https://crates.io/crates/memvid-core) |

---

## Instalace (Rust)

### Požadavky

-   **Rust 1.85.0+** — Instalace z [rustup.rs](https://rustup.rs)

### Přidejte do svého projektu

```toml
[dependencies]
memvid-core = "2.0"
```

### Funkční příznaky

| Funkce              | Popis                                                      |
| ------------------- | ---------------------------------------------------------- |
| `lex`               | Fulltextové vyhledávání s hodnocením BM25 (Tantivy)        |
| `pdf_extract`       | Čistá extrakce textu z PDF v Rustu                         |
| `vec`               | Vektorové vyhledávání podobnosti (HNSW + lokální vkládání textu přes ONNX) |
| `clip`              | Vizuální vkládání CLIP pro vyhledávání obrázků             |
| `whisper`           | Přepis zvuku pomocí Whisper                                |
| `temporal_track`    | Analýza datumu v přirozeném jazyce ("minulé úterý")        |
| `parallel_segments` | Vícevláknové načítání                                      |
| `encryption`        | Kapsle šifrované pomocí hesla (.mv2e)                 |

Povolte funkce podle potřeby:

```toml
[dependencies]
memvid-core = { version = "2.0", features = ["lex", "vec", "temporal_track"] }
```

---

## Rychlý start

```rust
use memvid_core::{Memvid, PutOptions, SearchRequest};

fn main() -> memvid_core::Result<()> {
    // Vytvoř nový paměťový soubor
    let mut mem = Memvid::create("knowledge.mv2")?;

    // Přidej dokumenty s metadaty
    let opts = PutOptions::builder()
        .title("Zápis jednání")
        .uri("mv2://meetings/2024-01-15")
        .tag("project", "alpha")
        .build();
    mem.put_bytes_with_options(b"Q4 plánované diskuze...", opts)?;
    mem.commit()?;

    // Vyhledávání
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

## Sestavení

Klonujte repozitář:

```bash
git clone https://github.com/memvid/memvid.git
cd memvid
```

Sestavení v režimu developkment:

```bash
cargo build
```

Sestavení v režimu production (optimalizované):

```bash
cargo build --release
```

Sestavení s konkrétními funkcemi:

```bash
cargo build --release --features "lex,vec,temporal_track"
```

---

## Spuštění testů

Spuštění všech testů:

```bash
cargo test
```

Spuštění testů s výstupem:

```bash
cargo test -- --nocapture
```

Spuštění konkrétního testu:

```bash
cargo test test_name
```

Spuštění pouze integračních testů:

```bash
cargo test --test lifecycle
cargo test --test search
cargo test --test mutation
```

---

## Příklady

Adresář `examples/` obsahuje funkční příklady:

### Základní použití

Demonstruje operace vytváření, vkládání, vyhledávání a práci s časovou osou:

```bash
cargo run --example basic_usage
```

### Načítání PDF

Načítání a vyhledávání v dokumentech PDF (demo používá dokument "Attention Is All You Need"):

```bash
cargo run --example pdf_ingestion
```

### Vizuální vyhledávání CLIP

Vyhledávání obrázků pomocí vložení CLIP (vyžaduje funkci `clip`):

```bash
cargo run --example clip_visual_search --features clip
```

### Přepis Whisper

Přepis zvuku (vyžaduje funkci `whisper`):

```bash
cargo run --example test_whisper --features whisper
```

---

## Modely vkládání textu

Funkce `vec` zahrnuje podporu lokálního vkládání textu pomocí modelů ONNX. Před použitím lokálního vkládání textu je nutné ručně stáhnout soubory modelů.

### Rychlý start: BGE-small (doporučeno)

Stáhněte si výchozí model BGE-small (384 dimenzí, rychlý a efektivní):

```bash
mkdir -p ~/.cache/memvid/text-models

# Download ONNX model
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5.onnx

# Download tokenizer
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5_tokenizer.json
```

### Dostupné modely

| Model                   | Rozměry    | Velikost | Nejvhodnější pro     |
| ----------------------- | ---------- | ------- | --------------------- |
| `bge-small-en-v1.5`     | 384        | ~120 MB | Výchozí, rychlý       |
| `bge-base-en-v1.5`      | 768        | ~420 MB | Lepší kvalita         |
| `nomic-embed-text-v1.5` | 768        | ~530 MB | Univerzální úkoly     |
| `gte-large`             | 1024       | ~1,3 GB | Nejvyšší kvalita      |

### Další modely

**BGE-base** (768 dimensions):
```bash
curl -L 'https://huggingface.co/BAAI/bge-base-en-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/bge-base-en-v1.5.onnx
curl -L 'https://huggingface.co/BAAI/bge-base-en-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/bge-base-en-v1.5_tokenizer.json
```

**Nomic** (768 dimensions):
```bash
curl -L 'https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/nomic-embed-text-v1.5.onnx
curl -L 'https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/nomic-embed-text-v1.5_tokenizer.json
```

**GTE-large** (1024 dimensions):
```bash
curl -L 'https://huggingface.co/thenlper/gte-large/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/gte-large.onnx
curl -L 'https://huggingface.co/thenlper/gte-large/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/gte-large_tokenizer.json
```

### Použití v kódu

```rust
use memvid_core::text_embed::{LocalTextEmbedder, TextEmbedConfig};
use memvid_core::types::embedding::EmbeddingProvider;

// Použít výchozí model (BGE-small)
let config = TextEmbedConfig::default();
let embedder = LocalTextEmbedder::new(config)?;

let embedding = embedder.embed_text("hello world")?;
assert_eq!(embedding.len(), 384);

// Použijte jiný model
let config = TextEmbedConfig::bge_base();
let embedder = LocalTextEmbedder::new(config)?;
```

Kompletní příklad s výpočtem podobnosti a hodnocením vyhledávání najdete v souboru `examples/text_embedding.rs`.

---

## Formát souboru

Vše je uloženo v jediném souboru `.mv2`:

```
┌────────────────────────────┐
│ Záhlaví (4 KB)             │  Magie, verze, kapacita
├────────────────────────────┤
│ Embedded WAL (1-64 MB)     │  Obnova po selhání
├────────────────────────────┤
│ Datové segmenty            │  Komprimované rámce
├────────────────────────────┤
│ Lex Index                  │  Tantivy full-text
├────────────────────────────┤
│ Vec Index                  │  Vektory HNSW
├────────────────────────────┤
│ Time Index                 │  Chronologické řazení
├────────────────────────────┤
│ TOC (zápatí)               │  Segmentové posuny
└────────────────────────────┘
```

Žádné další soubory, jako je `.wal`, `.lock`, `.shm` nejsou potřeba. Nikdy.

Kompletní specifikace formátu souboru najdete v [MV2_SPEC.md](MV2_SPEC.md).

---

## Podpora

Máte dotazy nebo připomínky?
E-mail: contact@memvid.com

**Dejte ⭐ a projevte svou podporu**

---

## Licence

Apache License 2.0 — podrobnosti najdete v souboru [LICENSE](LICENSE).
