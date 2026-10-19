"""Integration test: full put/search cycle via MemvidBridge (skipped if binary missing)."""

import json
import io
import zipfile
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


def office_archive(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, body in files.items():
            archive.writestr(name, body)
    return stream.getvalue()


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
@pytest.mark.parametrize("extension,files", [
    ("docx", {"word/document.xml": '<w:document xmlns:w="urn:word"><w:body><w:p><w:r><w:t>Orchard A&amp;B &#65;&#x42; &lt;C&gt;</w:t></w:r><w:r><w:t xml:space="preserve"> inline tail </w:t></w:r></w:p></w:body></w:document>'}),
    ("pptx", {"ppt/slides/slide1.xml": '<p:sld xmlns:p="urn:presentation" xmlns:a="urn:drawing"><a:p><a:r><a:t>Orchard A&amp;B &#65;&#x42; &lt;C&gt;</a:t></a:r><a:r><a:t> inline tail </a:t></a:r></a:p></p:sld>'}),
])
def test_office_xml_entities(tmp_path: Path, extension, files):
    bridge = MemvidBridge(tmp_path / f"{extension}.mv2")
    bridge.create()
    bridge.put(uri=f"file:///document.{extension}", title="Office document", body=office_archive(files))
    results = json.dumps(bridge.search("Orchard", top_k=5))
    assert "Orchard A&B AB <C> inline tail" in results


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_legacy_xls_values(tmp_path: Path):
    bridge = MemvidBridge(tmp_path / "xls.mv2")
    bridge.create()
    bridge.put(uri="file:///ledger.xls", title="Legacy workbook", body=(Path(__file__).parent / "fixtures/reader-compat.xls").read_bytes())
    results = json.dumps(bridge.search("Orchard", top_k=5))
    for expected in ["1234.5", "true", "45292", "1.5"]:
        assert expected in results


@pytest.mark.skipif(not bridge_available, reason=skip_reason)
def test_xlsx_values_and_metadata(tmp_path: Path):
    files = {
        "_rels/.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "[Content_Types].xml": '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/></Types>',
        "xl/workbook.xml": '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Orchard &amp; Ledger" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/sharedStrings.xml": '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="1" uniqueCount="1"><si><r><t xml:space="preserve">Shared </t></r><r><t>A&amp;B</t></r></si></sst>',
        "xl/styles.xml": '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><numFmts count="1"><numFmt numFmtId="164" formatCode="yyyy-mm-dd"/></numFmts><cellXfs count="2"><xf numFmtId="0"/><xf numFmtId="164"/></cellXfs></styleSheet>',
        "xl/worksheets/sheet1.xml": '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Orchard A&amp;B</t></is></c><c r="B1"><v>1234.5</v></c><c r="C1" t="b"><v>1</v></c><c r="D1" s="1"><v>45292</v></c><c r="E1" t="s"><v>0</v></c></row></sheetData><mergeCells count="1"><mergeCell ref="A2:B2"/></mergeCells></worksheet>',
    }
    bridge = MemvidBridge(tmp_path / "xlsx.mv2")
    bridge.create()
    bridge.put(uri="file:///ledger.xlsx", title="Modern workbook", body=office_archive(files))
    results = json.dumps(bridge.search("Orchard", top_k=5))
    for expected in ["Orchard", "A&B", "1234.5", "true", "45292", "Shared A&B"]:
        assert expected in results
