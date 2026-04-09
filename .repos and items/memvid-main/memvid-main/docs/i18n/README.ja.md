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
<strong>Memvidは、AIエージェントのための即時検索と長期記憶を備えた単一ファイル型メモリレイヤーです。</strong>
</br>
データベースを必要とせず、永続化、バージョン管理、ポータブル性を備えたメモリを実現します。
</p>

<h2 align="center">⭐️ スターで応援お願いします ⭐️</h2>
</p>

## Memvidとは？

Memvidは、データ、埋め込み、検索構造、メタデータを１つのファイルにパッケージ化するポータブルAIメモリシステムです。

複雑なRAGパイプラインやサーバーベースのベクトルデータベースを運用する代わりに、Memvidを使用することで直接ファイルから高速な検索が可能になります。

その結果、モデルに依存せずインフラ不要のメモリレイヤーが実現し、AIエージェントはどこでも使える永続的な長期記憶を持つことができます。

---

## スマートフレーム (Smart Frames) とは？

Memvidは、（ビデオを保存するためではなく）**追記に特化した効率的なスマートフレームのシーケンスとしてAIメモリを整理するため**に、ビデオエンコーディング技術から着想を得ています。

スマートフレームは、コンテンツをタイムスタンプ、チェックサム、基本メタデータとともに保存する不変（イミュータブル）な単位です。フレームは効率的な圧縮、インデックス作成、並列読み取りができるようグループ化されています。

このフレームベースの設計により、以下が可能になります。

- 既存のデータを変更したり破損したりすることなくデータを追加
- 過去のメモリ状態に対するクエリ
- 知識がどのように進化するかをタイムライン形式で検査
- コミットされた不変フレームによるクラッシュ耐性
- ビデオエンコーディング技術を応用した効率的な圧縮

その結果、AIシステムの「巻き戻し可能なメモリタイムライン」のように機能する単一のファイルが生成されます。

---

## コアコンセプト

- **成長するメモリエンジン (Living Memory Engine)**
  セッションをまたいでメモリを継続的に追加、分岐、進化させます。

- **カプセル・コンテキスト (`.mv2`)**
  ルールや有効期限を設定できる、自己完結型で共有可能なメモリカプセル。

- **タイムトラベル・デバッグ**
  任意のメモリ状態を巻き戻し、再現、または分岐させることができます。

- **スマート・リコール**
  予測キャッシングによる5ミリ秒未満のローカルメモリーアクセス。

- **コーデック・インテリジェンス**
  圧縮方式を自動選択し、時間の経過とともにアップグレードします。

---

## ユースケース

Memvidは、AIエージェントに永続的な記憶と高速な呼び出し機能を提供するポータブルでサーバーレスなメモリレイヤーです。モデルに依存せず、マルチモーダルに対応し、完全にオフラインで動作するため、実用的なアプリケーションで幅広く利用されています。

- 長期稼働AIエージェント
- エンタープライズ向けナレッジベース
- オフラインファーストAIシステム
- コードベースの理解
- カスタマーサポートエージェント
- ワークフロー自動化
- セールス・マーケティング支援
- パーソナル・ナレッジ・アシスタント
- 医療・法律・金融特化型エージェント
- 監査・デバッグ可能なAIワークフロー
- カスタムアプリケーション

---

## SDK と CLI

お好みの言語でMemvidを利用できます。

| パッケージ      | インストール                | リンク                                                                                                              |
| --------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **CLI**         | `npm install -g memvid-cli` | [![npm](https://img.shields.io/npm/v/memvid-cli?style=flat-square)](https://www.npmjs.com/package/memvid-cli)       |
| **Node.js SDK** | `npm install @memvid/sdk`   | [![npm](https://img.shields.io/npm/v/@memvid/sdk?style=flat-square)](https://www.npmjs.com/package/@memvid/sdk)     |
| **Python SDK**  | `pip install memvid-sdk`    | [![PyPI](https://img.shields.io/pypi/v/memvid-sdk?style=flat-square)](https://pypi.org/project/memvid-sdk/)         |
| **Rust**        | `cargo add memvid-core`     | [![Crates.io](https://img.shields.io/crates/v/memvid-core?style=flat-square)](https://crates.io/crates/memvid-core) |

---

## インストール (Rust)

### 要件

- **Rust 1.85.0+** - [rustup.rs](https://rustup.rs) からインストールしてください。

### プロジェクトへの追加

```toml
[dependencies]
memvid-core = "2.0"

```

### 機能フラグ (Feature Flags)

| 機能                | 説明                                                           |
| ------------------- | -------------------------------------------------------------- |
| `lex`               | BM25ランキングによる全文検索 (Tantivy)                         |
| `pdf_extract`       | Pure RustによるPDFテキスト抽出                                 |
| `vec`               | ベクトル類似性検索 (HNSW + ONNXによるローカルテキスト埋め込み) |
| `clip`              | 画像検索用のCLIPビジュアル埋め込み                             |
| `whisper`           | Whisperによる音声文字起こし                                    |
| `temporal_track`    | 自然言語による日付解析 (例: "last Tuesday")                    |
| `parallel_segments` | マルチスレッドによるデータ取り込み                             |
| `encryption`        | パスワードベースの暗号化カプセル (.mv2e)                       |

以下のように、必要に応じて有効化してください。

```toml
[dependencies]
memvid-core = { version = "2.0", features = ["lex", "vec", "temporal_track"] }
```

---

## クイックスタート

```rust
use memvid_core::{Memvid, PutOptions, SearchRequest};

fn main() -> memvid_core::Result<()> {
    // 新しいメモリファイルを作成
    let mut mem = Memvid::create("knowledge.mv2")?;

    // メタデータ付きでドキュメントを追加
    let opts = PutOptions::builder()
        .title("Meeting Notes")
        .uri("mv2://meetings/2024-01-15")
        .tag("project", "alpha")
        .build();
    mem.put_bytes_with_options(b"Q4 planning discussion...", opts)?;
    mem.commit()?;

    // 検索の実行
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

## ビルド

リポジトリをクローン：

```bash
git clone https://github.com/memvid/memvid.git
cd memvid
```

デバッグモードでビルド：

```bash
cargo build
```

リリースモードでビルド（最適化）：

```bash
cargo build --release
```

特定の機能フラグ付きでビルド：

```bash
cargo build --release --features "lex,vec,temporal_track"
```

---

## テストの実行

すべてのテストを実行：

```bash
cargo test
```

標準出力でテストを実行：

```bash
cargo test -- --nocapture
```

特定のテストを実行：

```bash
cargo test test_name
```

統合テストのみを実行：

```bash
cargo test --test lifecycle
cargo test --test search
cargo test --test mutation
```

---

## サンプル (Examples)

`examples/` ディレクトリには、実際に動作するサンプルコードが用意されています。

### 基本的な使い方 (Basic Usage)

作成 (create)、追加 (put)、検索 (search)、およびタイムライン操作のデモです。

```bash
cargo run --example basic_usage
```

### PDFの取り込み (PDF Ingestion)

PDFドキュメントの取り込みと検索のサンプルです。（論文「Attention Is All You Need」を使用）

```bash
cargo run --example pdf_ingestion
```

### CLIPによる画像検索 (CLIP Visual Search)

CLIP埋め込みを使用した画像検索のサンプルです。

```bash
cargo run --example clip_visual_search --features clip
```

### Whisperによる文字起こし (Whisper Transcription)

音声文字起こしのサンプルです。

```bash
cargo run --example test_whisper --features whisper
```

---

## テキスト埋め込みモデル

`vec` 機能は、ONNXモデルを使用したローカルでのテキスト埋め込みをサポートしています。利用前にモデルファイルを手動でダウンロードする必要があります。

### 推奨：BGE-small (デフォルト)

高速で効率的なBGE-smallモデル（384次元）をダウンロードします。

```bash
mkdir -p ~/.cache/memvid/text-models

# ONNXモデルのダウンロード
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5.onnx

# トークナイザーのダウンロード
curl -L 'https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/bge-small-en-v1.5_tokenizer.json
```

### モデル一覧

| モデル                  | 次元数 | サイズ | 最適な用途               |
| ----------------------- | ------ | ------ | ------------------------ |
| `bge-small-en-v1.5`     | 384    | ~120MB | デフォルト（高速・軽量） |
| `bge-base-en-v1.5`      | 768    | ~420MB | より高い精度が必要な場合 |
| `nomic-embed-text-v1.5` | 768    | ~530MB | 多目的なタスク           |
| `gte-large`             | 1024   | ~1.3GB | 最高精度                 |

### 他のモデル

**BGE-base** (768次元):

```bash
curl -L 'https://huggingface.co/BAAI/bge-base-en-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/bge-base-en-v1.5.onnx
curl -L 'https://huggingface.co/BAAI/bge-base-en-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/bge-base-en-v1.5_tokenizer.json
```

**Nomic** (768次元):

```bash
curl -L 'https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/nomic-embed-text-v1.5.onnx
curl -L 'https://huggingface.co/nomic-ai/nomic-embed-text-v1.5/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/nomic-embed-text-v1.5_tokenizer.json
```

**GTE-large** (1024次元):

```bash
curl -L 'https://huggingface.co/thenlper/gte-large/resolve/main/onnx/model.onnx' \
  -o ~/.cache/memvid/text-models/gte-large.onnx
curl -L 'https://huggingface.co/thenlper/gte-large/resolve/main/tokenizer.json' \
  -o ~/.cache/memvid/text-models/gte-large_tokenizer.json
```

### 使用例

```rust
use memvid_core::text_embed::{LocalTextEmbedder, TextEmbedConfig};
use memvid_core::types::embedding::EmbeddingProvider;

// デフォルトモデルを使用する場合 (BGE-small)
let config = TextEmbedConfig::default();
let embedder = LocalTextEmbedder::new(config)?;

let embedding = embedder.embed_text("hello world")?;
assert_eq!(embedding.len(), 384);

// モデルを変更する場合
let config = TextEmbedConfig::bge_base();
let embedder = LocalTextEmbedder::new(config)?;
```

類似性の計算と検索ランキングを含む完全な例については、`examples/text_embedding.rs` を参照してください。

---

## ファイル構成

すべてが単一の `.mv2` ファイルに収められます。

```
┌────────────────────────────┐
│ ヘッダー (4KB)              │  マジックナンバー、バージョン、容量
├────────────────────────────┤
│ 組み込みWAL (1-64MB)       │  クラッシュリカバリ用
├────────────────────────────┤
│ データセグメント            │  圧縮されたフレーム
├────────────────────────────┤
│ 全文検索インデックス (Lex)  │  Tantivy全文検索
├────────────────────────────┤
│ ベクトルインデックス (Vec)  │  HNSWベクトル
├────────────────────────────┤
│ タイムインデックス          │  時系列順序
├────────────────────────────┤
│ TOC (フッター)             │  セグメントオフセット
└────────────────────────────┘

```

`.wal`、`.lock`、`.shm` などのサイドカーファイルは一切生成されません。

フォーマット仕様の詳細は [MV2_SPEC.md](MV2_SPEC.md) を参照してください。

---

## サポート

ご質問やフィードバックはこちらまでご連絡ください。
メール: contact@memvid.com

**⭐でプロジェクトをサポートしてください。**

---

## ライセンス

Apache License 2.0 - 詳細は [LICENSE](LICENSE) ファイルをご覧ください。
