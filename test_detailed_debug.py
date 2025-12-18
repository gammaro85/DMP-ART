from utils.extractor import DMPExtractor
from docx import Document

print("Detailed Debug: Document Processing")
print("=" * 80)

# Initialize extractor with debug
extractor = DMPExtractor(debug_mode=True)

# Load document
doc = Document('uploads/Data Management Plan_S2025.docx')

# Extract all content (mimicking process_docx internals)
print("\n1. EXTRACTING CONTENT FROM TABLES")
print("-" * 80)

all_content = []

# Extract from tables (this is what process_docx does)
for table in doc.tables:
    table_content = extractor.extract_table_content(table)
    all_content.extend(table_content)

print(f"Total items extracted: {len(all_content)}")
print(f"\nFirst 10 items:")
for i, item in enumerate(all_content[:10]):
    print(f"{i+1}. [{len(item)} chars] {item[:120]}...")

print("\n\n2. TESTING FALLBACK LOGIC ON FIRST FEW ITEMS")
print("-" * 80)

# Test fallback on first few items
for i, item in enumerate(all_content[:5]):
    print(f"\n--- Item {i+1} ---")
    print(f"Text: {item[:100]}...")

    # Test section detection
    detected_section = extractor.detect_section_from_text(item, is_pdf=False)
    print(f"Section detected: {detected_section}")

    # If no section, test fallback
    if not detected_section:
        detected_sub, inferred_sec = extractor._detect_subsection_with_section_inference(item, is_pdf=False)
        print(f"Fallback - Subsection: {detected_sub}")
        print(f"Fallback - Inferred section: {inferred_sec}")
