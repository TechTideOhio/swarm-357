"""Integration test: full put/search cycle via MemvidBridge (skipped if binary missing)."""

import json
from pathlib import Path

import pytest

from techtide_swarm.memvid_bridge import MemvidBridge, resolve_bridge_binary


bridge_available = resolve_bridge_binary() is not None
skip_reason = "memvid-swarm-bridge binary not on PATH or MEMVID_SWARM_BRIDGE not set"


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_create_put_search_verify(tmp_path: Path):
    mv2 = tmp_path / "test-layer.mv2"
    bridge = MemvidBridge(mv2)

    bridge.create()
    assert mv2.exists()

    bridge.put(
        uri="swarm://test/key",
        title="research-001->sales-001",
        body=b"Acme Corp raised enterprise pricing 20% in Q1 2026.",
    )

    results = bridge.search("Acme pricing", top_k=5)
    assert "hits" in results or "results" in results

    report = bridge.verify()
    assert isinstance(report, dict)


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_verify_deep(tmp_path: Path):
    mv2 = tmp_path / "deep-test.mv2"
    bridge = MemvidBridge(mv2)
    bridge.create()
    bridge.put(uri="swarm://deep", title="test", body=b"deep verify content")

    report = bridge.verify(deep=True)
    assert isinstance(report, dict)


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_pdf_extraction_survives_dependency_upgrade(tmp_path: Path):
    content = b"BT /F1 18 Tf 40 100 Td (Orchard compatibility invoice) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    bridge = MemvidBridge(tmp_path / "pdf.mv2")
    bridge.create()
    bridge.put(uri="file:///invoice.pdf", title="PDF document", body=bytes(pdf))
    results = bridge.search("Orchard compatibility", top_k=5)
    assert "Orchard compatibility invoice" in json.dumps(results)
    assert isinstance(bridge.verify(deep=True), dict)
