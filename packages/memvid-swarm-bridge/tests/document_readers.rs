use memvid_core::reader::xlsx_ooxml::{parse_ooxml_metadata, NumFmtKind};
use memvid_core::XlsxReader;

#[test]
fn spreadsheet_metadata_and_structured_text_survive_migration() {
    let bytes = include_bytes!("../../techtide-swarm/tests/fixtures/reader-compat.xlsx");
    let metadata = parse_ooxml_metadata(bytes).unwrap();
    assert_eq!(metadata.num_fmt_for_xf(1), NumFmtKind::Date);
    let merged = &metadata.merged_regions["Orchard & Ledger"];
    assert_eq!(merged.len(), 1);
    assert_eq!(
        (
            merged[0].top_row,
            merged[0].left_col,
            merged[0].bottom_row,
            merged[0].right_col
        ),
        (1, 0, 1, 1)
    );
    let result = XlsxReader::extract_structured(bytes).unwrap();
    assert!(result.text.contains("Orchard"));
    assert!(result.text.contains("Shared A&B"));
    assert!(result.text.contains("1234.5"));
}
