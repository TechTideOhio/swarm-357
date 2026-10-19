import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "packages/memvid-swarm-bridge/vendor"
CHANGES = {
    "memvid-core": {
        '[dependencies.lopdf]\nversion = "0.39"': '[dependencies.lopdf]\nversion = "0.42"',
        '[dependencies.pdf-extract]\nversion = "0.10"': '[dependencies.pdf-extract]\nversion = "0.12.1"',
    },
    "tantivy": {
        '[dependencies.lru]\nversion = "0.12.0"': '[dependencies.lru]\nversion = "0.18.2"',
    },
}
OMITTED = {"Cargo.lock", ".cargo_vcs_info.json"}


def main():
    for entry in json.loads((VENDOR / "provenance.json").read_text()):
        name = entry["crate"] + "-" + entry["version"]
        with urllib.request.urlopen(entry["download"], timeout=60) as response:
            archive = response.read()
        if hashlib.sha256(archive).hexdigest() != entry["registry_sha256"]:
            raise ValueError(f"Archive checksum mismatch: {name}")
        expected = set()
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
            for member in source.getmembers():
                if member.isdir():
                    continue
                if not member.isfile():
                    raise ValueError(f"Unexpected archive entry: {member.name}")
                relative = Path(member.name).relative_to(name)
                if str(relative) in OMITTED:
                    continue
                expected.add(relative)
                content = source.extractfile(member).read()
                if str(relative) == "Cargo.toml":
                    text = content.decode()
                    for before, after in CHANGES[entry["crate"]].items():
                        if text.count(before) != 1:
                            raise ValueError(f"Unexpected manifest: {name}")
                        text = text.replace(before, after)
                    content = text.encode()
                if entry["crate"] == "memvid-core" and str(relative) == "src/pii.rs":
                    before = b'let text = "Use key: api_key=' + b'abcdefghij1234567890xyz";'
                    after = b'let text = concat!("Use key: api_key=", "abcdefghij1234567890xyz");'
                    if content.count(before) != 1:
                        raise ValueError("Unexpected upstream synthetic key fixture")
                    content = content.replace(before, after)
                local = VENDOR / name / relative
                if local.is_symlink() or not local.is_file() or local.read_bytes() != content:
                    raise ValueError(f"Unexpected vendor change: {name}/{relative}")
        actual = {p.relative_to(VENDOR / name) for p in (VENDOR / name).rglob("*") if p.is_file() or p.is_symlink()}
        if actual != expected:
            raise ValueError(f"Unexpected vendor files: {name}: {actual ^ expected}")
        print(f"Verified {name}: {len(expected)} files")


if __name__ == "__main__":
    main()
